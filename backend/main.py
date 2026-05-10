from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from typing import List, Optional
import logging
import time

from backend.ml.inference import predict_spacings, verify_spacings, MODEL_PATH
from backend.ml.dataset import generate_synthetic_dataset
from backend.ml.model import train_model
from backend.agent import parse_and_execute_intent
from backend.hil_mock import deploy_to_hardware

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

# Instrument the app for Prometheus metrics
Instrumentator().instrument(app).expose(app)

class PredictRequest(BaseModel):
    target_error: float

class PredictResponse(BaseModel):
    spacings: List[float]
    positions: List[float]

class VerifyRequest(BaseModel):
    spacings: List[float]
    target_error: float
    snr_db: Optional[float] = 20.0

class PatternPoint(BaseModel):
    angle: float
    magnitude: float

class VerifyResponse(BaseModel):
    achieved_error: float
    target_error: float
    crlb_error: float
    acceptable: bool
    pattern: List[PatternPoint]

class RetrainRequest(BaseModel):
    num_samples: int = 2000
    epochs: int = 10
    snr_db: float = 20.0

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    reply: str
    data: Optional[dict] = None

class DeployRequest(BaseModel):
    spacings: List[float]
    snr_db: float = 20.0

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

def background_retrain_task(num_samples: int, epochs: int, snr_db: float):
    logger.info(f"Starting background retraining with {num_samples} samples at {snr_db} dB SNR...")
    start_time = time.time()
    try:
        X, Y = generate_synthetic_dataset(num_samples=num_samples, snr_db=snr_db)
        train_model(X, Y, model_path=MODEL_PATH, epochs=epochs)
        elapsed = time.time() - start_time
        logger.info(f"Background retraining completed successfully in {elapsed:.2f}s.")
    except Exception as e:
        logger.error(f"Background retraining failed: {e}", exc_info=True)

@app.post("/model/retrain")
def retrain_model(request: RetrainRequest, background_tasks: BackgroundTasks):
    logger.info(f"Received request to retrain model with {request.num_samples} samples.")
    background_tasks.add_task(background_retrain_task, request.num_samples, request.epochs, request.snr_db)
    return {"message": "Retraining job has been queued in the background."}

@app.post("/chat", response_model=ChatResponse)
def chat_agent(request: ChatRequest):
    logger.info(f"Received chat request from session {request.session_id}")
    try:
        result = parse_and_execute_intent(request.message, request.session_id)
        logger.info("Chat request processed successfully")
        return result
    except Exception as e:
        logger.error(f"Chat request failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deploy")
def deploy_hardware(request: DeployRequest):
    logger.info("Received hardware deployment request.")
    try:
        result = deploy_to_hardware(request.spacings, request.snr_db)
        return result
    except Exception as e:
        logger.error(f"Deployment failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
