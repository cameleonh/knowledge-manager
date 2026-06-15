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
