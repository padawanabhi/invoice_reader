from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Path
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import shutil
from app import models, database, schemas
from app.celery_worker import process_receipt_task

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/receipts/upload", response_model=schemas.ReceiptResponse)
async def upload_receipt(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Save file
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create DB record
    receipt = models.Receipt(filename=file.filename, status="pending")
    db.add(receipt)
    db.commit()
    db.refresh(receipt)

    # Enqueue Celery task
    process_receipt_task.delay(receipt.id)

    return receipt

@app.get("/receipts/{receipt_id}", response_model=schemas.ReceiptResponse)
def get_receipt(receipt_id: int = Path(...), db: Session = Depends(get_db)):
    receipt = db.query(models.Receipt).filter(models.Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt

@app.get("/health")
def health_check():
    return {"status": "ok"} 