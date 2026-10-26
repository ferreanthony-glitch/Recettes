// Tests du coût (Miam!) : prix relevés seulement, formats entiers, conversions d unités, remplacement.
// Lance : node site/tests/cout.mjs  (Playwright + Chromium requis, comme moteur.mjs)
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

const res = await page.evaluate((N) => {
  const fails = {}, count = {};
  const fail = (rule, why) => { (fails[rule] = fails[rule] || []).length < 8 && fails[rule].push(String(why)); };
  const check = (rule, cond, why) => cond ? count[rule] = (count[rule] || 0) + 1 : fail(rule, why);
  const reset = () => { state.pins = []; state.stock = []; state.ban = []; state.locks = {}; state.maxv = 7; state.ppl = 2; PROF = []; banCache = {key: "", m: {}}; delete state.valid; state.checked = {}; hbSave({ev: []}); };
  // Articles connus sans prix relevé au drive (à compléter quand on les trouve) : jamais de prix inventé pour eux
  const NO_PRICE = ["petits pains complets", "petit pain complet", "fromage de brebis râpé", "escalopes de veau", "bœuf à braiser (paleron)", "vin blanc sec (facultatif)", "légumes d'accompagnement au choix"];

  // 1. Chaque prix vient du relevé : produit, code-barres, format, prix, source datée
  check("source et date", PRIX_SRC.nom && /^\d{4}-\d\d-\d\d$/.test(PRIX_SRC.date), JSON.stringify(PRIX_SRC));
  Object.entries(PRIX).forEach(([k, p]) => check("relevé complet", p.p && /^\d{8,14}$/.test(p.ean) && p.q > 0 && p.e > 0 && ["g", "ml", "pc", "botte"].includes(p.u), k + " " + JSON.stringify(p)));
  // 2. Tous les articles des 70 plats et des petits-déjeuners ont un prix, sauf la liste connue
  const all = new Map(); Object.values(Q).concat([BREAKFAST]).forEach(l => l.forEach(([n, q, u]) => all.set(n + "|" + u, [n, q, u])));
  all.forEach(([n, q, u]) => { const c = priceItem({name: n, q, u});
    check("article chiffré ou connu sans prix", (c && !c.miss) || NO_PRICE.includes(n), n + " (" + u + ")"); });
  // 3. Formats entiers : assez pour le besoin, un format de moins ne suffirait pas ; le coût des repas ne dépasse jamais la caisse
  for (let i = 0; i < N; i++) { reset(); generate(); const co = costOf(state.sel);
    check("coût des repas ≤ caisse", co.used <= co.cost + 1e-6 && co.used > 0, co.used + " / " + co.cost);
    co.lines.forEach(([it, c]) => { const u = it.u === "gousse" ? "pc" : it.u;
      const need = u === c.p.u || ["g", "ml"].includes(u) && ["g", "ml"].includes(c.p.u) ? it.q : conv(it.q, u, c.p.u, it.name);
      check("formats entiers suffisants", c.packs * c.p.q >= need - 1e-6 && (c.packs === 1 || (c.packs - 1) * c.p.q < need), it.name + " " + need + " pour " + c.packs + "×" + c.p.q);
      check("prix = formats × prix relevé", Math.abs(c.cost - c.packs * c.p.e) < 1e-9, it.name); });
    check("pas d'article sans prix inattendu", co.miss.every(m => NO_PRICE.includes(m)), co.miss.join(", "));
  }
  // 4. Personnes : 4 personnes coûtent environ deux fois plus que 2
  reset(); generate(); const c2 = costOf(state.sel).used; state.ppl = 4; const c4 = costOf(state.sel).used; state.ppl = 2;
  check("coût proportionnel aux personnes", Math.abs(c4 / c2 - 2) < 0.02, c2 + " → " + c4);
  // 5. Affichage : semaine, liste, source et date, jamais d'« économie »
  reset(); generate(); validateWeek(); renderList();
  const cm = document.getElementById("cost-msg").textContent;
  check("coût dans Mes courses", /Coût estimé des repas : ≈ \d+ €/.test(cm) && /À la caisse/.test(cm) && cm.includes(PRIX_SRC.nom) && cm.includes("26/10/2026"), cm.slice(0, 200));
  check("coût dans le générateur", /Coût estimé des repas ≈ \d+ €, soit ≈ \d+,\d\d € par jour et par personne/.test(document.getElementById("gen-msg").textContent), document.getElementById("gen-msg").textContent.slice(0, 300));
  check("produit et prix sur chaque ligne chiffrée", document.querySelectorAll("#list small.px").length === costOf().lines.length, document.querySelectorAll("#list small.px").length + " / " + costOf().lines.length);
  check("aucune économie affichée", !/économi/i.test(document.body.innerText), "mot trouvé");
  // 6. Remplacer un repas : le coût suit, la raison donnée correspond au calcul
  let shown = 0;
  for (let i = 0; i < N; i++) { reset(); generate(); validateWeek();
    const k = ["1-1", "2-0", "3-1", "4-0", "5-1"][i % 5], os = replaceOptions(state.sel, k, 99);
    os.forEach(o => { const nx = {...state.sel}; o.targets.forEach(x => nx[x] = o.id); const d = costOf(nx).used - costOf(state.sel).used;
      check("écart de coût exact", Math.abs(d - o.dc) < 0.011, o.id + " " + d + " / " + o.dc);
      const w = o.why.find(x => /€ de courses/.test(x));
      check("raison de prix cohérente", Math.abs(o.dc) < 1 ? !w : w && w.includes(Math.round(Math.abs(o.dc)) + " €") && (o.dc > 0) === w.includes("+"), o.id + " " + o.dc + " " + w); });
    const o = os[0], c0 = costOf(state.sel).used; replaceMeal(k, o.id); const c1 = costOf(state.sel).used, msg = document.getElementById("swap-msg").textContent;
    if (Math.abs(c1 - c0) >= 0.5) { shown++; check("compte rendu : coût avant → après", msg.includes("Coût estimé des repas : ≈ " + Math.round(c0) + " € → " + Math.round(c1) + " €"), msg.slice(0, 200)); }
  }
  // 7. Courge du poulet thaï : 300 g comme dans la fiche, fusionnée avec la butternut entière d'un autre plat
  check("courge du poulet thaï en grammes", Q.thai.find(x => x[0] === "butternut")[1] === 300 && Q.thai.find(x => x[0] === "butternut")[2] === "g", JSON.stringify(Q.thai));
  reset(); state.sel = {...state.sel}; const ks = SLOTS.map(s => s.k); ks.forEach(k => state.sel[k] = "salbro"); state.sel["1-0"] = "thai"; state.sel["1-1"] = "butter";
  const bn = buildList(state.sel).filter(x => stem(x.name) === "butternut");
  check("butternut sur une seule ligne", bn.length === 1, JSON.stringify(bn.map(x => [x.q, x.u])));
  reset();
  return {fails, count, shown};
}, +process.argv[2] || 12);

let bad = 0;
for (const [rule, n] of Object.entries(res.count)) if (!res.fails[rule]) console.log("OK     " + rule + " (" + n + ")");
for (const [rule, why] of Object.entries(res.fails)) { bad++; console.log("ÉCHEC  " + rule + "\n         " + why.join("\n         ")); }
if (jsErr.length) { bad++; console.log("ERREURS JS : " + [...new Set(jsErr)].join(" | ")); }
console.log("(" + res.shown + " remplacements avec écart de coût affiché)");
await browser.close(); srv.close();
process.exit(bad ? 1 : 0);
