// Tests du petit-déjeuner (Miam!) : un choix par jour, la liste de courses et le coût le suivent.
// Lance : node site/tests/petitdej.mjs  (Playwright + Chromium requis, comme moteur.mjs)
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
  const fail = (rule, why) => { (fails[rule] = fails[rule] || []).length < 8 && fails[rule].push(String(why)); };
  const check = (rule, cond, why) => cond ? count[rule] = (count[rule] || 0) + 1 : fail(rule, why);
  const qty = (items, name) => items.filter(i => same(i.name, name)).reduce((a, i) => a + i.q, 0);
  state.stock = []; state.ppl = 2; delete state.valid; delete state.bk; state.checked = {}; state.alt = {};

  // 1. Sans choix, la semaine garde l'ancien petit-déjeuner (mêmes quantités qu'avant)
  check("défaut", bkOf().join() === BK_DEF.join(), bkOf());
  const base = buildList(), noBk = Object.values(counts(state.sel)).length;
  const old = {"skyr nature": 600, "yaourts nature": 12, "saumon fumé": 320, "cream cheese": 80};
  const dish = buildList(state.sel, {}, []);   // la liste sans aucun petit-déjeuner
  Object.entries(old).forEach(([n, q]) => check("défaut", Math.abs(qty(base, n) - qty(dish, n) - q) < 1e-6, n + " " + (qty(base, n) - qty(dish, n))));

  // 2. Chaque petit-déjeuner ajoute exactement ses articles, une fois par jour choisi
  Object.entries(BK).forEach(([b, x]) => {
    const l = buildList(state.sel, {}, Array(7).fill(b));
    x.q.forEach(([n, q, u]) => { const tot = Object.values(BK[b].q).filter(y => same(y[0], n) && y[2] === u).reduce((a, y) => a + y[1], 0) * 7;
      const got = l.filter(i => same(i.name, n) && i.u === u).reduce((a, i) => a + i.q, 0) - dish.filter(i => same(i.name, n) && i.u === u).reduce((a, i) => a + i.q, 0);
      check("articles", Math.abs(got - tot) < 1e-6, b + " " + n + " " + got + " ≠ " + tot); });
    (x.pl || []).forEach(p => check("placard", l.some(i => i.u === "pl" && i.name === p), b + " " + p));
    check("nom", x.n && x.s && x.s.length <= 16, b);
  });

  // 3. Le nombre de personnes suit
  state.ppl = 4; check("personnes", Math.abs(qty(buildList(state.sel, {}, Array(7).fill("skyr")), "skyr nature") - qty(buildList(state.sel, {}, []), "skyr nature") - 4200) < 1e-6, "4 pers."); state.ppl = 2;

  // 4. Choisir un petit-déjeuner dans le tableau : la case, la liste et la validation suivent
  render();
  const s0 = document.querySelectorAll("#grid td.bkc select");
  check("tableau", s0.length === 7, s0.length);
  check("tableau", document.querySelectorAll("#grid td.cell").length === 14, "les 14 repas restent");
  validateWeek(); check("validation", sameSel() && state.valid.bk.join() === BK_DEF.join(), JSON.stringify(state.valid.bk));
  const sel = document.querySelectorAll("#grid td.bkc select")[2]; sel.value = "oeufbacon"; sel.dispatchEvent(new Event("change"));
  check("choix", bkOf()[2] === "oeufbacon" && document.querySelectorAll("#grid td.bkc .cname")[2].textContent === BK.oeufbacon.s, bkOf());
  check("validation suit", sameSel() && state.valid.bk[2] === "oeufbacon", "semaine validée mise à jour");
  check("liste suit", qty(buildList(), "bacon") - qty(dish, "bacon") === 100, qty(buildList(), "bacon"));
  state.bk = [...bkOf()]; state.bk[3] = "choco"; check("à revalider", !sameSel(), "changement non validé");
  state.bk = [...state.valid.bk];

  // 5. Le coût n'utilise que des prix relevés, et change avec le choix
  Object.entries(BK).forEach(([b, x]) => { const l = buildList(state.sel, {}, Array(7).fill(b)); l.filter(it => x.q.some(y => same(it.name, y[0]))).forEach(it => { const c = priceItem(it); check("prix", !c || !c.miss, b + " " + it.name); }); });

  // 6. Synchronisation : le choix voyage avec la semaine
  check("sync", JSON.stringify(ghData().bk) === JSON.stringify(bkOf()), "ghData");
  const o = JSON.parse(unb64u(pack().slice(1))); check("lien", o.b.join() === bkOf().join() && o.v.b.join() === state.valid.bk.join(), JSON.stringify(o.b));

  // 7. Ancienne semaine validée sans petit-déjeuner : le défaut, sans erreur
  delete state.valid.bk; check("ancienne validation", listBk().join() === BK_DEF.join(), listBk());
  state.bk = ["x"]; check("valeur abîmée", bkOf() === BK_DEF, "bk invalide ignoré");
  delete state.bk; delete state.valid; render();
  return {fails, count};
});
await browser.close(); srv.close();
const n = Object.values(res.count).reduce((a, b) => a + b, 0), bad = Object.keys(res.fails);
console.log(n + " vérifications réussies.");
if (jsErr.length) { console.log("Erreurs JS :", jsErr); process.exit(1); }
if (bad.length) { bad.forEach(r => console.log("ÉCHEC " + r + " :", res.fails[r].join(" | "))); process.exit(1); }
console.log("Tout est bon.");
