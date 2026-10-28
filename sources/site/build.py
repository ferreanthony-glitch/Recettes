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

import os
ROOT = Path(os.environ.get("MIAM_ROOT", "/mnt/project-files"))   # MIAM_ROOT : fabriquer depuis un autre dossier (ex. sources/ du dépôt)
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

# Feuille commune à toutes les pages, Ma semaine comprise (direction artistique d'octobre 2026) : site/style.css
CSS = (SITE / "style.css").read_text(encoding="utf-8")

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Bricolage+Grotesque:opsz,wght@12..96,500..800&display=swap">')

# Pictogrammes au trait du kit Miam! (24 × 24, trait 1,8), en ligne pour suivre la couleur du texte
_IC = {
    "semaine": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/>',
    "courses": '<path d="M2 4h3l3 13h11l3-10H6M9 21h.01M18 21h.01"/>',
    "cuisine": '<path d="M6 20h12v-8a5 5 0 0 0-3-9 5 5 0 0 0-6 0 5 5 0 0 0-3 9zM6 16h12"/>',
    "recueil": '<path d="M12 5Q7 2 3 5v15q5-3 9 0 4-3 9 0V5q-4-3-9 0v15"/>',
    "guide": '<path d="M20 4Q4 3 4 15q0 8 8 5Q20 16 20 4ZM4 21q6-9 12-11"/>',
    "compte": '<circle cx="12" cy="8" r="4"/><path d="M4 21q0-7 8-7t8 7"/>',
    "search": '<circle cx="10" cy="10" r="7"/><path d="m15 15 6 6"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 3"/>',
    "lock": '<rect x="5" y="10" width="14" height="12" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
    "swap": '<path d="M7 4v16M7 4 3 8M7 4l4 4M17 20V4M17 20l-4-4M17 20l4-4"/>',
    "check": '<path d="M4 12l5 5L20 6"/>',
    "back": '<path d="m15 5-7 7 7 7"/>',
}


