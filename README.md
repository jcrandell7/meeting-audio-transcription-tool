# Meeting Audio Transcription Tool

A local, GPU-accelerated web application for transcribing audio and video files with automatic speaker diarization. Built with WhisperX and pyannote-audio, this tool runs entirely on your own hardware for privacy and speed.

## Features

- **Drag & Drop Interface** - Simple web UI for uploading audio/video files
- **GPU Accelerated** - Utilizes NVIDIA GPUs for fast transcription (1 hour audio in ~5 minutes)
- **Speaker Diarization** - Automatically detects and labels different speakers
- **Speaker Identification** - Play audio samples of each speaker to identify them, then assign custom names
- **Speaker Merging** - Give multiple detected speakers the same name to merge them
- **Multiple Export Formats** - Download transcripts as TXT, SRT (subtitles), or JSON
- **Wide Format Support** - MP3, WAV, FLAC, OGG, M4A, AAC, WMA, WEBM, MP4, MKV, AVI, MOV

## Requirements

### Hardware
- **NVIDIA GPU** with CUDA support (tested on RTX 4060 Ti)
- 8GB+ VRAM recommended for large-v3 model
- 16GB+ system RAM

### Software
- Ubuntu 22.04/24.04 (or compatible Linux distribution)
- NVIDIA drivers with CUDA support
- Python 3.10+
- ffmpeg

## Installation

### 1. Install System Dependencies

```bash
sudo apt update
sudo apt install -y ffmpeg python3-venv git build-essential
```

### 2. Verify NVIDIA GPU

```bash
nvidia-smi
```
You should see your GPU listed. If not, install NVIDIA drivers first.

### 3. Clone the Repository

```bash
git clone https://github.com/jcrandell7/meeting-audio-transcription-tool.git
cd meeting-audio-transcription-tool
```

### 4. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 5. Install PyTorch with CUDA

```bash
pip install --upgrade pip

# For CUDA 12.x (most recent NVIDIA drivers)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Verify GPU access:
```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### 6. Install Python Dependencies

```bash
pip install whisperx flask flask-cors pyannote.audio
```

### 7. Set Up HuggingFace Token (Required for Speaker Diarization)

Speaker diarization uses gated models that require a HuggingFace account:

1. Create an account at [huggingface.co](https://huggingface.co)
2. Accept the terms for these models:
   - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
   - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
3. Create an access token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
4. Set the environment variable:
   ```bash
   export HF_TOKEN=your_token_here
   ```

**Tip:** Add this to your `~/.bashrc` to make it permanent:
```bash
echo 'export HF_TOKEN=your_token_here' >> ~/.bashrc
```

### 8. Create Required Directories

```bash
mkdir -p uploads outputs clips
```

## Usage

### Starting the Server

```bash
# Make sure you're in the project directory with venv activated
source venv/bin/activate
export HF_TOKEN=your_token_here  # if not already set

# Run the startup script
./start.sh
```

Or run directly:
```bash
python app.py
```

### Using the Application

1. Open your browser to **http://localhost:5000**
2. Drag and drop an audio/video file (or click to browse)
3. Check "Enable speaker diarization" if you want speaker detection
4. Click **Transcribe**
5. Wait for processing (progress bar shows status)
6. Review the transcript with speaker labels
7. **Optional:** Click play buttons to hear each speaker, then enter names
8. Download your transcript in TXT, SRT, or JSON format

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `HF_TOKEN` | HuggingFace access token for diarization models | For diarization |
| `HF_HUB_OFFLINE` | Set to `1` to run offline (after models are cached) | No |
| `TRANSFORMERS_OFFLINE` | Set to `1` to run offline | No |

### Running Offline

After the first run (which downloads and caches the models), you can run offline by uncommenting these lines in `start.sh`:

```bash
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
```

## Troubleshooting

### "CUDA not available"
- Ensure NVIDIA drivers are installed: `nvidia-smi`
- Reinstall PyTorch with CUDA support
- Check that your GPU has enough VRAM

### "Unable to load libcudnn_cnn.so.9"
The `start.sh` script sets the correct `LD_LIBRARY_PATH`. If running directly with `python app.py`, you may need to set it manually:
```bash
export LD_LIBRARY_PATH="./venv/lib/python3.12/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH"
```

### "403 Forbidden" for HuggingFace models
- Make sure you've accepted the terms for all required models on HuggingFace
- Verify your token has read access
- Check that `HF_TOKEN` is exported correctly

### Diarization shows wrong number of speakers
Speaker diarization is not perfect. You can:
- Merge speakers by giving them the same name
- The algorithm may split one person into multiple speakers if their voice changes significantly

## Tech Stack

- **[WhisperX](https://github.com/m-bain/whisperX)** - Fast Whisper transcription with word-level timestamps
- **[Whisper large-v3](https://github.com/openai/whisper)** - OpenAI's speech recognition model
- **[pyannote-audio](https://github.com/pyannote/pyannote-audio)** - Speaker diarization
- **[Flask](https://flask.palletsprojects.com/)** - Python web framework
- **[ffmpeg](https://ffmpeg.org/)** - Audio/video processing

## License

MIT License - feel free to use and modify for your own purposes.

## Acknowledgments

- OpenAI for the Whisper model
- The WhisperX team for the enhanced pipeline
- The pyannote team for speaker diarization
