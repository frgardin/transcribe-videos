from dataclasses import dataclass
from enum import Enum


class OutputFormat(str, Enum):
    txt = "txt"
    srt = "srt"
    vtt = "vtt"


@dataclass
class Segment:
    start: float
    end: float
    text: str


def _hms(seconds: float, ms_sep: str = ",") -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds % 1) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d}{ms_sep}{ms:03d}"


def _hms_short(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def to_txt(segments: list["Segment"], timestamps: bool = False) -> str:
    if not timestamps:
        return " ".join(seg.text.strip() for seg in segments)
    return "\n".join(f"[{_hms_short(seg.start)}] {seg.text.strip()}" for seg in segments)


def to_srt(segments: list["Segment"]) -> str:
    blocks = []
    for i, seg in enumerate(segments, 1):
        blocks.append(
            f"{i}\n{_hms(seg.start)} --> {_hms(seg.end)}\n{seg.text.strip()}\n"
        )
    return "\n".join(blocks)


def to_vtt(segments: list["Segment"]) -> str:
    lines = ["WEBVTT", ""]
    for seg in segments:
        lines.append(f"{_hms(seg.start, '.')} --> {_hms(seg.end, '.')}")
        lines.append(seg.text.strip())
        lines.append("")
    return "\n".join(lines)


def render(segments: list["Segment"], fmt: OutputFormat, timestamps: bool = False) -> str:
    if fmt == OutputFormat.srt:
        return to_srt(segments)
    if fmt == OutputFormat.vtt:
        return to_vtt(segments)
    return to_txt(segments, timestamps=timestamps)
