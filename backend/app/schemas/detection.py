from pydantic import BaseModel

class DetectionRequest(BaseModel):
    source: str = "upbit"
    payload: dict = {}

class DetectionResponse(BaseModel):
    detected: bool
    message: str
