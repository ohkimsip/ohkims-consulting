"""오킴스 컨설팅 홈페이지 빌드.

content/site.json(고정 문구)과 content/posts/<글이름>/index.md(글)를 읽어
_site/ 아래에 메인·분류 목록·글 상세 페이지를 만든다.

    python build.py            # 게시된 글만
    python build.py --drafts   # draft: true 글과 content/drafts/ 도 포함(로컬 확인용)

글 파일 머리말(--- 사이) 항목:
    title     제목 (필수)
    category  client-stories | inside-ohkims | tech-insights | magazine (필수)
    date      2026-11-13 또는 2026-11-13 14:30 (필수)
    author    작성자 (선택)
    tags      쉼표로 구분 (선택)
    summary   목록·미리보기용 한두 문장 (선택, 없으면 본문 앞부분)
    cover     대표 사진 파일 이름(글 폴더 안) (선택)
    meta      카드 오른쪽 작은 글씨, 예: WIPO · 2024 (선택)
    draft     true 이면 게시하지 않음 (선택)
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
OUT = ROOT / "_site"
STATIC = ["styles.css", "main.js", "CNAME", ".nojekyll"]
REQUIRED = ("title", "category", "date")


@dataclass
class Post:
    slug: str
    title: str
    category: str
    date: datetime
    author: str = ""
    tags: list[str] = field(default_factory=list)
    summary: str = ""
    cover: str = ""
    meta: str = ""
    body_html: str = ""
    src_dir: Path | None = None

    @property
    def url(self) -> str:
        return f"/posts/{self.slug}/"

    @property
    def date_label(self) -> str:
        return self.date.strftime("%Y.%m.%d")

    @property
    def iso(self) -> str:
        return self.date.strftime("%Y-%m-%d")

    @property
    def cover_url(self) -> str:
        return f"{self.url}{self.cover}" if self.cover else ""


def parse_front_matter(text: str) -> tuple[dict, str]:
    text = text.lstrip("﻿")
    if not text.startswith("---"):
        raise ValueError("머리말(---)이 없습니다")
    end = text.find("\n---", 3)
    if end < 0:
        raise ValueError("머리말 끝(---)이 없습니다")
    head, body = text[3:end], text[end + 4:]
    meta: dict[str, str] = {}
    for line in head.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"머리말 줄 형식 오류: {line!r}")
        k, v = line.split(":", 1)
        meta[k.strip().lower()] = v.strip().strip('"').strip("'")
    return meta, body.lstrip("\n")


def parse_date(s: str) -> datetime:
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    raise ValueError(f"날짜 형식 오류: {s!r} (예: 2026-11-13)")


def make_markdown() -> markdown.Markdown:
    md = markdown.Markdown(extensions=["extra", "sane_lists"], output_format="html")
    # 글 안의 생 HTML은 실행하지 않고 글자로 보이게 한다(외부 문서에서 들어오므로).
    md.preprocessors.deregister("html_block")
    md.inlinePatterns.deregister("html")
    return md


def plain_excerpt(md_text: str, limit: int = 110) -> str:
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", md_text)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[#>*_`|-]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= limit else t[:limit].rstrip() + "…"


def load_posts(cat_ids: set[str], include_drafts: bool) -> list[Post]:
    dirs = sorted((CONTENT / "posts").glob("*/index.md"))
    if include_drafts:
        dirs += sorted((CONTENT / "drafts").glob("*/index.md"))
    posts, seen, errors = [], set(), []
    md = make_markdown()
    for f in dirs:
        slug = f.parent.name
        try:
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
                raise ValueError("폴더 이름은 영문 소문자·숫자·하이픈만")
            meta, body = parse_front_matter(f.read_text(encoding="utf-8"))
            missing = [k for k in REQUIRED if not meta.get(k)]
            if missing:
                raise ValueError(f"필수 항목 없음: {', '.join(missing)}")
            if meta["category"] not in cat_ids:
                raise ValueError(f"분류 오류: {meta['category']!r}")
            if meta.get("draft", "").lower() == "true" and not include_drafts:
                continue
            if slug in seen:
                raise ValueError("같은 폴더 이름이 두 번 있습니다")
            seen.add(slug)
            cover = meta.get("cover", "")
            if cover and not (f.parent / cover).is_file():
                raise ValueError(f"대표 사진 파일 없음: {cover}")
            md.reset()
            posts.append(Post(
                slug=slug,
                title=meta["title"],
                category=meta["category"],
                date=parse_date(meta["date"]),
                author=meta.get("author", ""),
                tags=[t.strip() for t in re.split(r"[,·]", meta.get("tags", "")) if t.strip()],
                summary=meta.get("summary") or plain_excerpt(body),
                cover=cover,
                meta=meta.get("meta", ""),
                body_html=md.convert(body),
                src_dir=f.parent,
            ))
        except Exception as e:  # 한 글이 잘못돼도 나머지는 빌드
            errors.append(f"  - {f.relative_to(ROOT)}: {e}")
    if errors:
        print("다음 글은 건너뜀:\n" + "\n".join(errors), file=sys.stderr)
    posts.sort(key=lambda p: (p.date, p.slug), reverse=True)
    return posts


def clean_dir(path: Path) -> None:
    """출력 폴더를 비운다. 동기화 프로그램이 빈 폴더를 붙잡아도 파일만 지우고 넘어간다."""
    path.mkdir(parents=True, exist_ok=True)
    for p in sorted(path.rglob("*"), key=lambda x: len(x.parts), reverse=True):
        try:
            p.unlink() if p.is_file() or p.is_symlink() else p.rmdir()
        except OSError:
            pass


def build(include_drafts: bool) -> int:
    site = json.loads((CONTENT / "site.json").read_text(encoding="utf-8"))
    cats = {c["id"]: c for c in site["categories"]}
    posts = load_posts(set(cats), include_drafts)
    by_cat = {cid: [p for p in posts if p.category == cid] for cid in cats}

    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["lines"] = lambda arr: "<br>".join(arr)
    common = dict(site=site, cats=cats, by_cat=by_cat, now=datetime.now())

    clean_dir(OUT)

    def write(rel: str, tpl: str, **ctx):
        path = OUT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(env.get_template(tpl).render(**common, **ctx), encoding="utf-8")

    write("index.html", "home.html", page_title=site["site"]["name"],
          page_desc=site["site"]["description"], canonical="/")

    for cid, cat in cats.items():
        write(f"category/{cid}/index.html", "category.html", cat=cat, items=by_cat[cid],
              page_title=f"{cat['title']} | {site['site']['name']}",
              page_desc=cat["desc"], canonical=f"/category/{cid}/")

    for p in posts:
        related = [q for q in by_cat[p.category] if q.slug != p.slug][:3]
        write(f"posts/{p.slug}/index.html", "post.html", post=p, cat=cats[p.category],
              related=related, page_title=f"{p.title} | {site['site']['name']}",
              page_desc=p.summary, canonical=p.url,
              og_image=p.cover_url or cats[p.category]["image"])
        for extra in p.src_dir.iterdir():  # 글 폴더의 사진 등
            if extra.name != "index.md" and extra.is_file():
                shutil.copy2(extra, OUT / "posts" / p.slug / extra.name)

    # 검색용 목록, sitemap, robots
    (OUT / "search.json").write_text(json.dumps([
        {"t": p.title, "s": p.summary, "g": " ".join(p.tags), "c": cats[p.category]["title"],
         "d": p.date_label, "u": p.url} for p in posts], ensure_ascii=False), encoding="utf-8")
    base = site["site"]["url"].rstrip("/")
    urls = ["/"] + [f"/category/{c}/" for c in cats] + [p.url for p in posts]
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{html.escape(base + u)}</loc></url>\n" for u in urls)
        + "</urlset>\n", encoding="utf-8")
    robots = "User-agent: *\nDisallow: /\n" if site["site"].get("noindex") else \
        f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n"
    (OUT / "robots.txt").write_text(robots, encoding="utf-8")

    shutil.copytree(ROOT / "assets", OUT / "assets", dirs_exist_ok=True)
    for name in STATIC:
        if (ROOT / name).exists():
            shutil.copy2(ROOT / name, OUT / name)

    counts = ", ".join(f"{cats[c]['title']} {len(v)}" for c, v in by_cat.items())
    print(f"빌드 완료: 글 {len(posts)}편 ({counts}) → {OUT}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--drafts", action="store_true", help="draft 글과 content/drafts/ 포함")
    ap.add_argument("--out", help="출력 폴더(기본 _site). 로컬 확인은 OneDrive 밖 폴더 권장")
    args = ap.parse_args()
    if args.out:
        OUT = Path(args.out).resolve()
    sys.exit(build(args.drafts))
