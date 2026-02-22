from fastapi import APIRouter
from app.api.v1 import detection, analysis, alerts, health

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(detection.router, prefix="/detection", tags=["detection"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
