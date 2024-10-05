# Build stage for Python
FROM python:3.12-slim AS python-builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y gcc curl

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Node.js build stage for React frontend
FROM node:18 as frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from python-builder stage
COPY --from=python-builder /usr/local /usr/local

# Copy application files
COPY backend/ ./backend/
COPY requirements.txt ./

# Copy built React app
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Set Python path
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 8030

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8030"]