import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from transcribe_yt.formats import Segment


def _extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:embed/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from URL: {url}")


def get_captions(url: str, language: str | None = None) -> list[Segment] | None:
    try:
        video_id = _extract_video_id(url)
        languages = [language] if language else []
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages or None)
        return [
            Segment(
                start=entry["start"],
                end=entry["start"] + entry["duration"],
                text=entry["text"],
            )
            for entry in transcript
        ]
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception:
        return None
