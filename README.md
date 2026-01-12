# Meeting Audio Transcription Tool

A local web application for transcribing audio and video files with automatic speaker diarization. Built with WhisperX and pyannote-audio.

**This branch (`docker`) contains the Dockerized version that runs on any machine.**

## Features

- **Drag & Drop Interface** - Simple web UI for uploading audio/video files
- **Speaker Diarization** - Automatically detects and labels different speakers
- **Speaker Identification** - Play audio samples of each speaker, then assign custom names
- **Speaker Merging** - Give multiple detected speakers the same name to merge them
- **Multiple Export Formats** - Download transcripts as TXT, SRT (subtitles), or JSON
- **Wide Format Support** - MP3, WAV, FLAC, OGG, M4A, AAC, WMA, WEBM, MP4, MKV, AVI, MOV

## Platform Support

| Platform | Docker File | Performance |
|----------|-------------|-------------|
| Linux + NVIDIA GPU | `docker-compose.yml` | ~5 min per hour of audio |
| Mac (Apple Silicon) | `docker-compose.cpu.yml` | ~20-40 min per hour of audio |
| Mac (Intel) | `docker-compose.cpu.yml` | ~30-60 min per hour of audio |
| Windows | `docker-compose.cpu.yml` | ~30-60 min per hour of audio |
| Linux (no GPU) | `docker-compose.cpu.yml` | ~30-60 min per hour of audio |

## Quick Start

### Prerequisites

1. **Docker Desktop** installed
   - Mac: [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Windows: [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Linux: `sudo apt install docker.io docker-compose`

2. **HuggingFace Account** (for speaker diarization)
   - Create account at [huggingface.co](https://huggingface.co)
   - Accept terms for these models:
     - [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
     - [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
   - Create access token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### Installation

```bash
# Clone the repository (docker branch)
git clone -b docker https://github.com/jcrandell7/meeting-audio-transcription-tool.git
cd meeting-audio-transcription-tool

# Create your .env file with your HuggingFace token
cp .env.example .env
# Edit .env and add your token
```

Edit the `.env` file:
```
HF_TOKEN=your_huggingface_token_here
```

### Running

#### Linux with NVIDIA GPU

```bash
# Start with GPU support
docker compose up --build

# Or run in background
docker compose up --build -d
```

Open your browser to **http://localhost:5000**

#### Mac / Windows / Linux without GPU

```bash
# Start with CPU-optimized configuration
docker compose -f docker-compose.cpu.yml up --build

# Or run in background
docker compose -f docker-compose.cpu.yml up --build -d
```

Open your browser to **http://localhost:5001** (note: port 5001, not 5000)

> **Mac Users**: Port 5001 is used because macOS uses port 5000 for AirPlay Receiver.

### Stopping

```bash
# If running in foreground, press Ctrl+C

# If running in background (GPU version)
docker compose down

# If running in background (CPU version)
docker compose -f docker-compose.cpu.yml down
```

## Usage

1. Open the web interface in your browser
   - Linux GPU: **http://localhost:5000**
   - Mac/Windows/CPU: **http://localhost:5001**
2. Drag and drop an audio/video file (or click to browse)
3. Check "Enable speaker diarization" if you want speaker detection
4. Click **Transcribe** and wait for processing
5. Review the transcript with speaker labels
6. Click play buttons to hear each speaker, then enter their names
7. Download your transcript in TXT, SRT, or JSON format

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HF_TOKEN` | HuggingFace access token | Required for diarization |
| `WHISPER_MODEL` | Whisper model size | `large-v3` (GPU) / `medium` (CPU) |

### Available Whisper Models

| Model | Size | RAM Required | Accuracy |
|-------|------|--------------|----------|
| `tiny` | ~75 MB | ~2 GB | Low |
| `base` | ~150 MB | ~2 GB | Basic |
| `small` | ~500 MB | ~3 GB | Good |
| `medium` | ~1.5 GB | ~6 GB | Better |
| `large-v3` | ~3 GB | ~12 GB | Best |

To change the model, set `WHISPER_MODEL` in your `.env` file:
```
HF_TOKEN=your_token_here
WHISPER_MODEL=medium
```

### Persisted Data

Both docker-compose files automatically persist:
- `./outputs/` - Your transcription files (TXT, SRT, JSON)
- `./clips/` - Speaker audio samples
- Model cache (in Docker volumes) - Avoids re-downloading

## First Run Notes

The first time you run the application, it will download the AI models:
- **Whisper model** (size varies by model selected)
- **pyannote models** (~100 MB) - Speaker diarization

This may take 5-15 minutes depending on your internet speed. The models are cached, so subsequent starts are fast.

## Troubleshooting

### "Error: HF_TOKEN not set"
Make sure you created the `.env` file with your HuggingFace token:
```bash
cp .env.example .env
# Edit .env and add: HF_TOKEN=your_token_here
```

### "403 Forbidden" for HuggingFace models
You need to accept the model terms on HuggingFace:
1. Go to [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
2. Click "Agree and access repository"
3. Repeat for [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)

### Container won't start / Out of memory
The models require significant RAM. Ensure Docker Desktop has enough memory allocated:
- **CPU mode (medium model)**: At least 8GB RAM
- **GPU mode (large-v3 model)**: At least 12GB RAM
- Mac/Windows: Docker Desktop → Settings → Resources → Memory

### "Failed to fetch" error in browser (Mac/Windows)
This usually means the container ran out of memory during transcription. Either:
1. Increase Docker Desktop memory allocation
2. Use a smaller Whisper model (set `WHISPER_MODEL=small` in `.env`)

### Transcription is very slow
This is expected for CPU processing. Consider:
- Using a smaller model (`WHISPER_MODEL=small` or `medium`)
- Using shorter audio files
- Splitting long recordings
- For faster processing, use Linux with an NVIDIA GPU

### Port 5000 already in use (Mac)
macOS uses port 5000 for AirPlay Receiver. The CPU compose file uses port 5001 instead. Make sure you're accessing **http://localhost:5001**

## Tech Stack

- **[WhisperX](https://github.com/m-bain/whisperX)** - Fast Whisper transcription with word-level timestamps
- **[Whisper](https://github.com/openai/whisper)** - OpenAI's speech recognition model
- **[pyannote-audio](https://github.com/pyannote/pyannote-audio)** - Speaker diarization
- **[Flask](https://flask.palletsprojects.com/)** - Python web framework
- **[ffmpeg](https://ffmpeg.org/)** - Audio/video processing

## License

MIT License - feel free to use and modify for your own purposes.
