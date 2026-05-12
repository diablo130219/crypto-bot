import logging
from datetime import datetime
from binance_api import get_ohlcv
from config import (
    SYMBOLS, SYMBOL_NAMES,
    RSI_PERIOD, MA_FAST, MA_SLOW,
    MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    WEIGHT_RSI, WEIGHT_MACD, WEIGHT_MA,
    BUY_THRESHOLD, SELL_THRESHOLD,
    MIN_MINUTES_BETWEEN_SIGNALS,
    VOLUME_PERIOD, VOLUME_MULTIPLIER
)

logger = logging.getLogger(__name__)


def calc_rsi(closes, period=14):
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    if len(gains) < period:
        return 50.0
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    return 100 - (100 / (1 + avg_gain / avg_loss))


def calc_ema(values, period):
    ema, k = [], 2 / (period + 1)
    for i, v in enumerate(values):
        ema.append(v if i == 0 else v * k + ema[-1] * (1 - k))
    return ema


def calc_macd(closes, fast=12, slow=26, signal=9):
    fast_ema = calc_ema(closes, fast)
    slow_ema = calc_ema(closes, slow)
    macd_line = [f - s for f, s in zip(fast_ema, slow_ema)]
    signal_line = calc_ema(macd_line, signal)
    return macd_line[-1], signal_line[-1]


def calc_sma(values, period):
    return sum(values[-period:]) / period if len(values) >= period else values[-1]


def calc_volume_ratio(candles, period=20):
    """Rapporto tra volume attuale e volume medio delle ultime N candele."""
    if len(candles) < period + 1:
        return 1.0
    volumes = [c["volume"] for c in candles]
    avg_volume = sum(volumes[-period-1:-1]) / period
    current_volume = volumes[-1]
    if avg_volume == 0:
        return 1.0
    return current_volume / avg_volume


def score_rsi(rsi):
    if rsi <= 20:
        return 95
    if rsi <= 30:
        return 80
    if rsi <= 40:
        return 65
    if rsi <= 50:
        return 55
    if rsi <= 60:
        return 45
    if rsi <= 70:
        return 30
    if rsi <= 80:
        return 15
    return 5


def score_macd(macd, signal):
    diff = macd - signal
    denom = max(abs(signal), 0.0001)
    if diff > 0:
        return 55 + min(diff / denom, 1.0) * 40
    return 45 - min(abs(diff) / denom, 1.0) * 40


def score_ma(ma_fast, ma_slow):
    if ma_slow == 0:
        return 50
    pct = (ma_fast - ma_slow) / ma_slow * 100
    if pct > 3:
        return 85
    if pct > 1:
        return 70
    if pct > 0:
        return 55
    if pct > -1:
        return 45
    if pct > -3:
        return 30
    return 15


def composite_score(rsi_s, macd_s, ma_s):
    total = WEIGHT_RSI + WEIGHT_MACD + WEIGHT_MA
    return round((rsi_s * WEIGHT_RSI + macd_s * WEIGHT_MACD + ma_s * WEIGHT_MA) / total, 1)


def signal_from_score(score):
    if score >= BUY_THRESHOLD:
        return "BUY"
    if score <= SELL_THRESHOLD:
        return "SELL"
    return "HOLD"


def confidence_count(signal, rsi, macd, macd_sig, ma_fast, ma_slow):
    if signal == "BUY":
        checks = [rsi <= 55, macd > macd_sig, ma_fast >= ma_slow]
    elif signal == "SELL":
        checks = [rsi >= 45, macd < macd_sig, ma_fast <= ma_slow]
    else:
        return 0
    return sum(1 for x in checks if x)


class SignalEngine:
    def __init__(self):
        self._last_signal = {}

    def _can_send(self, symbol, signal):
        last = self._last_signal.get(symbol)
        if not last or last["signal"] != signal:
            return True
        minutes = (datetime.now() - last["time"]).total_seconds() / 60
        return minutes >= MIN_MINUTES_BETWEEN_SIGNALS

    def analyze(self, symbol):
        candles = get_ohlcv(symbol)
        if not candles or len(candles) < MACD_SLOW + MACD_SIGNAL + 10:
            return None

        closes = [c["close"] for c in candles]
        price = closes[-1]
        rsi = calc_rsi(closes, RSI_PERIOD)
        macd, macd_sig = calc_macd(closes, MACD_FAST, MACD_SLOW, MACD_SIGNAL)
        ma_fast = calc_sma(closes, MA_FAST)
        ma_slow = calc_sma(closes, MA_SLOW)
        volume_ratio = calc_volume_ratio(candles, VOLUME_PERIOD)

        score = composite_score(score_rsi(rsi), score_macd(macd, macd_sig), score_ma(ma_fast, ma_slow))
        signal = signal_from_score(score)
        conf = confidence_count(signal, rsi, macd, macd_sig, ma_fast, ma_slow)

        if signal in ("BUY", "SELL") and conf < 2:
            signal = "HOLD"

        # Filtro volume: blocca segnali se il volume e' troppo basso
        volume_ok = volume_ratio >= VOLUME_MULTIPLIER
        if signal in ("BUY", "SELL") and not volume_ok:
            logger.info(f"{symbol}: segnale {signal} bloccato - volume basso ({volume_ratio:.2f}x media)")
            signal = "HOLD"

        return {
            "symbol": SYMBOL_NAMES.get(symbol, symbol),
            "raw_symbol": symbol,
            "price": price,
            "score": score,
            "signal": signal,
            "confidence": conf,
            "volume_ratio": round(volume_ratio, 2),
            "volume_ok": volume_ok,
            "indicators": {
                "rsi": rsi,
                "macd": macd,
                "macd_signal": macd_sig,
                "ma_fast": ma_fast,
                "ma_slow": ma_slow,
            },
        }

    def analyze_all(self):
        results = {}
        for symbol in SYMBOLS:
            result = self.analyze(symbol)
            if not result:
                continue

            display_name = result["symbol"]
            signal = result["signal"]
            ind = result["indicators"]

            if signal in ("BUY", "SELL") and self._can_send(symbol, signal):
                self._last_signal[symbol] = {"signal": signal, "time": datetime.now()}
                results[display_name] = result
                logger.info(
                    f"{display_name}: {signal} | score={result['score']} | conf={result['confidence']}/3 | "
                    f"RSI={ind['rsi']:.1f} | MACD={ind['macd']:.4f}/{ind['macd_signal']:.4f} | "
                    f"MA={ind['ma_fast']:.2f}/{ind['ma_slow']:.2f} | "
                    f"Volume={result['volume_ratio']}x"
                )
            else:
                logger.info(
                    f"{display_name}: HOLD | score={result['score']} | RSI={ind['rsi']:.1f} | "
                    f"Volume={result['volume_ratio']}x"
                )
        return results
