# trs

A CLI tool that transcribes YouTube videos and local audio/video files into text.

For YouTube videos it tries to fetch the built-in captions first (instant, no model needed). If captions are unavailable it falls back to downloading the audio and running [faster-whisper](https://github.com/SYSTRAN/faster-whisper) locally — no cloud API required. Local files are always transcribed with Whisper directly.

---

## Installation

**Requirements:** Python 3.10+

```bash
git clone https://github.com/frgardin/transcribe-yt.git
cd transcribe-yt
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

> The Whisper fallback does **not** require `ffmpeg` — audio is passed in its native format directly to faster-whisper.

---

## Commands

### `trs youtube` — Transcribe a YouTube video

```bash
trs youtube <url> -o output.txt [OPTIONS]
```

**Examples:**
```bash
# Plain text, captions if available
trs youtube "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -o transcript.txt

# Force Portuguese captions, fall back with language hint
trs youtube "https://youtu.be/dQw4w9WgXcQ" -o transcript.txt --language pt

# Generate an SRT subtitle file
trs youtube "https://youtu.be/dQw4w9WgXcQ" -o subtitles.srt --format srt

# Plain text with timestamps, using the small Whisper model
trs youtube "https://youtu.be/dQw4w9WgXcQ" -o transcript.txt --model small --timestamps
```

**Options:**

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--output` | `-o` | *(required)* | Output file path |
| `--model` | `-m` | `base` | Whisper model size (see table below) |
| `--language` | `-l` | auto-detect | Language code of the audio, e.g. `en`, `pt`, `es` |
| `--format` | `-f` | `txt` | Output format: `txt`, `srt`, `vtt` |
| `--timestamps` | `-t` | off | Prefix each line with `[MM:SS]` (txt only) |

---

### `trs file` — Transcribe a local audio or video file

```bash
trs file <path> -o output.txt [OPTIONS]
```

Supports any format faster-whisper can read: `mp3`, `mp4`, `wav`, `m4a`, `webm`, `mkv`, `ogg`, `flac`, and more.

**Examples:**
```bash
# Transcribe an MP3
trs file podcast.mp3 -o transcript.txt

# Portuguese audio, with timestamps
trs file interview.mp4 -o transcript.txt --language pt --timestamps

# Export as WebVTT subtitles using the small model
trs file lecture.mp4 -o lecture.vtt --format vtt --model small

# Use GPU acceleration
trs file recording.wav -o notes.txt --device cuda
```

**Options:**

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--output` | `-o` | *(required)* | Output file path |
| `--model` | `-m` | `base` | Whisper model size (see table below) |
| `--language` | `-l` | auto-detect | Language code of the audio, e.g. `en`, `pt`, `es` |
| `--format` | `-f` | `txt` | Output format: `txt`, `srt`, `vtt` |
| `--timestamps` | `-t` | off | Prefix each line with `[MM:SS]` (txt only) |
| `--device` | — | `cpu` | `cpu` or `cuda` for GPU acceleration |

---

## Output formats

| Format | Flag | Description |
|--------|------|-------------|
| Plain text | `--format txt` | All text joined, optionally with `[MM:SS]` timestamps |
| SubRip | `--format srt` | Standard `.srt` subtitle file with timecodes |
| WebVTT | `--format vtt` | Standard `.vtt` subtitle file for HTML5 video |

---

## Whisper model sizes

Used when captions are unavailable (YouTube) or always (local files). Downloaded from HuggingFace on first use and cached locally.

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| `tiny` | ~75 MB | Fastest | Lower |
| `base` | ~150 MB | Fast | Good |
| `small` | ~470 MB | Moderate | Better |
| `medium` | ~1.5 GB | Slow | High |
| `large` | ~3 GB | Slowest | Best |

---

## How it works

```
trs youtube <url>               trs file <path>
      │                               │
      ▼                               ▼
Try YouTube captions          Load local file
      │                               │
      ├── Found ──────────────────────┤
      │                               │
      └── Not found                   │
            │                         │
            ▼                         │
      Download audio (yt-dlp)         │
            │                         │
            └──────────┬──────────────┘
                       ▼
             Whisper transcription
             (faster-whisper, local)
                       │
                       ▼
             Format output (txt / srt / vtt)
                       │
                       ▼
                  Write to file ✓
```

---

## Project structure

```
transcribe_yt/
├── cli.py        # typer CLI — youtube and file subcommands
├── captions.py   # YouTube captions fetcher
├── whisper.py    # yt-dlp download + faster-whisper transcription
└── formats.py    # Segment type and txt/srt/vtt renderers
```
