# youtube-lesson-site

A [Claude Code](https://claude.com/claude-code) skill that turns a YouTube video into a single-file "main points" lesson website: dark theme, sticky table of contents, numbered sections, analogies, SVG figures, tables, optional interactive labs and practice tasks.

Content comes only from the video's captions. If a video has no captions, the skill stops and asks you for a transcript instead of guessing from the title.

## Install

Skills live in a `skills/` folder that Claude Code scans. Pick one:

**Personal (all projects)**

```bash
git clone https://github.com/gamakusumah/youtube-lesson-site.git ~/.claude/skills/youtube-lesson-site
```

**Single project**

```bash
git clone https://github.com/gamakusumah/youtube-lesson-site.git .claude/skills/youtube-lesson-site
```

Restart Claude Code (or start a new session) so it picks up the skill.

## Usage

Give Claude a YouTube link and ask for a summary page:

```
Make a main-points lesson site for https://www.youtube.com/watch?v=VIDEO_ID
```

or invoke it directly with `/youtube-lesson-site`. The result is saved as `./<slug>-lesson.html` in the working directory. Existing files are never overwritten. Ask for a translation and you get a separate file.

## Requirements

- Python 3 (standard library only).
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp), used to fetch captions. If it isn't on your `PATH` or in `~/.local/bin`, the script downloads the standalone binary to `~/.local/bin/yt-dlp`.
- Optional: a Playwright browser tool, which Claude uses to check the finished page.

The page loads fonts from Google Fonts; offline it falls back to system fonts.

## Layout

```
SKILL.md                        skill instructions
scripts/get_transcript.py       fetches and cleans captions
references/content-guidelines.md  section design and accuracy rules
assets/reference-design.html    fixed page design to copy from
```
