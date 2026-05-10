from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
import time

from backend.ml.inference import predict_spacings, verify_spacings
from backend.agent import parse_and_execute_intent

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("sentinel-api")

app = FastAPI(title="Radar Array Spacing Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictRequest(BaseModel):
    target_error: float

class PredictResponse(BaseModel):
    spacings: List[float]
    positions: List[float]

class VerifyRequest(BaseModel):
    spacings: List[float]
    target_error: float
    snr_db: Optional[float] = 20.0

class VerifyResponse(BaseModel):
    achieved_error: float
    target_error: float
    crlb_error: float
    acceptable: bool

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    data: Optional[dict] = None

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    start_time = time.time()
    logger.info(f"Received predict request for target error: {request.target_error}°")
    try:
        result = predict_spacings(request.target_error)
        latency = (time.time() - start_time) * 1000
        logger.info(f"Prediction successful in {latency:.2f}ms. Generated {len(result['spacings'])} spacings.")
        return result
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify", response_model=VerifyResponse)
def verify(request: VerifyRequest):
    logger.info(f"Received verify request for target error: {request.target_error}° at {request.snr_db} dB SNR")
    try:
        result = verify_spacings(request.spacings, request.target_error, request.snr_db)
        logger.info(f"Verification completed. Achieved: {result['achieved_error']:.4f}°, CRLB: {result['crlb_error']:.4f}°")
        return result
    except Exception as e:
        logger.error(f"Verification failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model/info")
def get_model_info():
    return {
        "architecture": "Multi-layer perceptron (MLP)",
        "inputs": "Target RMS angular error",
        "outputs": "Optimal element spacings [d1, d2, d3]"
    }

@app.post("/chat", response_model=ChatResponse)
def chat_agent(request: ChatRequest):
    logger.info("Received chat request")
    try:
        result = parse_and_execute_intent(request.message)
        logger.info("Chat request processed successfully")
        return result
    except Exception as e:
        logger.error(f"Chat request failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
