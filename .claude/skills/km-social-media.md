---
name: km-social-media
description: Use when scraping social media content. Detects social media URLs and extracts content via Playwright CLI with scroll-based reply loading.
---

# 소셜 미디어 콘텐츠 스크래핑 스킬

> Knowledge Manager 파이프라인의 소셜 미디어 URL 자동 감지 및 Playwright 기반 콘텐츠 추출 스킬

---

## MANDATORY ACTIONS

Run the following tools in order when a social media URL is detected.

### Tool Priority (CRITICAL)

> Threads/Instagram use login walls and dynamic loading — scrapling returns only the first post.
> Use Playwright CLI as the primary tool.

```
# 1. Use Playwright CLI (Bash — required for SNS. Scrolls to load replies)
Run: playwright-cli open "[URL]"       # Open browser and navigate
Run: sleep 3                           # Wait for dynamic content
Run: playwright-cli snapshot           # Create accessibility snapshot
# Check the snapshot: Read(".playwright-cli/page-*.yml")
# If replies are truncated:
Run: playwright-cli press End          # Scroll to bottom
Run: sleep 2
Run: playwright-cli snapshot           # Add more content
Run: playwright-cli close              # Close browser

# 2. Use Scrapling only if CLI fails (may return first post only)
Run: python3 scripts/scrapling-crawl.py fetch "[URL]" --mode dynamic --output markdown
Run: python3 scripts/scrapling-crawl.py fetch "[URL]" --mode stealth --output markdown
```

### Playwright MCP — Do Not Use for SNS

Use `playwright-cli` (Bash) exclusively for social media. See km-content-extraction for non-SNS sources.
MCP is unstable with SNS dynamic loading and scroll control.

---

## Instagram 미디어(이미지/릴스) 원본 파일 수집

> Playwright 스크래핑은 **본문/댓글 텍스트**만 가져온다. 이미지·릴스 비디오 **원본 파일**을 vault에 저장하려면 `instaloader`를 사용한다.
> Instagram CDN은 브라우저 외 HTTP 요청(curl/fetch/`page.goto(이미지URL)`)을 **403**으로 차단한다. 브라우저가 `<img>`로 로드할 때만 200이 떨어지므로, **`instaloader`(로컬 Python)** 가 가장 안정적이고 단순하다.

### 사전 요구

- Python 3.10+ 와 `uv` (없으면 `pip install instaloader`)
- **비로그인(anonymous)**: 공개 계정 가능. 약 15~20건 연속 요청 후 rate limit(429/403) → 스크립트의 `--delay`/`--retries`로 완화. 대량·비공개 계정은 `--login <user>` 세션 사용.

### 절차

1. URL에서 **shortcode** 추출
   - 게시물: `https://www.instagram.com/p/<shortcode>/`
   - 릴스:     `https://www.instagram.com/reel/<shortcode>/`
2. 스크립트 실행 (`uv`가 instaloader를 임시 설치):
   ```bash
   uv run --with instaloader python scripts/instagram-dl.py <shortcode> [<shortcode2> ...] \
     --media-root "<VAULT>/Resources/images/SNS" \
     --notes-dir  "<VAULT>/Zettelkasten/인사이트/SNS-media" \
     --delay 3 --retries 3
   ```
   **dedup**: `Resources/images/SNS/{shortcode}/` 에 미디어가 이미 있으면 skip한다. 강제 재수집은 `--force`.
3. 결과 (각 shortcode당)
   - 미디어: `{media-root}/{shortcode}/` 아래 원본 — 사진은 `.jpg`, 릴스는 `.mp4`. **캐러셀은 전체 슬라이드** 모두 저장.
   - 노트: `{notes-dir}/{author}-{shortcode}.md` — frontmatter(`likes`/`comments`/`author`/`post_date`/`shortcode`/`media_count`) + 캡션 원문 + `![[...]]` 이미지/비디오 임베드.
4. 실패(403/429)한 shortcode는 스크립트가 요약 출력 → 수 분 후 재시도.

### 비디오(릴스)

`instagram-dl.py`는 `download_videos=True`로 릴스 `.mp4`를 받고 썸네일은 생략한다. 노트에 `![[...mp4]]`로 임베드하면 Obsidian에서 재생 가능.

### Threads 게시물 (주의)

`instaloader`는 **Instagram 전용**. Threads(`threads.net/@user/post/...`) 게시물은 미디어 수집을 지원하지 않는다. 본문은 위 **MANDATORY ACTIONS**의 Playwright 스크래핑으로 처리한다.

### 대량/배치

shortcode 여러 개를 한 번에 넘기면 순차 처리(게시물 간 delay). 1건당 약 3~6초. 전체 완료 후 `OK N/M` 요약과 실패 목록을 출력한다.

---

## Threads 게시물 수집 (비디오 + 본문 자동 분기)

> Threads는 **비디오 / 이미지 / 텍스트(칼럼)** 게시물이 혼재한다. 플랫폼 감지 후 자동 분기한다.
> Threads도 Meta CDN이라 별도 HTTP(curl/fetch)는 403 → **비디오는 전용 스크립트, 본문은 Playwright**로 수집.

### 1. 비디오 게시물 — `download_threads_video.py`

```bash
python -B ~/.claude/skills/threads-video-downloader/scripts/download_threads_video.py "<THREADS_URL>" \
  --output-dir "<VAULT>/Resources/images/SNS/<shortcode>" --overwrite
```
- public 게시물만. private/login-gated는 실패.
- 비디오가 없는 게시물 → `error: No video_versions URL found` → 텍스트/이미지 케이스(아래)로 넘어간다.

### 2. 텍스트 / 이미지 칼럼 — Playwright

1. `browser_navigate(URL)` → `browser_evaluate`로 `[aria-label="칼럼 본문"]` region의 `innerText` 추출. 이게 원문 전체(페이지 분할 "1/2" 표시와 댓글까지 포함).
2. 메타: region 텍스트 첫 줄 = username, "N일/시간" = 작성 시각, 숫자 = 좋아요.
3. 이미지: 게시물이 `image_versions2`를 가지면 URL 캡처 — Instagram과 동일하게 reload 후 `page.on('response')`로 가로채기(브라우저만 200).
4. 비디오가 있었으면 1번에서 받은 mp4를 노트에 임베드.

### 노트

`Zettelkasten/인사이트/SNS-media/{author}-{shortcode}.md` — Instagram과 동일 frontmatter(`platform: Threads`). Threads는 본문 자체가 콘텐츠이므로 **원문 전체를 그대로** 저장하고, 비디오/이미지가 있으면 임베드.
