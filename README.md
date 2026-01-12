# Meeting Audio Transcription Tool

A local web application for transcribing audio and video files with automatic speaker diarization. Built with WhisperX and pyannote-audio.

**This branch (`docker`) contains the Dockerized version that runs on any machine.**

- **Linux with NVIDIA GPU**: Full GPU acceleration (fast, ~5 min per hour of audio)
- **Mac / Windows / Linux without GPU**: Runs on CPU (slower but works everywhere)

## Features

- **Drag & Drop Interface** - Simple web UI for uploading audio/video files
- **Speaker Diarization** - Automatically detects and labels different speakers
- **Speaker Identification** - Play audio samples of each speaker, then assign custom names
- **Speaker Merging** - Give multiple detected speakers the same name to merge them
- **Multiple Export Formats** - Download transcripts as TXT, SRT (subtitles), or JSON
- **Wide Format Support** - MP3, WAV, FLAC, OGG, M4A, AAC, WMA, WEBM, MP4, MKV, AVI, MOV

## Platform Support

| Platform | Support | Notes |
|----------|---------|-------|
| Linux + NVIDIA GPU | Yes | GPU accelerated, ~5 min per hour of audio |
| Mac (Apple Silicon M1/M2/M3) | Yes | Runs on CPU, ~15-30 min per hour of audio |
| Mac (Intel) | Yes | Runs on CPU, ~30-60 min per hour of audio |
| Linux (no GPU) | Yes | CPU mode, ~30-60 min per hour of audio |
| Windows | Yes | Via Docker Desktop, CPU mode |

## Quick Start (Docker)

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

```bash
# Start the application
docker compose up --build

# Or run in background
docker compose up --build -d
```

Open your browser to **http://localhost:5000**

### Stopping

```bash
# If running in foreground, press Ctrl+C

# If running in background
docker compose down
```

## Usage

1. Open **http://localhost:5000** in your browser
2. Drag and drop an audio/video file (or click to browse)
3. Check "Enable speaker diarization" if you want speaker detection
4. Click **Transcribe** and wait for processing
5. Review the transcript with speaker labels
6. Click play buttons to hear each speaker, then enter their names
7. Download your transcript in TXT, SRT, or JSON format

## First Run Notes

The first time you run the application, it will download the AI models:
- **Whisper large-v3** (~3 GB) - Speech recognition
- **pyannote models** (~100 MB) - Speaker diarization

This may take 5-15 minutes depending on your internet speed. The models are cached, so subsequent starts are fast.

## Performance Expectations

This Docker version runs on CPU, which is slower than GPU but works everywhere:

| Audio Length | Approximate Time |
|--------------|------------------|
| 5 minutes | 2-5 minutes |
| 30 minutes | 10-20 minutes |
| 1 hour | 20-40 minutes |
| 2 hours | 40-80 minutes |

*Times vary based on your CPU. Apple Silicon Macs tend to be faster than Intel.*

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `HF_TOKEN` | HuggingFace access token | For diarization |

### Persisted Data

The `docker-compose.yml` automatically persists:
- `./outputs/` - Your transcription files (TXT, SRT, JSON)
- `./clips/` - Speaker audio samples
- Model cache (in Docker volumes) - Avoids re-downloading

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
The models require significant RAM. Ensure Docker Desktop has at least **8GB RAM** allocated:
- Mac/Windows: Docker Desktop → Settings → Resources → Memory

### Transcription is very slow
This is expected for CPU processing. Consider:
- Using shorter audio files
- Splitting long recordings
- For faster processing, use the [`main` branch](https://github.com/jcrandell7/meeting-audio-transcription-tool/tree/main) with an NVIDIA GPU

## Native Installation (Without Docker)

If you prefer running without Docker, see the [`main` branch](https://github.com/jcrandell7/meeting-audio-transcription-tool/tree/main) for native installation instructions. The native version:
- Requires manual Python environment setup
- Supports NVIDIA GPU acceleration (much faster)
- Is better for Linux machines with NVIDIA GPUs

## Tech Stack

- **[WhisperX](https://github.com/m-bain/whisperX)** - Fast Whisper transcription with word-level timestamps
- **[Whisper large-v3](https://github.com/openai/whisper)** - OpenAI's speech recognition model
- **[pyannote-audio](https://github.com/pyannote/pyannote-audio)** - Speaker diarization
- **[Flask](https://flask.palletsprojects.com/)** - Python web framework
- **[ffmpeg](https://ffmpeg.org/)** - Audio/video processing

## License

MIT License - feel free to use and modify for your own purposes.
