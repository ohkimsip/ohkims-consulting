"""글 대표 이미지 자동 생성(1200×630, 목록 카드·공유·AI 미리보기용).

사진이 없는 글마다 분류별 무늬 + 핵심 주제어(첫 태그) + 분류·작성자를 넣은 오킴스 남색 이미지를 만든다.
제목은 넣지 않는다(카드·글 제목과 겹치지 않게). 한글 글꼴이 없으면 만들지 않고 분류 기본 사진을 쓴다.
"""
from __future__ import annotations

import math
import random
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # 로컬에 Pillow가 없으면 생성하지 않는다
    Image = None

W, H = 1200, 630
NAVY = (11, 45, 55)
BRAND = (23, 75, 88)
ACCENT = (226, 239, 185)
LINE = (255, 255, 255)

FONT_BOLD = ["/usr/share/fonts/truetype/nanum/NanumGothicExtraBold.ttf",
             "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
             "C:/Windows/Fonts/malgunbd.ttf"]
FONT_REG = ["/usr/share/fonts/truetype/nanum/NanumGothic.ttf", "C:/Windows/Fonts/malgun.ttf"]

CAT_EN = {"client-stories": "CLIENT STORIES", "inside-ohkims": "INSIDE OHKIMS",
          "tech-insights": "TECH & IP INSIGHTS", "magazine": "ATTORNEY MAGAZINE"}


def _font(cands: list[str], size: int):
    for c in cands:
        if Path(c).is_file():
            return ImageFont.truetype(c, size)
    return None


def available() -> bool:
    return Image is not None and _font(FONT_BOLD, 10) is not None


def _gradient(img):
    px = img.load()
    for y in range(H):
        for x in range(0, W, 4):
            t = (x / W) * 0.6 + (y / H) * 0.4
            c = tuple(int(NAVY[i] + (BRAND[i] - NAVY[i]) * t) for i in range(3))
            for dx in range(4):
                if x + dx < W:
                    px[x + dx, y] = c


def _pattern(d, cat: str, rnd: random.Random):
    a = 34  # 무늬 투명도
    if cat == "tech-insights":  # 회로 격자
        step = 48
        for x in range(640, W + step, step):
            d.line([(x, 0), (x, H)], fill=LINE + (a // 2,), width=1)
        for y in range(0, H + step, step):
            d.line([(640, y), (W, y)], fill=LINE + (a // 2,), width=1)
        for _ in range(16):
            x = 640 + step * rnd.randint(0, 11)
            y = step * rnd.randint(0, 13)
            L = step * rnd.randint(1, 4)
            d.line([(x, y), (x + L, y)], fill=ACCENT + (90,), width=3)
            d.ellipse([x + L - 5, y - 5, x + L + 5, y + 5], fill=ACCENT + (120,))
    elif cat == "magazine":  # 동심원
        cx, cy = 1010, 250
        for r in range(40, 520, 34):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=LINE + (a,), width=2)
        d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=ACCENT + (160,))
    elif cat == "inside-ohkims":  # 사선
        for x in range(500, W + H, 26):
            d.line([(x, 0), (x - H, H)], fill=LINE + (a,), width=2)
    else:  # 고객 소식: 점 격자
        for x in range(680, W, 30):
            for y in range(30, H, 30):
                r = 2 + (rnd.random() < 0.12) * 3
                d.ellipse([x - r, y - r, x + r, y + r], fill=LINE + (a + 30,))


def _wrap(d, text: str, font, max_w: int, max_lines: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines[:max_lines]


def make_cover(out: Path, *, cat: str, cat_title: str, keyword: str, author: str, date_label: str,
               logo: Path | None, seed: str) -> bool:
    if not available():
        return False
    rnd = random.Random(seed)
    img = Image.new("RGB", (W, H), NAVY)
    _gradient(img)
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    _pattern(ImageDraw.Draw(over), cat, rnd)
    img = Image.alpha_composite(img.convert("RGBA"), over)
    d = ImageDraw.Draw(img)

    f_lab = _font(FONT_BOLD, 22)
    f_key = _font(FONT_BOLD, 76)
    f_sub = _font(FONT_REG, 26)
    x0 = 72
    # 분류 라벨
    d.ellipse([x0, 82, x0 + 10, 92], fill=ACCENT)
    d.text((x0 + 22, 74), f"{CAT_EN.get(cat, '')}  ·  {cat_title}", font=f_lab, fill=(255, 255, 255, 210))
    # 핵심 주제어(크게)
    size = 76
    lines = _wrap(d, keyword, f_key, 620, 2)
    while len(lines) == 2 and d.textlength(lines[-1], font=f_key) > 620 and size > 48:
        size -= 6
        f_key = _font(FONT_BOLD, size)
        lines = _wrap(d, keyword, f_key, 620, 2)
    y = 230 if len(lines) == 1 else 190
    for ln in lines:
        d.text((x0, y), ln, font=f_key, fill=(255, 255, 255))
        y += int(size * 1.25)
    d.rectangle([x0, y + 18, x0 + 64, y + 22], fill=ACCENT)
    # 아래: 작성자·날짜
    d.line([(x0, H - 110), (W - 72, H - 110)], fill=(255, 255, 255, 60), width=1)
    who = f"{author}  ·  특허법인 오킴스" if author else "특허법인 오킴스"
    d.text((x0, H - 86), who, font=f_sub, fill=(255, 255, 255, 230))
    if date_label:
        tw = d.textlength(date_label, font=f_sub)
        d.text((W - 72 - tw, H - 86), date_label, font=f_sub, fill=(255, 255, 255, 170))
    # 오른쪽 위 로고(흰색으로)
    if logo and logo.is_file():
        lg = Image.open(logo).convert("RGBA")
        lg = lg.resize((150, int(150 * lg.height / lg.width)))
        white = Image.new("RGBA", lg.size, (255, 255, 255, 255))
        white.putalpha(lg.split()[3])
        img.alpha_composite(white, (W - 72 - lg.width, 60))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, "PNG", optimize=True)
    return True
