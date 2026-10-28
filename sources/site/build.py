#!/usr/bin/env python3
"""Génère le site statique du recueil à partir des fiches Markdown.

Usage : python3 /mnt/project-files/site/build.py
Sortie : /mnt/project-files/site/public/ (à déposer tel quel chez l'hébergeur).
"""
import hashlib
import html
import json
import re
import shutil
from pathlib import Path

import markdown

import nutrition as N
from urllib.parse import quote, unquote

ROOT = Path("/mnt/project-files")
SRC = ROOT / "recettes"
PLANS = ROOT / "plans"
SITE = ROOT / "site"
OUT = SITE / "public"
# Visuels du recueil : photos Wikimedia Commons choisies par leur nom de fichier (plat identique ou proche).
# Version affichée en bas des pages, pour savoir quelle mise à jour l'appareil a chargée
import datetime as _dt
VERSION = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=2))).strftime("%d/%m %H:%M")
_VIS = json.loads((SITE / "visuels.json").read_text(encoding="utf-8")) if (SITE / "visuels.json").exists() else {}


PHOTOS = False   # photos retirées du recueil à la demande d'Antho (17/10) ; visuels.json reste prêt si on les remet


def visual(slug):
    v = _VIS.get(slug) if PHOTOS else None
    if not v:
        return None, None
    f = quote(unquote(v["file"]), safe="_-.,()")
    return (f"https://commons.wikimedia.org/wiki/Special:FilePath/{f}?width=600",
            f"https://commons.wikimedia.org/wiki/File:{f}")

SECTIONS = [
    ("plats", "Plats"),
    ("mijotes", "Mijotés"),
    ("petit-dejeuner", "Petits-déjeuners"),
    ("autres", "Collations et repères"),
    ("plans", "Plans de semaine"),
]

