# 오킴스 IP & Business Consulting 홈페이지

주소: https://oksip-insight.com (GitHub Pages, 저장소 `ohkimsip/ohkims-consulting`)

## 구조

| 위치 | 내용 |
|---|---|
| `content/site.json` | 메인 고정 문구(메뉴, 대표 문구, 컨설팅 분야, 연락처 등)와 분류 4개 |
| `content/posts/<글이름>/index.md` | 글 한 편. 같은 폴더에 사진을 함께 둔다 |
| `content/drafts/` | 로컬 확인용 시험 글(저장소에 올라가지 않음) |
| `templates/` | 메인·분류 목록·글 상세 틀 |
| `build.py` | 위 내용을 읽어 `_site/`에 페이지를 만든다 |
| `.github/workflows/pages.yml` | main에 올리면 GitHub가 빌드해 배포 |

## 글 올리기

1. `content/posts/2026-11-13-ai-claims/index.md` 처럼 폴더를 만든다(영문 소문자·숫자·하이픈).
2. 맨 위 머리말을 채운다.

```
---
title: 생성형 AI 발명, 청구항은 어떻게 쓸까
category: magazine        # client-stories | inside-ohkims | tech-insights | magazine
date: 2026-11-13
author: 김종승 변리사
tags: AI, 청구항
summary: 목록에 보일 한두 문장
cover: cover.jpg          # 선택, 같은 폴더의 사진
---
본문(마크다운)
```

3. main에 올리면 1~2분 뒤 반영된다. 글을 내릴 때는 폴더를 지우거나 `draft: true`.

## 로컬 확인

```
python build.py --drafts --out C:/ohkims_site_preview
python -m http.server 8765 --directory C:/ohkims_site_preview
```

## 공개 전 할 일

- `content/site.json`의 `"noindex": true`를 `false`로 바꾸면 검색 노출이 열린다(robots.txt도 자동으로 바뀐다).
