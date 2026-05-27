---
description: Zettelkasten quick save - text/URL content to Obsidian without questions or vault exploration
allowedTools: Read, Write, Bash, Glob, Grep, mcp__obsidian__*, mcp__playwright__*, WebFetch
---

# /km-quick — Zettelkasten Quick Save

> **질문 없이, vault 탐색 없이, 바로 저장.**
> 무거운 knowledge-manager 워크플로우 없이 텍스트나 URL 콘텐츠를 Zettelkasten에 원본 그대로 저장합니다.

---

## 워크플로우 (4단계)

```
Zettelkasten 폴더 확인 → 입력 감지 → 콘텐츠 추출(필요시) → 저장
```

### Step 0: Zettelkasten 폴더 구조 확인

처음 한 번만 폴더 구조를 확인하여 카테고리 경로를 파악합니다.

```
mcp__obsidian__list_notes({ folder: "Zettelkasten" })
→ 기존 폴더/카테고리 목록 확인
→ 이후 저장 시 적절한 카테고리 경로 선택에 활용
```

### Step 1: 입력 감지

사용자 입력을 분석하여 소스 유형 판별:

| 입력 유형 | 감지 조건 | 처리 |
|----------|----------|------|
| **일반 텍스트** | URL 패턴 없음 | frontmatter 추가 후 바로 저장 |
| **일반 URL** | `http(s)://` + 정적 사이트 | WebFetch로 추출 |
| **소셜 URL** | `threads.net`, `instagram.com` | webReader로 추출 |
| **YouTube** | `youtube.com`, `youtu.be` | WebFetch로 메타+설명 추출 |

소셜 URL 감지 시 → `km-social-media.md` 스킬 참조 (Playwright 필수).

### Step 2: 콘텐츠 추출 (URL인 경우만)

```
URL 감지 시:
├─ threads.net/* → mcp__web_reader__webReader로 본문+이미지 추출
├─ instagram.com/* → 동일
├─ youtube.com/* → WebFetch로 제목/설명/메타 추출
└─ 기타 URL → WebFetch로 본문+이미지 추출

텍스트 입력 시:
→ 추출 생략, 입력 그대로 사용
```

**이미지 추출 규칙:**
- 콘텐츠 본문에 포함된 이미지만 추출 (프로필 아바타, 아이콘, 배너 제외)
- 이미지 URL이 발견되면 vault에 다운로드 후 `![[이미지경로]]`로 임베드
- 이미지 저장 경로: `Zettelkasten/Resources/images/{topic}/`
- 이미지가 없으면 텍스트만 저장

추출 실패 시 사용자에게 원본 텍스트 직접 붙여넣기 요청. 절대 내용 추측 금지.

### Step 3: 저장

**Obsidian MCP로 직접 저장. 질문 없이 자동 판단.**

```javascript
// 자동 생성 규칙
id = 현재시각 YYYYMMDDHHmm
title = 콘텐츠 첫 줄 또는 URL 제목 (50자 이내)
tags = 콘텐츠에서 자동 추출 (2-5개)
category = 자동 분류 (아래 표 참조)
source = 원본 URL (반드시 기재)
```

**카테고리 자동 분류:**

| 키워드 힌트 | category |
|------------|----------|
| 코드, 개발, 프로그래밍, API, 프레임워크 | 프로그래밍 |
| AI, 머신러닝, 딥러닝, LLM, 모델 | AI-연구 |
| 논문, 연구, 실험, 논의 | 리서치 |
| 요리, 레시피, 음식 | 요리 |
| 여행, 맛집, 리뷰 | 라이프 |
| 정치, 경제, 사회, 뉴스 | 뉴스 |
| 기타 | 인사이트 |

**저장 경로:**
```
Zettelkasten/{category}/{title} - {YYYY-MM-DD}.md
```

**노트 템플릿:**

```markdown
---
id: {YYYYMMDDHHmm}
title: {제목}
created: {YYYY-MM-DDTHH:mm:ss}
tags: [{태그1}, {태그2}]
category: {카테고리}
source: {원본 URL}
type: atomic
---

# {제목}

{원본 콘텐츠 그대로}

---

> **원본 출처**: [{원본 제목 또는 도메인}]({원본 URL})
```

### 저장 실행

```
1순위: mcp__obsidian__create_note({ path, content })
2순위: Write 도구로 vault 경로에 직접 저장
```

저장 후 Obsidian에서 자동 열기 (obsidian-auto-open 규칙 적용).

저장 후 경로만 사용자에게 보고.

---

## 명시적으로 하지 않는 것

```
❌ AskUserQuestion 호출 없음
❌ Vault 그래프 탐색 없음
❌ 키워드/태그 검색 없음
❌ 교차 검증 없음
❌ 콘텐츠 분석/요약 없음 (원본 그대로)
❌ 연결 강화 없음
❌ MOC/분할 없음
```

---

## 사용 예시

```
/km-quick 된장찌개 레시피: 고기 볶고 된장 넣고...
→ Zettelkasten/요리/된장찌개 레시피 - 2026-05-23.md

/km-quick https://threads.net/@user/post/abc123
→ webReader로 스크래핑 → Zettelkasten/인사이트/@user 포스트 - 2026-05-23.md

/km-quick 오늘 회의에서 나온 아이디어: ...
→ Zettelkasten/인사이트/회의 아이디어 - 2026-05-23.md
```

---

## 참조

- `km-social-media.md` — Threads/Instagram 스크래핑 상세
- `zettelkasten-note.md` — 노트 템플릿 규격
- 전체 분석 필요 시 → `/knowledge-manager` 사용
