# Prix relevés

- `magasins.tsv` : un magasin par ligne (id, enseigne, nom, adresse, source, fichier de prix, date du relevé).
  Source : « drive en ligne » (relevé sur le site ou le connecteur de l'enseigne) ou « ticket de caisse ».
- Chaque fichier de prix a les colonnes : cle, produit, ean, quantite, unite, prix, note.
  `cle` = l'article de la liste de courses réduit par `stem()` (sans accents, sans pluriel). L'EAN peut rester vide pour un ticket.
- Le premier magasin sert de référence pour le coût de la semaine ; tous ceux qui ont des prix entrent dans la comparaison de Mes courses.
- Jamais de prix estimé ou recopié d'un autre magasin : un article sans relevé reste « sans prix ».

## Relevé hebdomadaire Carrefour (tâche planifiée, samedi matin)

1. Pour chaque ligne de `releve-brut.tsv`, appeler `search_products` (magasin `0078-150-1375`, mode DRIVE) avec le nom du produit.
   N'utiliser ni `search_multiple_products` (il écrit dans le panier) ni aucun outil de panier ou de commande.
2. Si le même EAN est trouvé, mettre à jour son prix. Garder `price`, le prix normal, et non `discounted_price` : une promotion passagère n'est pas le prix habituel.
3. Si l'EAN a disparu, chercher l'équivalent le plus proche (même type, même format si possible) et le noter dans la colonne note.
   S'il n'y en a pas, supprimer la ligne : l'article redevient « sans prix ». Ne jamais garder un ancien prix en le présentant comme actuel.
4. Mettre la date du jour dans `magasins.tsv` (ligne carrefour-noisy), puis lancer le build et toutes les suites de tests.
5. Ouvrir la PR, puis donner à Antho, en quelques lignes : le nombre de prix changés, les plus fortes hausses et baisses, et les produits remplacés ou retirés.

## Ticket de caisse (autres enseignes)

1. Ajouter le magasin dans `magasins.tsv`, avec la source « ticket de caisse » et la date du ticket, et créer son fichier, par exemple `ticket-lidl-champigny.tsv`.
2. Ne recopier que les lignes lisibles, au prix payé. Le format vient de l'étiquette ou du ticket ; s'il n'est pas lisible, ne pas mettre la ligne.
3. Utiliser une `cle` identique à celle de `releve-brut.tsv` pour le même article, sinon la comparaison ne le retrouve pas.
