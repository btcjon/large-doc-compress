# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies and UV
RUN apt-get update && apt-get install -y gcc curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

COPY requirements.txt ./
RUN uv pip install --system -r requirements.txt

# Node.js build stage for React frontend
FROM node:18 as frontend-builder

WORKDIR /app/frontend

# Copy package.json and package-lock.json (if available)
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source files
COPY frontend/ ./

# Build the React app
RUN npm run build

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /usr/local /usr/local

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