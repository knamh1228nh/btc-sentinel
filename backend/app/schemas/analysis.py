from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    context: str = ""
    detection_data: dict = {}

class AnalysisResponse(BaseModel):
    summary: str
    risk_level: str
