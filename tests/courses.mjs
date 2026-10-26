// Tests de la liste de courses et des données des plats (Miam!).
// Lance : node site/tests/courses.mjs  (Playwright + Chromium requis, comme moteur.mjs)
// La page public/semaine.html est servie localement ; chaque test appelle les vraies fonctions de la page.
import { createRequire } from "module";
import http from "http";
import fs from "fs";
import path from "path";
import { execSync } from "child_process";
const require = createRequire(import.meta.url);
const { chromium } = require(path.join(execSync("npm root -g").toString().trim(), "playwright"));

const PUB = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../public");
const TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".json": "application/json", ".webmanifest": "application/json", ".png": "image/png"};
const srv = http.createServer((q, s) => {
  const f = path.join(PUB, decodeURIComponent(q.url.split("?")[0]));
  fs.readFile(f, (e, b) => { if (e) { s.writeHead(404); s.end(); return; } s.writeHead(200, {"Content-Type": TYPES[path.extname(f)] || "application/octet-stream"}); s.end(b); });
}).listen(0);
const browser = await chromium.launch({executablePath: fs.existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined});
const page = await browser.newPage();
const jsErr = [];
page.on("pageerror", e => jsErr.push(e.message));
await page.goto("http://127.0.0.1:" + srv.address().port + "/semaine.html");

