// Tests des magasins (Miam!) : le plus proche par enseigne (OpenStreetMap simulé) et la comparaison des prix relevés.
// Lance : node site/tests/magasins.mjs  (Playwright + Chromium requis, comme moteur.mjs)
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
const page = await browser.newPage({viewport: {width: 390, height: 844}});
const jsErr = [];
page.on("pageerror", e => jsErr.push(e.message));
const fails = {}, count = {};
const check = (rule, cond, why) => cond ? count[rule] = (count[rule] || 0) + 1 : (fails[rule] = fails[rule] || []).push(String(why));
const base = "http://127.0.0.1:" + srv.address().port;

// 1. Profil : code postal → magasin le plus proche de chaque enseigne (réponses des deux services simulées)
const AT = [48.8386, 2.5222];
await page.route("https://data.geopf.fr/**", r => r.fulfill({status: 503, body: ""}));   // service principal en panne : l'adresse de secours prend le relais
await page.route("https://api-adresse.data.gouv.fr/**", r => r.fulfill({json: {features: [{geometry: {coordinates: [AT[1], AT[0]]}, properties: {city: "Bry-sur-Marne"}}]}}));
await page.route("https://overpass-api.de/**", r => r.fulfill({json: {elements: [
  {type: "node", lat: 48.85, lon: 2.55, tags: {name: "Lidl", brand: "Lidl", "addr:street": "rue de Bernau", "addr:city": "Champigny-sur-Marne"}},
  {type: "node", lat: 48.80, lon: 2.60, tags: {name: "Lidl", brand: "Lidl"}},
  {type: "way", center: {lat: 48.845, lon: 2.53}, tags: {name: "Carrefour Market", "addr:city": "Bry-sur-Marne"}},
  {type: "node", lat: 48.83, lon: 2.51, tags: {name: "E.Leclerc", brand: "E.Leclerc"}},
  {type: "node", lat: 48.84, lon: 2.52, tags: {name: "Franprix"}}]}}));
await page.goto(base + "/compte.html");
check("prix relevés affichés sans recherche", /Carrefour/.test(await page.textContent("#mg-list")) && /prix relevés le/.test(await page.textContent("#mg-list")), await page.textContent("#mg-list"));
await page.fill("#cp", "943");
await page.click("#cp-go");
check("code postal invalide refusé", /5 chiffres/.test(await page.textContent("#mg-st")), await page.textContent("#mg-st"));
await page.fill("#cp", "94360");
await page.click("#cp-go");
await page.waitForFunction(() => /Bry-sur-Marne/.test(document.getElementById("mg-st").textContent));
const cards = await page.$$eval("#mg-list .mg", a => a.map(x => x.innerText));
check("une ligne par enseigne", cards.length === 7, cards.length);
const lidl = cards.find(t => /^Lidl/.test(t)) || "";
check("le plus proche gardé", /rue de Bernau/.test(lidl) && /km/.test(lidl), lidl);
check("enseigne absente signalée", /Aucun magasin trouvé/.test(cards.find(t => /^Aldi/.test(t)) || ""), cards.join(" | "));
check("enseigne hors liste ignorée", !cards.some(t => /Franprix/.test(t)), "Franprix");
check("sans prix : dit clairement", /Pas encore de prix/.test(cards.find(t => /^E\.Leclerc/.test(t)) || ""), cards.join(" | "));
check("Carrefour : prix relevés", /prix relevés le/.test(cards.find(t => /^Carrefour/.test(t)) || ""), cards.join(" | "));
check("crédits OpenStreetMap", await page.isVisible(".mg-osm"), "absents");
const saved = await page.evaluate(() => JSON.parse(localStorage.getItem("recettes-magasins")));
check("gardé sur l'appareil", saved.cp === "94360" && saved.near.length === 7, JSON.stringify(saved).slice(0, 120));
await page.reload();
check("retrouvé au rechargement", (await page.inputValue("#cp")) === "94360" && (await page.$$("#mg-list .mg")).length === 7, "perdu");
check("téléphone : pas de défilement horizontal", await page.evaluate(() => document.documentElement.scrollWidth <= 390), "déborde");

// 2. Mes courses : comparaison seulement entre magasins relevés, sur le même panier
await page.goto(base + "/semaine.html");
const r = await page.evaluate(() => {
  const out = {};
  out.one = compareStores() === null && document.getElementById("cmp-msg").hidden;
  const items = buildList(), keys = Object.keys(PRIX);
  // Magasin fictif de test : la moitié des articles de Carrefour, au double du prix
  const half = Object.fromEntries(keys.filter((k, i) => i % 2 === 0).map(k => [k, {...PRIX[k], e: PRIX[k].e * 2}]));
  MAGS.push({id: "test", e: "Test", n: "Magasin test", a: "", src: "ticket de caisse", date: "2026-10-27", prix: half});
  const c = compareStores(items);
  const todo = items.filter(it => it.u !== "pl" && !it.enough && it.q > 1e-9);
  const common = todo.filter(it => MAGS.every(m => { const x = priceItem(it, m.prix); return x && !x.miss; }));
  out.n = c.n === common.length && c.of === todo.length && c.n > 0 && c.n < c.of;
  const sum = P => Math.round(common.reduce((a, it) => a + priceItem(it, P).cost, 0) * 100) / 100;
  out.tot = c.rows.find(x => x.m.id === "test").cost === sum(half) && c.rows.find(x => x.m.id === MAGS[0].id).cost === sum(PRIX);
  out.best = c.best && c.best.id === MAGS[0].id;
  out.noBorrow = todo.filter(it => !half[stem(it.name)]).every(it => priceItem(it, half).miss || !priceItem(it, half));
  renderList();
  const t = document.getElementById("cmp-msg");
  out.shown = !t.hidden && /Comparer les magasins/.test(t.textContent) && /ticket du/.test(t.textContent) && /Le moins cher sur ce panier : Carrefour/.test(t.textContent);
  out.txt = t.textContent;
  out.ref = costOf().cost > 0;   // le coût de la semaine reste celui du magasin de référence
  MAGS.pop(); renderList();
  out.gone = document.getElementById("cmp-msg").hidden;
  return out;
});
check("un seul magasin : pas de comparaison", r.one, "affichée");
check("panier commun", r.n, r.txt);
check("totaux du panier commun", r.tot, r.txt);
check("moins cher désigné", r.best, r.txt);
check("aucun prix emprunté à un autre magasin", r.noBorrow, "prix emprunté");
check("affiché dans Mes courses", r.shown, r.txt);
check("coût de référence intact", r.ref, "coût");
check("magasin retiré : comparaison masquée", r.gone, "toujours là");

await browser.close(); srv.close();
let bad = 0;
for (const [rule, n] of Object.entries(count)) if (!fails[rule]) console.log("OK     " + rule + " (" + n + ")");
for (const [rule, why] of Object.entries(fails)) { bad++; console.log("ÉCHEC  " + rule + "\n         " + why.join("\n         ")); }
if (jsErr.length) { bad++; console.log("ERREURS JS : " + [...new Set(jsErr)].join(" | ")); }
process.exit(bad ? 1 : 0);
