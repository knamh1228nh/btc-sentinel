from pydantic import BaseModel

class AnalysisResult(BaseModel):
    summary: str
    risk_level: str
    raw_response: str
