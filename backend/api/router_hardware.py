from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import logging

from backend.hil_mock import deploy_to_hardware

logger = logging.getLogger("sentinel-router-hardware")

router = APIRouter()

class DeployRequest(BaseModel):
    spacings: List[float]
    snr_db: float = 20.0

@router.post("/deploy")
def deploy_hardware(request: DeployRequest):
    logger.info("Received hardware deployment request.")
    try:
        result = deploy_to_hardware(request.spacings, request.snr_db)
        return result
    except Exception as e:
        logger.error(f"Deployment failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
