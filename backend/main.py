import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
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

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        # Process the file contents here using your condense_text function
        # For this example, we'll use a temporary file to store the contents
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(contents)
            temp_file_path = temp_file.name

        output_file = f"{temp_file_path}_condensed.txt"
        
        # Assuming condense_text is an async function
        await condense_text(temp_file_path, output_file)
        
        # Read the condensed content
        async with aiofiles.open(output_file, mode='r') as f:
            condensed_content = await f.read()

        # Clean up temporary files
        os.unlink(temp_file_path)
        os.unlink(output_file)

        return {
            "filename": file.filename,
            "message": "File processed successfully",
            "condensed_content": condensed_content
        }
    except Exception as e:
        logging.error(f"Error processing uploaded file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

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
    port = int(os.getenv("PORT", 8030))
    uvicorn.run(app, host="0.0.0.0", port=port)