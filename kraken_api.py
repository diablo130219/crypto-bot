import requests
import logging
from config import KRAKEN_BASE_URL, CANDLE_INTERVAL, CANDLE_LIMIT

logger = logging.getLogger(__name__)

def get_ohlcv(symbol):
    url = f"{KRAKEN_BASE_URL}/OHLC"
    params = {"pair": symbol, "interval": CANDLE_INTERVAL, "count": CANDLE_LIMIT}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("error"):
            logger.error(f"Kraken API error per {symbol}: {data['error']}")
            return None
        result_key = list(data["result"].keys())[0]
        return [
            {"time": c[0], "open": float(c[1]), "high": float(c[2]),
             "low": float(c[3]), "close": float(c[4]), "volume": float(c[6])}
            for c in data["result"][result_key]
        ]
    except requests.RequestException as e:
        logger.error(f"Errore fetch Kraken {symbol}: {e}")
        return None
