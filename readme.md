# Large Document Compressor

This project provides a tool for condensing large documents using AI techniques. It includes both a frontend interface and a backend API.

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/large-doc-compress.git
   cd large-doc-compress
   ```

2. Install backend dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```
   cd frontend
   npm install
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

## Running the Application

### Backend

1. Start the backend server:
   ```
   uvicorn backend.main:app --host 0.0.0.0 --port 8030
   ```

### Frontend

1. In a new terminal, navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Start the React development server:
   ```
   npm start
   ```

3. Open your browser and go to `http://localhost:3000` to use the frontend interface.

## Using the Frontend

1. Upload a file:
   - Click on the file input field and select a .txt, .md, or .pdf file.
   - Click the "Upload and Process" button.
   - The processed file will be automatically downloaded.

2. Process a URL:
   - Enter a URL in the input field.
   - Click the "Process URL" button.
   - The condensed text will be displayed on the page.

## Using the API

The API provides two endpoints:

1. Upload and process a file:
   ```
   POST /upload
   Content-Type: multipart/form-data
   file: <file_content>
   ```

2. Process a URL:
   ```
   POST /process-url
   Content-Type: application/json
   {
     "url": "https://example.com/document.txt"
   }
   ```

Example using curl:

```bash
# Upload a file
curl -X POST -F "file=@/path/to/your/file.txt" http://localhost:8030/upload -o condensed_output.txt

# Process a URL
curl -X POST -H "Content-Type: application/json" -d '{"url": "https://example.com/document.txt"}' http://localhost:8030/process-url
```

## Docker

To run the application using Docker:

1. Build the Docker image:
   ```
   docker build -t large-doc-compress .
   ```

2. Run the container:
   ```
   docker run -p 8030:8030 -e OPENROUTER_API_KEY=your_api_key_here large-doc-compress
   ```

3. Access the application at `http://localhost:8030`

## Notes

- The frontend is configured to communicate with the backend at `http://localhost:8030`. If you change the backend port, update the frontend code accordingly.
- Make sure to keep your OpenRouter API key confidential and not expose it in public repositories.