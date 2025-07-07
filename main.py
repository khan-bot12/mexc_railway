import logging 
from fastapi import FastAPI, Request
from trade import place_order, test_connection
import uvicorn

app = FastAPI()

# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("main")

@app.post("/webhook")
async def webhook(request: Request):
    try:
        logger.info("📥 Incoming webhook for API test")
        result = test_connection()
        logger.info(f"📤 Test Result: {result}")
        return result
    except Exception as e:
        logger.error(f"❌ Error handling webhook: {e}")
        return {"error": str(e)}

# To run locally with: uvicorn main:app --host 0.0.0.0 --port 10000 --reload
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)
