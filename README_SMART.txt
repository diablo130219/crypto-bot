CryptoNow Smart Bot - File da sostituire nel repo crypto-bot

Sostituisci questi file nel repo crypto-bot:
- bot.py
- signals.py
- config.py

Controlla requirements.txt:
- python-telegram-bot
- requests

Variabili Railway richieste:
- TELEGRAM_TOKEN
- TELEGRAM_CHAT_ID
- TRACKER_URL
- TRACKER_API_TOKEN

Cosa cambia:
- BUY/SELL = segnali veri, inviati anche al tracker
- WATCH_BUY/WATCH_SELL = pre-segnali Telegram, NON aprono trade nel tracker
- Anti-spam per simbolo e tipo segnale
- Messaggi Telegram in HTML più stabili
