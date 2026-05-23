# Quick Save — Zettelkasten 즉시 저장 스킬

> `/km-quick` 명령어용 경량 스킬 참조. 질문·탐색·분석 없이 원본 그대로 Obsidian Zettelkasten에 저장.

---

## 스킬 계약

| 항목 | 내용 |
|------|------|
| **하는 것** | 텍스트/URL 콘텐츠를 frontmatter만 붙여서 Zettelkasten/에 즉시 저장 |
| **트리거** | `/km-quick` 명령어 호출 |
| **하지 않는 것** | 질문, vault 탐색, 분석, 요약, 분할, 연결 강화, 이미지 추출 |
| **필요 리소스** | Obsidian MCP (1순위) 또는 Write (폴백) |

## 저장 경로 규칙

```
Zettelkasten/{category}/{title} - {YYYY-MM-DD}.md
```

카테고리 자동 분류 키워드: 프로그래밍, AI-연구, 리서치, 요리, 라이프, 뉴스, 인사이트(기본)

## Frontmatter 최소 스키마

```yaml
id: YYYYMMDDHHmm          # 필수
title: string              # 필수
created: ISO 8601          # 필수
tags: [array]              # 필수 (2-5개)
category: string           # 필수
source: string             # 필수 (URL 또는 "direct-input")
type: atomic               # 고정
```

## 소셜 미디어 URL 감지

| 패턴 | 처리 |
|------|------|
| `threads.net/*` | Playwright 스크래핑 → km-social-media.md 참조 |
| `instagram.com/*` | 동일 |
| `youtube.com/*` | WebFetch로 메타 추출 |
| 기타 URL | WebFetch로 본문 추출 |

## 성능 목표

- 텍스트 입력: **2-3초** 이내 저장 완료
- URL 입력: **10-15초** 이내 (스크래핑 포함)
- 전체 knowledge-manager 대비 **10배 이상** 빠름
