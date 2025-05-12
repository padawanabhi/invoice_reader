import os
from celery import Celery
import pytesseract
from PIL import Image
import json
import requests # For local LLM
from app.database import SessionLocal
from app.models import Receipt

LLM_MODE = os.getenv("LLM_MODE", "local")

def extract_fields_with_llm(ocr_text):
    prompt = (
        "Extract the following fields from this receipt OCR text:\n"
        "- merchant (store name)\n"
        "- date (in YYYY-MM-DD or DD.MM.YYYY format)\n"
        "- total (final amount, with currency if possible)\n"
        "Return a JSON object with keys: merchant, date, total.\n"
        "OCR text:\n"
        f"{ocr_text}\n"
        "JSON:"
    )

    content = "{}"
    try:
        if LLM_MODE == "cloud":
            # Use OpenAI API
            import openai
            openai.api_key = os.getenv("OPENAI_API_KEY")
            if not openai.api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set for cloud mode")

            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for extracting structured data from receipts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=256,
            )
            content = response.choices[0].message.content
        else:
            # Use local LLM (Ollama, LM Studio, etc.)
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            if not ollama_url:
                 raise ValueError("OLLAMA_BASE_URL environment variable not set for local mode")

            data = {
                "model": "llama3.2",  # or your local model name
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant for extracting structured data from receipts."},
                    {"role": "user", "content": prompt}
                ],
                "format": "json", # Request JSON output if model supports it
                "stream": False
            }
            print(f"Sending request to local LLM at {ollama_url}")
            r = requests.post(f"{ollama_url}/api/chat", json=data, timeout=120) # Increased timeout
            r.raise_for_status()
            response_data = r.json()
            content = response_data.get("message", {}).get("content", "{}")
            print(f"Received response from local LLM: {content[:200]}...")

    except Exception as llm_error:
        print(f"Error communicating with LLM ({LLM_MODE} mode): {llm_error}")
        return None, None, None # Return None if LLM fails

    # Parse the JSON from the LLM's response
    try:
        content = content.strip()
        # Clean potential markdown code blocks
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        result = json.loads(content)
        merchant = result.get("merchant")
        date = result.get("date")
        total = result.get("total")
        print(f"Successfully parsed LLM response: Merchant={merchant}, Date={date}, Total={total}")
    except json.JSONDecodeError as json_error:
        print(f"Failed to parse LLM JSON response: {json_error}")
        print(f"Raw LLM content: {content}")
        merchant = date = total = None
    except Exception as parse_error:
        print(f"An unexpected error occurred during LLM response parsing: {parse_error}")
        merchant = date = total = None

    return merchant, date, total

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery(
    "invoice_reader",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

@celery_app.task
def test_task(x, y):
    return x + y

@celery_app.task
def process_receipt_task(receipt_id):
    db = SessionLocal()
    receipt = None # Initialize receipt
    try:
        receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
        if not receipt:
            print(f"Receipt {receipt_id} not found")
            return

        file_path = os.path.join("uploads", receipt.filename)
        if not os.path.exists(file_path):
            print(f"File {file_path} not found for receipt {receipt_id}")
            receipt.status = "error_file_not_found"
            db.commit()
            return

        print(f"Starting OCR for receipt {receipt_id}...")
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        print(f"OCR completed for receipt {receipt_id}. Text length: {len(text)}")
        receipt.ocr_text = text # Save OCR text early

        print(f"Starting LLM extraction for receipt {receipt_id} using {LLM_MODE} mode...")
        merchant, date, total = extract_fields_with_llm(text)

        # Update DB
        receipt.merchant = merchant
        receipt.date = date
        receipt.total = total
        receipt.status = "processed"
        db.commit()
        print(f"Successfully processed receipt {receipt_id}")

    except pytesseract.TesseractNotFoundError:
        print(f"Tesseract not found. Ensure it's installed in the celery_worker container.")
        if receipt: receipt.status = "error_tesseract"
    except Exception as e:
        print(f"Error processing receipt {receipt_id}: {e}")
        if receipt: receipt.status = "error_processing"
    finally:
        if receipt and db.is_active: # Commit status changes on error
             try:
                 db.commit()
             except Exception as commit_err:
                 print(f"Failed to commit error status for receipt {receipt_id}: {commit_err}")
        if db:
            db.close() 