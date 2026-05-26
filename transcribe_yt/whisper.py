import tempfile
import os
import yt_dlp
from faster_whisper import WhisperModel


def transcribe_with_whisper(url: str, model_size: str = "base") -> str:
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
        audio_path = audio_files[0]

        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_path)
        return " ".join(segment.text.strip() for segment in segments)
