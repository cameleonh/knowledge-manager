# Quick Save — Zettelkasten 즉시 저장 스킬

> `/km-quick` 명령어용 경량 스킬 참조. 질문·탐색·분석 없이 원본 그대로 Obsidian Zettelkasten에 저장.

---

## 스킬 계약

| 항목 | 내용 |
|------|------|
| **하는 것** | 텍스트/URL 콘텐츠를 frontmatter만 붙여서 Zettelkasten/에 즉시 저장. 이미지 포함 시 vault에 다운로드 후 임베드. 원본 URL 기재. |
| **트리거** | `/km-quick` 명령어 호출 |
| **하지 않는 것** | 질문, vault 탐색, 분석, 요약, 분할, 연결 강화 |
| **필요 리소스** | Obsidian MCP (1순위) 또는 Write (폴백) |

## 워크플로우

```
Step 0: Zettelkasten 폴더 구조 확인 (list_notes)
Step 1: 입력 감지 (텍스트 / URL / 소셜 URL / YouTube)
Step 2: 콘텐츠 + 이미지 추출 (webReader / WebFetch)
Step 3: 저장 (frontmatter + 원본 + 원본 출처)
```

## 저장 경로 규칙

```
Zettelkasten/{category}/{title} - {YYYY-MM-DD}.md
```

카테고리 자동 분류 키워드: 프로그래밍, AI-연구, 리서치, 요리, 라이프, 뉴스, 인사이트(기본)

## 이미지 처리

- 콘텐츠 본문 이미지만 (프로필 아바타, 아이콘, 배너 제외)
- 저장 경로: `Zettelkasten/Resources/images/{topic}/`
- 본문에 `![[이미지경로]]` 임베드

## Frontmatter 스키마

```yaml
id: YYYYMMDDHHmm          # 필수
title: string              # 필수
created: ISO 8601          # 필수
tags: [array]              # 필수 (2-5개)
category: string           # 필수
source: string             # 필수 (원본 URL)
type: atomic               # 고정
```

## 노트 템플릿

```markdown
---
id: {id}
title: {title}
created: {created}
tags: [{tags}]
category: {category}
source: {원본 URL}
type: atomic
---

# {title}

{원본 콘텐츠 그대로}

---

> **원본 출처**: [{원본 제목}]({원본 URL})
```

## 소셜 미디어 URL 감지

| 패턴 | 처리 |
|------|------|
| `threads.net/*` | webReader로 본문+이미지 추출 |
| `instagram.com/*` | 동일 |
| `youtube.com/*` | WebFetch로 메타 추출 |
| 기타 URL | WebFetch로 본문+이미지 추출 |

## 성능 목표

- 텍스트 입력: **2-3초** 이내 저장 완료
- URL 입력: **10-15초** 이내 (스크래핑 포함)
- 전체 knowledge-manager 대비 **10배 이상** 빠름
