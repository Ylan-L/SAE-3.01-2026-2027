// layout.js : header et footer communs à toutes les pages d'AgriFutur

const LOGO_SVG = `<svg aria-hidden="true" fill="none" height="22" width="22" viewBox="0 0 24 24" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"><path d="M20 4c-8 0-14 4-14 10 0 3 2 5 5 5 6 0 9-7 9-15Z"/><path d="M4 21c2-5 6-9 12-12"/></svg>`;

const MENU = [
  ["index.html", "Accueil"],
  ["explorer.html", "Choisir"],
  ["comparer.html", "Comparer"],
  ["carte.html", "Carte"],
  ["methode.html", "Méthodologie"],
  ["aide.html", "Aide"],
  ["apropos.html", "À propos"],
];

const page = location.pathname.split("/").pop() || "index.html";

const navLinks = MENU.map(([href, label]) =>
  href === page
    ? `<a href="${href}" class="active" aria-current="page">${label}</a>`
    : `<a href="${href}">${label}</a>`
).join("\n      ");

const HEADER = `
  <header class="site-header">
    <input type="checkbox" id="menu-toggle" class="menu-toggle" aria-label="Ouvrir le menu">
    <a class="brand" href="index.html" aria-label="AgriFutur, accueil">
      <span class="brand-mark">${LOGO_SVG}</span>
      <span>AgriFutur</span>
    </a>
    <nav class="nav" aria-label="Navigation principale">
      ${navLinks}
    </nav>
    <div class="header-actions">
      <span class="projection-badge"><span></span> Projections 2050</span>
      <label class="menu-button" for="menu-toggle"><svg aria-hidden="true" fill="none" height="20" width="20" viewBox="0 0 24 24" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8"><path d="M4 7h16"/><path d="M4 12h16"/><path d="M4 17h16"/></svg></label>
    </div>
  </header>`;

const FOOTER = `
  <footer>
    <a class="brand footer-brand" href="index.html"><span class="brand-mark">${LOGO_SVG}</span><span>AgriFutur</span></a>
    <p>Projections climatiques indicatives, pas des prévisions.</p>
    <p>Données météorologiques : <a href="https://open-meteo.com/">Open-Meteo.com</a>, licence <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.</p>
    <div class="scope">
        <a href="mentions.html">Mentions légales</a>
        <a href="rgpd.html">Confidentialité (RGPD)</a>
        <a href="methode.html">Méthodologie et sources</a>
        <a href="aide.html">Aide et glossaire</a>
        <a href="apropos.html">À propos</a>
    </div> 
    <div class="logos"><img src="img/upec-iutcv_info-color.png" alt="UPEC — Université Paris-Est Créteil, IUT de Créteil-Vitry"></div>
  </footer>`;

// On remplace les repères par le vrai header/footer (sans div en plus,
// pour que le CSS existant continue de s'appliquer).
const h = document.getElementById("site-header");
const f = document.getElementById("site-footer");
if (h) h.outerHTML = HEADER;
if (f) f.outerHTML = FOOTER;