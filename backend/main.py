from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from backend.ml.inference import predict_spacings, verify_spacings
from backend.agent import parse_and_execute_intent

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

class VerifyResponse(BaseModel):
    achieved_error: float
    target_error: float
    acceptable: bool

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    data: Optional[dict] = None

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    try:
        result = predict_spacings(request.target_error)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify", response_model=VerifyResponse)
def verify(request: VerifyRequest):
    try:
        result = verify_spacings(request.spacings, request.target_error)
        return result
    except Exception as e:
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
    try:
        result = parse_and_execute_intent(request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
