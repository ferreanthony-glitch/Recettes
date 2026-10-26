// Tests des habitudes (Miam!) : plats remplacés ou choisis à la main, effet sur le générateur et les suggestions.
// Lance : node site/tests/habitudes.mjs  (Playwright + Chromium requis, comme moteur.mjs)
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
  const reset = () => { state.pins = []; state.stock = []; state.ban = []; state.locks = {}; state.maxv = 7; PROF = []; banCache = {key: "", m: {}}; delete state.valid; state.checked = {}; hbSave({ev: []}); };
  const ids = Object.keys(R);

  // 1. Un geste isolé ne compte pas, l'effet grandit puis plafonne
  reset();
  const [a, b] = ids;
  hbRecord(a, b);
  check("un seul geste : aucun effet", habitScore(a) === 0 && habitScore(b) === 0 && habitLine() === "", [habitScore(a), habitScore(b)]);
  hbRecord(a, b);
  check("deux remplacements : moins proposé", habitScore(a) === -2 && habitScore(b) === 1.5, [habitScore(a), habitScore(b)]);
  for (let i = 0; i < 10; i++) hbRecord(a, b);
  check("effet plafonné", habitScore(a) === -6 && habitScore(b) === 4.5, [habitScore(a), habitScore(b)]);
  check("explication visible", habitLine().includes(R[a].n) && habitLine().includes(R[b].n), habitLine());
  for (let i = 0; i < 40; i++) hbRecord(ids[2], ids[3]);
  check("30 derniers gestes gardés", hbLoad().ev.length === 30 && !habits().out[a], hbLoad().ev.length);
  hbRecord(a, a); hbRecord("inconnu", a);
  check("gestes sans objet ignorés", hbLoad().ev.length === 30 && hbLoad().ev.every(e => e[0] !== e[1] && R[e[0]]), "enregistré");

  // 2. Remplacer un repas l'enregistre, l'annulation l'efface
  reset(); generate(); validateWeek();
  const o = replaceOptions(state.sel, "1-1")[0], cur = state.sel["1-1"];
  replaceMeal("1-1", o.id);
  check("remplacement retenu", hbLoad().ev.length === 1 && hbLoad().ev[0][0] === cur && hbLoad().ev[0][1] === o.id, JSON.stringify(hbLoad()));
  document.querySelector("#swap-msg button").click();
  check("annulation : rien retenu", hbLoad().ev.length === 0, JSON.stringify(hbLoad()));
  // Choisir un plat à la main dans une case
  const alt = ids.find(id => id !== state.sel["2-0"] && R[id].q);
  const cur2 = state.sel["2-0"]; pick("2-0", alt);
  check("choix à la main retenu", hbLoad().ev.length === 1 && hbLoad().ev[0][0] === cur2 && hbLoad().ev[0][1] === alt, JSON.stringify(hbLoad()));
  pick("2-0", alt);
  check("même plat : rien de plus", hbLoad().ev.length === 1, hbLoad().ev.length);

  // 3. Le générateur propose moins un plat souvent remplacé (règles strictes inchangées)
  reset();
  const freq = {}; for (let i = 0; i < N; i++) { generate(); new Set(Object.values(state.sel)).forEach(id => freq[id] = (freq[id] || 0) + 1); }
  const top = Object.keys(freq).sort((x, y) => freq[y] - freq[x]).slice(0, 3);
  top.forEach(id => { hbRecord(id, ids.find(x => x !== id)); hbRecord(id, ids.find(x => x !== id)); hbRecord(id, ids.find(x => x !== id)); hbRecord(id, ids.find(x => x !== id)); });
  let after = 0; for (let i = 0; i < N; i++) { generate(); after += top.filter(id => Object.values(state.sel).includes(id)).length; }
  const before = top.reduce((x, id) => x + freq[id], 0);
  check("plats souvent remplacés moins proposés", after < before, before + " → " + after);
  check("le générateur le dit", /Tes habitudes comptent : moins souvent/.test(document.getElementById("prof-line").textContent), document.getElementById("prof-line").textContent.slice(0, 200));
  check("lien Effacer affiché", !!document.getElementById("hb-forget"), "absent");
  // Les plats souvent choisis remontent dans les suggestions de remplacement, avec la raison
  reset(); generate();
  const os = replaceOptions(state.sel, "3-1", 99), last = os[os.length - 1];
  for (let i = 0; i < 4; i++) hbRecord(ids.find(x => x !== last.id), last.id);
  const os2 = replaceOptions(state.sel, "3-1", 99);
  const s1 = last.sc, s2 = os2.find(x => x.id === last.id).sc;   // le score monte d'exactement 1,5 × 4,5 (effet plafonné), le rang dépend des autres critères
  check("plat souvent choisi : remonte", Math.abs(s2 - s1 - 1.5 * 4.5) < 1e-9 && os2.find(x => x.id === last.id).why.includes("tu le choisis souvent"), s1 + " → " + s2);
  check("habitudes : règles strictes intactes", os2.map(x => x.id).sort().join() === os.map(x => x.id).sort().join(), "liste des plats possibles changée");
  // Effacer
  window.confirm = () => true; renderGen(); document.getElementById("hb-forget").click();
  check("effacer les habitudes", hbLoad().ev.length === 0 && !document.getElementById("hb-forget"), JSON.stringify(hbLoad()));
  reset();
  return {fails, count};
}, +process.argv[2] || 15);

let bad = 0;
for (const [rule, n] of Object.entries(res.count)) if (!res.fails[rule]) console.log("OK     " + rule + " (" + n + ")");
for (const [rule, why] of Object.entries(res.fails)) { bad++; console.log("ÉCHEC  " + rule + "\n         " + why.join("\n         ")); }
if (jsErr.length) { bad++; console.log("ERREURS JS : " + [...new Set(jsErr)].join(" | ")); }
await browser.close(); srv.close();
process.exit(bad ? 1 : 0);
