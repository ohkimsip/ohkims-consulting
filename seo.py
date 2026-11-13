"""검색·AI 노출용 파일: robots.txt, sitemap.xml, rss.xml, llms.txt, 구조화 데이터 조각."""
from __future__ import annotations

import html
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

# 생성형 AI 검색이 인용할 수 있게 주요 AI 로봇도 명시적으로 허용한다(11.13 사용자 결정: 검색 노출 열기)
AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
           "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "Bingbot", "Yeti",
           "Daumoa"]


def robots_txt(base: str, noindex: bool) -> str:
    if noindex:
        return "User-agent: *\nDisallow: /\n"
    lines = ["User-agent: *", "Allow: /", ""]
    for b in AI_BOTS:
        lines += [f"User-agent: {b}", "Allow: /", ""]
    lines += [f"Sitemap: {base}/sitemap.xml", ""]
    return "\n".join(lines)


def sitemap_xml(base: str, entries: list[tuple[str, str]]) -> str:
    """entries = [(경로, YYYY-MM-DD 또는 '')]"""
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, d in entries:
        out.append(f"  <url><loc>{html.escape(base + u)}</loc>" + (f"<lastmod>{d}</lastmod>" if d else "") + "</url>")
    out.append("</urlset>\n")
    return "\n".join(out)


def rss_xml(base: str, title: str, desc: str, posts, cats: dict, limit: int = 30) -> str:
    def rfc822(dt: datetime) -> str:
        return dt.replace(tzinfo=KST).strftime("%a, %d %b %Y %H:%M:%S +0900")
    items = []
    for p in posts[:limit]:
        items.append(
            "    <item>\n"
            f"      <title>{html.escape(p.title)}</title>\n"
            f"      <link>{html.escape(base + p.url)}</link>\n"
            f"      <guid isPermaLink=\"true\">{html.escape(base + p.url)}</guid>\n"
            f"      <description>{html.escape(p.summary)}</description>\n"
            f"      <category>{html.escape(cats[p.category]['title'])}</category>\n"
            + (f"      <dc:creator>{html.escape(p.author)}</dc:creator>\n" if p.author else "")
            + f"      <pubDate>{rfc822(p.date)}</pubDate>\n"
            "    </item>")
    now = rfc822(datetime.now(KST).replace(tzinfo=None))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">\n  <channel>\n'
            f"    <title>{html.escape(title)}</title>\n    <link>{html.escape(base)}/</link>\n"
            f"    <description>{html.escape(desc)}</description>\n    <language>ko</language>\n"
            f"    <lastBuildDate>{now}</lastBuildDate>\n" + "\n".join(items) + "\n  </channel>\n</rss>\n")


def llms_txt(base: str, site: dict, posts, cats: dict, authors: list, ex: dict | None) -> str:
    """llms.txt — 생성형 AI가 사이트를 빨리 이해하도록 요약과 주요 주소를 적는다."""
    f = site["footer"]
    L = [f"# {site['site']['name']}", "",
         f"> {site['site']['description']}", "",
         f"{f['nameKo']}({f['nameEn']})의 IP·기술사업화 컨설팅 사이트입니다. "
         f"주소: {f['address']}. 전화 02-6952-8689. 메일 ip@ohkimslaw.com. 공식 홈페이지: https://www.ohkimsip.com/", ""]
    if ex:
        L += ["## 컨설팅 분야", ""]
        L += [f"- [{a['title']}]({base}/expertise/{a['slug']}/): {a['lead']}" for a in ex["areas"]]
        L += [f"- [우리 기업에 맞는 컨설팅 찾기]({base}/expertise/)", ""]
    if authors:
        L += ["## 변리사", ""]
        L += [f"- [{a['display']}]({base}/authors/{a['slug']}/): {a['role']}. 전문 분야 {', '.join(a['expertise'][:6])}"
              for a in authors]
        L.append("")
    for cid, c in cats.items():
        items = [p for p in posts if p.category == cid][:20]
        if not items:
            continue
        L += [f"## {c['title']}", "", c["desc"], ""]
        L += [f"- [{p.title}]({base}{p.url}): {p.summary}" + (f" ({p.author})" if p.author else "") for p in items]
        L.append("")
    L += ["## 참고", "", f"- [전체 주소 목록]({base}/sitemap.xml)", f"- [새 글 RSS]({base}/rss.xml)", ""]
    return "\n".join(L)


def org_ld(base: str, site: dict) -> dict:
    f = site["footer"]
    return {"@context": "https://schema.org", "@type": "LegalService", "@id": base + "/#org",
            "name": f["nameKo"], "alternateName": [f["nameEn"], "오킴스", "OhKims IP"],
            "url": base + "/", "logo": base + "/assets/logo.png", "image": base + "/assets/hero.jpg",
            "description": site["site"]["description"], "telephone": "+82-2-6952-8689", "email": "ip@ohkimslaw.com",
            "address": {"@type": "PostalAddress", "streetAddress": "논현로 427-1, 4층", "addressLocality": "강남구",
                        "addressRegion": "서울특별시", "addressCountry": "KR"},
            "areaServed": "KR", "sameAs": ["https://www.ohkimsip.com/"],
            "knowsAbout": ["특허", "상표", "디자인", "기술사업화", "IP-R&D", "특허 분쟁", "해외 출원"]}


def website_ld(base: str, site: dict) -> dict:
    return {"@context": "https://schema.org", "@type": "WebSite", "@id": base + "/#site",
            "name": site["site"]["name"], "url": base + "/", "inLanguage": "ko",
            "publisher": {"@id": base + "/#org"}}


def crumbs_ld(base: str, items: list[tuple[str, str]]) -> dict:
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": base + u} for i, (n, u) in enumerate(items, 1)]}