const res = await page.evaluate(() => {
  const fails = {}, count = {};
  const fail = (rule, why) => { (fails[rule] = fails[rule] || []).length < 6 && fails[rule].push(why); };
  const ok = rule => count[rule] = (count[rule] || 0) + 1;
  const ids = Object.keys(R), rnd = a => a[Math.floor(Math.random() * a.length)];
  const randomSel = () => Object.fromEntries(SLOTS.map(sl => [sl.k, rnd(ids)]));
  const lines = () => buildList().filter(i => i.u !== "pl");
  delete state.valid; state.stock = []; state.ppl = 2;

  // 1. Un produit = une ligne : aucun nom (ramené au singulier) sur deux lignes, sauf unités vraiment inconvertibles
  for (let t = 0; t < 60; t++) {
    state.sel = randomSel();
    const seen = {};
    lines().forEach(i => { const k = stem(i.name); (seen[k] = seen[k] || []).push(i.u); });
    let bad = Object.entries(seen).filter(([, us]) => us.length > 1);
    bad.length ? fail("un produit, une ligne", bad.map(([k, us]) => k + " (" + us.join(", ") + ")").join(" ; ")) : ok("un produit, une ligne");
  }
  // 2. Personnes : les quantités suivent exactement le nombre de personnes
  for (let t = 0; t < 20; t++) {
    state.sel = randomSel(); state.ppl = 2;
    const a = Object.fromEntries(lines().map(i => [i.key, i.q]));
    state.ppl = 4;
    const b = Object.fromEntries(lines().map(i => [i.key, i.q]));
    const bad = Object.keys(a).filter(k => Math.abs(b[k] - 2 * a[k]) > 1e-6);
    bad.length ? fail("quantités × personnes", bad.slice(0, 3).join(", ")) : ok("quantités × personnes");
    state.ppl = 2;
  }
  // 3. Repas : un plat sur deux repas = deux fois la recette (une fois pour « once », qui fait déjà deux repas)
  const base = toSlots(V.A.p);
  ids.forEach(id => {
    const ref = {...base}; Object.keys(ref).forEach(k => { if (ref[k] === id) ref[k] = id === "salbro" ? "tmz" : "salbro"; });
    const o = {...ref, "1-0": id}, w = {...ref, "1-0": id, "2-0": id};
    state.sel = o; const lo = lines().filter(i => i.src.has(R[id].n));
    state.sel = w; const lw = lines().filter(i => i.src.has(R[id].n));
    // on compare seulement les lignes propres au plat
    const own = lo.filter(i => i.src.size === 1).map(i => i.key);
    const exp = R[id].once ? 1 : 2, bad = own.filter(k => { const a = lo.find(i => i.key === k), b = lw.find(i => i.key === k); return !b || Math.abs(b.q - exp * a.q) > 1e-6; });
    bad.length ? fail("repas × recette", id + " : " + bad.join(", ")) : ok("repas × recette");
  });
  // 4. Coches : un nouveau tirage ne touche pas à la liste validée ; une nouvelle semaine repart de zéro, une mise à jour garde les coches
  state.sel = toSlots(V.A.p); state.checked = {}; delete state.valid; state.pins = []; state.ban = []; state.locks = {}; PROF = []; banCache = {key: "", m: {}};
  document.getElementById("validate").click();
  const k0 = buildList()[0].key; state.checked[k0] = true;
  generate();
  state.checked[k0] ? ok("coches gardées après un tirage") : fail("coches gardées après un tirage", "coche perdue");
  // mise à jour en cours de semaine : on fait comme si la semaine validée avait commencé il y a 3 jours
  const back = n => { const d = today(); d.setDate(d.getDate() - n); return iso(d); };
  state.valid.start = back(3); state.sel["3-1"] = state.sel["3-1"] === "gratin" ? "soupct" : "gratin";
  document.getElementById("validate").click();
  state.valid.start === back(3) ? ok("mise à jour : même semaine") : fail("mise à jour : même semaine", "départ décalé au " + state.valid.start);
  state.checked[k0] ? ok("mise à jour : coches gardées") : fail("mise à jour : coches gardées", "coche perdue");
  // samedi (6 jours après le départ) : on valide la semaine suivante, liste vierge
  state.valid.start = back(6);
  document.getElementById("validate").click();
  state.valid.start === iso(dayDate(0)) ? ok("samedi : semaine suivante") : fail("samedi : semaine suivante", "départ " + state.valid.start);
  !Object.keys(state.checked).length ? ok("nouvelle semaine : liste vierge") : fail("nouvelle semaine : liste vierge", Object.keys(state.checked).join(", "));
  delete state.valid; state.checked = {};
  // 5. Données : chaque plat a sa recette (lue dans la fiche) et chaque article acheté figure dans la fiche
  // Articles achetés en plus de la fiche, voulus : œufs durs des plats légers, salade et légumes servis à côté
  const EXTRA = {courg: ["œufs"], souppd: ["œufs"], soupcf: ["œufs"], soupoti: ["œufs"], c_cake: ["salade"], croq: ["légumes d'accompagnement"]};
  // Noms différents pour le même produit (achat → fiche)
  const ALIAS = {"filets de poulet": /poulet/, "bœuf haché": /(viande|bœuf) hachée?/, "butternut": /courge|butternut/, "pâtes complètes": /pâtes|coquillettes/, "chèvre frais": /chèvre/, "mozzarella": /mozzarella/, "pecorino": /pecorino/, "fromage de brebis": /brebis|pecorino/};
  ids.forEach(id => {
    const rc = RECIPES[id];
    if (!rc || !rc.ing.length || !rc.steps.length) { fail("recette lue dans la fiche", id); return; }
    ok("recette lue dans la fiche");
    const names = rc.ing.map(x => norm(x[0])).join(" | ");
    Q[id].forEach(([n]) => {
      if ((EXTRA[id] || []).some(e => same(n, e))) return;
      const al = Object.keys(ALIAS).find(a => n.startsWith(a));
      const words = norm(n).replace(/\(.*?\)/g, "").split(/[\s,]+/).filter(w => w.length > 2 && !["des","les","aux","pour"].includes(w)).map(w => w.replace(/(s|x)$/, ""));
      const hit = al ? ALIAS[al].test(rc.ing.map(x => x[0].toLowerCase()).join(" | ")) : words.some(w => names.includes(w));
      hit ? ok("achat présent dans la fiche") : fail("achat présent dans la fiche", id + " : " + n);
    });
  });
  return {fails, count};
});

let bad = 0;
for (const [rule, n] of Object.entries(res.count)) if (!res.fails[rule]) console.log("OK     " + rule + " (" + n + " vérifications réussies)");
for (const [rule, why] of Object.entries(res.fails)) { bad++; console.log("ÉCHEC  " + rule + "\n         " + why.join("\n         ")); }
if (jsErr.length) { bad++; console.log("ERREURS JS : " + [...new Set(jsErr)].join(" | ")); }
await browser.close(); srv.close();
process.exit(bad ? 1 : 0);
