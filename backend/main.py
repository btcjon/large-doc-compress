import os
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import aiofiles
import tempfile
import aiohttp
import logging
from typing import Any, Dict
from dotenv import load_dotenv
from .ai_condense_text import condense_text
from redis.asyncio import Redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis = Redis(host="localhost", port=6379, db=0, decode_responses=False)

@app.on_event("startup")
async def startup():
    redis_client = await redis
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")

class UrlRequest(BaseModel):
    url: HttpUrl

class ProcessedResponse(BaseModel):
    condensed_text: str

@app.get("/")
async def root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Text Condenser</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #1a1a1a;
                color: #ffffff;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                background-color: #2a2a2a;
                padding: 2rem;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            h1 {
                margin-bottom: 2rem;
            }
            .upload-form {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .file-input {
                margin-bottom: 1rem;
            }
            .submit-button {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to AI Text Condenser</h1>
            <form class="upload-form" action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept=".txt,.pdf,.doc,.docx" class="file-input">
                <button type="submit" class="submit-button">Upload and Process</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('path/to/your/favicon.ico')  # Update this path

# Add this new dictionary to store job statuses
job_statuses: Dict[str, str] = {}

@app.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
        temp_file.write(contents)
        temp_file_path = temp_file.name

    output_file = f"{temp_file_path}_condensed.txt"
    job_id = os.path.basename(output_file)
    
    job_statuses[job_id] = "processing"
    background_tasks.add_task(process_file, temp_file_path, output_file, job_id)
    
    return {"status": "Processing started", "job_id": job_id}

async def process_file(input_file: str, output_file: str, job_id: str):
    try:
        await condense_text(input_file, output_file)
        job_statuses[job_id] = "completed"
    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        job_statuses[job_id] = "error"
    finally:
        os.unlink(input_file)

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in job_statuses:
        raise HTTPException(status_code=404, detail="Job not found")
    
    status = job_statuses[job_id]
    if status == "completed":
        output_file = f"/tmp/{job_id}"
        if os.path.exists(output_file):
            async with aiofiles.open(output_file, mode='r') as f:
                condensed_content = await f.read()
            os.unlink(output_file)
            del job_statuses[job_id]
            return {"status": "completed", "condensed_content": condensed_content}
        else:
            return {"status": "error", "message": "Output file not found"}
    elif status == "error":
        del job_statuses[job_id]
        return {"status": "error", "message": "Error during processing"}
    else:
        return {"status": "processing"}

@app.post("/process-url", response_model=ProcessedResponse)
@cache(expire=3600)
async def process_url(url_request: UrlRequest):
    temp_file_path = ""
    output_file = ""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(str(url_request.url)) as response:
                response.raise_for_status()
                content = await response.text()

        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(content.encode('utf-8'))
            temp_file_path = temp_file.name

        output_file = f"{temp_file_path}_condensed.txt"
        await condense_text(temp_file_path, output_file)

        async with aiofiles.open(output_file, mode='r') as f:
            condensed_content = await f.read()

        return ProcessedResponse(condensed_text=condensed_content)
    except aiohttp.ClientError as e:
        logging.error(f"Error fetching URL: {str(e)}")
        raise HTTPException(status_code=400, detail="Error fetching URL")
    except Exception as e:
        logging.error(f"Error processing URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing URL")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        if output_file and os.path.exists(output_file):
            os.unlink(output_file)

@app.middleware("http")
async def log_requests(request: Any, call_next: Any) -> Any:
    logging.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Response status: {response.status_code}")
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8030))
    uvicorn.run(app, host="0.0.0.0", port=port)