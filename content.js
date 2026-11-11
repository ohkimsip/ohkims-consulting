/*
 * 홈페이지에 들어가는 글은 모두 이 파일에서 고칩니다.
 * 고친 뒤 index.html을 새로 고침하면 바로 반영됩니다.
 * 글 링크(href)는 아직 상세 페이지가 없어 "#"으로 두었습니다.
 */
window.SITE_CONTENT = {
  nav: [
    { label: "고객 소식", href: "#client-stories" },
    { label: "오킴스 활동", href: "#inside-ohkims" },
    { label: "기술 동향", href: "#tech-insights" },
    { divider: true },
    { label: "컨설팅 분야", href: "#expertise" },
    { label: "About OhKims", href: "#about", external: true }
  ],

  hero: {
    eyebrow: "Insight into your next growth",
    titleLines: ["기술의 가능성을,", "비즈니스의 <em>가치로.</em>"],
    desc: ["깊이 있는 기술 이해와 지식재산 전략으로", "기업의 다음 성장을 함께 설계합니다."],
    cta: { label: "오킴스의 컨설팅을 만나보세요", href: "#expertise" },
    quote: ["From insight", "to <i>impact.</i>"],
    footLeft: "OhKims Patent Law Firm",
    footRight: "Strategy · Intellectual Property · Growth"
  },

  perspective: {
    eyebrow: "The OhKims Perspective",
    title: "<strong>변화를 읽고,</strong> 기회를 만듭니다.",
    aside: ["고객의 성장 이야기부터 산업의 새로운 흐름까지,", "오킴스의 시선으로 전합니다."],
    columns: [
      {
        id: "client-stories",
        no: "01",
        title: "고객 소식",
        en: "Client stories",
        image: "assets/card1.jpg",
        imageAlt: "도심 빌딩 사이의 거리",
        imageCaption: "Technology meets business",
        feature: {
          tag: "이차전지 · 소재",
          meta: "전문가 수행 이력",
          titleLines: ["첨단 소재의 기술력을,", "단단한 IP 경쟁력으로"],
          desc: "이차전지부터 반도체 소재까지. 기술의 본질을 이해하는 전문성이 권리의 차이를 만듭니다.",
          href: "#"
        },
        list: [
          { tag: "모빌리티 · 에너지", title: "연료전지 아이디어의 가능성을 구체적인 권리로", href: "#" },
          { tag: "대학 · 기술사업화", title: "연구실의 기술이 시장을 만나는 접점", href: "#" }
        ]
      },
      {
        id: "inside-ohkims",
        no: "02",
        title: "오킴스 활동",
        en: "Inside OhKims",
        image: "assets/card2.jpg",
        imageAlt: "유리 칸막이가 있는 사무실 복도",
        imageCaption: "Inside our perspective",
        feature: {
          tag: "IP-R&D · 전략",
          meta: "공개 연혁 · 2025",
          titleLines: ["R&D의 방향을 묻고,", "IP에서 해답을 찾습니다"],
          desc: "특허 분석을 넘어 연구개발의 다음 방향으로. 오킴스가 함께해 온 IP-R&D의 여정입니다.",
          href: "#"
        },
        list: [
          { tag: "글로벌 · 브랜드", title: "국경을 넘어 이어지는 브랜드 보호 전략", href: "#" },
          { tag: "기업 성장 · IP 지원", title: "지역의 혁신기업과 함께 쌓아가는 성장의 기반", href: "#" }
        ]
      },
      {
        id: "tech-insights",
        no: "03",
        title: "기술 동향",
        en: "Tech & IP insights",
        image: "assets/card3.jpg",
        imageAlt: "전자 회로 기판 확대 사진",
        imageCaption: "A new view on innovation",
        feature: {
          tag: "AI · 특허 인사이트",
          meta: "WIPO · 2024",
          titleLines: ["생성형 AI의 경쟁 지형,", "특허 데이터로 읽다"],
          desc: "새로운 기술이 산업을 바꿀 때, 특허 데이터는 경쟁의 방향을 이해하는 또 하나의 지도입니다.",
          href: "#"
        },
        list: [
          { tag: "모빌리티 · WIPO", title: "미래 모빌리티, 지속가능성과 디지털화의 교차점", href: "#" },
          { tag: "R&D · 분석 방법", title: "공백기술 분석에서 찾는 다음 R&D의 기회", href: "#" }
        ]
      }
    ]
  },

  expertise: {
    eyebrow: "Our Expertise",
    titleLines: ["기술을 이해하고,", "성장의 길을 제시합니다."],
    desc: ["아이디어의 시작부터 시장으로의 확장까지.", "기업의 단계에 맞는 IP 전략을 함께 만듭니다."],
    cta: { label: "우리 기업에 맞는 컨설팅 찾기", href: "#contact" },
    items: [
      { no: "01", title: "IP 권리화 · 포트폴리오", desc: "선행기술 분석, 국내외 권리 확보, 분쟁 예방", href: "#" },
      { no: "02", title: "R&D 전략 컨설팅", desc: "기술 동향과 공백기술 분석, 회피설계, R&D 기획", href: "#" },
      { no: "03", title: "기술사업화 · 가치평가", desc: "IP 자산화, 기술이전, 투자 연계, SMK", href: "#" },
      { no: "04", title: "기술 브랜딩 · 글로벌 전략", desc: "브랜드 포트폴리오, 제품 디자인, 해외 권리화", href: "#" }
    ]
  },

  partner: {
    eyebrow: "Your partner, OhKims",
    words: ["Value.", "Growth.", "Together."],
    titleLines: ["가치 있는 성장,", "오킴스와 함께."],
    desc: ["전기·전자, 화학·바이오, 기계·모빌리티 등", "다양한 기술 분야의 전문성을 바탕으로", "기업의 아이디어를 지식재산의 가치로 연결합니다."],
    cta: { label: "오킴스 더 알아보기", href: "#about" }
  },

  contact: {
    eyebrow: "Let's talk about your next",
    titleLines: ["다음 성장을 위한", "첫 대화를 시작하세요."],
    linkLabel: "컨설팅 상담 문의",
    linkHref: "mailto:ip@ohkimslaw.com",
    phone: "02. 6952. 8689",
    tel: "tel:0269528689"
  },

  footer: {
    nameKo: "특허법인 오킴스",
    nameEn: "OhKims Patent Law Firm",
    links: [
      { label: "공식 홈페이지", href: "#", external: true },
      { label: "콘텐츠 출처", href: "#" }
    ],
    address: "서울특별시 강남구 논현로 427-1, 4층 (역삼동)",
    tel: "T. 02-6952-8689",
    email: "E. ip@ohkimslaw.com",
    bizNo: "사업자등록번호 720-86-01387",
    copyright: "© 2026 OhKims Patent Law Firm."
  }
};
