import requests
import logging
from config import CANDLE_INTERVAL, CANDLE_LIMIT

logger = logging.getLogger(__name__)

BINANCE_BASE_URL = "https://api.binance.com/api/v3"

def get_ohlcv(symbol):
    url = f"{BINANCE_BASE_URL}/klines"
    params = {
        "symbol": symbol,
        "interval": CANDLE_INTERVAL,
        "limit": CANDLE_LIMIT
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [
            {
                "time": c[0],
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
                "volume": float(c[5])
            }
            for c in data
        ]
    except requests.RequestException as e:
        logger.error(f"Errore fetch Binance {symbol}: {e}")
        return None
