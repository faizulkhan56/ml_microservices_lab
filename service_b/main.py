from fastapi import FastAPI
from pydantic import BaseModel
import logging
import uvicorn
import random

# -----------------------------
# Logging configuration
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("service_b")

app = FastAPI(title="Service B - ML Prediction")

# -----------------------------
# Request model
# -----------------------------
class PredictionRequest(BaseModel):
    input: str


# -----------------------------
# A tiny demo "ML model"
# -----------------------------
class SimpleMlModel:
    """A toy model for the lab.

    - picks a random class from a fixed list
    - returns a confidence score (0.7 to 0.99)
    - also returns input length
    """

    def __init__(self):
        self.classes = ["cat", "dog", "bird", "fish", "rabbit"]
        logger.info("ML model initialized")

    def predict(self, input_text: str):
        logger.info("Making prediction for input: %s", input_text)
        predicted_class = random.choice(self.classes)
        confidence = round(random.uniform(0.7, 0.99), 2)

        return {
            "class": predicted_class,
            "confidence": confidence,
            "input_length": len(input_text),
        }


# Initialize our "model"
model = SimpleMlModel()


@app.get("/")
def read_root():
    return {"service": "Service B - ML Prediction", "status": "running"}


@app.post("/predict")
async def predict(request: PredictionRequest):
    logger.info("Received prediction request with input: %s", request.input)

    prediction = model.predict(request.input)

    return {
        "prediction": prediction,
        "message": (
            f"Predicted class: {prediction['class']} "
            f"with {prediction['confidence']*100:.1f}% confidence"
        ),
    }


@app.get("/health")
def health_check():
    return {"service": "Service B", "status": "healthy"}


if __name__ == "__main__":
    # Run with: python main.py
    # For production you'd usually run: uvicorn main:app --host 0.0.0.0 --port 8001
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
