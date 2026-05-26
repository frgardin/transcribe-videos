# transcribe-yt

A CLI tool that transcribes YouTube videos into text files.

It tries to fetch YouTube's own captions first (instant). If captions are unavailable, it falls back to downloading the audio and transcribing it locally with [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — no cloud API needed.

## Usage

```bash
transcribe-yt <url> -o output.txt
```

**Examples:**

```bash
# Basic transcription
transcribe-yt "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -o transcript.txt

# Use a more accurate Whisper model for the fallback
transcribe-yt "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -o transcript.txt --model small
```

**Options:**

| Flag | Description | Default |
|------|-------------|---------|
| `-o`, `--output` | Output file path (required) | — |
| `--model` | Whisper model size used when captions are unavailable | `base` |

**Whisper model sizes** (used only when captions are unavailable):

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| `tiny` | ~75 MB | Fastest | Lower |
| `base` | ~150 MB | Fast | Good |
| `small` | ~470 MB | Moderate | Better |
| `medium` | ~1.5 GB | Slow | High |
| `large` | ~3 GB | Slowest | Best |

The model is downloaded from HuggingFace on first use and cached locally.

## How it works

```
YouTube URL
    │
    ▼
Try YouTube captions (youtube-transcript-api)
    │
    ├── Captions found → write to file ✓
    │
    └── No captions →
            Download audio (yt-dlp, no ffmpeg needed)
                │
                ▼
            Transcribe locally (faster-whisper)
                │
                ▼
            Write to file ✓
```

## Installation

**Requirements:** Python 3.10+

```bash
git clone https://github.com/frgardin/transcribe-yt.git
cd transcribe-yt
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

> **Note:** The Whisper fallback does **not** require `ffmpeg` — audio is passed in its native format directly to faster-whisper.

## Project structure

```
transcribe_yt/
├── cli.py        # typer CLI entry point
├── captions.py   # YouTube captions fetcher
└── whisper.py    # yt-dlp + faster-whisper fallback
```
