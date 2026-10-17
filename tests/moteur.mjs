// Tests automatiques du générateur de Ma semaine (Miam!).
// Lance : node site/tests/moteur.mjs [nombre de tirages]  (Playwright + Chromium requis)
// La page public/semaine.html est servie localement et chaque test appelle le vrai generate() de la page.
import { createRequire } from "module";
import http from "http";
import fs from "fs";
import path from "path";
import { execSync } from "child_process";
const require = createRequire(import.meta.url);
const { chromium } = require(path.join(execSync("npm root -g").toString().trim(), "playwright"));

const PUB = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../public");
const N = +process.argv[2] || 300;
const TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".json": "application/json", ".webmanifest": "application/json", ".png": "image/png"};
const srv = http.createServer((q, s) => {
  const f = path.join(PUB, decodeURIComponent(q.url.split("?")[0]));
  fs.readFile(f, (e, b) => { if (e) { s.writeHead(404); s.end(); return; } s.writeHead(200, {"Content-Type": TYPES[path.extname(f)] || "application/octet-stream"}); s.end(b); });
}).listen(0);
const URL_ = "http://127.0.0.1:" + srv.address().port + "/semaine.html";

const browser = await chromium.launch({executablePath: fs.existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined});
const page = await browser.newPage();
const jsErr = [];
page.on("pageerror", e => jsErr.push(e.message));
await page.goto(URL_);

// Tout se passe dans la page : tirages aléatoires de réglages, appel de generate(), vérification des règles
const res = await page.evaluate(async (N) => {
  const fails = {}, count = {};
  const fail = (rule, why) => { (fails[rule] = fails[rule] || []).length < 5 && fails[rule].push(why); };
  const ok = rule => count[rule] = (count[rule] || 0) + 1;
  const posteOf = {}; P.forEach(p => p.slots.forEach(([d, m]) => posteOf[d + "-" + m] = p));
  const ids = Object.keys(R), rnd = a => a[Math.floor(Math.random() * a.length)];
  const ALGS = Object.keys(typeof ALG_RX === "undefined" ? {} : ALG_RX);
  // Mots repères indépendants du moteur, pour vérifier les allergènes autrement que par ses propres étiquettes
  const ALG_CHECK = {gluten: /\b(pâtes|spaghetti|coquillettes|lasagne|farine|pain|semoule|boulgour|tortilla|wrap|chapelure|galette de blé)/i, lait: /\b(lait de vache|fromage|parmesan|emmental|mozzarella|feta|crème fraîche|beurre|yaourt|skyr|comté|pecorino|chèvre|cream cheese|fromage blanc)\b/i, œufs: /\b(œufs?|oeufs?)\b/i};
  const BANS = ["poulet", "courgette", "champignons", "bœuf haché", "pois chiches", "riz", "lait de coco", "viande", "patate douce", "tomates cerises", "épinards"];
  const t0 = Date.now();
  for (let run = 0; run < N; run++) {
    // Réglages tirés au hasard
    state.maxv = Math.floor(Math.random() * 15);
    state.sais = rnd([0, 0, 0, 50, 80]);
    state.ban = Math.random() < 0.5 ? [] : [...new Set(Array.from({length: 1 + Math.floor(Math.random() * 3)}, () => rnd(BANS)))];
    state.pins = Math.random() < 0.4 ? [...new Set(Array.from({length: 1 + Math.floor(Math.random() * 3)}, () => rnd(ids)))] : [];
    state.stock = [];
    const alg = ALGS.length && Math.random() < 0.4 ? [rnd(ALGS)] : [];
    const reg = rnd(["", "", "", "flexi", "pesce", "vege"]);
    PROF = alg.length || reg ? [{prenom: "Test", alg, reg}] : [];
    banCache = {key: "", m: {}};
    const msg = document.getElementById("gen-msg"); msg.textContent = "";
    generate();
    const txt = msg.textContent, sel = state.sel;
    if (/Aucune semaine possible/.test(txt)) { ok("tirage impossible signalé"); continue; }
    const stuck = /Aucun plat compatible/.test(txt);
    const of = p => sel[p.slots[0][0] + "-" + p.slots[0][1]];
    // Règle 1 : jamais au-delà de la conservation ; au-delà du frigo, la part va au congélateur
    SLOTS.forEach(sl => {
      const id = sel[sl.k], p = posteOf[sl.k];
      if (p.f !== "r" || !R[id].r) return;
      const [fr, fz] = KEEP[id] || [3, 0];
      if (sl.d > fr && !fz) fail("conservation", R[id].n + " " + DAYS[sl.d] + " (tient " + fr + " j, ne se congèle pas)");
      else ok("conservation");
      const k = keepInfo(sl);
      if (sl.d > fr && fz && !(k && k.freeze)) fail("congélation", R[id].n + " " + DAYS[sl.d] + " : part non envoyée au congélateur");
      else if (k && k.bad) fail("congélation", R[id].n + " " + DAYS[sl.d] + " affiché trop tard");
      else ok("congélation");
    });
    // Règle 2 : plafond de repas avec viande (sauf si aucune autre possibilité : le message doit le dire)
    const meat = SLOTS.filter(sl => R[sel[sl.k]].v).length;
    if (meat > maxV() && !/Impossible de rester/.test(txt) && !stuck) fail("viande", meat + " repas avec viande pour un plafond de " + maxV());
    else ok("viande");
    // Règle 3 : aliments chers uniquement sur des plats doublés, et sur 2 repas au plus
    const cher = {};
    P.forEach(p => { const id = of(p); (R[id].c || []).forEach(c => cher[c] = (cher[c] || 0) + p.slots.length);
      if ((R[id].c || []).length && p.slots.length < 2 && !state.pins.includes(id)) fail("aliments chers", R[id].n + " sur un seul repas (" + p.t + ")"); });
    Object.entries(cher).forEach(([c, n]) => n > 2 ? fail("aliments chers", c + " sur " + n + " repas") : ok("aliments chers"));
    // Règle 4 : soupes le soir seulement
    SLOTS.forEach(sl => { if (sl.m === 0 && /^soupe/i.test(R[sel[sl.k]].n)) fail("soupes le soir", R[sel[sl.k]].n + " " + DAYS[sl.d] + " midi"); else ok("soupes le soir"); });
    // Règle 5 : allergènes du profil et aliments à éviter (les plats imposés à la main sont signalés, pas retirés)
    if (!stuck) P.forEach(p => {
      const id = of(p); if (state.pins.includes(id)) return;
      if (banned(id)) fail("allergènes et aliments à éviter", R[id].n + " contient " + banned(id));
      const names = dishNames(id).join(" ");
      alg.forEach(a => { if (ALG_CHECK[a] && ALG_CHECK[a].test(names)) fail("allergènes (contrôle indépendant)", R[id].n + " semble contenir " + a + " : " + names.match(ALG_CHECK[a])[0]); });
      if ((reg === "vege" || reg === "pesce") && R[id].v) fail("allergènes et aliments à éviter", R[id].n + " : viande pour un profil " + reg);
      ok("allergènes et aliments à éviter");
    });
  }
  PROF = []; return {fails, count, ms: Date.now() - t0};
}, N);

