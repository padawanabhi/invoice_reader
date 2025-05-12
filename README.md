# Invoice Analysis & Export Platform

This project is a web-based platform for uploading invoice/receipt images, extracting key information using OCR and AI (LLM), and allowing users to view the results.

## Features

*   **File Upload:** Upload receipt/invoice images (.png, .jpg) via a React frontend.
*   **OCR Processing:** Tesseract OCR runs asynchronously via Celery to extract text from images.
*   **AI Data Extraction:** Uses a Large Language Model (LLM) - configurable for cloud (OpenAI GPT) or local (Ollama) - to extract structured data (Merchant, Date, Total) from the OCR text.
*   **Database Storage:** Stores receipt metadata, OCR text, and extracted fields in a PostgreSQL database.
*   **Status Check:** View the processing status and extracted data for each uploaded receipt via the UI or API.
*   **Dockerized:** Fully containerized using Docker and Docker Compose for easy setup and deployment.

## Tech Stack

*   **Backend:** FastAPI (Python)
*   **Frontend:** React
*   **Async Tasks:** Celery + Redis
*   **Database:** PostgreSQL + SQLAlchemy + Alembic (for migrations)
*   **OCR:** Tesseract (via pytesseract) + Pillow
*   **AI Extraction:** OpenAI API or Local LLM (e.g., Ollama)
*   **Containerization:** Docker, Docker Compose
*   **Web Server (Frontend):** Nginx

## Prerequisites

*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/)
*   **(Optional) Ollama:** If you want to use a local LLM for data extraction. Install from [ollama.com](https://ollama.com/).

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd invoice_reader
    ```

2.  **Create `.env` File:**
    Create a file named `.env` in the project root directory (`invoice_reader/`) and add the following content:

    ```dotenv
    # .env

    # --- Database & Celery (Defaults should work with Docker Compose) ---
    DATABASE_URL=postgresql://postgres:postgres@db:5432/invoice_db
    CELERY_BROKER_URL=redis://redis:6379/0
    CELERY_RESULT_BACKEND=redis://redis:6379/0

    # --- LLM Configuration ---
    # Set LLM_MODE to 'cloud' or 'local'
    LLM_MODE=cloud

    # Only needed if LLM_MODE=cloud and using OpenAI
    OPENAI_API_KEY=your_openai_api_key_here

    # Only needed if LLM_MODE=local
    # Use host.docker.internal for Docker on Mac/Windows to reach Ollama on host
    # For Linux host, you might need to find the Docker bridge IP or use --network="host"
    OLLAMA_BASE_URL=http://host.docker.internal:11434
    # Example for LM Studio: OLLAMA_BASE_URL=http://host.docker.internal:1234/v1
    ```
    *   **Important:** Replace `your_openai_api_key_here` with your actual OpenAI API key if using `LLM_MODE=cloud`.

3.  **(Optional) Setup Local LLM (Ollama):**
    If you set `LLM_MODE=local` in `.env`:
    *   Make sure the Ollama application is running on your host machine.
    *   Pull the model specified in `app/celery_worker.py` (default is `llama3`):
        ```bash
        ollama pull llama3
        ```

## Running the Application

1.  **Build Docker Images:**
    ```bash
    docker-compose build
    ```

2.  **Start Services:**
    ```bash
    docker-compose up -d
    ```
    This will start the FastAPI backend, React frontend, Celery worker, PostgreSQL database, and Redis broker.

## Using the Application

1.  **Access Frontend:** Open your web browser and navigate to:
    [http://localhost:3000](http://localhost:3000)

2.  **Upload Receipt:**
    *   Click "Choose File" and select an invoice/receipt image (.png, .jpg).
    *   Click "Upload".
    *   You will see the assigned Receipt ID upon successful upload.

3.  **Check Status:**
    *   Enter the Receipt ID obtained after uploading into the "Check Receipt Status" section.
    *   Click "Check".
    *   The status ("pending", "processed", "error_...") and extracted data (Merchant, Date, Total) will be displayed.

## API Endpoints

*   `POST /receipts/upload`: Upload a receipt file (multipart/form-data with 'file' field).
*   `GET /receipts/{receipt_id}`: Get status and details of a specific receipt.
*   `GET /health`: Health check endpoint for the backend.

## Configuration

*   **LLM Mode (`.env` file):**
    *   `LLM_MODE=cloud`: Uses the OpenAI API (requires `OPENAI_API_KEY`).
    *   `LLM_MODE=local`: Uses a local LLM server specified by `OLLAMA_BASE_URL` (requires Ollama or similar running on the host).

## Stopping the Application

```bash
docker-compose down
```
To remove the database volume as well:
```bash
docker-compose down -v
```