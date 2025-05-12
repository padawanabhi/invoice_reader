from pydantic import BaseModel
from typing import Optional

class ReceiptResponse(BaseModel):
    id: int
    filename: str
    status: str
    merchant: Optional[str] = None
    date: Optional[str] = None
    total: Optional[str] = None
    group_id: Optional[int] = None

    class Config:
        orm_mode = True 