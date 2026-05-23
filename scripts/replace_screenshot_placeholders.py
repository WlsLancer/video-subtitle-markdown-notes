#!/usr/bin/env python3
"""Replace Screenshot-[mm:ss] placeholders with ffmpeg frame captures."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"Screenshot-\[(?P<time>(?:(?P<hours>\d{1,2}):)?(?P<minutes>\d{1,4}):(?P<seconds>\d{2}))\]")


def parse_time_to_seconds(value: str) -> int:
    parts = [int(part) for part in value.split(":")]
    if len(parts) == 2:
        minutes, seconds = parts
        hours = 0
    elif len(parts) == 3:
        hours, minutes, seconds = parts
    else:
        raise ValueError(f"Unsupported timestamp: {value}")
    if seconds > 59:
        raise ValueError(f"Timestamp seconds must be 00-59: {value}")
    return hours * 3600 + minutes * 60 + seconds


def normalize_label(total_seconds: int) -> str:
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"


def ffmpeg_timestamp(total_seconds: int) -> str:
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def markdown_path(path: Path, base_dir: Path) -> str:
    try:
        rel = path.relative_to(base_dir)
        return rel.as_posix()
    except ValueError:
        return path.resolve().as_posix()


def capture_frame(ffmpeg: str, video: Path, total_seconds: int, output: Path, overwrite: bool) -> None:
    if output.exists() and not overwrite:
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y" if overwrite else "-n",
        "-ss",
        ffmpeg_timestamp(total_seconds),
        "-i",
        str(video),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(output),
    ]
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"ffmpeg failed at {ffmpeg_timestamp(total_seconds)}: {detail}")


def resolve_ffmpeg(ffmpeg: str | None) -> str:
    if ffmpeg:
        if Path(ffmpeg).is_file():
            return str(Path(ffmpeg).resolve())
        found = shutil.which(ffmpeg)
        if found:
            return found
        raise FileNotFoundError(f"ffmpeg not found: {ffmpeg}")

    found = shutil.which("ffmpeg")
    if found:
        return found

    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        packages = Path(local_appdata) / "Microsoft" / "WinGet" / "Packages"
        matches = sorted(packages.glob("Gyan.FFmpeg_*/*/bin/ffmpeg.exe"), reverse=True)
        if matches:
            return str(matches[0])

    raise FileNotFoundError("ffmpeg not found. Install ffmpeg, restart the shell, or pass --ffmpeg <path-to-ffmpeg.exe>.")


def replace_placeholders(
    markdown: str,
    video: Path,
    output_md: Path,
    image_dir: Path,
    ffmpeg: str,
    overwrite: bool,
) -> tuple[str, list[Path]]:
    created: dict[int, Path] = {}

    def replacement(match: re.Match[str]) -> str:
        total_seconds = parse_time_to_seconds(match.group("time"))
        label = normalize_label(total_seconds)
        image_path = image_dir / f"screenshot-{label.replace(':', '-')}.jpg"
        if total_seconds not in created:
            capture_frame(ffmpeg, video, total_seconds, image_path, overwrite)
            created[total_seconds] = image_path
        link = markdown_path(image_path, output_md.parent)
        return f"![Screenshot {label}]({link})"

    return PLACEHOLDER_RE.sub(replacement, markdown), list(created.values())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True, type=Path, help="Source video file.")
    parser.add_argument("--markdown", required=True, type=Path, help="Markdown file containing Screenshot-[mm:ss] placeholders.")
    parser.add_argument("--output", required=True, type=Path, help="Final Markdown output path.")
    parser.add_argument("--image-dir", type=Path, help="Directory for generated screenshots. Defaults next to output Markdown.")
    parser.add_argument("--ffmpeg", help="ffmpeg executable path or command name.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output Markdown and screenshots.")
    args = parser.parse_args()

    video = args.video.expanduser().resolve()
    source_md = args.markdown.expanduser().resolve()
    output_md = args.output.expanduser().resolve()

    if not video.is_file():
        print(f"Video not found: {video}", file=sys.stderr)
        return 2
    if not source_md.is_file():
        print(f"Markdown not found: {source_md}", file=sys.stderr)
        return 2
    if output_md.exists() and not args.overwrite:
        print(f"Output exists, pass --overwrite to replace it: {output_md}", file=sys.stderr)
        return 2

    image_dir = args.image_dir.expanduser().resolve() if args.image_dir else output_md.with_name(f"{output_md.stem}_screenshots")
    markdown = source_md.read_text(encoding="utf-8-sig")

    try:
        ffmpeg = resolve_ffmpeg(args.ffmpeg)
        final_markdown, images = replace_placeholders(markdown, video, output_md, image_dir, ffmpeg, args.overwrite)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(final_markdown, encoding="utf-8")
    print(f"Wrote {output_md}")
    print(f"Generated {len(images)} screenshot(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
