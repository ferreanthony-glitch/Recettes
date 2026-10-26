# Miam! : phase 0, sécurité du générateur

## Comment le code est organisé

1. Le dépôt GitHub ne contient que le site déjà fabriqué. Les sources sont dans le dossier du projet : `recettes/` (une fiche .md par recette) et `site/` (les outils de fabrication).
2. `site/build.py` transforme les fiches en pages : le Recueil (`index.html`, `r/*.html`), le Guide et le Profil. Il calcule aussi les calories grâce à `site/nutrition.py` et `site/aliments.csv`.
3. Ma semaine tient dans un seul fichier, `site/semaine-source.html`. On y trouve les plats du générateur avec leurs quantités, leur conservation (frigo, congélation) et leurs recettes, puis le générateur lui-même, le tableau, la liste de courses et l'onglet Recettes.
4. Attention : le générateur ne lit pas les fiches. Ses 70 plats sont recopiés dans ce fichier, et les 79 fiches existent à part. Une fiche modifiée ne change donc pas le générateur toute seule.
5. Le stockage local se fait dans le navigateur. La clé `semaine-lasseche-1012-v3` garde la semaine, la validation, les cases cochées, les restes, les réglages et les favorites. Les notes, les favoris et le profil ont chacun leur propre clé.
6. La synchro passe par un fichier `semaine.json` placé sur une branche « donnees » du dépôt, avec une clé GitHub collée une fois par appareil. Le profil n'est jamais synchronisé. Dans la page Claude, une petite base de données joue ce rôle.
7. Ce qui n'existait pas : aucun test automatique, et aucune durée par étape dans les fiches (il n'y a qu'un temps total).

## Ce que les tests ont trouvé et ce que j'ai corrigé

Les tirages au hasard passaient déjà tous. Les cas limites construits à la main ont révélé 3 défauts :

| Test qui échouait | Effet pour toi | Correction |
|---|---|---|
| Poste bloqué | Quand tes aliments à éviter ne laissaient aucun plat pour un poste, le générateur gardait le plat déjà en place, même s'il ne tenait pas jusqu'au jour prévu (par exemple des roulés d'aubergine le vendredi et le samedi). | Le plat gardé doit maintenant tenir jusqu'au jour prévu. Sinon, le générateur en prend un qui tient et te le signale. |
| Plat cher imposé | Le veau ne pouvait aller que sur le cheat meal, donc un aliment cher n'y servait qu'un seul repas. | Le veau peut maintenant être cuisiné le dimanche, sur deux repas. Le générateur ne tire plus jamais un plat cher sur un repas seul. Si tu l'imposes toi-même, il le place quand même. |
| Plats cuisinés le jour même | Le vendredi soir et le cheat meal sont cuisinés le jour même. Pourtant, le générateur les traitait comme s'ils avaient été cuits le dimanche : les crevettes étaient écartées du vendredi, et 5 plats gourmands étaient marqués « à congeler » le samedi soir. | La conservation ne compte plus que pour les plats cuits le dimanche. |

Les anciennes données restent lisibles, car aucun format n'a changé.

## Tests lancés

`node site/tests/moteur.mjs 1000` : 1000 semaines générées en 4 min, avec un nombre de repas avec viande, des aliments à éviter, des plats imposés, un profil (allergène, végétarien, pescétarien, flexitarien) et une part de saison tirés au hasard. **Toutes les règles passent.**

| Règle | Vérifications |
|---|---|
| Jamais au-delà de la conservation au frigo | 12 000 |
| Au-delà du frigo, la part part au congélateur | 12 000 |
| Plafond de repas avec viande | 1 000 |
| Aliments chers sur des plats doublés, 2 repas au plus | 150 |
| Soupes le soir seulement | 14 000 |
| Allergènes du profil et aliments à éviter | 6 806 |
| Cas limites : poste bloqué, plat cher imposé, plats du jour même | 67 |
| Erreurs JavaScript sur la page | aucune |

## Comment tester sur ton téléphone

1. Ouvre Ma semaine et recharge la page une fois, en la tirant vers le bas.
2. Touche « Générer une semaine » plusieurs fois. Aucun plat ne doit être marqué en rouge « trop loin du dimanche ».
3. Mets « Crevettes coco, courgette » dans le vendredi soir : la case ne doit pas virer au rouge.
4. Impose le veau dans « Plats que je veux », puis génère : il doit tomber sur deux repas.

## Fichiers modifiés

- `site/semaine-source.html` (le générateur)
- `site/tests/moteur.mjs` (nouveau ; copié dans le dépôt sous `tests/`)
- Commit : « Générateur : tests automatiques et corrections des règles de conservation et d'aliments chers »

## Ce que je n'ai pas pu vérifier

- Je n'ai pas testé sur un vrai téléphone. Les tests tournent dans un navigateur Chromium sans écran.
- Le contrôle des allergènes s'appuie sur les noms d'ingrédients. Un allergène caché dans un produit transformé (une sauce, un bouillon cube) ne serait pas détecté.
- Il y a peu de plats chers (crevettes et veau), donc cette règle n'a été vérifiée que 150 fois.
