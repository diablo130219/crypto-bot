FIX COMPLETO DEFINITIVO - CryptoNow Bot

Sostituisci nel repo crypto-bot:
- bot.py
- signals.py
- config.py

Controlla requirements.txt:
python-telegram-bot
requests

Variabili Railway/Render necessarie:
TELEGRAM_TOKEN
TELEGRAM_CHAT_ID
TRACKER_URL=https://tracker-crypto.onrender.com
TRACKER_API_TOKEN=lo stesso token del tracker

Cosa fa:
- niente WATCH
- solo BUY / SELL
- modalità aggressiva controllata
- anti-spam 45 minuti
- invio Telegram
- invio tracker solo per BUY/SELL
