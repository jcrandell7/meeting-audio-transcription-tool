# Meeting Audio Transcription Tool - Docker Image
# Works on Mac (Intel & Apple Silicon), Linux, and Windows

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install PyTorch CPU version (works on all platforms)
RUN pip install --upgrade pip && \
    pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install Python dependencies
# Note: Installing whisperx from git for latest compatibility
RUN pip install \
    flask \
    flask-cors \
    whisperx \
    pyannote.audio \
    pandas

# Copy application files
COPY app.py .
COPY static/ static/

# Create directories for uploads, outputs, and clips
RUN mkdir -p uploads outputs clips

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run the application
CMD ["python", "app.py"]
