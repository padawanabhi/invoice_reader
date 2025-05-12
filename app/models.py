from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .database import Base

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    ocr_text = Column(Text, nullable=True)
    merchant = Column(String, nullable=True)
    date = Column(String, nullable=True)
    total = Column(String, nullable=True)
    group_id = Column(Integer, nullable=True) 