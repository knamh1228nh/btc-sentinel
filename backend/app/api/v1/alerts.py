from fastapi import APIRouter
from app.schemas.alert import AlertListResponse

router = APIRouter()

@router.get("/", response_model=AlertListResponse)
def list_alerts():
    """알림 목록 API"""
    return AlertListResponse(alerts=[], total=0)
