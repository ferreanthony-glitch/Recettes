"""Calcul des valeurs nutritionnelles d'une fiche à partir de la base aliments.csv (valeurs pour 100 g)."""
import csv
import re
import unicodedata
from pathlib import Path

BASE = Path(__file__).with_name("aliments.csv")
NUTR = ("kcal", "proteines", "glucides", "lipides", "fibres")


def norm(s):
    s = s.lower().replace("œ", "oe").replace("’", "'")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def load():
    rows = []
    with BASE.open(encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            for k in NUTR:
                r[k] = float(r[k])
            for k in ("piece_g", "cc_g", "flou_g"):
                r[k] = float(r[k]) if r[k] else None
            r["rx"] = re.compile(r["motifs"])
            rows.append(r)
    return rows


ALIMENTS = load()


def find(name):
    n = norm(name)
    return next((a for a in ALIMENTS if a["rx"].search(n)), None)


FRAC = {"½": ".5", "¼": ".25", "¾": ".75"}
UNIT = r"(kg|g\b|ml|cl|l\b|c\. a soupe|c\. a cafe|gousses?|pincees?|tranches?|pots?|verres?|poignees?|feuilles?|sticks?|brins?|bottes?|portions?)"
VAGUE = r"^((un|1) filet|un soupcon|un peu|quelques|une poignee|a volonte|selon|facultatif|non dose|—|-)"


def grams(qty, a):
    """Quantité écrite dans la fiche → grammes ; None si elle n'est pas chiffrée."""
    q = norm(qty)
    for k, v in FRAC.items():
        q = q.replace(k, v)
    q = re.sub(r"(\d),(\d)", r"\1.\2", q).strip()
    if re.match(VAGUE, q):
        return a["flou_g"]
    q = re.sub(r"^(une?|un)\b", "1", q)
    m = re.match(r"(\d*\.?\d+)(?:\s*a\s*(\d*\.?\d+))?\s*" + UNIT + "?", q)
    if not m:
        return None
    n = float(m.group(1))
    if m.group(2):
        n = (n + float(m.group(2))) / 2          # « 80 à 100 g » → 90 g
    u = m.group(3) or ""
    cc = a["cc_g"] or 5
    if u == "kg":
        return n * 1000
    if u in ("g", "ml"):
        return n
    if u == "cl":
        return n * 10
    if u == "l":
        return n * 1000
    if u == "c. a soupe":
        return n * cc * 3
    if u == "c. a cafe":
        return n * cc
    if u.startswith("gousse"):
        return n * 5
    if u.startswith("pincee") or u.startswith("brin"):
        return n * 0.3
    if u.startswith("verre"):
        return n * 200
    if u.startswith("botte"):
        return n * 25
    if u.startswith("poignee"):
        return n * 30
    if u.startswith("stick"):
        return n * 1.5
    return n * a["piece_g"] if a["piece_g"] else None   # pièces, tranches, pots, feuilles…


def portions(text):
    m = re.search(r"^- \*\*Portions\*\* ?: ?(.+)$", text, re.M)
    if not m:
        return 2
    p = norm(m.group(1))
    if (x := re.search(r"(\d+) portions", p)):
        return int(x.group(1))
    pers = int(x.group(1)) if (x := re.search(r"(\d+) personnes?", p)) else 2
    rep = int(x.group(1)) if (x := re.search(r"(\d+) repas", p)) else 1
    return pers * rep


def analyse(text):
    """Renvoie {par_portion: {kcal…}, portions, lignes: [(ingrédient, aliment, g, kcal)], ignores: [ingrédient]}."""
    sec = re.search(r"## Ingrédients.*?\n(.*?)(?:\n## |\Z)", text, re.S)
    if not sec:
        return None
    tot = dict.fromkeys(NUTR, 0.0)
    lignes, ignores = [], []
    for l in sec.group(1).splitlines():
        if not l.startswith("|") or re.match(r"\|\s*[-:]", l):
            continue
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) < 2 or norm(c[0]) in ("ingredient", "ingredients"):
            continue
        name = re.sub(r"^\*\*[^*]+\*\*\s*:\s*", "", c[0])
        a = find(name)
        if a is None:
            ignores.append(name)
            continue
        if a["kcal"] == 0:
            continue
        g = grams(c[1], a)
        if g is None:
            ignores.append(name)
            continue
        for k in NUTR:
            tot[k] += a[k] * g / 100
        lignes.append((name, a["aliment"], g, a["kcal"] * g / 100))
    if not lignes:
        return None
    n = portions(text)
    return {"par_portion": {k: v / n for k, v in tot.items()}, "portions": n, "lignes": lignes, "ignores": ignores}


def mois(spec):
    """« 9-4,6 » → ensemble des mois (1 à 12) ; les plages passent l'hiver si besoin."""
    out = set()
    for part in filter(None, spec.split(",")):
        a, _, b = part.partition("-")
        a, b = int(a), int(b or a)
        m = a
        while True:
            out.add(m)
            if m == b:
                break
            m = m % 12 + 1
    return out


SAISON = {a["aliment"]: mois(a.get("saison") or "") for a in ALIMENTS}
SAISONS = (("printemps", (3, 4, 5)), ("été", (6, 7, 8)), ("automne", (9, 10, 11)), ("hiver", (12, 1, 2)))


def saison(nut):
    """Mois où la recette est de saison : au moins 75 % (en poids) de ses fruits et légumes saisonniers le sont.
    None = aucun produit saisonnier (toute l'année)."""
    w = [(SAISON[al], g) for _, al, g, _ in nut["lignes"] if SAISON.get(al) and g]
    tot = sum(g for _, g in w)
    if not tot:
        return None
    return sorted(m for m in range(1, 13) if sum(g for s, g in w if m in s) >= 0.75 * tot)


def saisons_txt(months):
    if months is None:
        return "toute l'année"
    if not months:
        return "hors saison toute l'année"
    return ", ".join(n for n, ms in SAISONS if sum(m in months for m in ms) >= 2) or "courte saison"
