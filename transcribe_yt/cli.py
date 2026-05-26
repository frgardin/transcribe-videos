from pathlib import Path
from typing import Annotated
import typer
from transcribe_yt.captions import get_captions
from transcribe_yt.whisper import transcribe_url, transcribe_file
from transcribe_yt.formats import OutputFormat, render

app = typer.Typer(
    name="trs",
    help="Transcribe YouTube videos or local audio/video files to text.",
    no_args_is_help=True,
)

_model_help = "Whisper model size: tiny (~75 MB), base (~150 MB), small (~470 MB), medium (~1.5 GB), large (~3 GB). Larger = more accurate but slower."
_language_help = "Language code of the audio (e.g. 'en', 'pt', 'es'). Skips auto-detection and improves accuracy."
_format_help = "Output format: txt (plain text), srt (SubRip subtitles), vtt (WebVTT subtitles)."
_timestamps_help = "Prefix each line with a timestamp (e.g. [01:23]). Only applies to txt format."
_device_help = "Device to run Whisper on. Use 'cuda' for GPU acceleration if available."


@app.command("youtube", help="Transcribe a YouTube video. Fetches captions when available; falls back to local Whisper.")
def youtube_cmd(
    url: Annotated[str, typer.Argument(help="YouTube video URL.")],
    output: Annotated[Path, typer.Option("-o", "--output", help="Output file path.")],
    model: Annotated[str, typer.Option("--model", "-m", help=_model_help)] = "base",
    language: Annotated[str | None, typer.Option("--language", "-l", help=_language_help)] = None,
    fmt: Annotated[OutputFormat, typer.Option("--format", "-f", help=_format_help)] = OutputFormat.txt,
    timestamps: Annotated[bool, typer.Option("--timestamps", "-t", help=_timestamps_help)] = False,
):
    typer.echo("Fetching captions...")
    segments = get_captions(url, language=language)

    if segments is None:
        typer.echo("Captions unavailable, falling back to Whisper transcription...")
        typer.echo(f"Model: {model}  |  Language: {language or 'auto-detect'}  |  Device: cpu")
        segments = transcribe_url(url, model_size=model, language=language)

    output.write_text(render(segments, fmt, timestamps=timestamps), encoding="utf-8")
    typer.echo(f"Saved to {output}")


@app.command("file", help="Transcribe a local audio or video file using Whisper.")
def file_cmd(
    path: Annotated[Path, typer.Argument(help="Path to the audio or video file (mp3, mp4, wav, m4a, webm, mkv, …).")],
    output: Annotated[Path, typer.Option("-o", "--output", help="Output file path.")],
    model: Annotated[str, typer.Option("--model", "-m", help=_model_help)] = "base",
    language: Annotated[str | None, typer.Option("--language", "-l", help=_language_help)] = None,
    fmt: Annotated[OutputFormat, typer.Option("--format", "-f", help=_format_help)] = OutputFormat.txt,
    timestamps: Annotated[bool, typer.Option("--timestamps", "-t", help=_timestamps_help)] = False,
    device: Annotated[str, typer.Option("--device", help=_device_help)] = "cpu",
):
    typer.echo(f"Transcribing {path.name}...")
    typer.echo(f"Model: {model}  |  Language: {language or 'auto-detect'}  |  Device: {device}  |  Format: {fmt.value}")

    segments = transcribe_file(str(path), model_size=model, language=language, device=device)

    output.write_text(render(segments, fmt, timestamps=timestamps), encoding="utf-8")
    typer.echo(f"Saved to {output}")
