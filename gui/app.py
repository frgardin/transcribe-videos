from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton,
    QComboBox, QCheckBox, QTextEdit, QProgressBar,
    QFileDialog, QGroupBox, QFormLayout, QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from transcribe_yt.formats import OutputFormat
from gui.worker import TranscriptionWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("trs — Transcribe Videos")
        self.setMinimumWidth(540)
        self.setMinimumHeight(520)
        self._worker = None
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(16, 16, 16, 16)

        # ── Source ────────────────────────────────────────────────────────────
        self._tabs = QTabWidget()

        # YouTube tab
        yt_tab = QWidget()
        yt_form = QFormLayout(yt_tab)
        yt_form.setContentsMargins(8, 8, 8, 8)
        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        yt_form.addRow("URL:", self._url_input)
        self._tabs.addTab(yt_tab, "YouTube")

        # Local File tab
        file_tab = QWidget()
        file_form = QFormLayout(file_tab)
        file_form.setContentsMargins(8, 8, 8, 8)
        file_row = QHBoxLayout()
        self._file_input = QLineEdit()
        self._file_input.setPlaceholderText("Select an audio or video file…")
        file_browse_btn = QPushButton("Browse…")
        file_browse_btn.clicked.connect(self._browse_input)
        file_row.addWidget(self._file_input)
        file_row.addWidget(file_browse_btn)
        file_form.addRow("File:", file_row)
        self._gpu_check = QCheckBox("Use GPU (cuda)")
        file_form.addRow("", self._gpu_check)
        self._tabs.addTab(file_tab, "Local File")

        root.addWidget(self._tabs)

        # ── Output ────────────────────────────────────────────────────────────
        out_group = QGroupBox("Output")
        out_form = QFormLayout(out_group)
        out_row = QHBoxLayout()
        self._output_input = QLineEdit()
        self._output_input.setPlaceholderText("transcript.txt")
        out_browse_btn = QPushButton("Browse…")
        out_browse_btn.clicked.connect(self._browse_output)
        out_row.addWidget(self._output_input)
        out_row.addWidget(out_browse_btn)
        out_form.addRow("Save to:", out_row)
        root.addWidget(out_group)

        # ── Options ───────────────────────────────────────────────────────────
        opt_group = QGroupBox("Options")
        opt_form = QFormLayout(opt_group)

        self._model_combo = QComboBox()
        self._model_combo.addItems(["tiny", "base", "small", "medium", "large"])
        self._model_combo.setCurrentText("base")

        self._format_combo = QComboBox()
        self._format_combo.addItems(["txt", "srt", "vtt"])

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Model:"))
        row1.addWidget(self._model_combo)
        row1.addSpacing(16)
        row1.addWidget(QLabel("Format:"))
        row1.addWidget(self._format_combo)
        row1.addStretch()
        opt_form.addRow(row1)

        self._lang_input = QLineEdit()
        self._lang_input.setPlaceholderText("auto-detect  (e.g. en, pt, es)")
        self._lang_input.setFixedWidth(220)
        self._timestamps_check = QCheckBox("Timestamps")

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Language:"))
        row2.addWidget(self._lang_input)
        row2.addSpacing(16)
        row2.addWidget(self._timestamps_check)
        row2.addStretch()
        opt_form.addRow(row2)

        root.addWidget(opt_group)

        # ── Action row ────────────────────────────────────────────────────────
        action_row = QHBoxLayout()
        self._transcribe_btn = QPushButton("Transcribe")
        self._transcribe_btn.setFixedHeight(38)
        self._transcribe_btn.setFixedWidth(120)
        self._transcribe_btn.clicked.connect(self._start)
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)   # indeterminate pulse
        self._progress.setVisible(False)
        self._progress.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        action_row.addWidget(self._transcribe_btn)
        action_row.addWidget(self._progress)
        root.addLayout(action_row)

        # ── Log ───────────────────────────────────────────────────────────────
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFixedHeight(130)
        self._log.setFont(QFont("Monospace", 9))
        self._log.setPlaceholderText("Transcription log will appear here…")
        root.addWidget(self._log)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _browse_input(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select audio or video file", "",
            "Media files (*.mp3 *.mp4 *.wav *.m4a *.webm *.mkv *.ogg *.flac);;All files (*)"
        )
        if path:
            self._file_input.setText(path)
            if not self._output_input.text():
                self._output_input.setText(str(Path(path).with_suffix(".txt")))

    def _browse_output(self):
        fmt = self._format_combo.currentText()
        filters = {
            "txt": "Text files (*.txt)",
            "srt": "SubRip subtitles (*.srt)",
            "vtt": "WebVTT subtitles (*.vtt)",
        }
        path, _ = QFileDialog.getSaveFileName(
            self, "Save transcript as", "",
            f"{filters.get(fmt, 'All files (*)')};;All files (*)"
        )
        if path:
            self._output_input.setText(path)

    def _start(self):
        mode = "youtube" if self._tabs.currentIndex() == 0 else "file"
        source = (
            self._url_input.text().strip()
            if mode == "youtube"
            else self._file_input.text().strip()
        )
        output = self._output_input.text().strip()

        if not source:
            self._log.append("⚠  Please enter a URL or select a file.")
            return
        if not output:
            self._log.append("⚠  Please specify an output file path.")
            return

        fmt = OutputFormat(self._format_combo.currentText())
        language = self._lang_input.text().strip() or None
        device = "cuda" if self._gpu_check.isChecked() else "cpu"

        self._log.clear()
        self._transcribe_btn.setEnabled(False)
        self._progress.setVisible(True)

        self._worker = TranscriptionWorker(
            mode=mode,
            source=source,
            output=output,
            model=self._model_combo.currentText(),
            language=language,
            fmt=fmt,
            timestamps=self._timestamps_check.isChecked(),
            device=device,
        )
        self._worker.log.connect(self._log.append)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, path: str):
        self._log.append(f"✓  Saved to {path}")
        self._transcribe_btn.setEnabled(True)
        self._progress.setVisible(False)

    def _on_error(self, msg: str):
        self._log.append(f"✗  Error: {msg}")
        self._transcribe_btn.setEnabled(True)
        self._progress.setVisible(False)
