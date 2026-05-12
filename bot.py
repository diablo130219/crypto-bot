import time
import requests

from config import (
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID,
    TRACKER_URL,
    TRACKER_API_TOKEN,
    CHECK_INTERVAL_MINUTES,
)

from signals import SignalEngine


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(
            url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML"
            },
            timeout=10
        )
    except Exception as e:
        print("Errore Telegram:", e)


def send_to_tracker(symbol, side, price, score):
    try:
        requests.post(
            TRACKER_URL + "/api/trade",
            json={
                "token": TRACKER_API_TOKEN,
                "symbol": symbol,
                "side": side,
                "entry": price,
                "score": score,
                "status": "open",
                "source": "bot"
            },
            timeout=10
        )
    except Exception as e:
        print("Errore tracker:", e)


def format_telegram_message(symbol, signal, price, score, confidence, rsi, macd_signal, trend, volume_ratio, volume_ok):
    emoji = "🟢" if signal == "BUY" else "🔴"
    volume_emoji = "📈" if volume_ok else "⚠️"

    entry = price
    stop = round(price * 0.975, 2)
    target = round(price * 1.035, 2)

    return (
        f"{emoji} <b>{signal} {symbol}</b>\n"
        f"-------------------\n\n"
        f"Prezzo: <b>${price}</b>\n"
        f"Score: <b>{score}/100</b>\n"
        f"Confidence: <b>{confidence}/3</b>\n\n"
        f"<b>SETUP</b>\n"
        f"Entry: <b>${entry}</b>\n"
        f"Stop: <b>${stop}</b>\n"
        f"Target: <b>${target}</b>\n\n"
        f"<b>INDICATORI</b>\n"
        f"RSI: {round(rsi, 1)}\n"
        f"MACD: {macd_signal}\n"
        f"Trend: {trend}\n"
        f"{volume_emoji} Volume: {volume_ratio}x media\n\n"
        f"CryptoNow Bot v2"
    )


def run_bot():
    print("Bot v2 avviato con filtro volume...")
    engine = SignalEngine()

    while True:
        try:
            results = engine.analyze_all()

            for display_name, result in results.items():
                signal = result["signal"]
                score = result["score"]
                price = result["price"]
                confidence = result["confidence"]
                volume_ratio = result["volume_ratio"]
                volume_ok = result["volume_ok"]

                indicators = result["indicators"]
                rsi = indicators["rsi"]
                macd = indicators["macd"]
                macd_sig = indicators["macd_signal"]
                ma_fast = indicators["ma_fast"]
                ma_slow = indicators["ma_slow"]

                trend = "Rialzista" if ma_fast >= ma_slow else "Ribassista"
                macd_label = f"{macd:.4f} / {macd_sig:.4f}"

                print(f"{display_name}: {signal} | score={score} | volume={volume_ratio}x")

                if signal in ("BUY", "SELL"):
                    msg = format_telegram_message(
                        display_name,
                        signal,
                        price,
                        score,
                        confidence,
                        rsi,
                        macd_label,
                        trend,
                        volume_ratio,
                        volume_ok
                    )
                    send_telegram_message(msg)

                    if signal == "BUY":
                        raw_symbol = result.get("raw_symbol", display_name)
                        send_to_tracker(raw_symbol, signal, price, score)

        except Exception as e:
            print("Errore:", e)

        time.sleep(CHECK_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    send_telegram_message("CryptoNow Bot v2 avviato - Filtro Volume attivo ✅")
    run_bot()
