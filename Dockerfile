# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y gcc curl

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application files
COPY backend/ ./backend/
COPY pyproject.toml .

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Set Python path
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 8030

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8030"]