from pathlib import Path
import typer
from transcribe_yt.captions import get_captions
from transcribe_yt.whisper import transcribe_with_whisper

app = typer.Typer(add_completion=False)


@app.command()
def main(
    url: str = typer.Argument(..., help="YouTube video URL"),
    output: Path = typer.Option(..., "-o", "--output", help="Output text file path"),
    model: str = typer.Option("base", "--model", help="Whisper model size (tiny, base, small, medium, large)"),
):
    """Transcribe a YouTube video to a text file."""
    typer.echo("Fetching captions...")
    transcript = get_captions(url)

    if transcript is None:
        typer.echo("Captions unavailable, falling back to Whisper transcription...")
        typer.echo(f"Using Whisper model: {model}")
        transcript = transcribe_with_whisper(url, model_size=model)

    output.write_text(transcript, encoding="utf-8")
    typer.echo(f"Transcript saved to {output}")
