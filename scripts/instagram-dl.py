"""Batch-download Instagram posts and generate one Obsidian note per post.

Uses instaloader (anonymous / no-login by default). For each shortcode:
  1. Downloads all media (carousel images, single photo, reel video).
  2. Extracts metadata (author, caption, date, likes, comments, media count).
  3. Writes an Obsidian note with frontmatter + caption + embedded media.

Usage:
    uv run --with instaloader python ig_dl.py <shortcode> [shortcode ...] \
        --media-root "<dir>" --notes-dir "<dir>" [--delay 3] [--retries 3]

Shortcodes may be full URLs; the trailing path segment is used.
Anonymous use hits Instagram rate limits after ~15-20 rapid requests; the
built-in delay + retry softens this. For heavy volume, add a login session.
"""
from __future__ import annotations

import argparse
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

from instaloader import Instaloader, Post


def parse_shortcode(arg: str) -> str:
    return arg.rstrip("/").split("/")[-1]


def slugify(s: str) -> str:
    keep = "-_()"
    return "".join(c if (c.isalnum() or c in keep) else "_" for c in (s or ""))[:80]


def download_one(
    loader: Instaloader,
    shortcode: str,
    media_root: Path,
    notes_dir: Path,
    retries: int,
) -> dict:
    """Download one post; return a result dict."""
    media_dir = media_root / shortcode
    media_dir.mkdir(parents=True, exist_ok=True)
    post = None
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            post = Post.from_shortcode(loader.context, shortcode)
            loader.download_post(post, target=media_dir)
            break
        except Exception as e:  # instaloader raises various; retry on transient
            last_err = str(e)
            if attempt < retries:
                time.sleep(2 * attempt)
    if post is None:
        return {"shortcode": shortcode, "ok": False, "error": last_err}

    files = sorted(p.name for p in media_dir.iterdir() if p.is_file())
    media_files = [f for f in files if not f.endswith(".txt") and not f.endswith(".json") and f != "id"]

    cap = (post.caption or "").strip()
    note_name = f"{slugify(post.owner_username)}-{shortcode}.md"
    note_path = notes_dir / note_name

    embed_lines = "\n".join(
        f"![[Resources/images/SNS/{shortcode}/{f}]]" for f in media_files
    )

    try:
        post_date = post.date_local.strftime("%Y-%m-%d")
    except Exception:
        post_date = ""

    frontmatter = f"""---
id: {datetime.now().strftime("%Y%m%d%H%M")}
title: "{slugify(post.owner_username)} - {slugify(cap.splitlines()[0]) if cap else shortcode}"
created: {datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}
tags: [SNS, Instagram, {slugify(post.owner_username)}, 철훈공유]
category: 인사이트
source: https://www.instagram.com/p/{shortcode}/
author: {post.owner_username}
platform: Instagram
type: social-post
shortcode: {shortcode}
post_date: {post_date}
likes: {post.likes}
comments: {post.comments}
media_count: {post.mediacount}
---

"""

    body = f"""# {post.owner_username} — {cap.splitlines()[0] if cap else shortcode}

> **출처**: [@{post.owner_username}](https://www.instagram.com/{post.owner_username}/) · [원문](https://www.instagram.com/p/{shortcode}/)
> **게시일**: {post_date} · **좋아요** {post.likes} · **댓글** {post.comments} · 미디어 {post.mediacount}개

## 캡션

{cap if cap else '_(캡션 없음)_'}

## 미디어

{embed_lines}

---

- 수집 채널: [[철훈 공유 SNS 링크 모음 - 2026-06-14]]
"""

    note_path.write_text(frontmatter + body, encoding="utf-8")
    return {
        "shortcode": shortcode,
        "ok": True,
        "author": post.owner_username,
        "media": media_files,
        "note": str(note_path),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("shortcodes", nargs="+")
    ap.add_argument("--media-root", default="Resources/images/SNS")
    ap.add_argument("--notes-dir", default="Zettelkasten/인사이트/SNS-media")
    ap.add_argument("--delay", type=float, default=3.0)
    ap.add_argument("--retries", type=int, default=3)
    args = ap.parse_args()

    media_root = Path(args.media_root)
    notes_dir = Path(args.notes_dir)
    notes_dir.mkdir(parents=True, exist_ok=True)

    loader = Instaloader(
        download_videos=True,
        download_video_thumbnails=False,
        save_metadata=False,
        post_metadata_txt_pattern="",
        storyitem_metadata_txt_pattern="",
        quiet=True,
    )

    codes = [parse_shortcode(c) for c in args.shortcodes]
    results = []
    for i, code in enumerate(codes, 1):
        print(f"[{i}/{len(codes)}] {code} ...", flush=True)
        res = download_one(loader, code, media_root, notes_dir, args.retries)
        results.append(res)
        if res.get("ok"):
            print(f"  OK: {len(res['media'])} file(s) -> {res['note']}", flush=True)
        else:
            print(f"  FAIL: {res.get('error')}", flush=True)
        if i < len(codes):
            time.sleep(args.delay)

    ok = sum(1 for r in results if r.get("ok"))
    print(f"\n=== DONE: {ok}/{len(results)} ok ===", flush=True)
    fails = [r["shortcode"] for r in results if not r.get("ok")]
    if fails:
        print("FAILED: " + ", ".join(fails), flush=True)
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        raise SystemExit(130)
