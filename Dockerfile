# Meeting Audio Transcription Tool - Docker Image
# For Linux with NVIDIA GPU support

FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies including Python 3.10 (default on Ubuntu 22.04)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Upgrade pip
RUN pip3 install --upgrade pip

# Install PyTorch with CUDA support
RUN pip3 install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install Python dependencies
RUN pip3 install \
    flask \
    flask-cors \
    whisperx \
    "pyannote.audio>=3.1" \
    pandas \
    omegaconf

# Copy application files
COPY app.py .
COPY static/ static/

# Create directories for uploads, outputs, and clips
RUN mkdir -p uploads outputs clips

# Expose port
EXPOSE 5000

# Health check (using python since curl may not be available)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# Run the application
CMD ["python3", "app.py"]