CSS = """
/* Épuré : fond blanc, encre presque noire, un seul vert profond, filets fins, titres en serif. */
:root{--bg:#f7f3ec;--ink:#1c1d1d;--muted:#6b675f;--line:#e2dccf;--soft:#efe9dd;--accent:#5f7d63;--accent-soft:#e9efe6;
--font-display:"DM Sans",system-ui,-apple-system,"Segoe UI",sans-serif;--font-body:"DM Sans",system-ui,-apple-system,"Segoe UI",sans-serif;color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--font-body);font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:inherit}
.site{border-bottom:1px solid var(--line)}
.site .in{max-width:1180px;margin:0 auto;padding:18px 16px;display:flex;justify-content:space-between;align-items:baseline;gap:16px}
.brand{font-family:var(--font-display);font-size:1.35rem;font-weight:700;text-decoration:none;letter-spacing:-.02em}
.nav{display:flex;gap:22px}
.nav a{font-size:.72rem;text-transform:uppercase;letter-spacing:.14em;text-decoration:none;color:var(--muted);padding-bottom:3px;border-bottom:1px solid transparent}
.nav a:hover,.nav a.on{color:var(--ink);border-bottom-color:var(--ink)}
.wrap{max-width:1180px;margin:0 auto;padding:0 16px 80px}
h1,h2,h3{font-family:var(--font-display);font-weight:700;line-height:1.15;margin:0;letter-spacing:-.02em}
.hero{text-align:center;padding:56px 0 36px;display:grid;gap:12px;justify-items:center}
.hero h1{font-size:clamp(2.2rem,7vw,3.6rem);text-wrap:balance}
.hero p{margin:0;color:var(--muted);max-width:34em}
.label{font-size:.7rem;text-transform:uppercase;letter-spacing:.16em;color:var(--muted)}
.search{max-width:520px;margin:0 auto 28px}
input[type=search]{font:inherit;width:100%;padding:12px 2px;border:0;border-bottom:1px solid var(--ink);background:transparent;color:var(--ink);border-radius:0;-webkit-appearance:none;appearance:none}
input[type=search]::placeholder{color:var(--muted)}
input[type=search]:focus{outline:none;border-bottom-width:2px}
.filters{display:flex;justify-content:center;flex-wrap:wrap;gap:8px;margin-bottom:48px}
.filters button{font:inherit;font-size:.72rem;text-transform:uppercase;letter-spacing:.12em;padding:7px 14px;border:1px solid var(--line);border-radius:999px;background:transparent;color:var(--muted);cursor:pointer}
.filters button[aria-pressed="true"]{color:var(--ink);background:var(--accent-soft);border-color:var(--accent-soft)}
.sec{margin-bottom:56px}
.sec-head{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid var(--ink);padding-bottom:10px;margin-bottom:0}
.sec-head h2{font-size:1.6rem}
.sec-head span{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.list{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));column-gap:40px}
.card{display:grid;gap:6px;padding:22px 0;border-bottom:1px solid var(--line);text-decoration:none;color:var(--ink)}
.card .label{color:var(--accent)}
.card b{font-family:var(--font-display);font-weight:700;font-size:1.2rem;line-height:1.25;letter-spacing:-.01em}
.card span.t{font-size:.85rem;color:var(--muted)}
.card:hover b{text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:4px}
.empty{color:var(--muted);text-align:center}
.card .stars{font-size:.85rem;color:var(--accent);letter-spacing:.08em}
.tools{display:flex;flex-wrap:wrap;justify-content:center;gap:14px 26px;margin:-28px 0 44px;align-items:flex-start}
.tools>label,.sans summary{display:flex;align-items:baseline;gap:10px}
.tools select{font:inherit;font-size:.92rem;color:var(--ink);background:#fbf8f3;border:1px solid var(--line);padding:7px 10px;border-radius:10px;max-width:62vw}
.sans{flex-basis:100%;text-align:center}
.sans summary{justify-content:center;cursor:pointer;list-style:none;font-size:.92rem}
.sans summary::-webkit-details-marker{display:none}
.sans summary b{font-weight:400;border:1px solid var(--line);border-radius:10px;background:#fbf8f3;padding:7px 10px}
#sans{display:flex;flex-wrap:wrap;justify-content:center;gap:8px 18px;padding:14px 0 0;font-size:.9rem}
#sans label{display:flex;gap:6px;align-items:center;cursor:pointer}
#sans input{accent-color:var(--accent);width:16px;height:16px}
.item{position:relative;min-width:0}
.like{position:absolute;top:16px;right:-6px;border:0;background:none;padding:6px;cursor:pointer;color:var(--muted);line-height:0}
.like svg{width:24px;height:24px}.like.on{color:#c0533f}.like.on path{fill:currentColor}
.item .card b{padding-right:30px}
.rate .like-big{display:inline-flex;align-items:center;gap:8px;border:1px solid var(--line);background:none;border-radius:999px;padding:8px 16px;font:inherit;font-size:.85rem;color:var(--ink);cursor:pointer;margin-bottom:10px}
.rate .like-big svg{width:18px;height:18px;color:var(--muted)}.rate .like-big.on svg{color:#c0533f}.rate .like-big.on path{fill:currentColor}
.card .ph{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:12px;background:var(--accent-soft);display:block;margin-bottom:6px}
.item .cr{position:absolute;top:30px;right:8px;font-size:.62rem;color:#fff;background:rgba(0,0,0,.45);padding:2px 8px;border-radius:999px;text-decoration:none}
@media (max-width:1023px){.card.has-ph{grid-template-columns:96px 1fr;column-gap:14px;align-content:start}
.card.has-ph>*{grid-column:2}.card.has-ph .ph{grid-column:1;grid-row:1/span 6;aspect-ratio:1;margin:0;align-self:start}
.item .cr{top:calc(22px + 96px - 17px);left:0;right:auto;width:96px;text-align:center;box-sizing:border-box;padding:2px 0;border-radius:0 0 12px 12px}}
.card .sai.now{color:var(--accent)}
.card .e{font-size:1rem;letter-spacing:.2em}
.pics{display:flex;flex-wrap:wrap;justify-content:center;gap:8px}
.pic{display:inline-flex;gap:6px;align-items:center;font-size:.72rem;text-transform:uppercase;letter-spacing:.12em;border:1px solid var(--line);border-radius:999px;padding:5px 12px}
.pic i{font-style:normal;font-size:1rem}
.alg{margin:0;font-size:.85rem;color:var(--muted)}
.nut{background:#fbf8f3;border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:0 0 32px;display:grid;gap:12px;text-align:center}
.nut-v{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:6px}
.nut-v div{display:grid;gap:2px}
.nut-v b{font-family:var(--font-display);font-weight:700;font-size:1.1rem}
.nut-v span{font-size:.72rem;color:var(--muted)}
.nut details{text-align:left;font-size:.85rem;color:var(--muted)}
.nut summary{cursor:pointer;text-align:center;font-size:.72rem;text-transform:uppercase;letter-spacing:.14em}
.nut table{width:100%;border-collapse:collapse;margin:12px 0;font-size:.85rem}
.nut td,.nut th{padding:6px 6px 6px 0;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
.nut th{font-weight:400;font-size:.68rem;text-transform:uppercase;letter-spacing:.12em}
.nut p{margin:6px 0}
.nut a{color:var(--accent)}
.nav a,.snav a{white-space:nowrap}.nav a.acc,.snav a.acc{padding-left:14px;margin-left:-6px;border-left:1px solid var(--line)}
@media (max-width:480px){.site .in{gap:8px;padding-inline:12px}.brand{font-size:1.05rem}.nav,.snav{gap:8px!important}.nav a,.snav a{font-size:.62rem!important;letter-spacing:.02em!important}.nav a.acc,.snav a.acc{padding-left:7px;margin-left:-1px}}
@media (max-width:420px){.nut-v b{font-size:.95rem}.nav{gap:12px}.nav a{letter-spacing:.08em}}
.rate{display:grid;justify-items:center;gap:4px;margin:-12px 0 32px}
.rate div{display:flex;gap:2px}
.rate button{font-size:1.9rem;line-height:1;border:0;background:none;color:var(--line);cursor:pointer;padding:4px}
.rate button.on{color:var(--accent)}
.rate small{text-align:center;font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.recipe,.ali{max-width:720px;margin:0 auto}
#t .sort{all:unset;cursor:pointer;font:inherit;letter-spacing:inherit;text-transform:inherit;color:inherit;padding:6px 0;white-space:nowrap}
#t .sort.on{color:var(--accent);font-weight:600}
#t .sort::after{content:attr(data-dir);margin-left:3px;font-size:.8em}
#t .sort:focus-visible{outline:2px solid var(--accent);border-radius:4px}
/* Ordinateur : fiche en deux colonnes, l'essentiel (titre, temps, notes, valeurs) reste visible à gauche */
@media (min-width:1024px){
.recipe{max-width:none;display:grid;grid-template-columns:minmax(0,380px) minmax(0,1fr);gap:64px;align-items:start}
.r-side{position:sticky;top:24px;max-height:calc(100vh - 48px);overflow-y:auto}
.r-head{text-align:left;justify-items:start;padding:28px 0 22px}
.r-head h1{font-size:2.3rem}
.facts{justify-content:flex-start;margin-bottom:24px}
.facts div{padding:12px 16px 12px 0;text-align:left}
.facts div+div{padding-left:16px}
.rate{justify-items:start;margin:0 0 24px}
.nut-v b{font-size:1rem}
.recipe>article{padding-top:64px}
.list{grid-template-columns:repeat(3,minmax(0,1fr))}
.tools{margin-top:-20px}
}
.back{display:inline-block;margin:28px 0 0;font-size:.72rem;text-transform:uppercase;letter-spacing:.14em;color:var(--muted);text-decoration:none}
.r-head{text-align:center;padding:36px 0 28px;display:grid;gap:14px;justify-items:center}
.r-head h1{font-size:clamp(2rem,6vw,3rem);text-wrap:balance}
.facts{display:flex;justify-content:center;flex-wrap:wrap;border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin-bottom:36px}
.facts div{padding:14px 22px;display:grid;gap:2px;text-align:center}
.facts div+div{border-left:1px solid var(--line)}
.facts b{font-family:var(--font-display);font-weight:700;font-size:1.05rem}
article{display:grid;gap:14px;min-width:0}
article>*{margin:0}
article h2{font-size:1.5rem;margin-top:28px;padding-bottom:10px;border-bottom:1px solid var(--ink)}
article h3{font-size:1.15rem;margin-top:12px}
article ul,article ol{padding-left:1.2em;display:grid;gap:8px}
article ol{counter-reset:s;list-style:none;padding-left:0}
article ol>li{counter-increment:s;padding-left:2.4em;position:relative}
article ol>li::before{content:counter(s);position:absolute;left:0;top:0;font-family:var(--font-display);font-weight:700;font-size:1.1rem;color:var(--accent)}
article li::marker{color:var(--muted)}
.tw{overflow-x:auto}
article table{width:100%;border-collapse:collapse;font-size:.92rem}
article th,article td{padding:10px 8px 10px 0;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
article th{font-weight:400;font-size:.68rem;text-transform:uppercase;letter-spacing:.14em;color:var(--muted);border-bottom-color:var(--ink)}
article strong{font-weight:600}
article a{color:var(--accent)}
article code{font-size:.85em;overflow-wrap:anywhere}
article pre{overflow-x:auto;background:var(--soft);padding:12px}
article blockquote{margin:0;padding:4px 0 4px 18px;border-left:1px solid var(--ink);font-family:var(--font-display);font-style:italic}
.intro{font-size:.88rem;color:var(--muted);background:var(--soft);padding:14px 20px;border-radius:12px}
.intro summary{cursor:pointer;font-size:.72rem;text-transform:uppercase;letter-spacing:.14em}
.intro[open] summary{margin-bottom:12px}
.intro ul{gap:6px}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
footer{border-top:1px solid var(--line);text-align:center;padding:28px 16px;font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
@media (max-width:560px){.facts div{padding:12px 14px}.hero{padding:40px 0 28px}.nav{gap:16px}}
@media print{.site,.back,footer{display:none}}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,600;9..40,700&display=swap">')


def app_head(up=""):
    """Balises pour installer le site comme une app (écran d'accueil iPhone / Android)."""
    return (f'<link rel="manifest" href="{up}manifest.webmanifest"><link rel="apple-touch-icon" href="{up}icon-180.png">'
            '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">'
            '<meta name="apple-mobile-web-app-title" content="Miam!"><meta name="apple-mobile-web-app-status-bar-style" content="default">'
            f'<script>if ("serviceWorker" in navigator && /github\\.io$|^localhost$/.test(location.hostname)) navigator.serviceWorker.register("{up}sw.js", {{updateViaCache: "none"}}).catch(() => {{}});</script>')


def app_files():
    """Manifeste, icônes et service worker (cache hors ligne) de l'app."""
    (OUT / "manifest.webmanifest").write_text(json.dumps({
        "name": "Miam!", "short_name": "Miam!", "lang": "fr", "start_url": "semaine.html", "scope": "./",
        "display": "standalone", "background_color": "#f7f3ec", "theme_color": "#f7f3ec",
        "icons": [{"src": f"icon-{n}.png", "sizes": f"{n}x{n}", "type": "image/png", "purpose": "any"} for n in (192, 512)]
                 + [{"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]},
        ensure_ascii=False), encoding="utf-8")
    for n in (180, 192, 512):
        shutil.copy(SITE / "icones" / f"icon-{n}.png", OUT / f"icon-{n}.png")
    files = sorted(str(f.relative_to(OUT)) for f in OUT.rglob("*") if f.is_file() and f.name not in ("sw.js", "robots.txt"))
    version = hashlib.sha1("".join(f + str((OUT / f).stat().st_size) for f in files).encode()).hexdigest()[:10]
    (OUT / "sw.js").write_text(SW.replace("__V__", version).replace("__FILES__", json.dumps(files)), encoding="utf-8")


SW = r"""// Cache hors ligne : les pages sont relues sur le réseau quand il y en a, sinon servies depuis le cache.
const V = "recettes-__V__", FILES = __FILES__;
self.addEventListener("install", e => { e.waitUntil(caches.open(V).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== "GET") return;
  const local = u.origin === location.origin, font = /fonts\.(googleapis|gstatic)\.com$/.test(u.hostname);
  if (!local && !font) return;
  if (r.mode === "navigate" || u.pathname.endsWith(".html")) {
    e.respondWith(fetch(r, {cache: "no-cache"}).then(res => {   // toujours vérifier auprès du serveur : une mise à jour se voit au prochain chargement const c = res.clone(); caches.open(V).then(x => x.put(r, c)); return res; })
      .catch(() => caches.match(r, {ignoreSearch: true}).then(m => m || caches.match("index.html"))));
    return;
  }
  e.respondWith(caches.match(r).then(m => m || fetch(r).then(res => { const c = res.clone(); caches.open(V).then(x => x.put(r, c)); return res; })));
});
"""


CSS_V = hashlib.md5(CSS.encode()).hexdigest()[:8]


def page(title, body, depth=0, active=""):
    up = "../" * depth
    on = lambda k: ' class="on"' if active == k else ""
    head = (f'<header class="site"><div class="in"><a class="brand" href="{up}index.html">Miam!</a>'
            f'<nav class="nav"><a href="{up}semaine.html">Ma semaine</a>'
            f'<a href="{up}index.html"{on("recueil")}>Recueil</a><a href="{up}guide.html"{on("guide")}>Guide</a><a href="{up}compte.html" class="acc{' on' if active == 'compte' else ''}">Profil</a></nav></div></header>')
    return (f'<!doctype html><html lang="fr"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#f7f3ec"><meta name="color-scheme" content="light">'
            f'<title>{html.escape(title)}</title>{FONTS}<link rel="stylesheet" href="{up}style.css?v={CSS_V}">{app_head(up)}</head>'
            f'<body>{head}<main class="wrap">{body}</main><footer>2 personnes · batch cooking du dimanche · version du {VERSION}</footer></body></html>')


# Note de 1 à 5 étoiles, gardée dans le navigateur (clé « recettes-notes », lue aussi par Ma semaine)
HEART = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20.5s-7.5-4.6-9.2-9.4C1.6 7.6 3.9 4.5 7.2 4.5c2 0 3.6 1.1 4.8 2.8 1.2-1.7 2.8-2.8 4.8-2.8 3.3 0 5.6 3.1 4.4 6.6-1.7 4.8-9.2 9.4-9.2 9.4z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>'
# Plats favoris (cœur), gardés dans le navigateur (clé « recettes-likes », liste de slugs, lue par le recueil et Ma semaine)
RATE = """<div class="rate"><button type="button" class="like-big" id="like">""" + HEART + """<span>Ajouter à mes favoris</span></button><div id="stars"></div><small id="rate-t">Noter cette recette</small></div>
<script>
(() => {
  const slug = "__SLUG__", box = document.getElementById("stars"), t = document.getElementById("rate-t");
  const get = () => { try { return JSON.parse(localStorage.getItem("recettes-notes")) || {}; } catch (e) { return {}; } };
  function draw() {
    const n = get()[slug] || 0; box.innerHTML = "";
    for (let i = 1; i <= 5; i++) {
      const b = document.createElement("button"); b.type = "button"; b.textContent = "★";
      b.className = i <= n ? "on" : ""; b.setAttribute("aria-label", i + " étoile" + (i > 1 ? "s" : ""));
      b.onclick = () => { const all = get(); if (all[slug] === i) delete all[slug]; else all[slug] = i;
        try { localStorage.setItem("recettes-notes", JSON.stringify(all)); } catch (e) {} draw(); };
      box.append(b);
    }
    t.textContent = n ? "Ta note : " + n + "/5 · touche à nouveau pour l'effacer" : "Noter cette recette";
  }
  draw();
  const lb = document.getElementById("like");
  const likes = () => { try { return JSON.parse(localStorage.getItem("recettes-likes")) || []; } catch (e) { return []; } };
  const drawLike = () => { const on = likes().includes(slug); lb.classList.toggle("on", on); lb.setAttribute("aria-pressed", on);
    lb.querySelector("span").textContent = on ? "Dans mes favoris" : "Ajouter à mes favoris"; };
  lb.onclick = () => { const l = likes().filter(x => x !== slug); if (!likes().includes(slug)) l.push(slug);
    try { localStorage.setItem("recettes-likes", JSON.stringify(l)); localStorage.setItem("recettes-likes-u", Date.now()); } catch (e) {} drawLike(); };
  drawLike();
})();
</script>"""


def short_time(text):
    m = re.search(r"^- \*\*Temps\*\* ?: ?(.+)$", text, re.M)
    if not m:
        return ""
    t = re.search(r"((?:moins de |environ )?\d+(?:[,.]\d+)? ?(?:h(?: ?\d+)?|min))", m.group(1))
    return t.group(1) if t else ""


def short_portions(text):
    m = re.search(r"^- \*\*Portions\*\* ?: ?(.+)$", text, re.M)
    if not m:
        return ""
    return re.split(r"[,(;]", re.sub(r"\*\*|\*", "", m.group(1)))[0].strip()[:30]


def slugify(p):
    return p.stem


def meta(text, key):
    m = re.search(rf"^- \*\*{key}\*\* ?: ?(.+)$", text, re.M)
    if not m:
        return ""
    v = re.sub(r"\*\*|\*|`", "", m.group(1))
    v = re.sub(r"\s*\(.*?\)", "", v).strip()
    return v[:90]


DIFF = {1: "Très facile", 2: "Facile", 3: "Plus élaboré"}


def minutes(t):
    """« 1 h 15 », « 45 min » → minutes (None si absent)."""
    if not t:
        return None
    h = re.search(r"(\d+(?:[,.]\d+)?) ?h(?: ?(\d+))?", t)
    if h:
        return round(float(h.group(1).replace(",", ".")) * 60) + int(h.group(2) or 0)
    m = re.search(r"(\d+) ?min", t)
    return int(m.group(1)) if m else None


def kcal(text):
    m = re.search(r"^- \*\*Calories\*\* ?: ?(.+)$", text, re.M)
    n = m and re.search(r"(\d{2,4}) ?kcal", m.group(1))
    return int(n.group(1)) if n else None


def ingredients(text):
    """Noms d'ingrédients : première colonne des tableaux de la section Ingrédients."""
    m = re.search(r"## Ingrédients.*?\n(.*?)(?:\n## |\Z)", text, re.S)
    if not m:
        return ""
    names = [l.split("|")[1] for l in m.group(1).splitlines()
             if l.startswith("|") and not re.match(r"\|\s*-", l) and l.count("|") > 2]
    names = [n for n in names if n.strip().lower() not in ("ingrédient", "ingrédients", "aliment")]
    s = " ".join(names).lower().replace("œ", "oe")
    s = re.sub(r"\(ou [^)]*\)", "", s)   # les variantes « (ou jambon) » ne comptent pas
    s = s.replace("steak végétal", "galette végétale")
    # Faux amis : le coco et la muscade ne sont ni du lait ni des fruits à coque.
    s = re.sub(r"(lait|crème|creme|noix|beurre) de (coco|muscade|cacahuète)", r"\2", s)
    s = re.sub(r"lait (d'amande|d'avoine|de soja|végétal)", r"boisson \1", s)
    return s


def recipe_data(text):
    """Fiche → {t, ing, steps, keep} : les recettes de Ma semaine sont tirées des fiches à chaque fabrication."""
    m = re.search(r"^- \*\*Temps\*\* ?: ?(.+)$", text, re.M)
    sec = lambda rx: (re.search(rx + r".*?\n(.*?)(?=\n## |\Z)", text, re.S | re.M) or [None, ""])[1]
    ing = []
    for l in sec(r"^## Ingrédients").splitlines():
        if not l.startswith("|") or re.match(r"\|\s*:?-", l):
            continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) >= 2 and c[0].lower() not in ("ingrédient", "ingrédients", "aliment"):
            ing.append([c[0].replace("*", ""), c[1].replace("*", "")])
    steps = [l.strip().replace("**", "") for l in sec(r"^## Étapes").splitlines() if l.strip()]
    keep, cur = [], None
    for l in text.splitlines():
        k = re.match(r"^- \*\*(Conservation|Réchauffage)\*\* ?: ?(.*)$", l)
        if k:
            cur = [k.group(1), k.group(2).replace("**", "").strip()]
            keep.append(cur)
        elif cur and re.match(r"^\s+- ", l):   # sous-points : « Réfrigérateur : … », « Congélateur : … »
            cur[1] = (cur[1] + " " + l.strip()[2:].replace("**", "").strip()).strip()
        elif not l.startswith(" "):
            cur = None
    return {"t": m.group(1).strip() if m else "", "ing": ing, "steps": steps,
            "keep": [(a + " : " + b).strip() for a, b in keep]}


def difficulty(text):
    """Estimation : nombre d'étapes et d'ingrédients."""
    st = re.search(r"## Étapes.*?\n(.*?)(?:\n## |\Z)", text, re.S)
    steps = len(re.findall(r"^\d+\.", st.group(1), re.M)) if st else 0
    rows = 0
    m = re.search(r"## Ingrédients.*?\n(.*?)(?:\n## |\Z)", text, re.S)
    if m:
        rows = sum(1 for l in m.group(1).splitlines() if l.startswith("|") and not re.match(r"\|\s*-", l)) - 1
    score = steps + rows / 2
    if not steps and not rows:
        return None
    return 1 if score <= 8 else 2 if score <= 14 else 3


ALLERGENS = {
    "gluten": r"pâtes|spaghetti|tagliatelle|lasagne|farine|pain|semoule|boulgour|\bblé|chapelure|couscous|tortilla|wrap|galette de blé|orge|seigle|épeautre|sauce soja|nouille|panko|biscotte|flocons d'avoine|avoine",
    "lait": r"\blait\b(?! de coco| d'amande| d'avoine| de soja)|crème(?! de coco)|creme(?! de coco)|beurre(?! de cacahu)|fromage|comté|parmesan|feta|féta|mozzarella|yaourt|skyr|ricotta|chèvre|emmental|gruyère|mascarpone|cottage|béchamel|pecorino|burrata|cheddar|reblochon|raclette|cream cheese|kiri|boursin|st moret|saint-moret",
    "œuf": r"\boeuf|\boeufs",
    "fruits à coque": r"amande|\bnoix\b|noisette|cajou|pistache|pécan|macadamia",
    "arachide": r"cacahuète|arachide|beurre de cacahuète",
    "poisson": r"saumon|cabillaud|thon|poisson|colin|merlu|sardine|maquereau|\blieu|truite|dorade|anchois",
    "crustacés": r"crevette|gambas|crabe|homard|langoustine",
    "soja": r"tofu|tamari|soja|edamame|miso|tempeh",
    "moutarde": r"moutarde",
    "sésame": r"sésame|tahin",
}
PROTEINS = [
    ("volaille", r"poulet|dinde|volaille|canard"),
    ("bœuf", r"\bboeuf|veau|steak"),
    ("porc", r"porc|jambon(?! de dinde)|lardon|chorizo|bacon|saucisse"),
    ("agneau", r"agneau"),
    ("poisson", ALLERGENS["poisson"]),
    ("crevettes", ALLERGENS["crustacés"]),
]
SPICY = r"piment|harissa|cayenne|chili|sriracha|gochujang|tabasco|jalapeño|sambal|curry rouge|pâte de curry"
MEAT = {"volaille", "bœuf", "porc", "agneau"}


def tags(text):
    s = ingredients(text)
    if not s:
        return [], [], False
    prot = [k for k, rx in PROTEINS if re.search(rx, s)]
    if not prot:
        prot = ["végétarien"]
    alg = [k for k, rx in ALLERGENS.items() if re.search(rx, s)]
    return prot, alg, bool(re.search(SPICY, s))


def pictos(prot, hot):
    out = []
    if MEAT & set(prot):
        out.append(("🥩", "Viande"))
    if "poisson" in prot or "crevettes" in prot:
        out.append(("🐟", "Poisson ou fruits de mer"))
    if prot == ["végétarien"]:
        out.append(("🌱", "Végétarien"))
    if hot:
        out.append(("🌶️", "Pimenté"))
    return out


def nutrition_html(nut, cal_fiche):
    """Encadré « Par portion » + détail du calcul, à partir de la base aliments.csv."""
    p = nut["par_portion"]
    vals = "".join(f'<div><b>{round(p[k])}{u}</b><span>{lbl}</span></div>' for k, lbl, u in
                   (("kcal", "kcal", ""), ("proteines", "protéines", " g"), ("glucides", "glucides", " g"),
                    ("lipides", "lipides", " g"), ("fibres", "fibres", " g")))
    rows = "".join(f'<tr><td>{html.escape(n)}</td><td>{html.escape(a)}</td><td>{g:.0f} g</td><td>{k:.0f}</td></tr>'
                   for n, a, g, k in nut["lignes"])
    notes = [f"Calcul fait sur la recette entière puis divisé par {nut['portions']} portions."]
    skip = [n for n in nut["ignores"] if (a := N.find(n)) is None
            or (a["kcal"] >= 50 and not a["aliment"].startswith(("Épices", "Herbes")))]
    if skip:
        notes.append("Non compté (quantité non chiffrée ou aliment absent de la base) : " + ", ".join(skip) + ".")
    if cal_fiche:
        notes.append(f"La fiche d'origine annonçait {cal_fiche} kcal par personne.")
    return (f'<section class="nut"><span class="label">Par portion</span><div class="nut-v">{vals}</div>'
            f'<details><summary>Détail du calcul</summary><div class="tw"><table><thead><tr><th>Ingrédient</th><th>Aliment de la base</th>'
            f'<th>Recette</th><th>kcal</th></tr></thead><tbody>{rows}</tbody></table></div>'
            + "".join(f"<p>{html.escape(x)}</p>" for x in notes) + '<p><a href="../guide.html#aliments">Voir la base des aliments</a></p></details></section>')


# Page Compte : la clé GitHub de l'appareil qui sert à synchroniser Ma semaine (même clé localStorage que semaine.html)
COMPTE = SITE / "compte-source.html"
GUIDE = SITE / "guide-source.html"   # page « Comment ça marche » : règles du livret LaSèche, en version interactive


def magasins():
    """Magasins dont les prix ont été relevés (drive en ligne ou ticket de caisse) : prix/magasins.tsv, un fichier de prix par magasin."""
    out = []
    for ln in (SITE / "prix" / "magasins.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        c = ln.split("\t")
        if len(c) < 7 or not c[0].strip():
            continue
        prix = {}
        for row in (SITE / "prix" / c[5].strip()).read_text(encoding="utf-8").splitlines()[1:]:
            r = row.split("\t")
            if len(r) >= 6 and r[0].strip():
                prix[r[0].strip()] = {"p": r[1], "ean": r[2], "q": float(r[3]), "u": r[4], "e": float(r[5]), "n": r[6] if len(r) > 6 else ""}
        out.append({"id": c[0].strip(), "e": c[1].strip(), "n": c[2].strip(), "a": c[3].strip(), "src": c[4].strip(), "date": c[6].strip(), "prix": prix})
    return out


def aliments_section():
    """Base des aliments, section 8 du Guide (ancienne page Aliments)."""
    rows = "".join(f'<tr><td>{html.escape(a["aliment"])}</td>' + "".join(f'<td>{a[k]:g}</td>' for k in N.NUTR) + '</tr>'
                   for a in sorted(N.ALIMENTS, key=lambda a: a["aliment"].lower()) if a["kcal"] or a["aliment"] == "Eau")
    body = (f'<section class="g-box" id="aliments" aria-labelledby="al-t"><span class="g-k">8</span><h2 id="al-t">Les aliments</h2>'
            f'<p class="g-n">Valeurs pour 100 g, utilisées pour calculer chaque recette. Touche un en-tête de colonne pour trier. '
            f'Elles reprennent les ordres de grandeur de la table française Ciqual (Anses) ; ce sont des moyennes, pas des mesures de tes produits.</p>'
            f'<div class="ali"><div class="search"><input type="search" id="q" placeholder="Chercher un aliment" aria-label="Chercher un aliment"></div>'
            f'<article><div class="tw"><table id="t"><thead><tr>' + "".join(f'<th><button type="button" class="sort" data-k="{i}">{h}</button></th>' for i, h in enumerate(("Aliment", "kcal", "Prot.", "Gluc.", "Lip.", "Fibres"))) + '</tr></thead>'
            f'<tbody>{rows}</tbody></table></div></article></div>'
            '<script>const n = s => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/œ/g, "oe");'
            'document.getElementById("q").addEventListener("input", e => { const q = n(e.target.value);'
            ' for (const tr of document.querySelectorAll("#t tbody tr")) tr.hidden = q && !n(tr.cells[0].textContent).includes(q); });'
            'let sk = 0, sd = 1; const tb = document.querySelector("#t tbody");'
            'for (const b of document.querySelectorAll("#t .sort")) b.addEventListener("click", () => { const k = +b.dataset.k;'
            ' sd = k === sk ? -sd : (k ? -1 : 1); sk = k;'
            ' const v = tr => k ? parseFloat(tr.cells[k].textContent) : n(tr.cells[0].textContent);'
            ' [...tb.rows].sort((a, c) => (k ? v(a) - v(c) : v(a).localeCompare(v(c))) * sd).forEach(tr => tb.appendChild(tr));'
            ' for (const o of document.querySelectorAll("#t .sort")) { o.classList.toggle("on", o === b); o.dataset.dir = o === b ? (sd > 0 ? "▲" : "▼") : ""; } });'
            'document.querySelector("#t .sort").classList.add("on"); document.querySelector("#t .sort").dataset.dir = "▲";</script></section>')
    return body


def aliments_redirect():
    """L'ancienne adresse aliments.html renvoie vers la section du Guide."""
    return ('<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow">'
            '<meta http-equiv="refresh" content="0; url=guide.html#aliments"><title>Aliments</title></head>'
            '<body><a href="guide.html#aliments">Base des aliments</a></body></html>')


def collect():
    items = []
    for f in sorted(SRC.rglob("*.md")):
        rel = f.relative_to(SRC)
        if rel.parts[0] == "petit-dejeuner":
            sec = "autres" if f.stem == "logique-composition" else "petit-dejeuner"
        elif rel.parts[0] == "desserts":
            sec = "autres"
        elif f.stem == "collations":
            sec = "autres"
        elif "mijoté" in (re.search(r"^- \*\*Catégorie\*\* ?: ?(.+)$", f.read_text(encoding="utf-8"), re.M) or [""," "])[1]:
            sec = "mijotes"
        else:
            sec = "plats"
        items.append((sec, f))
    for f in sorted(PLANS.glob("*.md")):
        items.append(("plans", f))
    return items


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "r").mkdir(parents=True)
    (OUT / "style.css").write_text(CSS, encoding="utf-8")   # lien versionné par CSS_V
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")

    index = []
    kind = {"plats": "Plat", "mijotes": "Mijoté", "petit-dejeuner": "Petit-déjeuner", "autres": "Repère", "plans": "Plan"}
    for sec, f in collect():
        text = f.read_text(encoding="utf-8")
        m = re.search(r"^# (.+)$", text, re.M)
        title = m.group(1).strip() if m else f.stem.replace("-", " ")
        slug = ("plan-" if sec == "plans" else "") + slugify(f)
        t, por = short_time(text), short_portions(text)
        # Texte de recherche : titre + tableau d'ingrédients
        ing = re.search(r"## Ingrédients.*?\n(.*?)(?:\n## |\Z)", text, re.S)
        search = (title + " " + (ing.group(1) if ing else "")).lower()
        search = re.sub(r"[|*\-]+", " ", search)
        search = re.sub(r"\s+", " ", search)[:600]
        body_md = re.sub(r"^# .+\n", "", text, count=1, flags=re.M)
        body_html = markdown.markdown(body_md, extensions=["tables", "sane_lists"])
        # Les fiches citent parfois leur chemin dans le dossier partagé : on le lie vers la page du site.
        body_html = re.sub(r"<code>/mnt/project-files/recettes/(?:[\w-]+/)?([\w-]+)\.md</code>",
                           r'<a href="\1.html">\1</a>', body_html)
        body_html = body_html.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")
        # La liste de méta-données en tête de fiche (source, portions…) passe dans un encadré discret.
        body_html = re.sub(r"^\s*(<ul>.*?</ul>)", r'<details class="intro"><summary>Source, allergènes et préparation</summary>\1</details>', body_html, count=1, flags=re.S)
        mins, dif, cal_fiche = minutes(t), difficulty(text), kcal(text)
        nut = N.analyse(text) if sec != "plans" else None
        cal = round(nut["par_portion"]["kcal"]) if nut else None
        sm = N.saison(nut) if nut else False   # False = sans objet (plans, repères)
        prot, alg, hot = tags(text) if sec != "plans" else ([], [], False)
        pic = pictos(prot, hot)
        facts = "".join(f'<div><span class="label">{k}</span><b>{html.escape(v)}</b></div>'
                        for k, v in (("Temps", t), ("Portions", por),
                                     ("Difficulté", DIFF.get(dif, "") if sec != "plans" else "")) if v)
        nut_html = nutrition_html(nut, cal_fiche) if nut else ""
        art = (f'<div class="recipe"><aside class="r-side"><a class="back" href="../index.html">← Toutes les recettes</a>'
               f'<div class="r-head"><span class="label">{kind[sec]}</span><h1>{html.escape(title)}</h1>'
               + (f'<p class="alg">Contient : {", ".join(alg)}</p>' if alg else "")
               + (f'<p class="alg">Saison : {N.saisons_txt(sm)}</p>' if sm is not False else "") + '</div>'
               + (f'<div class="facts">{facts}</div>' if facts else '<div class="facts"></div>')
               + RATE.replace("__SLUG__", slug) + nut_html + '</aside>'
               + f'<article>{body_html}</article></div>')
        (OUT / "r" / f"{slug}.html").write_text(page(title, art, depth=1), encoding="utf-8")
        index.append({"s": sec, "t": title, "u": f"r/{slug}.html", "k": kind[sec],
                      "i": " · ".join(x for x in (t, por) if x), "q": search,
                      "m": mins, "d": dif, "c": cal, "a": alg, "p": prot, "e": "".join(e for e, _ in pic), "v": visual(slug)[0], "vf": visual(slug)[1],
                      "sm": sm if sm is not False else 0, "st": N.saisons_txt(sm) if sm is not False else ""})

    order = {k: n for n, (k, _) in enumerate(SECTIONS)}
    index.sort(key=lambda d: (order[d["s"]], d["t"].lower()))
    chips = '<button type="button" data-s="" aria-pressed="true">Tout</button>' + "".join(
        f'<button type="button" data-s="{k}" aria-pressed="false">{html.escape(v)}</button>' for k, v in SECTIONS)
    body = f"""
<section class="hero"><h1>Recueil de recettes</h1>
<p>Des plats simples et équilibrés, pensés pour cuisiner le dimanche et manger bien toute la semaine.</p></section>
<div class="search"><input type="search" id="q" placeholder="Rechercher une recette ou un ingrédient" aria-label="Rechercher"></div>
<div class="filters" id="chips">{chips}</div>
<div class="tools">
<label><span class="label">Trier</span><select id="order"><option value="az">A à Z</option><option value="note">Mes préférées</option><option value="time">Les plus rapides</option><option value="diff">Les plus faciles</option><option value="kcal">Les moins caloriques</option><option value="saison">De saison en ce moment</option></select></label>
<label><span class="label">Aliment</span><select id="prot"><option value="">Tous</option><option value="viande">Viande</option><option value="volaille">Volaille</option><option value="bœuf">Bœuf, veau</option><option value="porc">Porc, jambon</option><option value="poisson">Poisson</option><option value="crevettes">Crevettes</option><option value="végétarien">Végétarien</option><option value="pimenté">Pimenté</option></select></label>
<details class="sans"><summary><span class="label">Sans</span> <b id="sans-n">aucun allergène exclu</b></summary><div id="sans">{"".join(f'<label><input type="checkbox" value="{a}"> {a}</label>' for a in ALLERGENS)}</div></details>
</div>
<div id="out"></div>
<script>
// Lien venu du site ou de l'app avec une semaine : on l'ouvre dans Ma semaine
if (/^#w[\\w-]{{10,}}$/.test(location.hash)) location.replace("semaine.html" + location.hash);
const D = {json.dumps(index, ensure_ascii=False)};
const S = {json.dumps(dict(SECTIONS), ensure_ascii=False)};
const DIFFS = {json.dumps(DIFF, ensure_ascii=False)};
const MEAT = ["volaille", "bœuf", "porc", "agneau"];
let sec = "", F = {{ order: "az", prot: "", sans: [] }};
try {{ F = Object.assign(F, JSON.parse(localStorage.getItem("recettes-filtres")) || {{}}); }} catch (e) {{}}
const save = () => {{ try {{ localStorage.setItem("recettes-filtres", JSON.stringify(F)); }} catch (e) {{}} }};
const protOk = d => !F.prot || (F.prot === "viande" ? d.p.some(x => MEAT.includes(x)) : F.prot === "pimenté" ? d.e.includes("🌶") : d.p.includes(F.prot));
const MOIS = new Date().getMonth() + 1;
const now = d => d.sm === null || (Array.isArray(d.sm) && d.sm.includes(MOIS));   // null = toute l'année
const KEYS = {{ time: d => d.m, diff: d => d.d, kcal: d => d.c, saison: d => Array.isArray(d.sm) ? (d.sm.includes(MOIS) ? 0 : 2) : d.sm === null ? 1 : 3 }};
const NOTES = (() => {{ try {{ return JSON.parse(localStorage.getItem("recettes-notes")) || {{}}; }} catch (e) {{ return {{}}; }} }})();
const nt = d => NOTES[d.u.slice(2, -5)] || 0;
const HEART_SVG = {json.dumps(HEART)};
const LIKES = new Set((() => {{ try {{ return JSON.parse(localStorage.getItem("recettes-likes")) || []; }} catch (e) {{ return []; }} }})());
const saveLikes = () => {{ try {{ localStorage.setItem("recettes-likes", JSON.stringify([...LIKES])); localStorage.setItem("recettes-likes-u", Date.now()); }} catch (e) {{}} }};
const norm = s => s.normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").toLowerCase();
function render() {{
  const q = norm(document.getElementById("q").value.trim());
  const out = document.getElementById("out"); out.innerHTML = "";
  let n = 0;
  for (const k of Object.keys(S)) {{
    if (sec && sec !== k) continue;
    const rows = D.filter(d => d.s === k && (!q || q.split(/\\s+/).every(w => norm(d.q).includes(w))))
      .filter(d => (!F.prot && !F.sans.length) || (d.p.length && protOk(d) && !F.sans.some(a => d.a.includes(a))));
    if (!rows.length) continue;
    if (F.order === "note") rows.sort((a, b) => (nt(b) || 2.5) - (nt(a) || 2.5));   // sans note = entre 2 et 3 étoiles
    const key = KEYS[F.order];
    if (key) rows.sort((a, b) => (key(a) ?? 1e9) - (key(b) ?? 1e9));   // valeur inconnue = en fin de liste
    n += rows.length;
    const box = document.createElement("section"); box.className = "sec";
    const head = document.createElement("div"); head.className = "sec-head";
    const h = document.createElement("h2"); h.textContent = S[k];
    const c = document.createElement("span"); c.textContent = rows.length + (rows.length > 1 ? " recettes" : " recette");
    head.append(h, c); box.append(head);
    const list = document.createElement("div"); list.className = "list";
    for (const d of rows) {{
      const it = document.createElement("div"); it.className = "item";
      const a = document.createElement("a"); a.className = "card"; a.href = d.u;
      const l = document.createElement("span"); l.className = "label"; l.textContent = d.k;
      const b = document.createElement("b"); b.textContent = d.t;
      if (d.v) {{
        const im = document.createElement("img"); im.className = "ph"; im.src = d.v; im.alt = ""; im.loading = "lazy";
        const cr = document.createElement("a"); cr.className = "cr"; cr.href = d.vf; cr.target = "_blank"; cr.rel = "noopener";
        cr.textContent = "Photo : Commons"; cr.title = "Photo Wikimedia Commons : auteur et licence sur la page du fichier";
        im.onerror = () => {{ im.remove(); cr.remove(); a.classList.remove("has-ph"); }};
        a.classList.add("has-ph"); a.append(im); it.append(cr);
      }}
      a.append(l, b);
      if (nt(d)) {{ const st = document.createElement("span"); st.className = "stars"; st.textContent = "★".repeat(nt(d)) + "☆".repeat(5 - nt(d)); a.append(st); }}
      const info = [d.i, DIFFS[d.d], d.c && d.c + " kcal"].filter(Boolean).join(" · ");
      if (info) {{ const s = document.createElement("span"); s.className = "t"; s.textContent = info; a.append(s); }}
      if (d.st) {{ const s = document.createElement("span"); s.className = "t sai" + (Array.isArray(d.sm) && d.sm.includes(MOIS) ? " now" : "");
        s.textContent = "Saison : " + d.st + (Array.isArray(d.sm) && d.sm.includes(MOIS) ? " · de saison en ce moment" : ""); a.append(s); }}
      if (d.a.length) {{ const s = document.createElement("span"); s.className = "t"; s.textContent = "Contient : " + d.a.join(", "); a.append(s); }}
      it.prepend(a);
      const slug = d.u.slice(2, -5);
      if (d.s === "plats" || d.s === "mijotes") {{
        const lk = document.createElement("button"); lk.type = "button"; lk.className = "like" + (LIKES.has(slug) ? " on" : "");
        lk.innerHTML = HEART_SVG; lk.setAttribute("aria-pressed", LIKES.has(slug));
        lk.setAttribute("aria-label", (LIKES.has(slug) ? "Retirer des" : "Ajouter aux") + " favoris : " + d.t);
        lk.onclick = () => {{ if (LIKES.has(slug)) LIKES.delete(slug); else LIKES.add(slug); saveLikes();
          const on = LIKES.has(slug); lk.classList.toggle("on", on); lk.setAttribute("aria-pressed", on);
          lk.setAttribute("aria-label", (on ? "Retirer des" : "Ajouter aux") + " favoris : " + d.t); }};
        it.append(lk);
      }}
      list.append(it);
    }}
    box.append(list); out.append(box);
  }}
  if (!n) {{ const p = document.createElement("p"); p.className = "empty"; p.textContent = "Aucune recette ne correspond."; out.append(p); }}
}}
document.getElementById("q").addEventListener("input", render);
document.getElementById("chips").addEventListener("click", e => {{
  const b = e.target.closest("button"); if (!b) return;
  sec = b.dataset.s;
  for (const x of document.querySelectorAll("#chips button")) x.setAttribute("aria-pressed", x === b);
  render();
}});
const $o = document.getElementById("order"), $p = document.getElementById("prot"), $s = document.getElementById("sans");
const sansLabel = () => document.getElementById("sans-n").textContent = F.sans.length ? F.sans.join(", ") : "aucun allergène exclu";
$o.value = F.order; $p.value = F.prot;
for (const x of $s.querySelectorAll("input")) x.checked = F.sans.includes(x.value);
sansLabel();
$o.addEventListener("change", () => {{ F.order = $o.value; save(); render(); }});
$p.addEventListener("change", () => {{ F.prot = $p.value; save(); render(); }});
$s.addEventListener("change", () => {{ F.sans = [...$s.querySelectorAll("input:checked")].map(x => x.value); save(); sansLabel(); render(); }});
render();
</script>"""
    (OUT / "index.html").write_text(page("Miam!", body, active="recueil"), encoding="utf-8")
    (OUT / "aliments.html").write_text(aliments_redirect(), encoding="utf-8")
    (OUT / "guide.html").write_text(page("Comment ça marche", GUIDE.read_text(encoding="utf-8").replace("__ALIMENTS__", aliments_section()), active="guide"), encoding="utf-8")
    (OUT / "compte.html").write_text(page("Profil", COMPTE.read_text(encoding="utf-8").replace("__ALG__", json.dumps(list(ALLERGENS), ensure_ascii=False)).replace("__MAGS__", json.dumps([{k: m[k] for k in ("id", "e", "n", "a", "src", "date")} | {"k": len(m["prix"])} for m in magasins()], ensure_ascii=False)), active="compte"), encoding="utf-8")

    # Page « Ma semaine » : reprise de l'Artifact. Sans Claude, elle enregistre dans le navigateur (localStorage).
    sem = (SITE / "semaine-source.html").read_text(encoding="utf-8")
    sem = sem.replace("<meta charset=utf8>", '<meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="color-scheme" content="light"><meta name="theme-color" content="#f7f3ec">', 1)
    sem = sem.replace('<html>', '<html lang="fr">', 1)
    # Même habillage que le reste du site : fond blanc, vert profond, serif pour les titres, angles droits.
    skin = """<style>
:root{--bg:#f7f3ec;--surface:#fbf8f3;--ink:#1c1d1d;--muted:#6b675f;--line:#e2dccf;--accent:#5f7d63;--accent-soft:#e9efe6;--meat:#a4553f;--meat-soft:#f8ebe5;--cher:#a87a2c;--cher-soft:#f8f0dc;--ok:#3d6b45;color-scheme:light;
--font-display:"DM Sans",system-ui,sans-serif;--font-body:"DM Sans",system-ui,-apple-system,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#f7f3ec;--surface:#fbf8f3;--ink:#1c1d1d;--muted:#6b675f;--line:#e2dccf;--accent:#5f7d63;--accent-soft:#e9efe6;--meat:#a4553f;--meat-soft:#f8ebe5;--cher:#a87a2c;--cher-soft:#f8f0dc;--ok:#3d6b45;color-scheme:light}}
:root[data-theme="dark"]{--bg:#f7f3ec;--surface:#fbf8f3;--ink:#1c1d1d;--muted:#6b675f;--line:#e2dccf;--accent:#5f7d63;--accent-soft:#e9efe6;--meat:#a4553f;--meat-soft:#f8ebe5;--cher:#a87a2c;--cher-soft:#f8f0dc;--ok:#3d6b45;color-scheme:light}
h1,h2,.stat .n,.progress .n,.variants button b{font-weight:700!important;letter-spacing:-.02em}
h1{font-size:clamp(1.8rem,8vw,2.4rem)!important;text-align:center;text-wrap:balance}
header .label{text-align:center}
.alert{border-radius:10px!important}
.pins button{border-radius:999px!important;border-color:var(--line)!important;padding:6px 12px!important}
.stock-add button,.stock-add input,.stock-add select,#pin-add,.gen select,.gen input{border-radius:10px!important}
.stock-add button{border-color:var(--line)!important}
.gen{border-radius:14px!important}
.gen .go{border-radius:12px!important}
#stock button{border-radius:999px!important;border-color:var(--line)!important}
.tabs button[aria-selected="true"]{border-radius:0!important}
.tabs{border:0!important;border-bottom:1px solid var(--line)!important;padding:0!important;background:none!important}
.tabs button{font-size:.72rem!important;text-transform:uppercase;letter-spacing:.14em;font-weight:400!important;border-bottom:1px solid transparent!important}
.tabs button[aria-selected="true"]{background:none!important;color:var(--ink)!important;border-bottom-color:var(--ink)!important}
@media (max-width:560px){.tabs button{letter-spacing:.02em!important;font-size:.66rem!important;padding:10px 1px!important}}
.label{letter-spacing:.16em!important;font-weight:400!important}
.wrap,#view-semaine,#view-courses,#view-recettes,#postes{grid-template-columns:minmax(0,1fr)}
.alert{color:var(--ink)!important}
.keep.bad{font-weight:600!important}
.site{border-bottom:1px solid var(--line)}
.site .in{max-width:1180px;margin:0 auto;padding:18px 16px;display:flex;justify-content:space-between;align-items:baseline;gap:16px}
.brand{font-family:var(--font-display);font-size:1.35rem;font-weight:700;letter-spacing:-.02em;text-decoration:none;color:var(--ink)}
.snav{display:flex;gap:22px}
.snav a{font-size:.72rem;text-transform:uppercase;letter-spacing:.14em;text-decoration:none;color:var(--muted);padding-bottom:3px;border-bottom:1px solid transparent}
.snav a.on{color:var(--ink);border-bottom-color:var(--ink)}
.nav a,.snav a{white-space:nowrap}.nav a.acc,.snav a.acc{padding-left:14px;margin-left:-6px;border-left:1px solid var(--line)}
@media (max-width:480px){.site .in{gap:8px;padding-inline:12px}.brand{font-size:1.05rem}.nav,.snav{gap:8px!important}.nav a,.snav a{font-size:.62rem!important;letter-spacing:.02em!important}.nav a.acc,.snav a.acc{padding-left:7px;margin-left:-1px}}

</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,600;9..40,700&display=swap">
<header class="site"><div class="in"><a class="brand" href="index.html">Miam!</a>
<nav class="snav"><a href="semaine.html" class="on">Ma semaine</a><a href="index.html">Recueil</a><a href="guide.html">Guide</a><a href="compte.html" class="acc">Profil</a></nav></div></header>
"""
    sem = sem.replace('<div class="wrap">', skin + '<div class="wrap">', 1)
    # Calories par portion calculées avec la base aliments.csv, pour « Les plats de la semaine »
    kc, pr = {}, {}
    for _, f in collect():
        nut = N.analyse(f.read_text(encoding="utf-8"))
        if nut:
            kc[slugify(f)] = round(nut["par_portion"]["kcal"])
            pr[slugify(f)] = round(nut["par_portion"]["proteines"])
    sm = {}
    for _, f in collect():
        nut = N.analyse(f.read_text(encoding="utf-8"))
        if nut:
            sm[slugify(f)] = N.saison(nut)
    # Recettes (ingrédients, étapes, conservation) lues dans les fiches : une fiche modifiée met Ma semaine à jour
    fiches = {slugify(f): recipe_data(f.read_text(encoding="utf-8")) for sec, f in collect() if sec != "plans"}
    # Poids d'une pièce (aliments.csv) : sert à fusionner « 1 brocoli » et « 400 g de brocoli » dans la liste
    pieces = [[a["motifs"], a["piece_g"]] for a in N.ALIMENTS if a["piece_g"]]
    # Prix relevés (prix/releve-brut.tsv) : un produit par article, avec sa source et sa date ; jamais de prix inventé
    # Un fichier par magasin (prix/magasins.tsv) ; le premier sert de référence au coût de la semaine
    mags = magasins()
    prix, ref = mags[0]["prix"], mags[0]
    sem = sem.replace("const MAXV = 7,", "const PRIX = " + json.dumps(prix, ensure_ascii=False) + ", PRIX_SRC = " + json.dumps({"nom": ref["n"], "date": ref["date"]}, ensure_ascii=False) + ";\nconst MAGS = " + json.dumps(mags, ensure_ascii=False) + ";\nconst MAXV = 7,", 1)
    sem = sem.replace("const MAXV = 7,", "const FICHES = " + json.dumps(fiches, ensure_ascii=False) + ";\nfor (const id in SLUG) if (FICHES[SLUG[id]]) RECIPES[id] = FICHES[SLUG[id]];\nconst PIECES = " + json.dumps(pieces, ensure_ascii=False) + ";\nconst MAXV = 7,", 1)
    sem = sem.replace("const MAXV = 7,", "const SEANCE = " + (SITE / "seance.json").read_text(encoding="utf-8").strip() + ";\nconst KCAL = " + json.dumps(kc) + ";\nconst PROT = " + json.dumps(pr) + ";\nconst ALG_RX = " + json.dumps(ALLERGENS, ensure_ascii=False) + ";\nconst PT_RX = " + json.dumps(dict(PROTEINS), ensure_ascii=False) + ";\nconst SAISON = " + json.dumps(sm) + ";\nconst MAXV = 7,", 1)
    sem = sem.replace("</head>", app_head() + "</head>", 1)
    sem = sem.replace("</body>", f'<p class="ver" style="text-align:center;font-size:.72rem;color:var(--muted);margin:8px 0 24px">Version du {VERSION}</p></body>', 1)
    (OUT / "semaine.html").write_text(sem, encoding="utf-8")
    app_files()
    print(f"{len(index)} pages générées dans {OUT}")


if __name__ == "__main__":
    main()
