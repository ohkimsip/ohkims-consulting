/* 휴대폰 메뉴와 글 검색. 화면 내용은 build.py가 미리 만들어 둔다. */
(function () {
  const $ = (s) => document.querySelector(s);

  // 휴대폰 메뉴
  const menuBtn = $(".menu-btn");
  const setMenu = (open) => {
    document.body.classList.toggle("nav-open", open);
    menuBtn.setAttribute("aria-expanded", String(open));
    menuBtn.setAttribute("aria-label", open ? "메뉴 닫기" : "메뉴 열기");
  };
  menuBtn.addEventListener("click", () => setMenu(!document.body.classList.contains("nav-open")));
  $("#gnb").addEventListener("click", (e) => { if (e.target.closest("a")) setMenu(false); });

  // 글 검색 (search.json)
  const btn = $(".search-btn");
  const panel = $("#search-panel");
  const input = $("#search-input");
  const out = $("#search-results");
  let index = null;
  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  const render = () => {
    const q = input.value.trim().toLowerCase();
    if (!q || !index) { out.innerHTML = ""; return; }
    const words = q.split(/\s+/);
    const hits = index.filter((p) => {
      const hay = (p.t + " " + p.s + " " + p.g + " " + p.c).toLowerCase();
      return words.every((w) => hay.includes(w));
    }).slice(0, 8);
    out.innerHTML = hits.length
      ? hits.map((p) => `<li><a href="${p.u}"><span class="sr-cat">${esc(p.c)} · ${esc(p.d)}</span><span class="sr-title">${esc(p.t)}</span></a></li>`).join("")
      : `<li class="sr-none">「${esc(input.value.trim())}」에 맞는 글이 없습니다.</li>`;
  };

  btn.addEventListener("click", async () => {
    const open = panel.hidden;
    panel.hidden = !open;
    btn.setAttribute("aria-expanded", String(open));
    if (!open) return;
    input.focus();
    if (!index) {
      try { index = await (await fetch("/search.json")).json(); }
      catch { index = []; }
      render();
    }
  });
  input.addEventListener("input", render);
  input.addEventListener("keydown", (e) => { if (e.key === "Escape") { panel.hidden = true; btn.setAttribute("aria-expanded", "false"); btn.focus(); } });
})();

// 오킴스 활동 사진 넘김
document.querySelectorAll("[data-carousel]").forEach((box) => {
  const track = box.querySelector(".act-track");
  const slides = track.children.length;
  const prev = box.querySelector(".prev"), next = box.querySelector(".next");
  const dots = box.querySelectorAll(".act-dots span"), count = box.querySelector(".act-count");
  if (!prev) return;
  const idx = () => Math.round(track.scrollLeft / track.clientWidth);
  const update = () => {
    const i = idx();
    prev.disabled = i <= 0; next.disabled = i >= slides - 1;
    dots.forEach((d, k) => d.classList.toggle("on", k === i));
    if (count) count.textContent = `${i + 1} / ${slides}`;
  };
  prev.addEventListener("click", () => track.scrollBy({ left: -track.clientWidth }));
  next.addEventListener("click", () => track.scrollBy({ left: track.clientWidth }));
  track.addEventListener("scroll", () => requestAnimationFrame(update), { passive: true });
  update();
});
