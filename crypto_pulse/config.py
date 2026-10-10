import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("CRYPTO_API_BASE_URL", "https://api.binance.com")
DEFAULT_SYMBOL = os.getenv("CRYPTO_SYMBOL", "BTCUSDT")
DEFAULT_INTERVAL = os.getenv("CRYPTO_INTERVAL", "1h")
DEFAULT_LIMIT = int(os.getenv("CRYPTO_LIMIT", "100"))
