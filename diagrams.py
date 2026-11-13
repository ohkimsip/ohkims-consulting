"""본문 도해 블록을 오킴스 디자인 HTML로 그린다(그림 파일이 아니라 글자 — 검색·AI가 읽을 수 있다).

원고(마크다운)에 이렇게 쓴다:

```steps
출원 전 조사 | 선행기술을 찾아 차별점을 정리합니다
청구항 설계 | 보호 범위를 단계별로 나눕니다
```
```checklist
# 출원 전 점검
- 공개 일정이 출원보다 앞서지 않는가
- 비교 실험 결과가 있는가
```
```compare
구분 | 방법 청구항 | 장치 청구항
대상 | 처리 단계 | 구성 요소
```
```keypoint
알고리즘 자체가 아니라, 하드웨어와 결합해 기술 문제를 푸는 구성이 특허 대상입니다.
```
```flow
아이디어 > 선행조사 > 출원 > 심사 > 등록
```
"""
from __future__ import annotations

import html
import re

BLOCK = re.compile(r'<pre><code class="language-(steps|checklist|compare|keypoint|flow)">(.*?)</code></pre>', re.S)


def _lines(raw: str) -> list[str]:
    return [l.strip() for l in html.unescape(raw).splitlines() if l.strip()]


def _e(s: str) -> str:
    return html.escape(s, quote=False)


def _steps(lines):
    items = []
    for i, l in enumerate(lines, 1):
        l = re.sub(r"^\d+[.)]\s*", "", l)
        head, _, desc = l.partition("|")
        items.append(f'<li><span class="dg-n">{i}</span><div><strong>{_e(head.strip())}</strong>'
                     + (f"<p>{_e(desc.strip())}</p>" if desc.strip() else "") + "</div></li>")
    return f'<ol class="dg dg-steps">{"".join(items)}</ol>'


def _checklist(lines):
    title = "점검 목록"
    if lines and lines[0].startswith("#"):
        title, lines = lines[0].lstrip("# ").strip(), lines[1:]
    lis = "".join(f"<li>{_e(re.sub(r'^[-*•]\s*|^\[[ x]\]\s*', '', l))}</li>" for l in lines)
    return f'<div class="dg dg-check"><p class="dg-title">{_e(title)}</p><ul>{lis}</ul></div>'


def _compare(lines):
    rows = [[c.strip() for c in l.strip("|").split("|")] for l in lines if not re.fullmatch(r"[|\s:-]+", l)]
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    head = "".join(f"<th>{_e(c)}</th>" for c in rows[0])
    body = "".join("<tr>" + f"<th scope=\"row\">{_e(r[0])}</th>" + "".join(f"<td>{_e(c)}</td>" for c in r[1:]) + "</tr>"
                   for r in rows[1:])
    return f'<div class="dg dg-compare"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def _keypoint(lines):
    return f'<div class="dg dg-key"><p>{_e(" ".join(lines))}</p></div>'


def _flow(lines):
    parts = [p.strip() for p in re.split(r"\s*(?:>|→|->)\s*", " ".join(lines)) if p.strip()]
    chips = '<span class="dg-arrow" aria-hidden="true">→</span>'.join(f'<span class="dg-chip">{_e(p)}</span>' for p in parts)
    return f'<div class="dg dg-flow" role="list">{chips}</div>'


RENDER = {"steps": _steps, "checklist": _checklist, "compare": _compare, "keypoint": _keypoint, "flow": _flow}


def render(body_html: str) -> str:
    return BLOCK.sub(lambda m: RENDER[m.group(1)](_lines(m.group(2))), body_html)
