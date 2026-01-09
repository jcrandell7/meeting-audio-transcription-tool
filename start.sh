#!/bin/bash

# Audio Transcription Web UI Startup Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Set library path for CUDA/cuDNN libraries in venv
export LD_LIBRARY_PATH="$SCRIPT_DIR/venv/lib/python3.12/site-packages/nvidia/cudnn/lib:$SCRIPT_DIR/venv/lib/python3.12/site-packages/nvidia/cublas/lib:$SCRIPT_DIR/venv/lib/python3.12/site-packages/nvidia/cuda_runtime/lib:$LD_LIBRARY_PATH"

# Check if GPU is available
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

echo ""
echo "==========================================="
echo "  Audio Transcription Server"
echo "==========================================="
echo ""

# Check for HuggingFace token
if [ -z "$HF_TOKEN" ]; then
    echo "NOTE: Speaker diarization requires a HuggingFace token."
    echo "To enable diarization:"
    echo "  1. Create account at huggingface.co"
    echo "  2. Accept terms at huggingface.co/pyannote/speaker-diarization-3.1"
    echo "  3. Create token at huggingface.co/settings/tokens"
    echo "  4. Run: export HF_TOKEN=your_token_here"
    echo ""
    echo "Starting without diarization support..."
else
    echo "HuggingFace token found - diarization enabled"
fi

echo ""
echo "Open your browser to: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo "==========================================="
echo ""

# Start the Flask server
python app.py
