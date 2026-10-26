# Miam! : phase 1

## Sauvegarde

Avant de commencer, j'ai sauvegardé la version de la fin de la phase 0 à deux endroits :
- **Le site publié** : la branche `sauvegarde-avant-phase-1` du dépôt GitHub. Elle permet de revenir en arrière d'un seul geste.
- **Les sources** (fiches, générateur, outils) : l'archive `/mnt/project-files/sauvegardes/avant-phase-1-2026-10-17.tar.gz`.

## Ce qui a changé

Ma semaine a maintenant 5 onglets : Semaine, Aujourd'hui, Dimanche, Courses, Recettes.

### 1. Onglet « Dimanche » : le déroulé de la séance

- Il part de la semaine validée, ou des plats affichés tant que la semaine n'est pas validée.
- Les étapes sont rangées dans le temps et datées d'après ton heure de départ (9 h 30 par défaut, modifiable).
- Les tâches communes sont regroupées :
  - tous les légumes sont lavés et épluchés en une fois, au début ;
  - chaque féculent cuit dans une seule casserole pour tous les plats (le riz complet du dahl et celui du poulet ensemble, par exemple) ;
  - les œufs durs cuisent aussi tous ensemble.
- Le four et les plaques travaillent en parallèle : 4 plaques, et 2 plats à la fois dans le four s'ils cuisent à 20 °C près. Le préchauffage est lancé à l'avance. Pendant qu'un plat mijote ou cuit au four, la découpe du plat suivant continue.
- Le plat du dimanche midi passe en premier pour être prêt à l'heure du déjeuner. Si ce n'est pas possible, la page te prévient.
- La page affiche la durée totale estimée et le temps de travail actif. Une alerte apparaît au-delà de 3 h.
- Chaque étape se coche. Les coches restent sur le téléphone et repartent de zéro quand la semaine change.
- **Nouveau format de données** : les durées par étape sont dans un fichier à part, `site/seance.json`. Les fiches ne changent pas. Un plat sans durées détaillées est quand même planifié, avec une estimation globale.
- **Durées à relire** : tout est dans [estimations-seance.md](estimations-seance.md). Ce sont mes estimations, pas celles des livres.

### 2. Onglet « Aujourd'hui »

- Il affiche les repas du midi et du soir. Pour chacun, il dit s'il faut réchauffer (part du frigo, ou du congélateur sortie la veille) ou cuisiner, avec la consigne de réchauffage tirée de la fiche.
- Un encadré « Pour demain » dit ce qu'il faut sortir du congélateur ce soir.
- Le dimanche, l'onglet liste ce qu'il faut congeler en fin de séance et propose un bouton vers le déroulé.
- Il indique aussi le petit-déjeuner du jour. Des flèches permettent de voir la veille et le lendemain.
- **Le jour de la semaine** : il est calculé à partir de la date de validation. Une semaine validée un samedi commence le lendemain, et une semaine validée un dimanche commence le jour même. Si le calcul ne tombe pas juste, un menu en bas de l'onglet permet de choisir le dimanche de départ. Les anciennes validations restent lisibles.

### 3. Échanger deux repas en deux touchers

- Il y a un nouveau bouton « Échanger deux repas » au-dessus du tableau. Tu touches un repas, puis l'autre.
- Après le premier toucher, les cases hachurées en rouge sont celles où l'échange enfreindrait une règle : un plat qui ne tient pas jusque-là, ou une soupe à midi.
- Après l'échange, un message dit si une règle est enfreinte et si une part doit aller au congélateur. Un bouton « Annuler l'échange » est proposé.
- Le glisser-déposer marche toujours et affiche le même message.

## Ce que montrent les estimations

Sur 60 semaines générées au hasard, une séance de 6 plats dure **4 h 25 en moyenne** (de 3 h 37 à 5 h 11). La découpe occupe presque tout ce temps. On dépasse donc les 3 h visées. Il y a deux possibilités :
- mes durées de découpe sont trop prudentes, et ta relecture le dira ;
- ou 6 plats par dimanche, c'est trop pour 3 h, et il faudrait par exemple remplacer un poste par un plat rapide en semaine.

## Tests lancés

`node site/tests/moteur.mjs 1000` : 1000 semaines générées au hasard, plus 200 séances planifiées.

| Règle | Résultat |
|---|---|
| Règles de la phase 0 (conservation, congélation, viande, aliments chers, soupes, allergènes, cas limites) | OK |
| Séance : tous les plats du dimanche présents, toutes les étapes placées | OK (200 séances) |
| Séance : l'ordre de chaque recette est respecté | OK (16 377 vérifications) |
| Séance : jamais deux tâches actives en même temps pour une seule personne | OK (8 007) |
| Séance : 4 plaques au plus, four préchauffé avant chaque enfournement | OK |
| Séance : deux plats dans le four à des températures compatibles | **échouait** (une quiche à 160 °C avec un parmentier à 200 °C), **corrigé** |
| Échange : l'alerte apparaît exactement quand une règle est enfreinte | OK (400) |
| Échange en deux touchers sur la vraie page, avec l'annulation | OK |
| Aujourd'hui : dimanche de départ déduit de la date de validation | OK |
| Aucune erreur JavaScript, sur un écran de 360 px et sur ordinateur | OK |

## Comment tester sur ton téléphone

1. Ouvre Ma semaine et recharge la page en la tirant vers le bas. Si les onglets ne s'affichent pas bien, ferme l'app puis rouvre-la.
2. Valide ta semaine, puis ouvre **Dimanche**. Change l'heure de départ, coche une étape, et regarde si l'ordre te semble faisable.
3. Ouvre **Aujourd'hui** (aujourd'hui, la semaine commence demain). Touche › pour voir lundi, mercredi et jeudi : le jeudi doit annoncer une part sortie du congélateur.
4. Dans **Semaine**, touche « Échanger deux repas », puis le lundi midi : les soirs de soupe se hachurent. Touche le mardi midi pour échanger, puis « Annuler l'échange ».

## Fichiers modifiés

- `site/semaine-source.html` (les trois fonctions)
- `site/seance.json` (nouveau : durées par étape de 50 plats)
- `site/build.py` (charge seance.json, et onglets plus serrés sur petit écran)
- `site/tests/moteur.mjs` (tests de la phase 1)
- Rapports : `site/rapports/phase-1.md`, `site/rapports/estimations-seance.md`
- Commits : « onglet Dimanche », « onglet Aujourd'hui », « échanger deux repas en deux touchers », « Tests », puis la correction du four.

## Ce que je n'ai pas pu vérifier

- **Pas de test sur un vrai téléphone** : j'ai simulé un écran tactile de 360 px dans Chromium. Safari sur iPhone peut se comporter un peu autrement, surtout pour le toucher et le champ de l'heure.
- **Durées réelles** : je ne peux pas savoir combien de temps tu mets vraiment. Les durées restent des estimations tant que tu ne les as pas relues.
- **Un seul cuisinier** : le planificateur suppose une seule personne. À deux en cuisine, la séance serait plus courte, mais ce cas n'est pas prévu.
- **Changement de jour** : la vue Aujourd'hui se met à jour à l'ouverture de l'onglet. Si la page reste ouverte toute la nuit, il faut la recharger.
