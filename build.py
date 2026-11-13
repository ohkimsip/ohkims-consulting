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
    layout    photo 이면 사진형 글(오킴스 활동): 사진 넘김 + 짧은 글 + 해시태그 (선택)
    event·when·place·host  사진형 글의 행사명·일시·장소·주최 (선택)
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

import covers
import diagrams
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
    faq: list = field(default_factory=list)  # [(질문, 답)] — 「## 자주 묻는 질문」 아래 ### 질문들
    author_info: dict | None = None
    auto_cover: str = ""
    layout: str = ""
    photos: list = field(default_factory=list)  # 사진형 글의 사진 주소(순서대로)
    media_ratio: float = 4 / 3  # 사진형 글 사진 칸 비율(첫 사진 기준, 4:5~16:9로 제한)
    info: list = field(default_factory=list)  # [(항목, 값)] — 행사·일시·장소·주최

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

    @property
    def image_url(self) -> str:
        """목록·공유용 이미지: 직접 넣은 사진 → 자동 대표 이미지 순."""
        return self.cover_url or self.auto_cover


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


def extract_faq(md_text: str) -> list[tuple[str, str]]:
    """본문의 「## 자주 묻는 질문」 절에서 ### 질문과 그 아래 문단을 뽑는다(구조화 데이터용)."""
    m = re.search(r"^##\s*(자주 묻는 질문|FAQ)[^\n]*\n(.*?)(?=^##\s|\Z)", md_text, re.M | re.S)
    if not m:
        return []
    out = []
    for q, a in re.findall(r"^###\s*(.+?)\n(.*?)(?=^###\s|\Z)", m.group(2), re.M | re.S):
        a = plain_excerpt(a, 600)
        if q.strip() and a:
            out.append((q.strip(), a))
    return out


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
            layout = meta.get("layout", "").lower()
            photos = []
            if layout == "photo":
                # 사진형: 본문의 글 폴더 사진을 모두 위쪽 사진 넘김으로 옮기고 본문에서는 뺀다
                names = [n for n in re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", body)
                         if "/" not in n and (f.parent / n).is_file()]
                for n in names:
                    body = re.sub(rf"!\[[^\]]*\]\({re.escape(n)}\)[ \t]*\n?", "", body)
                photos = [f"/posts/{slug}/{n}" for n in dict.fromkeys(([cover] if cover else []) + names)]
                if not cover and names:
                    cover = names[0]
            media_ratio = 4 / 3
            if photos:
                try:
                    from PIL import Image
                    with Image.open(f.parent / photos[0].rsplit("/", 1)[-1]) as im:
                        w, h = im.size
                    media_ratio = min(max(w / h, 0.8), 16 / 9)
                except Exception:
                    pass
            info = [(lab, meta[k]) for k, lab in (("event", "행사"), ("when", "일시"), ("place", "장소"), ("host", "기관"))
                    if meta.get(k)]
            posts.append(Post(
                slug=slug,
                title=meta["title"],
                category=meta["category"],
                date=parse_date(meta["date"]),
                author=meta.get("author", ""),
                tags=list(dict.fromkeys(t.strip() for t in re.split(r"[,·]", meta.get("tags", "")) if t.strip())),
                summary=meta.get("summary") or plain_excerpt(body),
                cover=cover,
                meta=meta.get("meta", ""),
                body_html=diagrams.render(md.convert(body)),
                src_dir=f.parent,
                faq=extract_faq(body),
                layout=layout,
                photos=photos,
                media_ratio=media_ratio,
                info=info,
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

    authors_path = CONTENT / "authors.json"
    authors = json.loads(authors_path.read_text(encoding="utf-8"))["authors"] if authors_path.is_file() else []
    by_name = {}
    for a in authors:
        by_name[a["display"]] = by_name[a["name"]] = a
    for p in posts:
        p.author_info = by_name.get(p.author) or by_name.get(re.sub(r"\s*변리사$", "", p.author or ""))
    by_author = {a["slug"]: [p for p in posts if p.author_info is a] for a in authors}

    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["lines"] = lambda arr: "<br>".join(arr)
    env.filters["tojson_ld"] = lambda obj: json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")
    common = dict(site=site, cats=cats, by_cat=by_cat, authors=authors, by_author=by_author,
                  now=datetime.now())

    clean_dir(OUT)

    # 사진 없는 글의 대표 이미지(분류 무늬 + 핵심 주제어 + 작성자). 글꼴이 없으면 분류 기본 사진.
    for p in posts:
        if p.cover:
            continue
        rel = f"posts/{p.slug}/cover-auto.png"
        ok = covers.make_cover(OUT / rel, cat=p.category, cat_title=cats[p.category]["title"],
                               keyword=next((t for t in p.tags if t.replace(" ", "") != "오킴스활동"),
                                            cats[p.category]["title"]),
                               author=p.author, date_label=p.date_label,
                               logo=ROOT / "assets" / "logo.png", seed=p.slug)
        if ok:
            p.auto_cover = "/" + rel

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

    base_url = site["site"]["url"].rstrip("/")
    org = {"@type": "Organization", "name": "특허법인 오킴스", "alternateName": "OhKims Patent Law Firm",
           "url": "https://www.ohkimsip.com/"}

    def person_ld(a: dict) -> dict:
        return {"@type": "Person", "name": a["display"], "jobTitle": a["role"], "worksFor": org,
                "url": f"{base_url}/authors/{a['slug']}/", "sameAs": [a["profile_url"]],
                "knowsAbout": a["expertise"], "alumniOf": a["education"],
                **({"image": base_url + a["photo"]} if a.get("photo") else {})}

    for p in posts:
        related = [q for q in by_cat[p.category] if q.slug != p.slug][:3]
        ld = [{"@context": "https://schema.org", "@type": "Article", "headline": p.title,
               "description": p.summary, "datePublished": p.iso, "inLanguage": "ko",
               "mainEntityOfPage": base_url + p.url, "publisher": org,
               "image": base_url + (p.image_url or cats[p.category]["image"]),
               "author": person_ld(p.author_info) if p.author_info else org,
               "keywords": p.tags}]
        if p.faq:
            ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p.faq]})
        write(f"posts/{p.slug}/index.html", "post.html", post=p, cat=cats[p.category],
              related=related, page_title=f"{p.title} | {site['site']['name']}",
              page_desc=p.summary, canonical=p.url, json_ld=ld,
              og_image=p.image_url or cats[p.category]["image"])
        for extra in p.src_dir.iterdir():  # 글 폴더의 사진 등
            if extra.name != "index.md" and extra.is_file():
                shutil.copy2(extra, OUT / "posts" / p.slug / extra.name)

    # 변리사 소개
    if authors:
        write("authors/index.html", "authors.html", page_title=f"변리사 소개 | {site['site']['name']}",
              page_desc="특허법인 오킴스 IP·기술사업화 컨설팅 변리사 소개", canonical="/authors/",
              active_nav="/authors/",
              json_ld=[{"@context": "https://schema.org", **person_ld(a)} for a in authors])
        for a in authors:
            write(f"authors/{a['slug']}/index.html", "author.html", author=a, items=by_author[a["slug"]],
                  page_title=f"{a['display']} | {site['site']['name']}",
                  page_desc=f"{a['display']} — {a['tagline']}", canonical=f"/authors/{a['slug']}/",
                  active_nav="/authors/", json_ld=[{"@context": "https://schema.org", "@type": "ProfilePage",
                                                    "mainEntity": person_ld(a)}])

    # 컨설팅 분야(공식 홈페이지 업무분야 + 변리사 공개 이력)
    ex_path = CONTENT / "expertise.json"
    ex_urls = []
    if ex_path.is_file():
        ex = json.loads(ex_path.read_text(encoding="utf-8"))
        by_slug_a = {a["slug"]: a for a in authors}
        for area in ex["areas"]:
            area["team"] = []
            for t in area["attorneys"]:
                a = by_slug_a.get(t["slug"])
                if a:
                    picks = [h for k in t.get("pick", []) for h in a["highlights"] if k in h]
                    area["team"].append({"a": a, "picks": list(dict.fromkeys(picks))[:3]})
            kws = area.get("keywords", [])
            score = lambda p: sum(k in (p.title + " " + " ".join(p.tags) + " " + p.summary) for k in kws)
            area["related"] = sorted([p for p in posts if score(p) >= 2], key=lambda p: (-score(p), -p.date.timestamp()))[:3]
        by_slug = {a["slug"]: a for a in ex["areas"]}
        crumbs = lambda items: {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i, "name": n, "item": base_url + u} for i, (n, u) in enumerate(items, 1)]}
        write("expertise/index.html", "expertise_index.html", ex=ex, by_slug=by_slug,
              page_title=f"컨설팅 분야 | {site['site']['name']}", page_desc=ex["index"]["desc"],
              canonical="/expertise/", active_nav="/expertise/",
              json_ld=[crumbs([("홈", "/"), ("컨설팅 분야", "/expertise/")])])
        ex_urls.append("/expertise/")
        for area in ex["areas"]:
            url = f"/expertise/{area['slug']}/"
            ld = [{"@context": "https://schema.org", "@type": "Service", "name": area["title"],
                   "alternateName": area["en"], "description": area["lead"], "provider": org,
                   "serviceType": [s["t"] for s in area["services"]], "areaServed": "KR", "url": base_url + url,
                   "employee": [person_ld(t["a"]) for t in area["team"]]},
                  {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                      {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}}
                      for q, ans in area["faq"]]},
                  crumbs([("홈", "/"), ("컨설팅 분야", "/expertise/"), (area["title"], url)])]
            write(f"expertise/{area['slug']}/index.html", "expertise.html", area=area, areas=ex["areas"],
                  page_title=f"{area['title']} | {site['site']['name']}", page_desc=area["lead"],
                  canonical=url, active_nav="/expertise/", json_ld=ld)
            ex_urls.append(url)

    # 검색용 목록, sitemap, robots
    (OUT / "search.json").write_text(json.dumps([
        {"t": p.title, "s": p.summary, "g": " ".join(p.tags), "c": cats[p.category]["title"],
         "d": p.date_label, "u": p.url} for p in posts], ensure_ascii=False), encoding="utf-8")
    base = site["site"]["url"].rstrip("/")
    urls = ["/"] + [f"/category/{c}/" for c in cats] + [p.url for p in posts]
    if authors:
        urls += ["/authors/"] + [f"/authors/{a['slug']}/" for a in authors]
    urls += ex_urls
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
