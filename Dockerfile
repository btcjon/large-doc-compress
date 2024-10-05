# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application files
COPY . .

# Install Node.js and npm
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Build stage for React frontend
FROM node:18 as frontend-builder

# Set working directory
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

# ... (rest of the Dockerfile remains the same)

# Copy built React app
COPY --from=frontend-builder /app/frontend/build /app/frontend/build

# Install and build React app
WORKDIR /app/frontend
RUN npm install && npm run build

# Move back to the app directory
WORKDIR /app

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Make sure scripts in .local are usable:
ENV PATH=/root/.local/bin:$PATH

# Expose the port the app runs on
EXPOSE 8030

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8030"]