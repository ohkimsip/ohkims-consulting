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