// Cas limites, construits à la main
const edge = await page.evaluate(() => {
  const out = [], check = (rule, cond, why) => out.push({rule, ok: !!cond, why});
  const of = (sel, p) => sel[p.slots[0][0] + "-" + p.slots[0][1]];
  const reset = () => { state.maxv = 7; state.sais = 0; state.ban = []; state.pins = []; state.stock = []; PROF = []; banCache = {key: "", m: {}}; };
  // 1. Poste sans plat possible : le plat gardé doit quand même tenir jusqu'au jour prévu
  reset();
  const dl3 = P.find(p => p.k === "dl3"), bad = Object.keys(R).find(id => R[id].r && dl3.slots.some(([d]) => tooLong(id, d)));
  if (bad) {
    dl3.slots.forEach(([d, m]) => state.sel[d + "-" + m] = bad);
    state.ban = [...new Set(POOL(dl3).map(id => R[id].i[0]))];
    generate();
    const id = of(state.sel, dl3);
    check("conservation (poste bloqué)", fitsPoste(id, dl3), R[id].n + " gardé le vendredi et le samedi midi alors qu'il ne tient que " + (KEEP[id] || [3])[0] + " jours");
  }
  // 2. Plat cher imposé : il doit aller sur un poste doublé quand c'est possible
  reset();
  Object.keys(R).filter(id => (R[id].c || []).length).forEach(id => {
    state.pins = [id]; generate();
    const p = P.find(p => of(state.sel, p) === id);
    const double = P.some(q => q.slots.length > 1 && R[id][q.f] && fitsPoste(id, q));
    check("aliments chers (plat imposé)", !p || p.slots.length > 1 || !double, R[id].n + " imposé et placé sur un seul repas (" + (p && p.t) + ") alors qu'un poste doublé était possible");
    check("aliments chers (plat imposé)", p && p.slots.length > 1, R[id].n + " : aucun poste doublé ne peut l'accueillir, il finit sur un seul repas");
  });
  // 3. Vendredi soir et cheat meal sont cuisinés le jour même : la conservation ne doit ni les écarter ni les signaler
  reset();
  P.filter(p => p.f !== "r").forEach(p => Object.keys(R).filter(id => R[id][p.f] && !p.slots.some(([d, m]) => wrongTime(id, m))).forEach(id => {
    check("plat cuisiné le jour même", fitsPoste(id, p), R[id].n + " écarté de « " + p.t + " » pour cause de conservation alors qu'il est cuisiné le jour même");
    const save = {...state.sel}; p.slots.forEach(([d, m]) => state.sel[d + "-" + m] = id);
    p.slots.forEach(([d, m]) => check("plat cuisiné le jour même", !keepInfo({k: d + "-" + m, d, m}), R[id].n + " signalé « à congeler » ou « trop tard » sur « " + p.t + " »"));
    state.sel = save; }));
  reset();
  return out;
});

await browser.close(); srv.close();
let bad = 0;
console.log(N + " semaines générées en " + Math.round(res.ms / 1000) + " s\n");
const rules = new Set([...Object.keys(res.count), ...Object.keys(res.fails)]);
for (const r of rules) {
  const f = res.fails[r];
  console.log((f ? "ÉCHEC  " : "OK     ") + r + " (" + (res.count[r] || 0) + " vérifications réussies)");
  if (f) { bad++; f.forEach(x => console.log("         - " + x)); }
}
const er = {};
edge.forEach(e => { er[e.rule] = er[e.rule] || {n: 0, f: []}; if (e.ok) er[e.rule].n++; else er[e.rule].f.push(e.why); });
for (const [r, v] of Object.entries(er)) {
  console.log((v.f.length ? "ÉCHEC  " : "OK     ") + r + " (" + v.n + " vérifications réussies)");
  if (v.f.length) { bad++; [...new Set(v.f)].slice(0, 6).forEach(x => console.log("         - " + x)); }
}
if (jsErr.length) { bad++; console.log("ÉCHEC  erreurs JavaScript : " + [...new Set(jsErr)].join(" | ")); }
process.exit(bad ? 1 : 0);
