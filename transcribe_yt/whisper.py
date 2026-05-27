import os
import tempfile
import yt_dlp
from faster_whisper import WhisperModel
from transcribe_yt.formats import Segment


def _run_whisper(audio_path: str, model_size: str, language: str | None, device: str) -> list[Segment]:
    compute_type = "float16" if device == "cuda" else "int8"
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    raw_segments, _ = model.transcribe(audio_path, language=language or None)
    return [Segment(start=s.start, end=s.end, text=s.text) for s in raw_segments]


def transcribe_url(
    url: str,
    model_size: str = "base",
    language: str | None = None,
    device: str = "cpu",
) -> list[Segment]:
    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(tmpdir, "audio.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        audio_files = [
            os.path.join(tmpdir, f)
            for f in os.listdir(tmpdir)
            if not f.endswith(".part")
        ]
        if not audio_files:
            raise RuntimeError("Audio download failed: no file found.")

        return _run_whisper(audio_files[0], model_size, language, device)


def transcribe_file(
    path: str,
    model_size: str = "base",
    language: str | None = None,
    device: str = "cpu",
) -> list[Segment]:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    return _run_whisper(path, model_size, language, device)
