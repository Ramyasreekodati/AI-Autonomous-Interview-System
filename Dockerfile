# --- STAGE 1: Build Frontend ---
FROM node:20-slim AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- STAGE 2: Build Backend & Serve App ---
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies for OpenCV/MediaPipe
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY .env .

# Copy built frontend from Stage 1
COPY --from=frontend-builder /frontend/dist ./frontend/dist

EXPOSE 7860

# Healthcheck to ensure the unified app is up
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:7860/ || exit 1

# Start the unified FastAPI server
ENTRYPOINT ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
