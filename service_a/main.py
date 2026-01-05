from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import logging
import uvicorn

# -----------------------------
# Logging configuration
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("service_a")

app = FastAPI(title="Service A - Input Logger")

# -----------------------------
# Request model
# -----------------------------
class InputData(BaseModel):
    data: str
    forward_to_model: bool = True

# Service B URL (hard-coded for the lab)
SERVICE_B_URL = "http://localhost:8001/predict"


@app.get("/")
def read_root():
    return {"service": "Service A - Input Logger", "status": "running"}


@app.post("/process")
async def process_input(input_data: InputData):
    # 1) Log the received input
    logger.info("Received input: %s", input_data.data)

    # 2) Optionally forward to Service B
    if input_data.forward_to_model:
        try:
            response = requests.post(
                SERVICE_B_URL,
                json={"input": input_data.data},
                timeout=3,  # keep short so failures return quickly
            )
            return {
                "status": "Input logged successfully",
                "model_prediction": response.json(),
            }
        except requests.RequestException as e:
            logger.error("Failed to reach Service B: %s", e)
            raise HTTPException(
                status_code=503,
                detail=f"Service B is unavailable: {str(e)}",
            )

    # 3) If not forwarding, just return logging status
    return {"status": "Input logged successfully"}


@app.get("/health")
def health_check():
    return {"service": "Service A", "status": "healthy"}


if __name__ == "__main__":
    # Run with: python main.py
    # For production you'd usually run: uvicorn main:app --host 0.0.0.0 --port 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
