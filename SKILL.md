---
name: video-subtitle-markdown-notes
description: Convert a provided video plus subtitle file into Chinese Markdown notes that preserve every subtitle word, add punctuation and one-level sectioning, insert screenshot placeholders for visually useful moments, then use ffmpeg to replace placeholders with local screenshot images. Use when the user provides video and subtitle files and asks for Markdown notes, transcript notes, lecture notes, course notes, or screenshot-enriched notes.
---

# Video Subtitle Markdown Notes

## Workflow

Use this skill only when both a video file and a subtitle/transcript file are available.

1. Read the subtitle file first. For timed formats such as `.srt`, `.vtt`, `.ass`, or `.ssa`, preserve cue timing because screenshot placeholders use the sentence end time.
2. Convert the subtitle text into Chinese Markdown notes. Keep necessary proper nouns, product names, APIs, code terms, URLs, commands, and English terminology in English.
3. Preserve all spoken/subtitle text. Do not summarize, omit, merge away, or delete content. Add punctuation, paragraph breaks, and Markdown structure only.
4. Use exactly one heading level: `##` for section titles. The first section is an introduction and must not have a heading.
5. Do not wrap the Markdown in a code block.
6. Insert screenshot placeholders only when they will genuinely help comprehension. Use `Screenshot-[mm:ss]` at the end of the relevant sentence, where `mm:ss` is the sentence or cue end time. If the video is longer than one hour, use total minutes, such as `75:12`.
7. Write the placeholder Markdown to a temporary `.md` file, run the screenshot replacement script, then provide the final Markdown body containing local image links.

## Screenshot Placeholder Rules

Add `Screenshot-[mm:ss]` at the end of a sentence when the sentence:

- Explains code, a command, an IDE/editor view, terminal output, or a visual diagram.
- Describes UI interaction, page layout, buttons, menus, settings, panels, or a workflow visible on screen.
- Contains deictic words such as `这么`, `这里`, or `这儿`.
- Mentions taking/opening/visiting a specific website, URL, address, or page.
- Compares key technical concepts where a visual frame helps distinguish the ideas.
- Would be materially easier to understand with the current frame.

Do not add placeholders mechanically. Skip screenshots for generic narration, greetings, repeated filler, or points that are fully clear from text alone.

## Markdown Requirements

Keep the output as Markdown body only:

- No surrounding explanations.
- No fenced code block around the full answer.
- No heading levels other than `##`.
- No bullet compression that removes original wording.
- No generated summary unless the original subtitle says it.
- No translation that changes meaning. Chinese should be natural, but every original idea and word-level content must remain represented.

## Running Screenshot Replacement

Confirm `ffmpeg` is available before running the replacement step. The script first checks `PATH`, then common winget `Gyan.FFmpeg` install locations. If needed, pass the executable path with `--ffmpeg`.

After creating placeholder Markdown, run:

```bash
python <skill_dir>/scripts/replace_screenshot_placeholders.py --video <video_path> --markdown <placeholder_md> --output <final_md>
```

The script creates a sibling image directory named `<final_md_stem>_screenshots` unless `--image-dir` is provided. It replaces each `Screenshot-[mm:ss]` placeholder with a local Markdown image link such as:

```markdown
![Screenshot 03:27](notes_screenshots/screenshot-03-27.jpg)
```

Use `--overwrite` when regenerating an existing output file or screenshots.

## Quality Check

Before finalizing:

- Verify there are no remaining `Screenshot-[...]` placeholders.
- Verify every generated image path exists.
- Spot-check a few screenshots against the nearby note text.
- Confirm the final Markdown still preserves all subtitle content and uses only `##` headings.
