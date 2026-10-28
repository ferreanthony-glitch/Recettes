// Tests de la séance du dimanche (Miam!) : durée visée, tes temps, minuteurs, règles d hygiène.
// Lance : node site/tests/seance.mjs  (Playwright + Chromium requis, comme moteur.mjs)
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
  const fail = (rule, why) => { (fails[rule] = fails[rule] || []).length < 6 && fails[rule].push(String(why)); };
  const check = (rule, cond, why) => cond ? count[rule] = (count[rule] || 0) + 1 : fail(rule, why);
  const reset = () => { state.pins = []; state.stock = []; state.ban = []; state.locks = {}; state.maxv = 7; PROF = []; banCache = {key: "", m: {}}; delete state.valid; state.checked = {}; teSave({m: {}}); seSave({}); };
  const COOK = n => ["O", "H", "F", "A", "R", "P"].includes(n.k);

  // 1. Durée visée : au-delà de 3 h la semaine perd des points, en dessous rien ne change
  check("pénalité de durée", seancePenalty(180) === 0 && seancePenalty(120) === 0 && seancePenalty(195) === 4 && seancePenalty(240) === 16, [seancePenalty(195), seancePenalty(240)]);
  // Le générateur garde la semaine la mieux notée une fois la durée comptée : jamais plus longue qu'une semaine tirée sans en tenir compte, en moyenne
  reset(); let gen = 0;
  for (let i = 0; i < N; i++) { generate(); gen += planSeance(state.sel).total; }
  gen /= N;
  check("semaines générées plus courtes", gen < 235, "moyenne " + Math.round(gen) + " min (sans la durée : ≈ 255 min)");
  check("durée dans le message", /séance du dimanche estimée à \d/.test(document.getElementById("gen-msg").textContent), document.getElementById("gen-msg").textContent.slice(0, 160));

  // 2. Tes temps : seules les étapes de travail s'apprennent, jamais les cuissons
  reset(); generate();
  const p0 = planSeance(state.sel, {m: {}});
  check("sans mesure = estimations", JSON.stringify(planSeance(state.sel).nodes.map(n => n.m)) === JSON.stringify(p0.nodes.map(n => n.m)) && p0.mine === 0, "différent");
  const c = p0.nodes.find(n => n.k === "C");
  const p1 = planSeance(state.sel, {m: {[c.key]: [2]}}), c1 = p1.nodes[c.i];
  check("une étape mesurée suit ton temps", Math.abs(c1.m - Math.round(c.est * 2)) <= 1 && c1.mine && p1.mine === 1, c.m + " → " + c1.m);
  check("les autres étapes ne bougent pas", p1.nodes.every((n, i) => i === c.i || n.end || n.m === p0.nodes[i].m), "autre étape modifiée");
  const keys = p0.nodes.filter(n => n.key).map(n => n.key), slow = {m: {}}; keys.slice(0, 6).forEach(k => slow.m[k] = [1.8]);
  const p2 = planSeance(state.sel, slow);
  check("ta vitesse générale dès 5 étapes", p2.nodes.filter(n => n.key && !keys.slice(0, 6).includes(n.key)).every(n => n.m === Math.max(1, Math.round(n.est * 1.8))), "vitesse générale non appliquée");
  check("cuissons jamais modifiées", p2.nodes.filter(COOK).every(n => n.m === p0.nodes[n.i].m) && planSeance(state.sel, {m: {L: [0.5], x: [0.5], y: [0.5], z: [0.5], w: [0.5]}}).nodes.filter(COOK).every(n => n.m === p0.nodes[n.i].m), "cuisson raccourcie");
  check("séance plus longue si tu vas plus lentement", p2.total >= p0.total, p0.total + " → " + p2.total);
  teSave({m: {}});
  check("mesure aberrante ignorée", !recordTime("k", 10, 2) && !recordTime("k", 10, 40) && !teLoad().m.k, JSON.stringify(teLoad()));
  for (let i = 0; i < 7; i++) recordTime("k", 10, 10 + i);
  check("cinq dernières mesures gardées", teLoad().m.k.length === 5 && teLoad().m.k[4] === 1.6, JSON.stringify(teLoad().m.k));
  check("médiane des mesures", speeds().own.k === 1.4, speeds().own.k);

  // 3. En cuisine : cocher une étape de travail enregistre ton temps
  reset(); generate(); showTab("seance"); renderSeance();
  const plan = planSeance(state.sel), steps = [...document.querySelectorAll("#se-steps > li")];
  const iC = plan.steps.findIndex(n => n.k === "C" && n.key);
  const sigOf = n => n.k + "|" + (n.id || "") + "|" + n.t;
  const s0 = seLoad(); s0.mark = Date.now() - plan.steps[iC].est * 1.3 * 6e4; seSave(s0);
  steps[iC].querySelector("input").click();
  const got = teLoad().m[plan.steps[iC].key];
  check("cocher enregistre ton temps", got && Math.abs(got[0] - 1.3) < 0.15, JSON.stringify(teLoad()));
  check("repère posé pour l'étape suivante", Date.now() - seLoad().mark < 5000, seLoad().mark);
  check("étape marquée « ton temps »", /ton temps/.test(document.querySelectorAll("#se-steps > li")[planSeance(state.sel).steps.findIndex(n => n.key === plan.steps[iC].key)].textContent), "libellé absent");
  check("bouton oublier mes temps", !document.getElementById("se-forget").hidden, "caché");
  check("durée annoncée d'après tes temps", /d'après tes temps/.test(document.getElementById("se-sum").textContent), document.getElementById("se-sum").textContent.slice(0, 160));
  // Cocher une cuisson n'apprend rien
  const before = JSON.stringify(teLoad()), iO = planSeance(state.sel).steps.findIndex(n => COOK(n) && n.k !== "P");
  document.querySelectorAll("#se-steps > li")[iO].querySelector("input").click();
  check("cuisson cochée : rien appris", JSON.stringify(teLoad()) === before, "appris");

  // 4. Minuteurs
  reset(); generate(); renderSeance();
  const pl = planSeance(state.sel), iT = pl.steps.findIndex(n => n.k === "O" || n.k === "H" || n.k === "F");
  const li = () => document.querySelectorAll("#se-steps > li")[iT];
  check("minuteur sur chaque cuisson", pl.steps.every((n, i) => !TIMED(n) || document.querySelectorAll("#se-steps > li")[i].querySelector(".se-timer")) && pl.steps.every((n, i) => TIMED(n) || !document.querySelectorAll("#se-steps > li")[i].querySelector(".se-timer")), "minuteur manquant ou en trop");
  li().querySelector(".se-timer").click();
  const sig = sigOf(pl.steps[iT]), end = seLoad().timers[sig];
  check("minuteur lancé à la bonne durée", Math.abs(end - Date.now() - pl.steps[iT].m * 6e4) < 5000, end);
  check("décompte affiché", /^Reste \d+:\d\d/.test(li().querySelector(".se-timer").textContent), li().querySelector(".se-timer").textContent);
  const s1 = seLoad(); s1.timers[sig] = Date.now() - 1000; seSave(s1); renderSeance();
  check("sonnerie à la fin", li().querySelector(".se-timer").classList.contains("ring") && /Temps écoulé/.test(li().textContent), li().textContent.slice(0, 120));
  li().querySelector("input").click();
  check("cocher arrête le minuteur", !seLoad().timers[sig] && !li().querySelector(".se-timer"), JSON.stringify(seLoad().timers));
  li().querySelector("input").click(); li().querySelector(".se-timer").click(); li().querySelector(".se-timer").click();
  check("arrêter le minuteur", !seLoad().timers[sig], "toujours là");

  // 5. Hygiène : règles fixes et dates limites du frigo sur les boîtes
  check("règles d'hygiène affichées", document.querySelectorAll(".se-safe dt").length === SAFETY.length && /2 h/.test(document.querySelector(".se-safe").textContent), "absentes");
  const endN = pl.steps.find(n => n.end);
  check("boîtes : frigo jusqu'au jour limite", endN.ing.every(([nm, t]) => /frigo jusqu'à (dimanche|lundi|mardi|mercredi|jeudi|vendredi|samedi) au plus tard/.test(t) || /congélateur/.test(t)), JSON.stringify(endN.ing).slice(0, 200));
  const lim = pl.ids.filter(id => (KEEP[id] || [3])[0] < 7).every(id => { const bs = endN.ing.filter(x => x[0] === R[id].n.replace(/ \*$/, "").split(/,| au | aux | à la | de | et /)[0]); return !bs.length || bs.some(b => b[1].includes(DAYS[(KEEP[id] || [3])[0]].toLowerCase())); });
  check("jour limite = durée de la fiche", lim, "jour différent de KEEP");
  // Aucun repas prévu au-delà de sa limite (sans congélation)
  check("aucun repas après sa limite", SLOTS.every(sl => !keepInfo(sl, state.sel) || !keepInfo(sl, state.sel).bad), "repas trop tard");
  // 6. Trois espaces : Ma semaine, Mes courses, En cuisine (qui regroupe Aujourd'hui, la séance et les recettes)
  const vis = () => TABS.filter(x => !document.getElementById("view-" + x).hidden);
  check("3 espaces affichés", document.querySelectorAll(".tabs [role=tab]").length === 3, document.querySelectorAll(".tabs [role=tab]").length);
  showTab("semaine"); check("Ma semaine", vis().join() === "semaine" && document.getElementById("subtabs").hidden && document.getElementById("space-title").textContent === "Ma semaine", vis());
  document.getElementById("tab-courses").click(); check("Mes courses", vis().join() === "courses" && document.getElementById("tab-courses").getAttribute("aria-selected") === "true", vis());
  document.getElementById("tab-cuisine").click();
  const exp = today().getDay() === 0 ? "seance" : lastCuisine;
  check("En cuisine : séance le dimanche, sinon dernière vue", vis().join() === exp && !document.getElementById("subtabs").hidden, vis() + " / " + exp);
  ["jour", "seance", "recettes"].forEach(x => { document.getElementById("sub-" + x).click();
    check("En cuisine › " + x, vis().join() === x && document.getElementById("tab-cuisine").getAttribute("aria-selected") === "true" && document.getElementById("sub-" + x).getAttribute("aria-selected") === "true", vis()); });
  showTab("semaine"); document.getElementById("tab-cuisine").click();
  check("En cuisine se souvient de la vue", vis().join() === (today().getDay() === 0 ? "seance" : "recettes"), vis());
  showTab("semaine");
  reset();
  return {fails, count};
}, +process.argv[2] || 12);

let bad = 0;
for (const [rule, n] of Object.entries(res.count)) if (!res.fails[rule]) console.log("OK     " + rule + " (" + n + ")");
for (const [rule, why] of Object.entries(res.fails)) { bad++; console.log("ÉCHEC  " + rule + "\n         " + why.join("\n         ")); }
if (jsErr.length) { bad++; console.log("ERREURS JS : " + [...new Set(jsErr)].join(" | ")); }
// Téléphone : pas de défilement horizontal dans En cuisine, minuteur lancé
const ph = await browser.newPage({viewport: {width: 390, height: 844}});
await ph.goto(page.url());
await ph.evaluate(() => { generate(); showTab("seance"); renderSeance(); document.querySelector(".se-timer").click(); document.querySelector(".se-safe").open = true; });
const ov = await ph.evaluate(() => document.documentElement.scrollWidth - innerWidth);
console.log((ov > 0 ? (bad++, "ÉCHEC ") : "OK     ") + " téléphone 390 px sans défilement horizontal (" + ov + ")");
if (process.argv[3]) await ph.screenshot({path: process.argv[3], fullPage: false});
await browser.close(); srv.close();
process.exit(bad ? 1 : 0);
