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

WORKDIR /app

# Copy Python requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ ./backend/

# Copy built React app
COPY --from=frontend-builder /app/frontend/build /app/frontend/build

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Expose the port the app runs on
EXPOSE 8030

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8030"]