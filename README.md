# Miam!

Recueil de recettes et planificateur de repas de la semaine (site statique, GitHub Pages).

- À la racine : le site fabriqué (ne pas modifier à la main, il est régénéré).
- `sources/` : ce qui sert à le fabriquer.
  - `sources/recettes/` : une fiche Markdown par recette, la référence pour les ingrédients, les étapes et la conservation.
  - `sources/site/build.py` : fabrique le site (`pip install markdown`, puis `python3 build.py` depuis le dossier du projet).
  - `sources/site/semaine-source.html` : la page Ma semaine (générateur, liste de courses, séance du dimanche).
  - `sources/site/aliments.csv` : valeurs nutritionnelles et poids d'une pièce, par aliment.
  - `sources/site/seance.json` : tâches et durées de la séance de cuisine du dimanche.
- `tests/` : tests automatiques (Node + Playwright) : `node tests/moteur.mjs` (générateur, séance) et `node tests/courses.mjs` (liste de courses, données des plats).
