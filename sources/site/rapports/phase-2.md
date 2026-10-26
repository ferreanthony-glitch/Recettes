# Miam! : phase 2

## Ce que j'ai vérifié d'abord

- **Restes après validation** : non, rien ne se mettait à jour. Les restes servaient au générateur et étaient déduits de la liste de courses, mais valider une semaine ne les retirait pas. La semaine suivante, le générateur les comptait donc encore.
- **Verrouiller des repas puis relancer** : non, ça n'existait pas. Il y avait seulement « Plats que je veux », qui impose un plat sans fixer son jour.

## Ce qui a changé

### 4. Les restes se mettent à jour à la validation
- Quand tu valides, ce que les plats utilisent est retiré de « Ce qu'il me reste ». Une ligne sous le bouton dit ce qui a changé, par exemple « 500 g riz → 300 g, 3 aubergine → plus rien ».
- Un reste qui périme avant le jour où le plat est cuisiné n'est pas compté.
- La liste de courses de la semaine validée continue de déduire les restes d'avant la validation, sinon elle te ferait racheter ce que tu as déjà.
- « Mettre à jour » (revalider) ne déduit pas deux fois. Si tu as ajouté ou retiré un reste entre-temps, c'est pris en compte.
- Limite : si l'unité du reste ne se convertit pas (des « bottes » contre des grammes, par exemple), le reste n'est pas touché, et le message te demande de le retirer à la main.

### 5. Verrouiller des repas, puis relancer
- Bouton « Verrouiller des repas » au-dessus du tableau : tu touches les repas à garder (ils prennent un cadenas), puis « Terminé ».
- « Générer ma semaine » ne change plus que les autres repas.
- Un plat cuisiné en double reste pour ses deux repas : son jumeau prend un contour fin.
- « Tout déverrouiller » enlève tous les cadenas. Les verrous restent tant que tu ne les enlèves pas, même d'une semaine à l'autre.

### 6. Pourquoi ces plats ?
- Sous le tableau, une ligne par plat explique d'abord quand et comment il est cuisiné. Par exemple : « placé jeudi midi : il se congèle », « tient 3 jours au frigo », « rapide, cuisiné le jour même ».
- La ligne dit ensuite ce qui l'a fait choisir : ton reste utilisé, une note de 4 ou 5 étoiles, la limite de viande, la saison, les ingrédients partagés avec d'autres plats.
- N'apparaissent que les raisons que le générateur prend vraiment en compte. Par exemple, il ne dit pas « un de tes favoris », car les cœurs ne changent pas son choix : ils ne servent qu'à classer la liste « Plats que je veux ».
- Un repas changé à la main est marqué « choisi à la main ».

## Tests lancés

`node site/tests/moteur.mjs 1000` : **22 règles, toutes OK**. Les nouvelles :

| Règle | Vérifications |
|---|---|
| Les repas verrouillés ne bougent jamais (verrous tirés au hasard) | 971 |
| Chaque plat a son explication, et « il se congèle » apparaît dès qu'une part va au congélateur | 7 512 |
| Restes : retirés à la validation, pas de double déduction, liste de courses inchangée | 3 |

Je n'ai trouvé aucune erreur JavaScript, ni sur écran de téléphone simulé ni sur ordinateur.

## Comment tester sur ton téléphone

1. Recharge Ma semaine.
2. **Restes** : dans « Ce qu'il me reste », ajoute « 2 aubergines ». Génère jusqu'à ce qu'un plat en utilise, puis valide. La ligne sous le bouton doit dire « 2 aubergines → plus rien », et l'aubergine doit disparaître des restes.
3. **Verrou** : touche « Verrouiller des repas », puis le lundi midi et le vendredi soir, puis « Terminé ». Génère plusieurs fois : ces repas ne bougent pas.
4. **Explications** : ouvre « Pourquoi ces plats ? » sous le tableau.

## Fichiers modifiés

- `site/semaine-source.html` (les trois fonctions)
- `site/tests/moteur.mjs` (nouveaux tests)
- Commits : « les restes se mettent à jour à la validation », « verrouiller des repas avant de relancer le générateur », « une ligne d'explication pour chaque plat placé »

## Ce que je n'ai pas pu vérifier

- Je n'ai pas testé sur un vrai iPhone.
- La synchro entre appareils : les verrous et les explications restent sur l'appareil où tu les as faits. Les restes mis à jour, eux, voyagent avec la semaine validée. Je n'ai pas pu tester la synchro réelle, faute de ta clé GitHub.

## Phase 3 : ce qui est faisable sans serveur (à confirmer avant que je commence)

### 7. Coût de la semaine
Entièrement faisable. Je crée une table de prix approximatifs par ingrédient : prix au kilo, à la pièce ou au litre, ordres de grandeur de supermarché que je saisis à la main. Tu peux la modifier dans la page, et tes prix restent sur ton appareil. Ma semaine affiche le coût estimé de la semaine et de chaque plat.
Limite : ce sont des prix moyens que je fixe moi-même, pas les prix du jour de ton magasin.

### 8. Import d'une recette par lien
- **Coller un lien seul : non, pas de façon fiable.** Le navigateur interdit à une page de lire une page d'un autre site, sauf si ce site l'autorise, et les sites de recettes ne l'autorisent pas.
- **Ce que je propose : coller le texte de la recette.** Tu copies la recette depuis le site ou depuis l'app, et tu la colles dans Miam!. La page reconnaît le titre, les ingrédients (quantité, unité, aliment) et les étapes, te montre le résultat à corriger, puis l'ajoute à tes recettes. Elle estime aussi les calories avec la base d'aliments.
  - Ce qu'elle ne fait pas : la photo, le temps de conservation et le type de poste (rapide ou dimanche), que tu choisis toi-même.
  - Autre limite : la recette importée reste sur ton appareil. Pour qu'elle entre dans le recueil publié, il faudra me la donner, ou passer par une option plus lourde.
- **Option plus lourde, possible mais pas recommandée maintenant :** utiliser ta clé GitHub pour qu'un petit robot GitHub lise le lien et range la recette dans le dépôt. Ça marche sans serveur à toi. En revanche, c'est plus long à mettre en place, ça casse dès qu'un site change sa présentation, et la recette importée serait publique, car le dépôt l'est.
