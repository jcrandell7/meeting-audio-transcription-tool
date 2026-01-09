import os
import json
import tempfile
import subprocess
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import torch
import whisperx
from pyannote.audio import Pipeline as DiarizationPipeline

app = Flask(__name__, static_folder='static')
CORS(app)

UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
OUTPUT_FOLDER = Path(__file__).parent / 'outputs'
CLIPS_FOLDER = Path(__file__).parent / 'clips'
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)
CLIPS_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'ogg', 'oga', 'm4a', 'aac', 'wma', 'aiff', 'webm', 'mp4', 'mkv', 'avi', 'mov'}

HF_TOKEN = os.environ.get('HF_TOKEN', None)

device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if device == "cuda" else "int8"

model = None
diarize_model = None


def get_model():
    global model
    if model is None:
        print("Loading Whisper model (large-v3)...")
        model = whisperx.load_model("large-v3", device, compute_type=compute_type)
        print("Model loaded.")
    return model


def get_diarize_model():
    global diarize_model
    if diarize_model is None:
        if not HF_TOKEN:
            raise ValueError(
                "Speaker diarization requires a HuggingFace token. "
                "1) Create account at huggingface.co "
                "2) Accept terms at huggingface.co/pyannote/speaker-diarization-3.1 "
                "3) Create token at huggingface.co/settings/tokens "
                "4) Set HF_TOKEN environment variable before starting"
            )
        print("Loading diarization model...")
        diarize_model = DiarizationPipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=HF_TOKEN
        )
        diarize_model.to(torch.device(device))
        print("Diarization model loaded.")
    return diarize_model


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def convert_to_wav(input_path, output_path):
    """Convert audio to 16kHz mono WAV for optimal processing."""
    cmd = [
        'ffmpeg', '-y', '-i', str(input_path),
        '-ar', '16000', '-ac', '1',
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def extract_speaker_clips(audio_path, diarize_segments, base_name, clip_duration=5):
    """Extract a short audio clip for each speaker."""
    speaker_clips = {}

    # Group segments by speaker and find a good clip for each
    speaker_segments = {}
    for seg in diarize_segments:
        speaker = seg['speaker']
        if speaker not in speaker_segments:
            speaker_segments[speaker] = []
        speaker_segments[speaker].append(seg)

    for speaker, segments in speaker_segments.items():
        # Find a segment that's at least 2 seconds long, prefer longer ones
        best_segment = None
        for seg in segments:
            duration = seg['end'] - seg['start']
            if duration >= 2:
                if best_segment is None or duration > (best_segment['end'] - best_segment['start']):
                    best_segment = seg
                if duration >= clip_duration:
                    break

        if best_segment is None and segments:
            best_segment = segments[0]

        if best_segment:
            start = best_segment['start']
            duration = min(clip_duration, best_segment['end'] - start)

            clip_filename = f"{base_name}_{speaker}.mp3"
            clip_path = CLIPS_FOLDER / clip_filename

            cmd = [
                'ffmpeg', '-y', '-i', str(audio_path),
                '-ss', str(start), '-t', str(duration),
                '-acodec', 'libmp3lame', '-ab', '128k',
                str(clip_path)
            ]
            try:
                subprocess.run(cmd, capture_output=True, check=True)
                speaker_clips[speaker] = clip_filename
            except subprocess.CalledProcessError as e:
                print(f"Failed to extract clip for {speaker}: {e}")

    return speaker_clips


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/favicon.ico')
def favicon():
    return '', 204


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

    enable_diarization = request.form.get('diarization', 'true').lower() == 'true'
    speaker_names = request.form.get('speaker_names', '{}')

    try:
        speaker_names = json.loads(speaker_names)
    except json.JSONDecodeError:
        speaker_names = {}

    original_filename = file.filename
    file_ext = original_filename.rsplit('.', 1)[1].lower()

    with tempfile.NamedTemporaryFile(suffix=f'.{file_ext}', delete=False) as tmp:
        file.save(tmp.name)
        temp_input = tmp.name

    try:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_tmp:
            temp_wav = wav_tmp.name

        print(f"Converting {original_filename} to WAV...")
        convert_to_wav(temp_input, temp_wav)

        print("Loading audio...")
        audio = whisperx.load_audio(temp_wav)

        print("Transcribing...")
        whisper_model = get_model()
        result = whisper_model.transcribe(audio, batch_size=16)

        print("Aligning...")
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
        result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

        diarization_error = None
        speaker_clips = {}
        if enable_diarization:
            print("Diarizing...")
            try:
                diarize_pipeline = get_diarize_model()
                diarize_output = diarize_pipeline(temp_wav)

                # pyannote 4.x returns DiarizeOutput, extract the Annotation
                diarize_annotation = diarize_output.speaker_diarization

                # Convert pyannote Annotation to DataFrame format whisperx expects
                import pandas as pd
                diarize_segments = []
                for turn, _, speaker in diarize_annotation.itertracks(yield_label=True):
                    diarize_segments.append({
                        'start': turn.start,
                        'end': turn.end,
                        'speaker': speaker
                    })
                diarize_df = pd.DataFrame(diarize_segments)

                result = whisperx.assign_word_speakers(diarize_df, result)

                # Extract speaker audio clips
                speaker_clips = extract_speaker_clips(
                    temp_wav, diarize_segments,
                    Path(original_filename).stem
                )
            except ValueError as e:
                diarization_error = str(e)
                print(f"Diarization skipped: {e}")
            except Exception as e:
                import traceback
                traceback.print_exc()
                diarization_error = f"Diarization failed: {e}"
                print(f"Diarization failed: {e}")
                print("Continuing without diarization...")

        if speaker_names:
            for segment in result.get("segments", []):
                speaker = segment.get("speaker", "")
                if speaker in speaker_names:
                    segment["speaker_name"] = speaker_names[speaker]

        base_name = Path(original_filename).stem
        output_json = OUTPUT_FOLDER / f"{base_name}_transcript.json"
        output_txt = OUTPUT_FOLDER / f"{base_name}_transcript.txt"
        output_srt = OUTPUT_FOLDER / f"{base_name}_transcript.srt"

        with open(output_json, 'w') as f:
            json.dump(result, f, indent=2)

        with open(output_txt, 'w') as f:
            for segment in result.get("segments", []):
                speaker = segment.get("speaker_name", segment.get("speaker", ""))
                text = segment.get("text", "").strip()
                if speaker:
                    f.write(f"[{speaker}]: {text}\n")
                else:
                    f.write(f"{text}\n")

        with open(output_srt, 'w') as f:
            for i, segment in enumerate(result.get("segments", []), 1):
                start = format_timestamp(segment.get("start", 0))
                end = format_timestamp(segment.get("end", 0))
                speaker = segment.get("speaker_name", segment.get("speaker", ""))
                text = segment.get("text", "").strip()

                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                if speaker:
                    f.write(f"[{speaker}]: {text}\n\n")
                else:
                    f.write(f"{text}\n\n")

        detected_speakers = set()
        for segment in result.get("segments", []):
            if "speaker" in segment:
                detected_speakers.add(segment["speaker"])

        response = {
            'success': True,
            'language': result.get("language", "unknown"),
            'segments': result.get("segments", []),
            'speakers': sorted(list(detected_speakers)),
            'speaker_clips': speaker_clips,
            'files': {
                'json': f"{base_name}_transcript.json",
                'txt': f"{base_name}_transcript.txt",
                'srt': f"{base_name}_transcript.srt"
            }
        }
        if diarization_error:
            response['diarization_warning'] = diarization_error
        return jsonify(response)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

    finally:
        if os.path.exists(temp_input):
            os.unlink(temp_input)
        if 'temp_wav' in locals() and os.path.exists(temp_wav):
            os.unlink(temp_wav)


def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


@app.route('/api/download/<filename>')
def download_file(filename):
    file_path = OUTPUT_FOLDER / filename
    if file_path.exists():
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


@app.route('/api/clips/<filename>')
def serve_clip(filename):
    """Serve speaker audio clips."""
    file_path = CLIPS_FOLDER / filename
    if file_path.exists():
        return send_file(file_path, mimetype='audio/mpeg')
    return jsonify({'error': 'Clip not found'}), 404


@app.route('/api/update-speakers', methods=['POST'])
def update_speakers():
    """Re-generate transcript files with updated speaker names."""
    data = request.json
    json_file = data.get('json_file')
    speaker_names = data.get('speaker_names', {})

    if not json_file:
        return jsonify({'error': 'No JSON file specified'}), 400

    json_path = OUTPUT_FOLDER / json_file
    if not json_path.exists():
        return jsonify({'error': 'Transcript file not found'}), 404

    with open(json_path, 'r') as f:
        result = json.load(f)

    for segment in result.get("segments", []):
        speaker = segment.get("speaker", "")
        if speaker in speaker_names:
            segment["speaker_name"] = speaker_names[speaker]
        elif "speaker_name" in segment:
            del segment["speaker_name"]

    with open(json_path, 'w') as f:
        json.dump(result, f, indent=2)

    base_name = json_file.replace('_transcript.json', '')
    output_txt = OUTPUT_FOLDER / f"{base_name}_transcript.txt"
    output_srt = OUTPUT_FOLDER / f"{base_name}_transcript.srt"

    with open(output_txt, 'w') as f:
        for segment in result.get("segments", []):
            speaker = segment.get("speaker_name", segment.get("speaker", ""))
            text = segment.get("text", "").strip()
            if speaker:
                f.write(f"[{speaker}]: {text}\n")
            else:
                f.write(f"{text}\n")

    with open(output_srt, 'w') as f:
        for i, segment in enumerate(result.get("segments", []), 1):
            start = format_timestamp(segment.get("start", 0))
            end = format_timestamp(segment.get("end", 0))
            speaker = segment.get("speaker_name", segment.get("speaker", ""))
            text = segment.get("text", "").strip()

            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            if speaker:
                f.write(f"[{speaker}]: {text}\n\n")
            else:
                f.write(f"{text}\n\n")

    return jsonify({
        'success': True,
        'segments': result.get("segments", [])
    })


if __name__ == '__main__':
    print(f"Using device: {device}")
    print(f"Compute type: {compute_type}")
    print("Starting server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
