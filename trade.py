import time
import hmac
import hashlib
import requests
import os
from dotenv import load_dotenv
import logging

# Load API keys from .env
load_dotenv()
API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_API_SECRET")

# Setup logging
logger = logging.getLogger("trade")
logger.info(f"🔍 API KEY from .env: {API_KEY}")
logger.info(f"🔍 API SECRET loaded: {'Yes' if API_SECRET else 'No'}")

# MEXC API URL
BASE_URL = "https://contract.mexc.com"

def get_timestamp():
    return str(int(time.time() * 1000))

def sign_request(params: dict, secret: str) -> str:
    query_string = "&".join([f"{key}={params[key]}" for key in sorted(params)])
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def place_order(action: str, symbol: str, quantity: float, leverage: int):
    try:
        logger.info("🟢 Placing new order...")

        side = 1 if action.lower() == "buy" else 2
        symbol = symbol.replace("USDT", "_USDT")

        params = {
            "api_key": API_KEY,
            "req_time": get_timestamp(),
            "symbol": symbol,
            "price": "0",  # Market order
            "vol": str(quantity),
            "leverage": str(leverage),
            "side": side,
            "open_type": 2,
            "positionId": 0,
            "orderType": 1,
            "type": 1
        }

        params["sign"] = sign_request(params, API_SECRET)

        logger.info(f"🔐 Order Payload: {params}")

        for attempt in range(3):
            try:
                response = requests.post(f"{BASE_URL}/api/v1/private/order/submit", data=params, timeout=10)
                logger.info(f"📩 Raw response text: {response.text}")
                logger.info(f"📊 Status Code: {response.status_code}")
                return response.json()
            except requests.exceptions.ReadTimeout:
                logger.warning(f"⚠️ ReadTimeout: retrying ({attempt+1}/3)...")
                time.sleep(2)

        return {"error": "Timeout after 3 retries"}

    except Exception as e:
        logger.error(f"❌ Error placing order: {e}")
        return {"error": str(e)}

def test_connection():
    logger.info("🔍 Testing MEXC API connection with open orders request...")

    params = {
        "api_key": API_KEY,
        "req_time": get_timestamp(),
        "symbol": "ETH_USDT"
    }

    params["sign"] = sign_request(params, API_SECRET)

    try:
        response = requests.get(f"{BASE_URL}/api/v1/private/order/list/open", params=params, timeout=10)
        logger.info(f"✅ API Connection Response: {response.text}")
        return response.json()
    except Exception as e:
        logger.error(f"❌ API Test Failed: {e}")
        return {"error": str(e)}
