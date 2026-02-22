from pydantic import BaseModel
from typing import List

class AlertItem(BaseModel):
    id: str
    title: str
    severity: str

class AlertListResponse(BaseModel):
    alerts: List[AlertItem]
    total: int