def icon(name, cls="ic"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round">{_IC[name]}</svg>')


# Logo : « Miam! » en Bricolage Grotesque, précédé du petit cœur tomate du kit
HEART_LOGO = '<svg class="logo-h" viewBox="0 0 30 32" aria-hidden="true"><path d="M14 9C6 -3 -6 11 14 27C34 11 22 -3 14 9Z" fill="#C66B52"/></svg>'
# Branche de sauge du kit (illustration au trait, utilisée avec parcimonie : pied du menu, en-têtes de page)
SAUGE = ('<svg class="sauge" viewBox="0 0 210 290" aria-hidden="true"><g fill="#E8EEE3" stroke="#5E795F" stroke-width="5" stroke-linejoin="round">'
         '<path d="M70 270 Q100 160 135 45" fill="none" stroke-width="7" stroke-linecap="round"/><path d="M94 192 Q12 177 29 120 Q81 127 94 192Z"/>'
         '<path d="M106 146 Q166 150 182 87 Q126 91 106 146Z"/><path d="M122 94 Q68 82 85 25 Q125 38 122 94Z"/><path d="M75 238 Q133 235 156 184 Q96 181 75 238Z"/></g></svg>')
# Navigation : menu latéral sur ordinateur, barre d'onglets en bas sur téléphone. Mes courses et En cuisine sont des vues de semaine.html.
NAV = [("semaine", "Ma semaine", "Semaine", "semaine.html#semaine"), ("courses", "Mes courses", "Courses", "semaine.html#courses"),
       ("cuisine", "En cuisine", "Cuisine", "semaine.html#cuisine"), ("recueil", "Recettes", "Recettes", "index.html"),
       ("guide", "Guide", "Guide", "guide.html"), ("compte", "Profil", "Profil", "compte.html")]


def shell(active="", up=""):
    """Menu commun : barre latérale (ordinateur), barre du haut et onglets du bas (téléphone)."""
    on = lambda k: ' class="on" aria-current="page"' if active == k else ""
    side = "".join(f'<a href="{up}{u}" data-space="{k}"{on(k)}>{icon(k)}<span>{l}</span></a>' for k, l, _, u in NAV)
    tabs = "".join(f'<a href="{up}{u}" data-space="{k}"{on(k)}><span class="ti">{icon(k)}</span><span>{s}</span></a>' for k, _, s, u in NAV if k != "guide")
    logo = f'<a class="logo" href="{up}semaine.html#semaine" aria-label="Miam!, ma semaine">{HEART_LOGO}<span>Miam!</span></a>'
    return (f'<aside class="sidebar">{logo}<p class="tagline">Bien manger, simplement.</p><nav class="snav" aria-label="Menu">{side}</nav>'
            f'<div class="side-foot">{SAUGE}<p>De bons repas,<br>toute la semaine.</p></div></aside>'
            f'<header class="topbar">{logo}<a class="tb-guide{" on" if active == "guide" else ""}" href="{up}guide.html">{icon("guide")}<span>Guide</span></a></header>'
            f'<nav class="tabbar" aria-label="Menu">{tabs}</nav>')


def app_head(up=""):
    """Balises pour installer le site comme une app (écran d'accueil iPhone / Android)."""
    return (f'<link rel="manifest" href="{up}manifest.webmanifest"><link rel="icon" href="{up}icon-192.png"><link rel="apple-touch-icon" href="{up}icon-180.png">'
            '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">'
            '<meta name="apple-mobile-web-app-title" content="Miam!"><meta name="apple-mobile-web-app-status-bar-style" content="default">'
            f'<script>if ("serviceWorker" in navigator && /github\\.io$|^localhost$/.test(location.hostname)) navigator.serviceWorker.register("{up}sw.js", {{updateViaCache: "none"}}).catch(() => {{}});</script>')


def app_files():
    """Manifeste, icônes et service worker (cache hors ligne) de l'app."""
    (OUT / "manifest.webmanifest").write_text(json.dumps({
        "name": "Miam!", "short_name": "Miam!", "lang": "fr", "start_url": "semaine.html", "scope": "./",
        "display": "standalone", "background_color": "#F7F3EB", "theme_color": "#F7F3EB",
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
    return (f'<!doctype html><html lang="fr"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            f'<meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#F7F3EB"><meta name="color-scheme" content="light">'
            f'<title>{html.escape(title)}{" · Miam!" if title != "Miam!" else ""}</title>{FONTS}<link rel="stylesheet" href="{up}style.css?v={CSS_V}">{app_head(up)}</head>'
            f'<body><div class="app">{shell(active, up)}<main class="app-main"><div class="wrap">{body}</div>'
            f'<footer class="foot">Miam! · version du {VERSION}</footer></main></div></body></html>')


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
        art = (f'<div class="recipe"><aside class="r-side"><a class="back" href="../index.html">{icon("back")}Toutes les recettes</a>'
               f'<div class="r-head"><span class="label">{kind[sec]}</span><h1>{html.escape(title)}</h1>'
               + (f'<p class="alg">Contient : {", ".join(alg)}</p>' if alg else "")
               + (f'<p class="alg">Saison : {N.saisons_txt(sm)}</p>' if sm is not False else "") + '</div>'
               + (f'<div class="facts">{facts}</div>' if facts else '<div class="facts"></div>')
               + RATE.replace("__SLUG__", slug) + nut_html + '</aside>'
               + f'<article>{body_html}</article></div>')
        (OUT / "r" / f"{slug}.html").write_text(page(title, art, depth=1, active="recueil"), encoding="utf-8")
        index.append({"s": sec, "t": title, "u": f"r/{slug}.html", "k": kind[sec],
                      "i": " · ".join(x for x in (t, por) if x), "q": search,
                      "m": mins, "d": dif, "c": cal, "a": alg, "p": prot, "e": "".join(e for e, _ in pic), "v": visual(slug)[0], "vf": visual(slug)[1],
                      "sm": sm if sm is not False else 0, "st": N.saisons_txt(sm) if sm is not False else ""})

    order = {k: n for n, (k, _) in enumerate(SECTIONS)}
    index.sort(key=lambda d: (order[d["s"]], d["t"].lower()))
    chips = '<button type="button" data-s="" aria-pressed="true">Tout</button>' + "".join(
        f'<button type="button" data-s="{k}" aria-pressed="false">{html.escape(v)}</button>' for k, v in SECTIONS)
    body = f"""
<header class="page-head"><div class="ph-text"><p class="eyebrow">Le recueil</p><h1>Mes recettes</h1>
<p class="sub">Des plats simples et équilibrés, pensés pour cuisiner le dimanche et bien manger toute la semaine.</p></div>{SAUGE}</header>
<div class="search">{icon('search')}<input type="search" id="q" placeholder="Rechercher une recette ou un ingrédient" aria-label="Rechercher"></div>
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
    (OUT / "index.html").write_text(page("Recettes", body, active="recueil"), encoding="utf-8")
    (OUT / "aliments.html").write_text(aliments_redirect(), encoding="utf-8")
    (OUT / "guide.html").write_text(page("Comment ça marche", GUIDE.read_text(encoding="utf-8").replace("__ALIMENTS__", aliments_section()), active="guide"), encoding="utf-8")
    (OUT / "compte.html").write_text(page("Profil", COMPTE.read_text(encoding="utf-8").replace("__ALG__", json.dumps(list(ALLERGENS), ensure_ascii=False)).replace("__MAGS__", json.dumps([{k: m[k] for k in ("id", "e", "n", "a", "src", "date")} | {"k": len(m["prix"])} for m in magasins()], ensure_ascii=False)), active="compte"), encoding="utf-8")

    # Page « Ma semaine » : reprise de l'Artifact. Sans Claude, elle enregistre dans le navigateur (localStorage).
    sem = (SITE / "semaine-source.html").read_text(encoding="utf-8")
    sem = sem.replace("<meta charset=utf8>", '<meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="color-scheme" content="light"><meta name="theme-color" content="#F7F3EB">', 1)
    sem = sem.replace('<html>', '<html lang="fr">', 1)
    # Même habillage que le reste du site : feuille commune, polices et menu (la vue ouverte est marquée par le script de la page)
    sem = sem.replace("</head>", FONTS + f'<link rel="stylesheet" href="style.css?v={CSS_V}"></head>', 1)
    sem = sem.replace("__SHELL__", shell("semaine"), 1).replace("__SAUGE__", SAUGE, 1)
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
    sem = sem.replace("__VERSION__", VERSION, 1)
    (OUT / "semaine.html").write_text(sem, encoding="utf-8")
    app_files()
    print(f"{len(index)} pages générées dans {OUT}")


if __name__ == "__main__":
    main()
