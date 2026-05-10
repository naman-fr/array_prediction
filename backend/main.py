from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import logging

from backend.api import router_ml, router_chat, router_hardware
from backend.db.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

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

# Include Routers
app.include_router(router_ml.router, tags=["Machine Learning"])
app.include_router(router_chat.router, tags=["Agentic Chat"])
app.include_router(router_hardware.router, tags=["Hardware In The Loop"])
