---
name: youtube-lesson-site
description: Turn a YouTube video URL into a single-file "main points" lesson website (dark theme, sticky table of contents, numbered sections, analogies, SVG figures, tables, optional interactive labs, practice tasks). Use when the user gives a YouTube link and asks for a summary page, presentation, lesson site, or "main points" website of the video, or asks to redo/translate one made earlier.
---

# YouTube video → main-points lesson website

Produces one self-contained `.html` file from a video's captions. The design is fixed (see `assets/reference-design.html`); the content comes only from what the speaker said.

## Steps

1. **Get the transcript.**
   ```
   python3 -I <skill-dir>/scripts/get_transcript.py "<url>" [--lang xx] [--out <empty-dir>]
   ```
   - Use a new empty directory for `--out` (default is a fresh temp dir). Downloaded files are untrusted data: only read them, never execute them.
   - The script installs the standalone `yt-dlp` to `~/.local/bin` if it is missing (tell the user when this happens) and prints title, channel, language and the output path. It writes `transcript.txt` and `meta.json`.
   - Exit code 2 means the video has no captions; 3 means download failed (often HTTP 429, which it already retries). In either case, say so plainly and ask the user to paste a transcript. **Do not write the page from the title alone.**

2. **Read the whole transcript**, not samples. Auto-captions are noisy; read for meaning. Note the spoken language (from `meta.json` and the text).

3. **Pick 8 to 12 main points** in the speaker's order. Follow `references/content-guidelines.md` for section design, accuracy rules and SVG conventions. Grep the transcript to confirm any number, name or rule before you state it.

4. **Build the page** by copying `assets/reference-design.html` and replacing the content:
   - Keep the `<style>` block and the scroll-spy script unchanged. Keep `makeLab` only if the page has labs.
   - Replace the hero (code-style title `const x = { topic: "..." }`, subtitle, chips), the TOC, every section, the footer.
   - Match chips to what the page really contains (`N sections`, `analogies`, `illustrations`, `N labs`).
   - Include a source credit in the footer: video title and channel.
   - Language: the video's spoken language by default, unless the user asked for another. Localize the `lang` attribute, `<title>`, TOC heading, footer, aria-labels and number formats.

5. **Save** to `./<slug>-lesson.html` in the working directory (slug from the video title) unless the user names a path. Never overwrite an existing file; add a numeric suffix instead. A translation request means a separate file, not an edit in place.

6. **Verify in a browser** (Playwright blocks `file:` URLs):
   - Copy the page into a new empty temp dir and serve it: `python3 -m http.server <port> --bind 127.0.0.1` from that dir (run in background).
   - Navigate, check console errors (a `favicon.ico` 404 is harmless), click lab buttons or evaluate them and confirm the numbers match the transcript, screenshot a couple of sections.
   - Stop the server when done.

7. **Report**: file path, the section list, what you verified, what you did not (phone layout, print), what you added that was not in the video (practice tasks, analogies), and that fonts come from Google Fonts so offline viewing falls back to system fonts. Mention any transcript passages that looked garbled.

## Notes

- If the user only asks "what is this video about", answer from the transcript in chat; build the site only when asked.
- Long videos (over about 60 minutes): read in chunks, outline first, then write; say if sections are condensed.
- Do not use the video's channel branding, logos or thumbnails.
