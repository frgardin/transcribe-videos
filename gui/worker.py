from pathlib import Path
from PySide6.QtCore import QThread, Signal
from transcribe_yt.captions import get_captions
from transcribe_yt.whisper import transcribe_url, transcribe_file
from transcribe_yt.formats import OutputFormat, render


class TranscriptionWorker(QThread):
    log = Signal(str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, mode, source, output, model, language, fmt, timestamps, device):
        super().__init__()
        self.mode = mode        # "youtube" or "file"
        self.source = source
        self.output = Path(output)
        self.model = model
        self.language = language
        self.fmt = fmt
        self.timestamps = timestamps
        self.device = device

    def run(self):
        try:
            if self.mode == "youtube":
                self.log.emit("Fetching captions...")
                segments = get_captions(self.source, language=self.language)
                if segments is None:
                    self.log.emit("Captions unavailable — falling back to Whisper transcription...")
                    self.log.emit(f"Model: {self.model}  |  Language: {self.language or 'auto-detect'}  |  Device: cpu")
                    segments = transcribe_url(self.source, model_size=self.model, language=self.language)
            else:
                name = Path(self.source).name
                self.log.emit(f"Transcribing {name}...")
                self.log.emit(f"Model: {self.model}  |  Language: {self.language or 'auto-detect'}  |  Device: {self.device}")
                segments = transcribe_file(
                    self.source, model_size=self.model, language=self.language, device=self.device
                )

            self.output.write_text(render(segments, self.fmt, timestamps=self.timestamps), encoding="utf-8")
            self.finished.emit(str(self.output))
        except Exception as exc:
            self.error.emit(str(exc))
