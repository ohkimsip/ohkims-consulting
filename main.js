/* content.js의 글을 화면에 채웁니다. 디자인을 바꿀 때만 이 파일을 고칩니다. */
(function () {
  const C = window.SITE_CONTENT;
  const $ = (sel) => document.querySelector(sel);
  const arrow = '<span class="arrow" aria-hidden="true"></span>';
  const lines = (arr) => arr.join("<br>");
  const extAttr = (item) => (item.external ? ' target="_blank" rel="noopener"' : "");

  // 메뉴
  $("#gnb").innerHTML = C.nav
    .map((n) =>
      n.divider
        ? '<span class="gnb-divider" aria-hidden="true"></span>'
        : `<a href="${n.href}"${n.external ? ' class="ext"' : ""}>${n.label}${n.external ? arrow : ""}</a>`
    )
    .join("");

  // 대표 이미지
  const h = C.hero;
  $("#hero").innerHTML = `
    <div class="hero-inner">
      <p class="eyebrow light"><span class="dot"></span>${h.eyebrow}</p>
      <h1>${lines(h.titleLines)}</h1>
      <p class="hero-desc">${lines(h.desc)}</p>
      <a class="link-line light" href="${h.cta.href}">${h.cta.label}${arrow}</a>
      <div class="hero-quote">
        <p>${lines(h.quote)}</p>
        <a class="circle-arrow" href="${h.cta.href}" aria-label="${h.cta.label}">${arrow}</a>
      </div>
      <div class="hero-foot"><span>${h.footLeft}</span><span>${h.footRight}</span></div>
    </div>`;

  // 고객 소식 · 오킴스 활동 · 기술 동향
  const p = C.perspective;
  $("#perspective").innerHTML = `
    <div class="section-head">
      <div>
        <p class="eyebrow">${p.eyebrow}</p>
        <h2>${p.title}</h2>
      </div>
      <p class="section-aside">${lines(p.aside)}</p>
    </div>
    <div class="columns">
      ${p.columns
        .map(
          (col) => `
        <article class="column" id="${col.id}">
          <header class="column-head">
            <span class="no">${col.no}</span>
            <h3>${col.title}</h3>
            <span class="en">${col.en}</span>
            <a class="plus" href="#" aria-label="${col.title} 전체 보기"></a>
          </header>
          <a class="feature" href="${col.feature.href}">
            <figure class="thumb">
              <img src="${col.image}" alt="${col.imageAlt}" loading="lazy">
              <figcaption>${col.imageCaption}</figcaption>
              <span class="circle-arrow small">${arrow}</span>
            </figure>
            <div class="feature-meta"><span class="tag">${col.feature.tag}</span><span>${col.feature.meta}</span></div>
            <h4>${lines(col.feature.titleLines)}</h4>
            <p>${col.feature.desc}</p>
          </a>
          <ul class="post-list">
            ${col.list
              .map(
                (it) => `<li><a href="${it.href}"><span class="tag">${it.tag}</span><span class="title">${it.title}</span>${arrow}</a></li>`
              )
              .join("")}
          </ul>
        </article>`
        )
        .join("")}
    </div>`;

  // 컨설팅 분야
  const e = C.expertise;
  $(".expertise").innerHTML = `
    <div class="expertise-intro">
      <p class="eyebrow">${e.eyebrow}</p>
      <h2>${lines(e.titleLines)}</h2>
      <p class="muted">${lines(e.desc)}</p>
      <a class="link-line" href="${e.cta.href}">${e.cta.label}${arrow}</a>
    </div>
    <ol class="expertise-list">
      ${e.items
        .map(
          (it) => `<li><a href="${it.href}"><span class="no">${it.no}</span><span class="body"><strong>${it.title}</strong><span>${it.desc}</span></span>${arrow}</a></li>`
        )
        .join("")}
    </ol>`;

  // 파트너 · 상담 문의
  const pt = C.partner;
  const ct = C.contact;
  $("#about").innerHTML = `
    <div class="partner-words">
      <p class="eyebrow">${pt.eyebrow}</p>
      <p class="serif-words">${pt.words.map((w, i) => `<span class="w${i + 1}">${w}</span>`).join("")}</p>
    </div>
    <div class="partner-text">
      <h2>${lines(pt.titleLines)}</h2>
      <p class="muted">${lines(pt.desc)}</p>
      <a class="link-line" href="${pt.cta.href}">${pt.cta.label}${arrow}</a>
    </div>
    <div class="contact-box" id="contact">
      <p class="eyebrow light">${ct.eyebrow}</p>
      <h2>${lines(ct.titleLines)}</h2>
      <a class="contact-link" href="${ct.linkHref}">${ct.linkLabel}${arrow}</a>
      <a class="contact-phone" href="${ct.tel}">${ct.phone}</a>
    </div>`;

  // 바닥글
  const f = C.footer;
  $("#footer").innerHTML = `
    <div class="container">
      <div class="footer-top">
        <p class="footer-name"><strong>${f.nameKo}</strong><span>${f.nameEn}</span></p>
        <nav class="footer-links" aria-label="바닥글 링크">
          ${f.links.map((l) => `<a href="${l.href}"${extAttr(l)}>${l.label}${l.external ? arrow : ""}</a>`).join("")}
          <a class="to-top" href="#">Back to top <span aria-hidden="true">↑</span></a>
        </nav>
      </div>
      <div class="footer-bottom">
        <address>${f.address}<br><span>${f.tel}</span><span>${f.email}</span><span>${f.bizNo}</span></address>
        <p class="copy">${f.copyright}<br>All rights reserved.</p>
      </div>
    </div>`;

  // 휴대폰 메뉴
  const btn = $(".menu-btn");
  btn.addEventListener("click", () => {
    const open = document.body.classList.toggle("nav-open");
    btn.setAttribute("aria-expanded", String(open));
    btn.setAttribute("aria-label", open ? "메뉴 닫기" : "메뉴 열기");
  });
  $("#gnb").addEventListener("click", (ev) => {
    if (ev.target.closest("a")) {
      document.body.classList.remove("nav-open");
      btn.setAttribute("aria-expanded", "false");
    }
  });
})();
