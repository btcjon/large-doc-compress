import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiofiles
import tempfile
import aiohttp
import logging
from typing import Any
from dotenv import load_dotenv
from .ai_condense_text import condense_text

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

class UrlRequest(BaseModel):
    url: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    temp_file_path = ""
    output_file = ""
    try:
        suffix = os.path.splitext(file.filename)[1] if file.filename else '.txt'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        output_file = f"{temp_file_path}_condensed.txt"
        await condense_text(temp_file_path, output_file)

        return FileResponse(output_file, media_type='text/plain', filename="condensed_text.txt")
    except Exception as e:
        logging.error(f"Error processing uploaded file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing file")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        if output_file and os.path.exists(output_file):
            os.unlink(output_file)

@app.post("/process-url")
async def process_url(url_request: UrlRequest):
    temp_file_path = ""
    output_file = ""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url_request.url) as response:
                response.raise_for_status()
                content = await response.text()

        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(content.encode('utf-8'))
            temp_file_path = temp_file.name

        output_file = f"{temp_file_path}_condensed.txt"
        await condense_text(temp_file_path, output_file)

        async with aiofiles.open(output_file, mode='r') as f:
            condensed_content = await f.read()

        return {"condensed_text": condensed_content}
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
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8030)))