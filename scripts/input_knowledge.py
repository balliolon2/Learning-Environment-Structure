#!/usr/bin/env python3
"""Convert sources into Markdown files under <topic>/knowledge/.

Usage (Windows):
    .venv\\Scripts\\python scripts\\input_knowledge.py <topic> <source> [<source> ...]

Each source is one of:
  - a .pdf, .txt or .md file: absolute path, path relative to the repo root,
    or path relative to <topic>/input-knowledge/
  - a YouTube URL: the transcript is fetched
  - any other http(s) URL: the main article text is extracted

Source-language text is kept as-is. Nothing is translated.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
TOPIC_RE = re.compile(r"[a-z0-9][a-z0-9-]*")
YOUTUBE_LANGS = ["th", "en"]


class IngestError(Exception):
    """A source that cannot be converted. The message is shown to the user."""


def slugify(text: str, max_len: int = 80) -> str:
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:max_len].strip("-") or "untitled"


def unique_path(path: Path) -> Path:
    """Return path, or path with a -2, -3, ... suffix if it already exists."""
    candidate = path
    i = 2
    while candidate.exists():
        candidate = path.with_name(f"{path.stem}-{i}{path.suffix}")
        i += 1
    return candidate


def front_matter(source: str, kind: str, title: str) -> str:
    def clean(value: str) -> str:
        return value.replace('"', "'")

    lines = [
        "---",
        f'source: "{clean(source)}"',
        f"type: {kind}",
        f'title: "{clean(title)}"',
        f"ingested_at: {dt.datetime.now().isoformat(timespec='seconds')}",
        "---",
    ]
    return "\n".join(lines) + "\n\n"


def resolve_file(topic_dir: Path, source: str) -> Path:
    raw = Path(source)
    if raw.is_absolute():
        candidates = [raw]
    else:
        candidates = [topic_dir / "input-knowledge" / raw, REPO_ROOT / raw]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise IngestError(
        f"{source}: file not found (looked in <topic>/input-knowledge/ and repo root)"
    )


def from_pdf(path: Path) -> tuple[str, str]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as exc:
            raise IngestError(f"{path.name}: encrypted PDF, cannot decrypt") from exc

    parts = []
    for number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            parts.append(f"## Page {number}\n\n{text}")
    if not parts:
        raise IngestError(f"{path.name}: no extractable text (scanned/image-only PDF?)")

    title = (reader.metadata.title if reader.metadata else None) or path.stem
    return "\n\n".join(parts), title


def from_text(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        # cp874 covers legacy Thai encodings (TIS-620)
        text = raw.decode("cp874")
    if not text.strip():
        raise IngestError(f"{path.name}: file is empty")
    return text.strip(), path.stem


def from_web(url: str) -> tuple[str, str]:
    import trafilatura

    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise IngestError(f"{url}: could not download page")
    text = trafilatura.extract(
        downloaded,
        output_format="markdown",
        include_links=True,
        include_tables=True,
    )
    if not text:
        raise IngestError(f"{url}: no main content extracted")
    meta = trafilatura.extract_metadata(downloaded)
    title = (meta.title if meta and meta.title else None) or urlparse(url).netloc
    return text, title


def youtube_id(url: str) -> str | None:
    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.").removeprefix("m.")
    if host == "youtu.be":
        return parsed.path.strip("/").split("/")[0] or None
    if host in ("youtube.com", "youtube-nocookie.com"):
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]
        match = re.match(r"/(shorts|embed|live)/([^/?#]+)", parsed.path)
        if match:
            return match.group(2)
    return None


def from_youtube(video_id: str) -> tuple[str, str]:
    from youtube_transcript_api import YouTubeTranscriptApi

    try:
        transcript = YouTubeTranscriptApi().fetch(video_id, languages=YOUTUBE_LANGS)
    except Exception as exc:
        raise IngestError(
            f"youtube:{video_id}: no transcript available ({type(exc).__name__})"
        ) from exc

    lines = []
    for snippet in transcript:
        minutes, seconds = divmod(int(snippet.start), 60)
        hours, minutes = divmod(minutes, 60)
        stamp = f"{hours}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"
        lines.append(f"- [{stamp}] {snippet.text}")
    if not lines:
        raise IngestError(f"youtube:{video_id}: transcript is empty")
    return "\n".join(lines), f"YouTube {video_id}"


def convert(topic_dir: Path, source: str) -> Path:
    """Convert one source and write it to <topic>/knowledge/. Returns the output path."""
    knowledge_dir = topic_dir / "knowledge"
    scheme = urlparse(source).scheme

    if scheme in ("http", "https"):
        video_id = youtube_id(source)
        if video_id:
            body, title = from_youtube(video_id)
            kind, base, display = "youtube", f"youtube-{video_id}", source
        else:
            body, title = from_web(source)
            kind, base, display = "web", title, source
    else:
        path = resolve_file(topic_dir, source)
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            body, title = from_pdf(path)
            kind = "pdf"
        elif suffix in (".txt", ".md"):
            body, title = from_text(path)
            kind = "text"
        else:
            raise IngestError(f"{source}: unsupported file type '{suffix or '(none)'}'")
        base, display = path.stem, path.name

    out = unique_path(knowledge_dir / f"{slugify(base)}.md")
    out.write_text(front_matter(display, kind, title) + body + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert sources into <topic>/knowledge/*.md")
    parser.add_argument("topic", help="topic folder name at repo root (kebab-case)")
    parser.add_argument("sources", nargs="+", help="file path, http(s) URL, or YouTube URL")
    args = parser.parse_args(argv)

    if not TOPIC_RE.fullmatch(args.topic):
        print(
            f"error: invalid topic name '{args.topic}' (use lowercase letters, digits, hyphens)",
            file=sys.stderr,
        )
        return 2

    topic_dir = REPO_ROOT / args.topic
    if not topic_dir.is_dir():
        print(f"error: topic '{args.topic}' does not exist; run /new-topic first", file=sys.stderr)
        return 2
    (topic_dir / "knowledge").mkdir(exist_ok=True)

    failures = 0
    for source in args.sources:
        try:
            out = convert(topic_dir, source)
        except IngestError as exc:
            failures += 1
            print(f"FAILED: {exc}", file=sys.stderr)
        except Exception as exc:  # missing dependency, network error, etc.
            failures += 1
            print(f"FAILED: {source}: {type(exc).__name__}: {exc}", file=sys.stderr)
        else:
            print(f"OK: {out.relative_to(REPO_ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
