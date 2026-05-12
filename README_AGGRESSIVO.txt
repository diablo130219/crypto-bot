CryptoNow Smart Bot - AGGRESSIVO

Sostituisci nel repo crypto-bot:
- signals.py
- config.py

Questa versione:
- elimina WATCH_BUY / WATCH_SELL
- invia solo BUY / SELL
- usa soglie aggressive: BUY >= 55, SELL <= 45
- anti-spam: 45 minuti
- mantiene confidence nei log

Controlla requirements.txt:
requests
python-telegram-bot
