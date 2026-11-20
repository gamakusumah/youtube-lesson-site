#!/usr/bin/env python3
"""Fetch a cleaned transcript (captions only, no video) for a YouTube URL.

Usage:
  python3 -I get_transcript.py <youtube-url> [--lang xx] [--out DIR]

Writes <out>/transcript.txt and <out>/meta.json and prints a short report.
Standard library only. Uses yt-dlp (found on PATH or ~/.local/bin); if it is
missing, the standalone yt-dlp script is downloaded to ~/.local/bin/yt-dlp.
"""
import argparse
import glob
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

YTDLP_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
LOCAL_BIN = os.path.expanduser("~/.local/bin/yt-dlp")


def die(msg, code=1):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(code)


def video_id(url):
    u = urllib.parse.urlparse(url)
    if u.netloc.endswith("youtu.be"):
        vid = u.path.strip("/")
    else:
        vid = urllib.parse.parse_qs(u.query).get("v", [""])[0]
        if not vid:
            m = re.search(r"/(?:shorts|embed|live)/([\w-]{11})", u.path)
            vid = m.group(1) if m else ""
    if not re.fullmatch(r"[\w-]{11}", vid or ""):
        die("could not find an 11-character video id in: " + url)
    return vid


def find_ytdlp():
    found = shutil.which("yt-dlp")
    if found:
        return found
    if os.path.isfile(LOCAL_BIN) and os.access(LOCAL_BIN, os.X_OK):
        return LOCAL_BIN
    print("yt-dlp not found; downloading standalone script to " + LOCAL_BIN, file=sys.stderr)
    os.makedirs(os.path.dirname(LOCAL_BIN), exist_ok=True)
    try:
        with urllib.request.urlopen(YTDLP_URL, timeout=60) as r, open(LOCAL_BIN, "wb") as f:
            shutil.copyfileobj(r, f)
    except Exception as e:  # noqa: BLE001
        die("could not download yt-dlp: %s. Install it manually or paste the transcript." % e)
    os.chmod(LOCAL_BIN, os.stat(LOCAL_BIN).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return LOCAL_BIN


def oembed(url):
    q = urllib.parse.quote(url, safe="")
    try:
        with urllib.request.urlopen(
            "https://www.youtube.com/oembed?format=json&url=" + q, timeout=20
        ) as r:
            d = json.load(r)
        return {"title": d.get("title", ""), "channel": d.get("author_name", "")}
    except Exception:  # noqa: BLE001
        return {"title": "", "channel": ""}


def run(cmd, timeout=180):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def pick_language(info, wanted):
    manual = list((info.get("subtitles") or {}).keys())
    auto = list((info.get("automatic_captions") or {}).keys())
    if wanted:
        return wanted
    spoken = (info.get("language") or "").split("-")[0]
    for cand in manual:
        if spoken and cand.split("-")[0] == spoken:
            return cand
    if manual:
        return manual[0]
    for cand in auto:  # original-language auto captions are usually "<lang>-orig"
        if cand.endswith("-orig"):
            return cand
    if spoken and spoken in auto:
        return spoken
    if "en" in auto:
        return "en"
    if auto:
        return auto[0]
    return ""


def clean_vtt(path):
    lines, last = [], None
    for raw in open(path, encoding="utf-8", errors="replace"):
        line = raw.strip()
        if not line or "-->" in line or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        line = re.sub(r"<[^>]+>", "", line).strip()
        if line and line != last:
            lines.append(line)
            last = line
    text = " ".join(lines)
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&#39;", "'"), ("&quot;", '"')):
        text = text.replace(a, b)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--lang", default="", help="caption language code, e.g. en, id")
    ap.add_argument("--out", default="", help="output dir (default: new temp dir)")
    a = ap.parse_args()

    vid = video_id(a.url)
    out = a.out or tempfile.mkdtemp(prefix="yt-transcript-")
    os.makedirs(out, exist_ok=True)
    ytdlp = find_ytdlp()
    meta = oembed(a.url)

    info = {}
    r = run([ytdlp, "--skip-download", "--dump-single-json", "--no-warnings", a.url])
    if r.returncode == 0:
        try:
            info = json.loads(r.stdout)
        except ValueError:
            info = {}
    lang = pick_language(info, a.lang)
    if not lang:
        die("no captions found for this video (manual or automatic). "
            "Ask the user to paste the transcript.", 2)

    # one language per request: asking for several at once triggered HTTP 429
    base = os.path.join(out, vid)
    cmd = [ytdlp, "--skip-download", "--write-subs", "--write-auto-subs",
           "--sub-langs", lang, "--sub-format", "vtt", "--sleep-subtitles", "3",
           "--no-warnings", "-o", base, a.url]
    files = []
    for attempt in range(4):
        r = run(cmd)
        files = glob.glob(base + ".*.vtt")
        if files:
            break
        if "429" in (r.stderr + r.stdout):
            wait = 20 * (attempt + 1)
            print("rate limited (HTTP 429); waiting %ds" % wait, file=sys.stderr)
            time.sleep(wait)
        else:
            break
    if not files:
        die("caption download failed: " + (r.stderr.strip().splitlines() or ["unknown"])[-1], 3)

    text = clean_vtt(files[0])
    if not text:
        die("captions downloaded but empty", 3)
    with open(os.path.join(out, "transcript.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    meta.update({
        "video_id": vid,
        "url": a.url,
        "title": meta["title"] or info.get("title", ""),
        "channel": meta["channel"] or info.get("channel", "") or info.get("uploader", ""),
        "caption_language": lang,
        "spoken_language": lang.replace("-orig", "").split("-")[0],
        "caption_kind": "manual" if lang in (info.get("subtitles") or {}) else "auto-generated",
        "duration_seconds": info.get("duration"),
        "characters": len(text),
    })
    with open(os.path.join(out, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("title:    ", meta["title"])
    print("channel:  ", meta["channel"])
    print("language: ", lang, "(%s)" % meta["caption_kind"])
    print("chars:    ", len(text))
    print("output:   ", out)


if __name__ == "__main__":
    main()
