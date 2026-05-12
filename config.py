"""
Configurazione CryptoNow Bot v2 - Binance + Filtro Volume
"""
import os

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Tracker
TRACKER_URL = os.getenv("TRACKER_URL", "https://tracker-crypto.onrender.com")
TRACKER_API_TOKEN = os.getenv("TRACKER_API_TOKEN", "")

# Binance
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "LINKUSDT"]
SYMBOL_NAMES = {
    "BTCUSDT": "BTC/USDT",
    "ETHUSDT": "ETH/USDT",
    "SOLUSDT": "SOL/USDT",
    "XRPUSDT": "XRP/USDT",
    "LINKUSDT": "LINK/USDT",
}

# Timeframe
CANDLE_INTERVAL = "1h"
CANDLE_LIMIT = 200
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "60"))

# Indicatori
RSI_PERIOD = 14
MA_FAST = 20
MA_SLOW = 50
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Pesi scoring
WEIGHT_RSI = 35
WEIGHT_MACD = 40
WEIGHT_MA = 25

# Soglie segnale
BUY_THRESHOLD = 63
SELL_THRESHOLD = 40

# Anti-spam
MIN_MINUTES_BETWEEN_SIGNALS = 60

# Filtro Volume
VOLUME_PERIOD = 20          # media delle ultime 20 candele
VOLUME_MULTIPLIER = 1.5     # volume attuale deve essere almeno 1.5x la media
