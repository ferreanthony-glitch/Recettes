// Tests du remplacement d'un repas (Miam!).
// Lance : node site/tests/remplacement.mjs  (Playwright + Chromium requis, comme moteur.mjs)
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
  const fail = (rule, why) => { (fails[rule] = fails[rule] || []).length < 6 && fails[rule].push(why); };
  const ok = rule => count[rule] = (count[rule] || 0) + 1;
  const check = (rule, cond, why) => cond ? ok(rule) : fail(rule, why);
  const ids = Object.keys(R), rnd = a => a[Math.floor(Math.random() * a.length)];
  const slot = k => SLOTS.find(s => s.k === k);
  const BANS = ["poulet", "courgette", "champignons", "bœuf haché", "pois chiches", "riz", "lait de coco", "viande", "patate douce"];
  const ALGS = Object.keys(typeof ALG_RX === "undefined" ? {} : ALG_RX);
  const reset = () => { state.pins = []; state.stock = []; state.ban = []; state.locks = {}; state.maxv = 7; PROF = []; banCache = {key: "", m: {}}; delete state.valid; state.checked = {}; };
  const back = n => { const d = today(); d.setDate(d.getDate() - n); return iso(d); };

  // 1. Règles strictes respectées par chaque plat proposé, sur des semaines générées avec des réglages au hasard
  for (let run = 0; run < N; run++) {
    reset();
    state.maxv = Math.floor(Math.random() * 15);
    state.ban = Math.random() < 0.5 ? [] : [rnd(BANS)];
    const alg = ALGS.length && Math.random() < 0.3 ? [rnd(ALGS)] : [], reg = rnd(["", "", "flexi", "pesce", "vege"]);
    PROF = alg.length || reg ? [{prenom: "Test", alg, reg}] : []; banCache = {key: "", m: {}};
    generate();
    const sel = state.sel;
    SLOTS.forEach(sl => {
      const p = POSTE_OF[sl.k], opts = replaceOptions(sel, sl.k);
      check("calcul reproductible", JSON.stringify(opts) === JSON.stringify(replaceOptions(sel, sl.k)), sl.k);
      opts.forEach(o => {
        const id = o.id, tag = R[id].n + " pour " + slotName(sl);
        check("pas le plat actuel", id !== sel[sl.k], tag);
        check("aliments à éviter et profil", !banned(id), tag + " contient " + banned(id));
        check("soupe le soir seulement", !o.targets.some(k => wrongTime(id, slot(k).m)), tag);
        check("façon de cuisiner du poste", !!R[id][p.f], tag + " (poste " + p.f + ")");
        check("conservation", p.f !== "r" || !o.targets.some(k => tooLong(id, slot(k).d)), tag);
        check("plat cher sur deux repas", !(R[id].c || []).length || o.targets.length >= 2, tag);
        const after = {...sel}; o.targets.forEach(k => after[k] = id);
        const meat = SLOTS.filter(s => R[after[s.k]].v).length;
        check("plafond de viande ou compromis annoncé", meat <= maxV() || o.relaxed || o.warn.some(w => /viande/.test(w)), tag + " : " + meat + "/" + maxV());
        const dup = SLOTS.some(s => !o.targets.includes(s.k) && after[s.k] === id);
        check("pas de doublon ou compromis annoncé", !dup || o.relaxed, tag);
        check("explication lisible", o.why.length && !/undefined|NaN/.test(o.why.concat(o.warn).join(" ")), tag + " : " + o.why.join(", "));
      });
    });
  }
  // 2. Un plat cuisiné pour deux repas est remplacé pour les deux
  reset(); state.sel = toSlots(V.A.p);
  check("plat double remplacé deux fois", JSON.stringify(replaceTargets(state.sel, "1-0")) === JSON.stringify(["1-0", "2-0"]), replaceTargets(state.sel, "1-0").join(","));
  state.sel["2-0"] = "chili";
  check("repas seul remplacé seul", JSON.stringify(replaceTargets(state.sel, "1-0")) === JSON.stringify(["1-0"]), replaceTargets(state.sel, "1-0").join(","));
  // 3. Semaine validée : tout suit (liste, coches, séance), le compte rendu dit vrai, et on peut annuler
  for (let t = 0; t < 12; t++) {
    reset(); generate(); validateWeek();
    const before = buildList(), k = rnd(SLOTS).k, opts = replaceOptions(state.sel, k);
    if (!opts.length) { ok("aucun plat possible : rien ne change"); continue; }
    before.slice(0, 5).forEach(i => state.checked[i.key] = true); persist();
    const snap = JSON.stringify({sel: state.sel, valid: state.valid, checked: state.checked, stock: state.stock});
    const o = opts[0], selBefore = {...state.sel}, d = listDiff(selBefore, Object.assign({...selBefore}, Object.fromEntries(o.targets.map(x => [x, o.id]))));
    replaceMeal(k, o.id);
    check("semaine validée mise à jour", sameSel() && o.targets.every(x => state.valid.sel[x] === o.id), k + " " + o.id);
    const after = buildList();
    check("liste = plats de la semaine", JSON.stringify(after.map(i => [i.key, i.q])) === JSON.stringify(buildList(state.sel).map(i => [i.key, i.q])), k);
    const real = listDiff(selBefore, state.sel);
    check("compte rendu des courses exact", JSON.stringify(real) === JSON.stringify(d), JSON.stringify(real).slice(0, 120));
    const kept = before.slice(0, 5).filter(i => after.some(a => a.key === i.key));
    check("coches gardées", kept.every(i => state.checked[i.key]), kept.map(i => i.key).join(", "));
    if (POSTE_OF[k].f === "r") { const pl = planSeance(state.valid.sel);
      check("séance recalculée", pl.ids.includes(o.id) && !o.targets.some(x => pl.ids.includes(selBefore[x]) && !Object.values(state.sel).includes(selBefore[x])), o.id); }
    const msg = document.getElementById("swap-msg").textContent;
    check("compte rendu affiché", /→/.test(msg) && !/undefined|NaN/.test(msg), msg.slice(0, 120));
    document.querySelector("#swap-msg button").click();
    check("annuler rétablit tout", JSON.stringify({sel: state.sel, valid: state.valid, checked: state.checked, stock: state.stock}) === snap, k);
  }
  // 4. Semaine en cours de modification (pas revalidée) : la semaine validée n'est pas touchée
  reset(); generate(); validateWeek(); state.sel["5-1"] = state.sel["5-1"] === "salbro" ? "tmz" : "salbro";
  const v0 = JSON.stringify(state.valid), o4 = replaceOptions(state.sel, "1-1")[0];
  replaceMeal("1-1", o4.id);
  check("brouillon : validée intacte", JSON.stringify(state.valid) === v0, "validée modifiée");
  // 5. Samedi : un remplacement ne fait pas glisser la semaine à la suivante
  reset(); generate(); validateWeek(); state.valid.start = back(6);
  replaceMeal("6-1", replaceOptions(state.sel, "6-1")[0].id);
  check("samedi : même semaine", state.valid.start === back(6), state.valid.start);
  // 6. Après la séance du dimanche : seulement des plats du jour même, et la part déjà cuisinée est prise en compte
  reset(); generate(); validateWeek(); state.valid.start = back(2);
  const o6 = replaceOptions(state.sel, "4-0");
  check("après la séance : plats rapides", o6.length && o6.every(o => R[o.id].q), o6.map(o => o.id).join(", "));
  if (o6.length) { tab = "semaine"; replaceMeal("4-0", o6[0].id);
    check("après la séance : part déjà cuisinée", /déjà cuisiné/.test(document.getElementById("swap-msg").textContent), document.getElementById("swap-msg").textContent.slice(0, 160)); }
  reset();
  return {fails, count};
}, +process.argv[2] || 20);

let bad = 0;
for (const [rule, n] of Object.entries(res.count)) if (!res.fails[rule]) console.log("OK     " + rule + " (" + n + " vérifications réussies)");
for (const [rule, why] of Object.entries(res.fails)) { bad++; console.log("ÉCHEC  " + rule + "\n         " + why.join("\n         ")); }
if (jsErr.length) { bad++; console.log("ERREURS JS : " + [...new Set(jsErr)].join(" | ")); }
await browser.close(); srv.close();
process.exit(bad ? 1 : 0);
