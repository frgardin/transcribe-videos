# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

The package registers a `trs` CLI entry point. Re-run `pip install -e .` after changing `pyproject.toml`.

## Running the CLI

```bash
trs --help
trs youtube "https://youtube.com/watch?v=..." -o out.txt
trs file audio.mp3 -o out.txt --format srt --language pt --timestamps
```

## Architecture

The pipeline has two input paths that converge on a shared output layer:

**YouTube path** (`trs youtube`):
1. `captions.py` — tries `youtube-transcript-api` to get captions as `list[Segment]`. Returns `None` on failure.
2. If `None`, `whisper.py:transcribe_url()` downloads audio via `yt-dlp` into a `tempfile.TemporaryDirectory` (no ffmpeg required — audio is passed in its native format), then calls `_run_whisper()`.

**Local file path** (`trs file`):
1. `whisper.py:transcribe_file()` validates the path and calls `_run_whisper()` directly.

**Shared output layer** (`formats.py`):
- `Segment(start, end, text)` is the common dataclass exchanged between all modules.
- `render(segments, fmt, timestamps)` converts to `txt`, `srt`, or `vtt`.

**CLI** (`cli.py`): thin typer layer — no business logic, just wires arguments to the above functions and writes the result to the output file.

## Key behaviours to preserve

- `get_captions()` must return `None` (not raise) on any failure — the YouTube command depends on this for the fallback.
- `transcribe_url()` must not add ffmpeg postprocessors to yt-dlp options; faster-whisper reads native audio formats via the `av` library.
- `compute_type` is `"float16"` for cuda and `"int8"` for cpu — changing this will break GPU runs.
