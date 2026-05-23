# Video Subtitle Markdown Notes

A Codex skill for turning a video plus subtitle file into Chinese Markdown notes, then replacing visual screenshot placeholders with local images captured from the source video.

## What It Does

- Converts timed subtitle files into Markdown notes.
- Preserves all subtitle text instead of summarizing or deleting content.
- Uses Chinese prose while keeping necessary proper nouns and technical terms in English.
- Uses only one Markdown heading level: `##`.
- Inserts `Screenshot-[mm:ss]` placeholders only when a visual frame helps comprehension.
- Uses `ffmpeg` to replace screenshot placeholders with local Markdown image links.

## Repository Layout

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   └── replace_screenshot_placeholders.py
└── examples/
    └── placeholder-notes.md
```

## Requirements

- Python 3.10+
- ffmpeg
- Codex or another workflow that can use `SKILL.md` instructions

The screenshot script first checks `PATH`, then common winget `Gyan.FFmpeg` install locations on Windows. You can also pass an explicit executable path with `--ffmpeg`.

## Install As A Codex Skill

Clone or copy this repository into your Codex skills directory:

```bash
~/.codex/skills/video-subtitle-markdown-notes
```

On Windows, this is typically:

```powershell
C:\Users\<you>\.codex\skills\video-subtitle-markdown-notes
```

## Screenshot Replacement

After generating Markdown with placeholders such as `Screenshot-[03:27]`, run:

```bash
python scripts/replace_screenshot_placeholders.py --video input.mp4 --markdown placeholder-notes.md --output final-notes.md
```

If ffmpeg is not discoverable:

```bash
python scripts/replace_screenshot_placeholders.py --video input.mp4 --markdown placeholder-notes.md --output final-notes.md --ffmpeg "C:\path\to\ffmpeg.exe"
```

The script writes screenshots next to the output Markdown by default:

```text
final-notes.md
final-notes_screenshots/
  screenshot-03-27.jpg
```

## License

MIT
