from fastapi import APIRouter
from app.schemas.analysis import AnalysisRequest, AnalysisResponse

router = APIRouter()

@router.post("/", response_model=AnalysisResponse)
def run_analysis(request: AnalysisRequest):
    """System 2: Gemini 분석 API"""
    return AnalysisResponse(summary="Analysis placeholder", risk_level="low")
