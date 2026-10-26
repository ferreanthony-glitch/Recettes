"""30 recettes créées par Claude (17/10/2026), marquées « * ». Écrit les fiches et les données de Ma semaine (R, Q, PLACARD, SLUG, KEEP, RECIPES)."""
import json, sys

SRC = ("Recette créée par Claude (17/10/2026), pas tirée d'un livre ni d'un site. Quantités calées sur le livret "
       "(moitié de l'assiette en légumes, 40 g de féculent cru par personne, gras limité). Non testée en cuisine : temps et assaisonnement à ajuster.")
FL, VI, PO, CR, FR, BO, EP, CO = "Fruits et légumes", "Boucherie / volaille", "Poissonnerie", "Crèmerie", "Frais", "Boulangerie", "Épicerie", "Conserves"
PL = "Placard"
SP = ("Sel, poivre", "—", PL)

D = [
 # ---------- À préparer le dimanche ----------
 dict(id="c_poulcar", slug="poulet-carottes-cumin-boulgour", n="Poulet aux carottes et cumin, boulgour", v=1, kind="r", keep_js=[3, 1],
  t="40 min, dont 15 min actives", cat="plat complet (viande + légume + féculent)", allerg="gluten (boulgour)",
  i=["poulet", "carottes", "oignon", "boulgour", "persil"],
  ing=[("Filets de poulet, en dés", "300 g (150 g par personne)", VI), ("Carottes", "4 (400 g)", FL), ("Oignon", "1", FL),
       ("Ail", "1 gousse", FL), ("Boulgour (cru)", "80 g (40 g par personne)", EP), ("Huile d'olive", "2 c. à café", PL),
       ("Cumin", "1 c. à café", PL), ("Paprika", "½ c. à café", PL), ("Jus de citron", "1 c. à soupe", FL),
       ("Persil frais", "2 c. à soupe, haché", FL), ("Bouillon de légumes", "20 cl", PL), SP],
  steps=["Éplucher les carottes et les couper en rondelles fines. Émincer l'oignon et l'ail.",
         "Dans une sauteuse, faire dorer le poulet 4 minutes dans l'huile avec le cumin et le paprika. Réserver.",
         "Dans la même sauteuse, faire revenir l'oignon, l'ail et les carottes 5 minutes.",
         "Remettre le poulet, verser le bouillon, couvrir et cuire 15 minutes à feu doux.",
         "Pendant ce temps, cuire le boulgour 10 minutes dans l'eau bouillante salée et l'égoutter.",
         "Finir avec le jus de citron et le persil, saler, poivrer, servir sur le boulgour."],
  sunday="Tout se fait le dimanche, poulet et boulgour dans des boîtes séparées ou ensemble.",
  keep="3 jours au réfrigérateur ; se congèle bien (2 mois).", heat="Micro-ondes 2 min 30 couvert, avec une cuillère d'eau sur le boulgour.",
  bal=["200 g de carottes par personne : la moitié de l'assiette en légumes.", "150 g de poulet par personne (le livret en compte 250 g pour une portion pleine).", "40 g de boulgour cru par personne."],
  Q=[["filets de poulet", 300, "g", "VI"], ["carotte", 4, "pc", "FL"], ["oignon", 1, "pc", "FL"], ["ail", 1, "gousse", "FL"], ["boulgour", 80, "g", "EP"], ["persil", 0.5, "botte", "FL"]],
  P=["cumin", "paprika", "citron", "bouillon de légumes (cube)", "huile d'olive"]),

 dict(id="c_dindecf", slug="curry-dinde-chou-fleur-riz", n="Curry de dinde au chou-fleur et riz", v=1, kind="r", keep_js=[3, 1],
  t="35 min, dont 15 min actives", cat="plat complet (viande + légume + féculent)", allerg="lait (yaourt)",
  i=["dinde", "chou-fleur", "oignon", "yaourt", "riz complet"],
  ing=[("Escalopes de dinde, en dés", "300 g (150 g par personne)", VI), ("Chou-fleur, en petits bouquets", "400 g (½ chou-fleur)", FL),
       ("Oignon", "1", FL), ("Ail", "1 gousse", FL), ("Gingembre frais", "1 petit morceau", FL), ("Curry", "2 c. à café", PL),
       ("Tomates concassées en conserve", "200 g", CO), ("Yaourt nature", "1 (125 g)", CR), ("Huile d'olive", "2 c. à café", PL),
       ("Riz complet (cru)", "80 g (40 g par personne)", EP), ("Coriandre fraîche", "quelques brins", FL), SP],
  steps=["Mettre le riz complet à cuire.", "Faire revenir l'oignon, l'ail et le gingembre hachés 3 minutes dans l'huile, ajouter le curry et mélanger 1 minute.",
         "Ajouter la dinde et la faire dorer 3 minutes.", "Ajouter le chou-fleur et les tomates, couvrir et cuire 15 minutes, jusqu'à ce que le chou-fleur soit tendre.",
         "Hors du feu, incorporer le yaourt. Saler, poivrer, parsemer de coriandre et servir avec le riz."],
  sunday="Se fait le dimanche. Ajouter le yaourt hors du feu pour qu'il ne tranche pas, même au réchauffage.",
  keep="3 jours au réfrigérateur ; se congèle bien (2 mois), riz compris.", heat="Micro-ondes 2 min 30 couvert, ou casserole à feu doux sans faire bouillir.",
  bal=["200 g de chou-fleur par personne plus la tomate : la moitié de l'assiette en légumes.", "150 g de dinde par personne, viande maigre.", "40 g de riz complet cru par personne."],
  Q=[["escalopes de dinde", 300, "g", "VI"], ["chou-fleur", 0.5, "pc", "FL"], ["oignon", 1, "pc", "FL"], ["ail", 1, "gousse", "FL"], ["gingembre frais (morceau)", 1, "pc", "FL"],
     ["tomates concassées", 200, "g", "CO"], ["yaourts nature", 1, "pc", "CR"], ["riz complet", 80, "g", "EP"], ["coriandre", 0.5, "botte", "FL"]],
  P=["curry", "huile d'olive"]),

 dict(id="c_parmpd", slug="parmentier-boeuf-patate-douce-epinards", n="Parmentier de bœuf à la patate douce et aux épinards", v=1, kind="r", keep_js=[3, 1],
  t="50 min, dont 20 min actives (20 min de four)", cat="plat complet au four (viande + légume + féculent)", allerg="lait",
  i=["bœuf haché", "patate douce", "épinards", "oignon", "emmental"],
  ing=[("Bœuf haché 5 %", "250 g (125 g par personne)", VI), ("Patates douces", "300 g (150 g par personne)", FL),
       ("Épinards frais (ou surgelés)", "300 g", FL), ("Oignon", "1", FL), ("Ail", "1 gousse", FL), ("Concentré de tomate", "1 c. à soupe", EP),
       ("Lait demi-écrémé", "5 cl", CR), ("Emmental râpé", "20 g", CR), ("Huile d'olive", "1 c. à café", PL), ("Noix de muscade", "1 pincée", PL), SP],
  steps=["Éplucher les patates douces, les couper en cubes et les cuire 15 minutes à l'eau. Les écraser avec le lait et la muscade.",
         "Préchauffer le four à 200 °C. Faire revenir l'oignon et l'ail dans l'huile, ajouter le bœuf et le concentré de tomate, cuire 5 minutes.",
         "Ajouter les épinards et les laisser tomber 3 minutes. Saler, poivrer.",
         "Étaler la viande aux épinards dans un plat, couvrir de purée, parsemer d'emmental.", "Enfourner 20 minutes, jusqu'à ce que le dessus dore."],
  sunday="Se monte et se cuit le dimanche, en un grand plat pour deux repas ou en deux plats dont un va au congélateur.",
  keep="3 jours au réfrigérateur ; se congèle très bien (3 mois).", heat="Four 15 min à 180 °C, ou micro-ondes 3 min.",
  bal=["150 g d'épinards par personne, plus la tomate : compléter avec une salade pour la moitié de l'assiette.", "125 g de bœuf haché 5 % par personne.", "150 g de patate douce par personne, la portion de féculent du livret."],
  Q=[["bœuf haché 5 %", 250, "g", "VI"], ["patate douce", 300, "g", "FL"], ["épinards frais", 300, "g", "FL"], ["oignon", 1, "pc", "FL"], ["ail", 1, "gousse", "FL"],
     ["lait demi-écrémé", 50, "ml", "CR"], ["emmental râpé", 20, "g", "CR"]],
  P=["concentré de tomate", "noix de muscade", "huile d'olive"]),

 dict(id="c_lentcar", slug="lentilles-vertes-mijotees-carottes-oeuf", n="Lentilles vertes mijotées aux carottes et œuf mollet", v=0, kind="r", keep_js=[4, 1],
  t="45 min, dont 10 min actives (35 min de mijotage)", cat="mijoté végétarien (légumineuse + légume + œuf)", allerg="œuf",
  i=["lentilles", "carottes", "oignon", "œufs"],
  ing=[("Lentilles vertes (crues)", "120 g (60 g par personne)", EP), ("Carottes", "3 (300 g)", FL), ("Oignon", "1", FL), ("Ail", "1 gousse", FL),
       ("Thym et laurier", "1 brin et 1 feuille", PL), ("Moutarde", "1 c. à café", PL), ("Vinaigre", "1 c. à soupe", PL), ("Huile d'olive", "2 c. à café", PL),
       ("Œufs, mollets, pour servir", "4 (2 par personne)", CR), ("Persil frais", "1 c. à soupe", FL), SP],
  steps=["Rincer les lentilles. Couper les carottes en rondelles, émincer l'oignon.",
         "Faire revenir l'oignon et l'ail 3 minutes dans 1 c. à café d'huile, ajouter les carottes, les lentilles, le thym et le laurier.",
         "Couvrir d'eau froide (2 fois leur volume), porter à ébullition et laisser mijoter 30 à 35 minutes, sans saler.",
         "Égoutter si besoin, puis assaisonner avec la moutarde, le vinaigre, le reste d'huile, sel et poivre.",
         "Au moment de servir, cuire les œufs 6 minutes, les écaler et les poser sur les lentilles avec le persil."],
  sunday="Les lentilles se font le dimanche et se mangent chaudes ou tièdes. Les œufs se cuisent le jour même (6 min) ou durs le dimanche.",
  keep="4 jours au réfrigérateur ; les lentilles se congèlent bien (3 mois), sans les œufs.", heat="Micro-ondes 2 min, ou à manger tiède en salade.",
  bal=["Lentilles et œufs se partagent la portion de protéines ; les lentilles comptent aussi comme féculent (200 g cuites par personne ≈ la portion du livret).",
       "150 g de carottes par personne : ajouter une salade verte pour la moitié de l'assiette."],
  Q=[["lentilles vertes", 120, "g", "EP"], ["carotte", 3, "pc", "FL"], ["oignon", 1, "pc", "FL"], ["ail", 1, "gousse", "FL"], ["œufs", 4, "pc", "CR"], ["persil", 0.5, "botte", "FL"]],
  P=["thym", "laurier", "moutarde", "vinaigre", "huile d'olive"]),

 dict(id="c_poulcit", slug="poulet-citron-courgettes-riz", n="Poulet citron, courgettes et riz", v=1, kind="r", keep_js=[3, 1],
  t="30 min, dont 15 min actives", cat="plat complet (viande + légume + féculent)", allerg="aucun courant",
  i=["poulet", "courgette", "citron", "riz complet"],
  ing=[("Filets de poulet, en lanières", "300 g (150 g par personne)", VI), ("Courgettes", "2 (400 g)", FL), ("Oignon", "1", FL), ("Ail", "1 gousse", FL),
       ("Citron (jus et zeste)", "1", FL), ("Herbes de Provence", "1 c. à café", PL), ("Huile d'olive", "2 c. à café", PL),
       ("Riz complet (cru)", "80 g (40 g par personne)", EP), SP],
  steps=["Cuire le riz complet.", "Faire dorer le poulet 5 minutes dans l'huile avec les herbes. Réserver.",
         "Faire revenir l'oignon et l'ail, puis les courgettes en demi-rondelles 8 minutes à feu vif.",
         "Remettre le poulet, ajouter le zeste et le jus du citron, cuire encore 2 minutes. Saler, poivrer, servir avec le riz."],
  sunday="Se fait le dimanche ; garder un peu de jus de citron à ajouter au moment de manger pour réveiller le plat.",
  keep="3 jours au réfrigérateur ; se congèle (2 mois), les courgettes deviennent plus molles.", heat="Micro-ondes 2 min couvert.",
  bal=["200 g de courgettes par personne : la moitié de l'assiette.", "150 g de poulet par personne.", "40 g de riz complet cru par personne."],
  Q=[["filets de poulet", 300, "g", "VI"], ["courgette", 2, "pc", "FL"], ["oignon", 1, "pc", "FL"], ["ail", 1, "gousse", "FL"], ["citron", 1, "pc", "FL"], ["riz complet", 80, "g", "EP"]],
  P=["herbes de Provence", "huile d'olive"]),

 dict(id="c_boulpp", slug="boulettes-boeuf-petits-pois-carottes", n="Boulettes de bœuf aux petits pois et carottes", v=1, kind="r", keep_js=[3, 1],
  t="40 min, dont 20 min actives", cat="mijoté (viande + légumes + féculent)", allerg="œuf, gluten (chapelure)",
  i=["bœuf haché", "petits pois", "carottes", "pommes de terre"],
  ing=[("Bœuf haché 5 %", "250 g (125 g par personne)", VI), ("Œuf", "1", CR), ("Chapelure", "1 c. à soupe", EP), ("Petits pois surgelés", "200 g", FR),
       ("Carottes", "2 (200 g)", FL), ("Oignon", "1", FL), ("Pommes de terre", "300 g (150 g par personne)", FL), ("Bouillon de légumes", "25 cl", PL),
       ("Thym", "1 c. à café", PL), ("Huile d'olive", "1 c. à café", PL), SP],
  steps=["Mélanger le bœuf, l'œuf, la chapelure, sel et poivre. Former une douzaine de boulettes.",
         "Les faire dorer 5 minutes dans l'huile dans une cocotte, puis les réserver.",
         "Faire revenir l'oignon, ajouter les carottes en rondelles et les pommes de terre en cubes, le thym et le bouillon.",
         "Couvrir et cuire 15 minutes, ajouter les petits pois et les boulettes, et poursuivre 10 minutes."],
  sunday="Se fait le dimanche dans une seule cocotte, et se garde dans son bouillon.",
  keep="3 jours au réfrigérateur ; se congèle bien (3 mois).", heat="Casserole à couvert 8 min ou micro-ondes 3 min.",
  bal=["Petits pois et carottes : 200 g de légumes par personne.", "125 g de bœuf haché 5 % par personne.", "150 g de pommes de terre par personne."],
  Q=[["bœuf haché 5 %", 250, "g", "VI"], ["œufs", 1, "pc", "CR"], ["petits pois surgelés", 200, "g", "FR"], ["carotte", 2, "pc", "FL"], ["oignon", 1, "pc", "FL"], ["pommes de terre", 300, "g", "FL"]],
  P=["chapelure", "bouillon de légumes (cube)", "thym", "huile d'olive"]),

 dict(id="c_porcmou", slug="filet-mignon-moutarde-haricots-verts", n="Filet mignon à la moutarde, haricots verts et pommes de terre", v=1, kind="r", keep_js=[3, 1],
  t="35 min, dont 15 min actives", cat="plat complet (viande + légume + féculent)", allerg="moutarde, lait",
  i=["porc", "haricots verts", "pommes de terre", "moutarde"],
  ing=[("Filet mignon de porc, en médaillons", "300 g (150 g par personne)", VI), ("Haricots verts (frais ou surgelés)", "300 g", FL),
       ("Pommes de terre", "300 g (150 g par personne)", FL), ("Échalote", "1", FL), ("Moutarde à l'ancienne", "1 c. à soupe", PL),
       ("Crème légère 15 %", "5 cl", CR), ("Huile d'olive", "1 c. à café", PL), SP],
  steps=["Cuire les pommes de terre en morceaux et les haricots verts 12 minutes à la vapeur ou à l'eau.",
         "Saisir les médaillons 3 minutes de chaque côté dans l'huile, saler, poivrer, réserver.",
         "Faire revenir l'échalote émincée, ajouter la moutarde, la crème et 3 c. à soupe d'eau, laisser épaissir 2 minutes.",
         "Remettre le porc dans la sauce 2 minutes et servir avec les légumes."],
  sunday="Se fait le dimanche ; garder la sauce avec la viande, les légumes à part.",
  keep="3 jours au réfrigérateur ; viande en sauce congelable (2 mois), haricots verts aussi.", heat="Micro-ondes 2 min, sauce couverte.",
  bal=["150 g de haricots verts par personne (le livret compte 150 g pour une portion de légumes).", "150 g de filet mignon, morceau maigre du porc.", "150 g de pommes de terre par personne."],
  Q=[["filet mignon de porc", 300, "g", "VI"], ["haricots verts", 300, "g", "FL"], ["pommes de terre", 300, "g", "FL"], ["échalote", 1, "pc", "FL"], ["crème légère", 50, "ml", "CR"]],
  P=["moutarde", "huile d'olive"]),

 dict(id="c_choubf", slug="chou-braise-boeuf-riz", n="Chou braisé au bœuf haché et riz", v=1, kind="r", keep_js=[4, 1],
  t="50 min, dont 15 min actives (35 min de mijotage)", cat="mijoté (viande + légume + féculent)", allerg="aucun courant",
  i=["chou", "bœuf haché", "carottes", "riz complet"],
  ing=[("Chou vert", "½ (500 g)", FL), ("Bœuf haché 5 %", "250 g (125 g par personne)", VI), ("Carotte", "1", FL), ("Oignon", "1", FL),
       ("Tomates concassées en conserve", "200 g", CO), ("Paprika", "1 c. à café", PL), ("Bouillon de légumes", "20 cl", PL),
       ("Huile d'olive", "1 c. à café", PL), ("Riz complet (cru)", "80 g (40 g par personne)", EP), SP],
  steps=["Émincer finement le chou, couper la carotte en dés et l'oignon.", "Faire revenir l'oignon et le bœuf 5 minutes dans l'huile avec le paprika.",
         "Ajouter le chou, la carotte, les tomates et le bouillon. Couvrir et laisser mijoter 35 minutes à feu doux.",
         "Pendant ce temps, cuire le riz. Saler, poivrer et servir."],
  sunday="Mijoté du dimanche : il est encore meilleur le lendemain.",
  keep="4 jours au réfrigérateur ; se congèle très bien (3 mois).", heat="Casserole à couvert 8 min ou micro-ondes 3 min.",
  bal=["250 g de chou par personne plus la carotte : plus que la moitié de l'assiette.", "125 g de bœuf 5 % par personne.", "40 g de riz complet cru par personne."],
  Q=[["chou vert", 0.5, "pc", "FL"], ["bœuf haché 5 %", 250, "g", "VI"], ["carotte", 1, "pc", "FL"], ["oignon", 1, "pc", "FL"], ["tomates concassées", 200, "g", "CO"], ["riz complet", 80, "g", "EP"]],
  P=["paprika", "bouillon de légumes (cube)", "huile d'olive"]),

 dict(id="c_tofubro", slug="tofu-brocoli-riz-tamari-gingembre", n="Tofu sauté au brocoli, sauce tamari-gingembre", v=0, kind="r", keep_js=[3, 0],
  t="30 min, dont 20 min actives", cat="plat végétarien (protéine végétale + légume + féculent)", allerg="soja, sésame possible selon le tamari",
  i=["tofu", "brocoli", "carottes", "gingembre", "riz complet"],
  ing=[("Tofu ferme", "400 g (200 g par personne)", FR), ("Brocoli", "1 tête (400 g)", FL), ("Carotte", "1", FL), ("Gingembre frais", "1 morceau", FL),
       ("Ail", "1 gousse", FL), ("Tamari (ou sauce soja)", "2 c. à soupe", EP), ("Miel", "1 c. à café", EP), ("Huile d'olive", "2 c. à café", PL),
       ("Riz complet (cru)", "80 g (40 g par personne)", EP)],
  steps=["Cuire le riz. Couper le tofu en cubes et le sécher dans un torchon.", "Faire dorer le tofu 8 minutes dans l'huile à feu vif, en le retournant. Réserver.",
         "Faire sauter le brocoli en petits bouquets et la carotte en bâtonnets 6 minutes avec un fond d'eau.",
         "Ajouter l'ail et le gingembre râpés, le tamari et le miel, remettre le tofu et mélanger 1 minute."],
  sunday="Se fait le dimanche. Le brocoli reste meilleur un peu croquant : arrêter la cuisson tôt.",
  keep="3 jours au réfrigérateur ; se congèle mal (le tofu devient spongieux).", heat="Poêle 4 min ou micro-ondes 2 min.",
  bal=["200 g de tofu ferme par personne (le livret en compte 250 g pour une portion).", "250 g de légumes par personne.", "40 g de riz complet cru par personne. Tamari plutôt que sauce soja, comme le livret."],
  Q=[["tofu ferme", 400, "g", "FR"], ["brocoli", 1, "pc", "FL"], ["carotte", 1, "pc", "FL"], ["gingembre frais (morceau)", 1, "pc", "FL"], ["ail", 1, "gousse", "FL"], ["riz complet", 80, "g", "EP"]],
  P=["sauce soja ou tamari", "miel", "huile d'olive"]),

 dict(id="c_quinoa", slug="salade-quinoa-pois-chiches-poivron-feta", n="Salade de quinoa, pois chiches, poivron et feta", v=0, kind="r", keep_js=[3, 0],
  t="25 min, dont 10 min actives", cat="salade complète froide (végétarien)", allerg="lait (feta)",
  i=["quinoa", "pois chiches", "poivron", "concombre", "feta"],
  ing=[("Quinoa (cru)", "80 g (40 g par personne)", EP), ("Pois chiches en conserve, égouttés", "200 g", CO), ("Poivron rouge", "1", FL),
       ("Tomates cerises", "200 g", FL), ("Oignon rouge", "½", FL), ("Feta", "60 g", CR), ("Menthe ou persil", "quelques brins", FL),
       ("Huile d'olive", "2 c. à café", PL), ("Jus de citron", "2 c. à soupe", FL), ("Cumin", "1 pincée", PL), SP],
  steps=["Rincer le quinoa et le cuire 12 minutes dans l'eau salée, l'égoutter et le laisser refroidir.",
         "Couper le poivron en dés, les tomates en deux, émincer finement l'oignon.",
         "Mélanger le quinoa, les pois chiches et les légumes. Assaisonner avec l'huile, le citron, le cumin, sel et poivre.",
         "Ajouter la feta émiettée et les herbes au moment de servir."],
  sunday="Se prépare le dimanche, assaisonnée ; la feta et les herbes s'ajoutent le jour même. Idéale pour un déjeuner à emporter.",
  keep="3 jours au réfrigérateur ; ne se congèle pas.", heat="Aucun, plat froid.",
  bal=["Pois chiches et feta se partagent la portion de protéines (végétarien).", "Poivron et tomates : 200 g de légumes par personne.", "40 g de quinoa cru par personne."],
  Q=[["quinoa", 80, "g", "EP"], ["pois chiches", 200, "g", "CO"], ["poivron rouge", 1, "pc", "FL"], ["tomates cerises", 200, "g", "FL"], ["oignon rouge", 0.5, "pc", "FL"],
     ["feta", 60, "g", "CR"], ["menthe", 0.5, "botte", "FL"], ["citron", 1, "pc", "FL"]],
  P=["cumin", "huile d'olive"]),

 dict(id="c_gratcf", slug="gratin-chou-fleur-jambon-oeufs", n="Gratin de chou-fleur, jambon et œufs", v=1, kind="r", keep_js=[3, 1],
  t="45 min, dont 15 min actives (25 min de four)", cat="plat au four (viande + légume), féculent à côté", allerg="œuf, lait, gluten (pain)",
  i=["chou-fleur", "jambon", "œufs", "fromage blanc", "emmental", "pain complet"],
  ing=[("Chou-fleur", "1 petit (600 g)", FL), ("Jambon cuit, en dés", "120 g", VI), ("Œufs", "3", CR), ("Fromage blanc 3 %", "150 g", CR),
       ("Emmental râpé", "30 g", CR), ("Noix de muscade", "1 pincée", PL), ("Pain complet, pour servir", "80 g (40 g par personne)", BO), SP],
  steps=["Cuire le chou-fleur en bouquets 10 minutes à la vapeur. Préchauffer le four à 190 °C.",
         "Battre les œufs avec le fromage blanc, la moitié de l'emmental, la muscade, sel et poivre.",
         "Mettre le chou-fleur et le jambon dans un plat, verser l'appareil, parsemer du reste d'emmental.",
         "Cuire 25 minutes jusqu'à ce que ce soit pris et doré. Servir avec le pain complet."],
  sunday="Se fait le dimanche, en même temps qu'un autre plat au four.",
  keep="3 jours au réfrigérateur ; se congèle en parts (2 mois).", heat="Four 12 min à 180 °C ou micro-ondes 2 min.",
  bal=["300 g de chou-fleur par personne : la moitié de l'assiette.", "Jambon et œufs pour la protéine.", "40 g de pain complet par personne."],
  Q=[["chou-fleur", 1, "pc", "FL"], ["jambon en dés", 120, "g", "VI"], ["œufs", 3, "pc", "CR"], ["fromage blanc", 150, "g", "CR"], ["emmental râpé", 30, "g", "CR"], ["pain complet", 80, "g", "BO"]],
  P=["noix de muscade"]),

 dict(id="c_ratoeuf", slug="ratatouille-oeufs-semoule", n="Ratatouille aux œufs et semoule", v=0, kind="r", keep_js=[4, 1],
  t="55 min, dont 20 min actives (35 min de mijotage)", cat="mijoté végétarien (légumes + œufs + féculent)", allerg="œuf, gluten (semoule)",
  i=["courgette", "aubergine", "poivron", "tomates", "œufs", "semoule"],
  ing=[("Courgette", "1", FL), ("Aubergine", "1", FL), ("Poivron rouge", "1", FL), ("Tomates", "3", FL), ("Oignon", "1", FL), ("Ail", "2 gousses", FL),
       ("Herbes de Provence", "1 c. à café", PL), ("Huile d'olive", "2 c. à café", PL), ("Œufs", "5", CR), ("Semoule complète (crue)", "80 g (40 g par personne)", EP), SP],
  steps=["Couper tous les légumes en dés. Faire revenir l'oignon et l'ail dans l'huile.",
         "Ajouter l'aubergine et le poivron 5 minutes, puis la courgette, les tomates et les herbes. Couvrir et mijoter 30 minutes.",
         "Pour servir, creuser des puits dans la ratatouille chaude, y casser les œufs, couvrir et cuire 5 à 6 minutes.",
         "Servir avec la semoule gonflée 5 minutes dans le même volume d'eau bouillante."],
  sunday="La ratatouille se fait le dimanche (elle gagne à reposer). Les œufs se cuisent dessus au moment du repas, en 6 minutes.",
  keep="4 jours au réfrigérateur ; la ratatouille se congèle très bien (3 mois).", heat="Réchauffer la ratatouille dans une poêle, puis y cuire les œufs.",
  bal=["Plus de 400 g de légumes par personne.", "2 à 3 œufs par personne : la portion de protéines du livret (3 œufs).", "40 g de semoule complète crue par personne."],
  Q=[["courgette", 1, "pc", "FL"], ["aubergine", 1, "pc", "FL"], ["poivron rouge", 1, "pc", "FL"], ["tomate", 3, "pc", "FL"], ["oignon", 1, "pc", "FL"], ["ail", 2, "gousse", "FL"],
     ["œufs", 5, "pc", "CR"], ["semoule complète", 80, "g", "EP"]],
  P=["herbes de Provence", "huile d'olive"]),

 dict(id="c_harbd", slug="haricots-blancs-tomate-dinde", n="Haricots blancs à la tomate et à la dinde", v=1, kind="r", keep_js=[4, 1],
  t="35 min, dont 15 min actives", cat="mijoté (viande + légumineuse + légume)", allerg="aucun courant",
  i=["dinde", "haricots blancs", "tomates", "carottes", "épinards"],
  ing=[("Escalopes de dinde, en dés", "250 g (125 g par personne)", VI), ("Haricots blancs en conserve, égouttés", "250 g", CO),
       ("Tomates concassées en conserve", "400 g", CO), ("Carottes", "2", FL), ("Oignon", "1", FL), ("Ail", "1 gousse", FL),
       ("Épinards frais", "100 g", FL), ("Thym et laurier", "1 brin et 1 feuille", PL), ("Paprika fumé", "½ c. à café", PL), ("Huile d'olive", "1 c. à café", PL), SP],
  steps=["Faire dorer la dinde 4 minutes dans l'huile avec le paprika, réserver.", "Faire revenir l'oignon, l'ail et les carottes en dés 5 minutes.",
         "Ajouter les tomates, le thym, le laurier et les haricots, mijoter 15 minutes à couvert.", "Remettre la dinde et les épinards 5 minutes. Saler, poivrer."],
  sunday="Mijoté du dimanche, encore meilleur le lendemain.", keep="4 jours au réfrigérateur ; se congèle très bien (3 mois).", heat="Casserole 6 min ou micro-ondes 2 min 30.",
  bal=["Les haricots blancs font le féculent (125 g égouttés par personne, environ l'équivalent de 40 g de féculent cru) et ajoutent des fibres.",
       "Tomates, carottes et épinards : 300 g de légumes par personne.", "125 g de dinde par personne."],
  Q=[["escalopes de dinde", 250, "g", "VI"], ["haricots blancs", 250, "g", "CO"], ["tomates concassées", 400, "g", "CO"], ["carotte", 2, "pc", "FL"], ["oignon", 1, "pc", "FL"],
     ["ail", 1, "gousse", "FL"], ["épinards frais", 100, "g", "FL"]],
  P=["thym", "laurier", "paprika", "huile d'olive"]),

 dict(id="c_pouepi", slug="poulet-epinards-pommes-de-terre-fromage-blanc", n="Poulet aux épinards et pommes de terre, sauce fromage blanc", v=1, kind="r", keep_js=[3, 1],
  t="35 min, dont 15 min actives", cat="plat complet (viande + légume + féculent)", allerg="lait",
  i=["poulet", "épinards", "pommes de terre", "fromage blanc", "ail"],
  ing=[("Filets de poulet", "300 g (150 g par personne)", VI), ("Épinards frais", "400 g", FL), ("Pommes de terre", "300 g (150 g par personne)", FL),
       ("Échalote", "1", FL), ("Ail", "1 gousse", FL), ("Fromage blanc 3 %", "100 g", CR), ("Moutarde", "1 c. à café", PL), ("Huile d'olive", "2 c. à café", PL), SP],
  steps=["Cuire les pommes de terre en cubes 12 minutes à l'eau.", "Faire dorer le poulet en morceaux 6 minutes dans l'huile, réserver.",
         "Faire revenir l'échalote et l'ail, ajouter les épinards et les laisser tomber 3 minutes.",
         "Hors du feu, ajouter le fromage blanc mélangé à la moutarde, le poulet et les pommes de terre. Saler, poivrer."],
  sunday="Se fait le dimanche ; le fromage blanc s'ajoute hors du feu pour garder une sauce lisse.",
  keep="3 jours au réfrigérateur ; se congèle (2 mois), la sauce peut un peu se séparer.", heat="Micro-ondes 2 min 30 à puissance moyenne.",
  bal=["200 g d'épinards par personne.", "150 g de poulet par personne, fromage blanc en plus.", "150 g de pommes de terre par personne."],
  Q=[["filets de poulet", 300, "g", "VI"], ["épinards frais", 400, "g", "FL"], ["pommes de terre", 300, "g", "FL"], ["échalote", 1, "pc", "FL"], ["ail", 1, "gousse", "FL"], ["fromage blanc", 100, "g", "CR"]],
  P=["moutarde", "huile d'olive"]),

 dict(id="c_souplen", slug="soupe-lentilles-corail-carotte-cumin", n="Soupe de lentilles corail, carotte et cumin", v=0, kind="r", keep_js=[4, 1],
  t="30 min, dont 10 min actives", cat="soupe complète du soir (légumineuse + légume)", allerg="lait (yaourt)",
  i=["lentilles", "carottes", "oignon", "yaourt"],
  ing=[("Lentilles corail (crues)", "100 g (50 g par personne)", EP), ("Carottes", "4 (400 g)", FL), ("Oignon", "1", FL), ("Ail", "1 gousse", FL),
       ("Cumin", "1 c. à café", PL), ("Bouillon de légumes", "80 cl", PL), ("Huile d'olive", "1 c. à café", PL), ("Jus de citron", "1 c. à soupe", FL),
       ("Yaourt nature, pour servir", "1 (125 g)", CR), SP],
  steps=["Faire revenir l'oignon et l'ail 3 minutes dans l'huile avec le cumin.", "Ajouter les carottes en rondelles, les lentilles rincées et le bouillon.",
         "Cuire 20 minutes, mixer, ajouter le citron. Saler, poivrer.", "Servir avec une cuillère de yaourt dans chaque bol."],
  sunday="Se fait entièrement le dimanche et se double sans effort.", keep="4 jours au réfrigérateur ; se congèle très bien (3 mois).", heat="Casserole 5 min, en ajoutant un peu d'eau si elle a épaissi.",
  bal=["Les lentilles apportent protéines et féculent ; le yaourt complète.", "200 g de carottes par personne.", "Soupe du soir uniquement, comme convenu."],
  Q=[["lentilles corail", 100, "g", "EP"], ["carotte", 4, "pc", "FL"], ["oignon", 1, "pc", "FL"], ["ail", 1, "gousse", "FL"], ["citron", 0.5, "pc", "FL"], ["yaourts nature", 1, "pc", "CR"]],
  P=["cumin", "bouillon de légumes (cube)", "huile d'olive"]),

 dict(id="c_soupbro", slug="soupe-brocoli-pois-chiches-rotis", n="Soupe de brocoli et pois chiches rôtis", v=0, kind="r", keep_js=[3, 1],
  t="35 min, dont 10 min actives", cat="soupe complète du soir (légume + légumineuse + fromage)", allerg="lait",
  i=["brocoli", "pommes de terre", "pois chiches", "cream cheese"],
  ing=[("Brocoli", "1 tête (400 g)", FL), ("Pomme de terre", "1 (150 g)", FL), ("Oignon", "½", FL), ("Bouillon de légumes", "70 cl", PL),
       ("Cream cheese (type Saint Môret)", "40 g", CR), ("Pois chiches en conserve, égouttés", "200 g", CO), ("Paprika", "1 c. à café", PL),
       ("Huile d'olive", "2 c. à café", PL), SP],
  steps=["Préchauffer le four à 200 °C. Sécher les pois chiches, les mélanger avec 1 c. à café d'huile et le paprika, les rôtir 20 minutes.",
         "Faire revenir l'oignon dans le reste d'huile, ajouter le brocoli, la pomme de terre en cubes et le bouillon. Cuire 15 minutes.",
         "Mixer avec le cream cheese. Saler, poivrer.", "Servir parsemé de pois chiches croustillants."],
  sunday="La soupe se fait le dimanche ; les pois chiches rôtis se gardent à part dans une boîte fermée pour rester croquants.",
  keep="Soupe : 3 jours au réfrigérateur, se congèle (3 mois). Pois chiches rôtis : 4 jours à température ambiante.", heat="Casserole 5 min ou micro-ondes 3 min.",
  bal=["200 g de brocoli par personne.", "Pois chiches et cream cheese pour la protéine : ajouter un œuf dur pour atteindre la portion pleine du livret.", "Soupe du soir uniquement."],
  Q=[["brocoli", 1, "pc", "FL"], ["pommes de terre", 150, "g", "FL"], ["oignon", 0.5, "pc", "FL"], ["cream cheese", 40, "g", "CR"], ["pois chiches", 200, "g", "CO"]],
  P=["bouillon de légumes (cube)", "paprika", "huile d'olive"]),

 dict(id="c_cake", slug="cake-sale-courgette-feta", n="Cake salé courgette, feta et menthe", v=0, kind="r", keep_js=[3, 1],
  t="55 min, dont 15 min actives (40 min de four)", cat="plat végétarien au four (œufs + légume + féculent)", allerg="œuf, lait, gluten",
  i=["courgette", "feta", "œufs", "farine", "menthe"],
  ing=[("Courgettes", "2 (400 g)", FL), ("Œufs", "4", CR), ("Farine", "80 g", EP), ("Levure chimique", "1 sachet", EP), ("Feta", "80 g", CR),
       ("Yaourt nature", "1 (125 g)", CR), ("Menthe fraîche", "quelques feuilles", FL), ("Huile d'olive", "1 c. à soupe", PL), SP],
  steps=["Préchauffer le four à 180 °C. Râper les courgettes, les saler et les presser dans un torchon pour enlever l'eau.",
         "Battre les œufs avec le yaourt et l'huile, ajouter la farine et la levure.", "Incorporer les courgettes, la feta émiettée et la menthe ciselée. Poivrer.",
         "Verser dans un moule à cake garni de papier cuisson et cuire 40 minutes (la lame d'un couteau doit ressortir sèche).", "Servir tiède ou froid avec une salade verte."],
  sunday="Se fait le dimanche ; se coupe en tranches pour des déjeuners froids.", keep="3 jours au réfrigérateur ; se congèle en tranches (2 mois).", heat="Bon froid ; sinon 1 min au micro-ondes.",
  bal=["2 œufs par personne plus la feta et le yaourt : protéines couvertes.", "40 g de farine par personne, la portion de féculent.", "200 g de courgettes par personne ; une salade verte à côté complète l'assiette."],
  Q=[["courgette", 2, "pc", "FL"], ["œufs", 4, "pc", "CR"], ["farine", 80, "g", "EP"], ["feta", 80, "g", "CR"], ["yaourts nature", 1, "pc", "CR"], ["menthe", 0.5, "botte", "FL"], ["salade", 1, "pc", "FL"]],
  P=["levure chimique", "huile d'olive"]),

 dict(id="c_pdfarc", slug="patates-douces-farcies-boeuf-haricots-rouges", n="Patates douces farcies au bœuf et haricots rouges", v=1, kind="r", keep_js=[3, 1],
  t="55 min, dont 15 min actives (40 min de four)", cat="plat complet au four (viande + légume + féculent)", allerg="lait (yaourt)",
  i=["patate douce", "bœuf haché", "haricots rouges", "poivron", "yaourt"],
  ing=[("Patates douces moyennes", "2 (300 g en tout)", FL), ("Bœuf haché 5 %", "200 g (100 g par personne)", VI), ("Haricots rouges en conserve, égouttés", "120 g", CO),
       ("Poivron", "1", FL), ("Oignon", "½", FL), ("Tomates concassées en conserve", "150 g", CO), ("Cumin", "1 c. à café", PL), ("Paprika", "1 c. à café", PL),
       ("Yaourt nature, pour servir", "1 (125 g)", CR), ("Coriandre fraîche", "quelques brins", FL), ("Huile d'olive", "1 c. à café", PL), SP],
  steps=["Préchauffer le four à 200 °C. Piquer les patates douces et les cuire entières 40 minutes.",
         "Pendant ce temps, faire revenir l'oignon et le poivron en dés, ajouter le bœuf, les épices, les tomates et les haricots. Mijoter 15 minutes.",
         "Fendre les patates douces, les garnir de chili et servir avec le yaourt et la coriandre."],
  sunday="Patates douces et garniture se font le dimanche, gardées séparément.", keep="3 jours au réfrigérateur ; la garniture se congèle très bien (3 mois).", heat="Micro-ondes 3 min, garniture sur la patate.",
  bal=["Poivron et tomate : compléter d'une salade pour la moitié de l'assiette.", "100 g de bœuf et les haricots rouges pour la protéine.", "150 g de patate douce par personne."],
  Q=[["patate douce", 300, "g", "FL"], ["bœuf haché 5 %", 200, "g", "VI"], ["haricots rouges", 120, "g", "CO"], ["poivron rouge", 1, "pc", "FL"], ["oignon", 0.5, "pc", "FL"],
     ["tomates concassées", 150, "g", "CO"], ["yaourts nature", 1, "pc", "CR"], ["coriandre", 0.5, "botte", "FL"]],
  P=["cumin", "paprika", "huile d'olive"]),

 # ---------- Rapides, le jour même ----------
 dict(id="c_omelpdt", slug="omelette-pommes-de-terre-epinards", n="Omelette aux pommes de terre et épinards", v=0, kind="q",
  t="20 min", cat="dîner rapide végétarien (œufs + légume + féculent)", allerg="œuf",
  i=["œufs", "pommes de terre", "épinards", "oignon"],
  ing=[("Œufs", "6", CR), ("Pommes de terre", "300 g (150 g par personne)", FL), ("Épinards frais", "200 g", FL), ("Oignon", "½", FL),
       ("Huile d'olive", "2 c. à café", PL), ("Salade verte, pour servir", "1 poignée par personne", FL), SP],
  steps=["Couper les pommes de terre en fines rondelles et les cuire 10 minutes à la poêle couverte dans l'huile avec l'oignon.",
         "Ajouter les épinards et les laisser tomber 2 minutes.", "Verser les œufs battus salés et poivrés, cuire 5 minutes à couvert à feu doux.", "Servir avec la salade."],
  sunday="Rien à préparer : plat du jour même. Les pommes de terre peuvent être cuites à l'avance pour gagner 10 minutes.",
  keep="Se mange le jour même ; les restes tiennent 1 jour au frigo, froids.", heat="Sans objet.",
  bal=["3 œufs par personne, la portion de protéines du livret.", "100 g d'épinards plus la salade.", "150 g de pommes de terre par personne."],
  Q=[["œufs", 6, "pc", "CR"], ["pommes de terre", 300, "g", "FL"], ["épinards frais", 200, "g", "FL"], ["oignon", 0.5, "pc", "FL"], ["salade", 1, "pc", "FL"]],
  P=["huile d'olive"]),

 dict(id="c_wrapdd", slug="wraps-dinde-crudites-fromage-blanc", n="Wraps de dinde, crudités et fromage blanc aux herbes", v=1, kind="q",
  t="20 min", cat="dîner rapide (viande + crudités + féculent)", allerg="gluten, lait",
  i=["dinde", "tortillas", "carottes", "salade", "fromage blanc"],
  ing=[("Escalopes de dinde", "250 g (125 g par personne)", VI), ("Tortillas de blé complet", "2 grandes", BO), ("Carotte, râpée", "1", FL),
       ("Concombre", "½", FL), ("Salade verte", "1 poignée", FL), ("Fromage blanc 3 %", "100 g", CR), ("Ciboulette", "quelques brins", FL),
       ("Paprika", "½ c. à café", PL), ("Huile d'olive", "1 c. à café", PL), SP],
  steps=["Couper la dinde en lanières, la saisir 5 minutes dans l'huile avec le paprika, saler, poivrer.",
         "Mélanger le fromage blanc avec la ciboulette ciselée, sel et poivre.", "Tartiner les tortillas de fromage blanc, garnir de crudités et de dinde, rouler."],
  sunday="La carotte peut être râpée le dimanche (3 jours au frigo).", keep="À manger le jour même.", heat="Sans objet.",
  bal=["125 g de dinde par personne.", "Crudités : compléter d'une salade à côté pour la moitié de l'assiette.", "Une tortilla par personne pour le féculent."],
  Q=[["escalopes de dinde", 250, "g", "VI"], ["tortillas", 2, "pc", "BO"], ["carotte", 1, "pc", "FL"], ["concombre", 0.5, "pc", "FL"], ["salade", 1, "pc", "FL"],
     ["fromage blanc", 100, "g", "CR"], ["ciboulette", 0.5, "botte", "FL"]],
  P=["paprika", "huile d'olive"]),

 dict(id="c_shaksh", slug="shakshuka-poivrons-pois-chiches", n="Shakshuka aux poivrons et pois chiches", v=0, kind="q",
  t="25 min", cat="dîner rapide végétarien (œufs + légumes + légumineuse)", allerg="œuf, gluten (pain)",
  i=["œufs", "poivron", "tomates", "pois chiches", "pain complet"],
  ing=[("Œufs", "4", CR), ("Poivrons", "2", FL), ("Oignon", "1", FL), ("Ail", "1 gousse", FL), ("Tomates concassées en conserve", "400 g", CO),
       ("Pois chiches en conserve, égouttés", "100 g", CO), ("Cumin", "1 c. à café", PL), ("Paprika", "1 c. à café", PL),
       ("Huile d'olive", "2 c. à café", PL), ("Persil ou coriandre", "quelques brins", FL), ("Pain complet, pour servir", "60 g (30 g par personne)", BO), SP],
  steps=["Faire revenir l'oignon et les poivrons en lanières 8 minutes dans l'huile, ajouter l'ail et les épices.",
         "Ajouter les tomates et les pois chiches, laisser réduire 8 minutes.", "Creuser 4 puits, y casser les œufs, couvrir et cuire 5 à 6 minutes.", "Parsemer d'herbes, servir avec le pain."],
  sunday="La sauce aux poivrons peut se faire le dimanche (3 jours au frigo) : il ne reste que les œufs à cuire.", keep="À manger le jour même.", heat="Sans objet.",
  bal=["2 œufs par personne plus les pois chiches.", "Poivrons et tomates : plus de 300 g de légumes par personne.", "30 g de pain complet par personne, les pois chiches complétant le féculent."],
  Q=[["œufs", 4, "pc", "CR"], ["poivron rouge", 2, "pc", "FL"], ["oignon", 1, "pc", "FL"], ["ail", 1, "gousse", "FL"], ["tomates concassées", 400, "g", "CO"],
     ["pois chiches", 100, "g", "CO"], ["persil", 0.5, "botte", "FL"], ["pain complet", 60, "g", "BO"]],
  P=["cumin", "paprika", "huile d'olive"]),

 dict(id="c_salthon", slug="salade-pois-chiches-thon-oeuf", n="Salade pois chiches, thon, tomates et œuf", v=0, kind="q",
  t="15 min", cat="salade complète rapide (poisson + légumineuse + légumes)", allerg="poisson, œuf",
  i=["thon", "pois chiches", "tomates cerises", "œufs", "salade"],
  ing=[("Thon au naturel, égoutté", "140 g (1 boîte)", CO), ("Pois chiches en conserve, égouttés", "200 g", CO), ("Œufs", "2", CR),
       ("Tomates cerises", "200 g", FL), ("Concombre", "½", FL), ("Salade verte", "2 poignées", FL), ("Oignon rouge", "¼", FL),
       ("Huile d'olive", "2 c. à café", PL), ("Vinaigre", "1 c. à soupe", PL), ("Moutarde", "½ c. à café", PL), SP],
  steps=["Cuire les œufs 9 minutes (durs), les refroidir et les écaler.", "Couper les tomates, le concombre et l'oignon.",
         "Faire une vinaigrette avec l'huile, le vinaigre et la moutarde.", "Mélanger salade, pois chiches, thon émietté et légumes, poser les œufs en quartiers, assaisonner."],
  sunday="Les œufs durs peuvent être cuits le dimanche (une semaine au frigo dans leur coquille).", keep="À manger le jour même.", heat="Sans objet.",
  bal=["Thon, œuf et pois chiches pour la protéine.", "Plus de 250 g de crudités par personne.", "Les pois chiches font le féculent (100 g égouttés par personne)."],
  Q=[["thon", 140, "g", "CO"], ["pois chiches", 200, "g", "CO"], ["œufs", 2, "pc", "CR"], ["tomates cerises", 200, "g", "FL"], ["concombre", 0.5, "pc", "FL"], ["salade", 1, "pc", "FL"],
     ["oignon rouge", 0.25, "pc", "FL"]],
  P=["vinaigre", "moutarde", "huile d'olive"]),

 dict(id="c_patcourg", slug="pates-courgette-citron-parmesan", n="Pâtes complètes, courgette, citron et parmesan", v=0, kind="q",
  t="20 min", cat="dîner rapide végétarien (féculent + légume + fromage, œuf)", allerg="gluten, lait, œuf",
  i=["pâtes complètes", "courgette", "citron", "parmesan", "œufs"],
  ing=[("Pâtes complètes (crues)", "80 g (40 g par personne)", EP), ("Courgettes", "2 (400 g)", FL), ("Ail", "1 gousse", FL), ("Citron (zeste et jus)", "½", FL),
       ("Parmesan râpé", "30 g", CR), ("Œufs, mollets", "4 (2 par personne)", CR), ("Huile d'olive", "2 c. à café", PL), ("Basilic", "quelques feuilles", FL), SP],
  steps=["Cuire les pâtes. Pendant ce temps, faire sauter les courgettes en dés avec l'ail dans l'huile, 6 minutes à feu vif.",
         "Cuire les œufs 6 minutes et les écaler.", "Mélanger pâtes, courgettes, zeste et jus de citron, parmesan et basilic. Poser les œufs dessus."],
  sunday="Rien à préparer.", keep="À manger le jour même.", heat="Sans objet.",
  bal=["200 g de courgettes par personne : la moitié de l'assiette.", "2 œufs et le parmesan pour la protéine.", "40 g de pâtes complètes crues par personne."],
  Q=[["pâtes complètes", 80, "g", "EP"], ["courgette", 2, "pc", "FL"], ["ail", 1, "gousse", "FL"], ["citron", 0.5, "pc", "FL"], ["parmesan râpé", 30, "g", "CR"], ["œufs", 4, "pc", "CR"], ["basilic", 0.5, "botte", "FL"]],
  P=["huile d'olive"]),

 dict(id="c_dindehv", slug="poelee-dinde-haricots-verts-riz", n="Poêlée de dinde, haricots verts et riz", v=1, kind="q",
  t="25 min", cat="dîner rapide (viande + légume + féculent)", allerg="soja (tamari)",
  i=["dinde", "haricots verts", "riz complet", "gingembre"],
  ing=[("Escalopes de dinde, en lanières", "250 g (125 g par personne)", VI), ("Haricots verts (surgelés)", "300 g", FR), ("Riz complet (cru)", "80 g (40 g par personne)", EP),
       ("Ail", "1 gousse", FL), ("Gingembre frais", "1 petit morceau", FL), ("Tamari (ou sauce soja)", "1 c. à soupe", EP), ("Huile d'olive", "2 c. à café", PL)],
  steps=["Cuire le riz (ou utiliser un reste du dimanche).", "Faire sauter les haricots verts 8 minutes dans la moitié de l'huile avec un fond d'eau.",
         "Ajouter la dinde, l'ail et le gingembre râpés et le reste d'huile, cuire 5 minutes à feu vif.", "Ajouter le tamari, mélanger, servir avec le riz."],
  sunday="Cuire le riz le dimanche fait gagner 20 minutes.", keep="À manger le jour même (restes : 1 jour au frigo).", heat="Sans objet.",
  bal=["150 g de haricots verts par personne.", "125 g de dinde par personne.", "40 g de riz complet cru par personne."],
  Q=[["escalopes de dinde", 250, "g", "VI"], ["haricots verts surgelés", 300, "g", "FR"], ["riz complet", 80, "g", "EP"], ["ail", 1, "gousse", "FL"], ["gingembre frais (morceau)", 1, "pc", "FL"]],
  P=["sauce soja ou tamari", "huile d'olive"]),

 # ---------- Gourmands (cheat meal) ----------
 dict(id="c_burger", slug="burger-maison-frites-patate-douce", n="Burger maison et frites de patate douce au four", v=1, kind="g",
  t="40 min, dont 15 min actives (25 min de four)", cat="cheat meal (viande + légumes + féculent)", allerg="gluten, lait, moutarde",
  i=["bœuf haché", "petits pains", "patate douce", "tomates", "salade"],
  ing=[("Bœuf haché 5 %, en 2 steaks", "250 g", VI), ("Petits pains complets (type burger)", "2", BO), ("Patates douces", "300 g", FL),
       ("Tomate", "1", FL), ("Oignon rouge", "½", FL), ("Salade verte", "2 poignées", FL), ("Emmental ou cheddar, en tranches", "40 g (2 tranches)", CR),
       ("Moutarde", "2 c. à café", PL), ("Huile d'olive", "2 c. à café", PL), ("Paprika", "½ c. à café", PL), SP],
  steps=["Préchauffer le four à 210 °C. Couper les patates douces en frites, les mélanger avec l'huile et le paprika, les cuire 25 minutes en les retournant à mi-cuisson.",
         "Former deux steaks, les saler, poivrer, et les cuire 3 minutes par face dans une poêle chaude ; poser le fromage la dernière minute.",
         "Toaster les pains, tartiner de moutarde, garnir de salade, tomate, oignon et steak.", "Servir avec les frites et le reste de salade."],
  sunday="Rien à préparer : c'est le plaisir du samedi soir.", keep="À manger le jour même.", heat="Sans objet.",
  bal=["Cheat meal : un plat gourmand par semaine, mais construit sur du bœuf 5 %, des frites au four et beaucoup de salade.", "Ajouter un petit dessert si l'envie est là, comme le prévoit le livret."],
  Q=[["bœuf haché 5 %", 250, "g", "VI"], ["petits pains complets", 2, "pc", "BO"], ["patate douce", 300, "g", "FL"], ["tomate", 1, "pc", "FL"], ["oignon rouge", 0.5, "pc", "FL"],
     ["salade", 1, "pc", "FL"], ["emmental en tranches", 40, "g", "CR"]],
  P=["moutarde", "paprika", "huile d'olive"]),

 dict(id="c_pizza", slug="pizza-tortilla-jambon-champignons", n="Pizza tortilla, jambon, champignons et mozzarella", v=1, kind="g",
  t="20 min", cat="cheat meal rapide (viande + légumes + féculent)", allerg="gluten, lait",
  i=["tortillas", "jambon", "champignons", "mozzarella", "sauce tomate"],
  ing=[("Tortillas de blé complet", "2 grandes", BO), ("Sauce tomate", "6 c. à soupe", EP), ("Jambon cuit", "2 tranches (90 g)", VI),
       ("Champignons de Paris", "150 g", FL), ("Mozzarella", "1 boule (125 g)", CR), ("Origan", "1 c. à café", PL), ("Roquette ou salade, pour servir", "2 poignées", FL),
       ("Huile d'olive", "1 c. à café", PL)],
  steps=["Préchauffer le four à 220 °C. Poser les tortillas sur une plaque.", "Étaler la sauce tomate, ajouter le jambon, les champignons émincés et la mozzarella.",
         "Saupoudrer d'origan et cuire 8 à 10 minutes jusqu'à ce que le bord soit croustillant.", "Servir avec la salade arrosée d'un filet d'huile."],
  sunday="Rien à préparer.", keep="À manger le jour même.", heat="Sans objet.",
  bal=["La tortilla remplace une pâte à pizza : bien plus légère.", "Une grosse poignée de salade à côté pour les légumes."],
  Q=[["tortillas", 2, "pc", "BO"], ["sauce tomate", 100, "g", "EP"], ["jambon", 90, "g", "VI"], ["champignons de Paris", 150, "g", "FL"], ["mozzarella", 1, "pc", "CR"], ["salade", 1, "pc", "FL"]],
  P=["origan", "huile d'olive"]),

 dict(id="c_lasagc", slug="lasagnes-courgettes-boeuf", n="Lasagnes de courgettes au bœuf", v=1, kind="rg", keep_js=[3, 1],
  t="1 h, dont 25 min actives (35 min de four)", cat="plat gourmand au four (viande + légume), pain à côté", allerg="lait, gluten (pain)",
  i=["courgette", "bœuf haché", "sauce tomate", "mozzarella", "parmesan"],
  ing=[("Courgettes", "2 grosses (500 g)", FL), ("Bœuf haché 5 %", "250 g", VI), ("Oignon", "1", FL), ("Ail", "1 gousse", FL), ("Sauce tomate", "300 g", EP),
       ("Mozzarella", "1 boule (125 g)", CR), ("Parmesan râpé", "20 g", CR), ("Origan", "1 c. à café", PL), ("Huile d'olive", "1 c. à café", PL),
       ("Pain complet, pour servir", "80 g (40 g par personne)", BO), SP],
  steps=["Couper les courgettes en longues tranches de 5 mm, les griller 2 minutes par face à la poêle sans matière grasse (pour enlever l'eau).",
         "Faire revenir l'oignon, l'ail et le bœuf dans l'huile, ajouter la sauce tomate et l'origan, mijoter 10 minutes.",
         "Préchauffer le four à 190 °C. Alterner dans un plat courgettes et sauce, finir par la mozzarella et le parmesan.", "Cuire 35 minutes, laisser reposer 5 minutes."],
  sunday="Se monte le dimanche ; il peut aussi servir de cheat meal le samedi.", keep="3 jours au réfrigérateur ; se congèle bien (2 mois).", heat="Four 15 min à 180 °C ou micro-ondes 3 min.",
  bal=["Les courgettes remplacent les pâtes : 250 g de légumes par personne.", "Le pain complet apporte le féculent."],
  Q=[["courgette", 2, "pc", "FL"], ["bœuf haché 5 %", 250, "g", "VI"], ["oignon", 1, "pc", "FL"], ["ail", 1, "gousse", "FL"], ["sauce tomate", 300, "g", "EP"],
     ["mozzarella", 1, "pc", "CR"], ["parmesan râpé", 20, "g", "CR"], ["pain complet", 80, "g", "BO"]],
  P=["origan", "huile d'olive"]),

 dict(id="c_gratcoq", slug="gratin-coquillettes-jambon-brocoli", n="Gratin de coquillettes au jambon et brocoli", v=1, kind="rg", keep_js=[3, 1],
  t="40 min, dont 15 min actives (20 min de four)", cat="plat gourmand au four (viande + légume + féculent)", allerg="gluten, lait",
  i=["pâtes complètes", "jambon", "brocoli", "lait", "emmental"],
  ing=[("Coquillettes complètes (crues)", "100 g", EP), ("Brocoli", "1 tête (400 g)", FL), ("Jambon cuit, en dés", "150 g", VI), ("Lait demi-écrémé", "25 cl", CR),
       ("Farine", "1 c. à soupe", EP), ("Emmental râpé", "40 g", CR), ("Noix de muscade", "1 pincée", PL), ("Beurre", "10 g", CR), SP],
  steps=["Cuire les coquillettes et le brocoli en petits bouquets ensemble, 8 minutes. Égoutter.", "Préchauffer le four à 200 °C.",
         "Faire fondre le beurre, ajouter la farine puis le lait en fouettant jusqu'à épaississement (béchamel légère). Muscade, sel, poivre.",
         "Mélanger pâtes, brocoli, jambon et béchamel dans un plat, parsemer d'emmental et gratiner 20 minutes."],
  sunday="Se fait le dimanche ; idéal pour un déjeuner réconfortant.", keep="3 jours au réfrigérateur ; se congèle (2 mois).", heat="Four 15 min à 180 °C ou micro-ondes 3 min avec un peu de lait.",
  bal=["200 g de brocoli par personne.", "50 g de coquillettes crues par personne : un peu plus que le livret, c'est le côté gourmand.", "Béchamel au lait demi-écrémé, 10 g de beurre pour deux."],
  Q=[["pâtes complètes", 100, "g", "EP"], ["brocoli", 1, "pc", "FL"], ["jambon en dés", 150, "g", "VI"], ["lait demi-écrémé", 250, "ml", "CR"], ["emmental râpé", 40, "g", "CR"]],
  P=["farine", "beurre", "noix de muscade"]),

 dict(id="c_fajit", slug="fajitas-poulet-poivrons", n="Fajitas de poulet aux poivrons", v=1, kind="qg",
  t="25 min", cat="cheat meal rapide (viande + légumes + féculent)", allerg="gluten, lait",
  i=["poulet", "poivron", "tortillas", "avocat", "fromage blanc"],
  ing=[("Filets de poulet, en lanières", "250 g", VI), ("Poivrons de couleurs", "2", FL), ("Oignon rouge", "1", FL), ("Tortillas de blé complet", "2 grandes (1 par personne)", BO),
       ("Avocat", "½", FL), ("Fromage blanc 3 %", "60 g", CR), ("Citron vert", "1", FL), ("Cumin", "1 c. à café", PL), ("Paprika", "1 c. à café", PL),
       ("Huile d'olive", "2 c. à café", PL), ("Coriandre fraîche", "quelques brins", FL), SP],
  steps=["Faire sauter les poivrons et l'oignon en lanières 6 minutes dans l'huile à feu vif.", "Ajouter le poulet et les épices, cuire 6 minutes, arroser de jus de citron vert.",
         "Écraser l'avocat avec un peu de citron, mélanger le fromage blanc avec la coriandre.", "Chauffer les tortillas et laisser chacun garnir la sienne."],
  sunday="Les poivrons peuvent être coupés le dimanche.", keep="À manger le jour même.", heat="Sans objet.",
  bal=["Poivrons et oignon : 250 g de légumes par personne.", "125 g de poulet par personne.", "Une grande tortilla par personne."],
  Q=[["filets de poulet", 250, "g", "VI"], ["poivron rouge", 2, "pc", "FL"], ["oignon rouge", 1, "pc", "FL"], ["tortillas", 2, "pc", "BO"], ["avocat", 0.5, "pc", "FL"],
     ["fromage blanc", 60, "g", "CR"], ["citron vert", 1, "pc", "FL"], ["coriandre", 0.5, "botte", "FL"]],
  P=["cumin", "paprika", "huile d'olive"]),

 dict(id="c_crumble", slug="crumble-sale-potimarron-poulet", n="Crumble salé potimarron et poulet", v=1, kind="rg", keep_js=[3, 1],
  t="55 min, dont 20 min actives (30 min de four)", cat="plat gourmand au four (viande + légume + féculent)", allerg="gluten, lait",
  i=["potimarron", "poulet", "poireaux", "parmesan", "flocons d'avoine"],
  ing=[("Potimarron", "500 g (½, avec la peau)", FL), ("Poireau", "1", FL), ("Filets de poulet, en dés", "250 g", VI), ("Crème légère 15 %", "5 cl", CR),
       ("Flocons d'avoine", "40 g", EP), ("Farine", "20 g", EP), ("Parmesan râpé", "25 g", CR), ("Beurre froid", "15 g", CR), ("Thym", "1 c. à café", PL), SP],
  steps=["Préchauffer le four à 190 °C. Couper le potimarron en cubes et le poireau en rondelles, les cuire 10 minutes à couvert avec un fond d'eau.",
         "Faire dorer le poulet 4 minutes, le mélanger aux légumes avec la crème et le thym, saler, poivrer, verser dans un plat.",
         "Sabler du bout des doigts les flocons, la farine, le parmesan et le beurre, répartir sur le dessus.", "Cuire 30 minutes jusqu'à ce que le crumble soit doré."],
  sunday="Se fait le dimanche ; légumes de saison en automne-hiver.", keep="3 jours au réfrigérateur ; se congèle (2 mois), le dessus ramollit un peu.", heat="Four 12 min à 180 °C pour garder le croustillant.",
  bal=["Potimarron et poireau : 300 g de légumes par personne.", "125 g de poulet par personne.", "Flocons et farine font le féculent (30 g par personne)."],
  Q=[["potimarron", 500, "g", "FL"], ["poireaux", 1, "pc", "FL"], ["filets de poulet", 250, "g", "VI"], ["crème légère", 50, "ml", "CR"], ["flocons d'avoine", 40, "g", "EP"],
     ["farine", 20, "g", "EP"], ["parmesan râpé", 25, "g", "CR"]],
  P=["beurre", "thym"]),
]

import importlib.util, os
_spec = importlib.util.spec_from_file_location("etapes", os.path.join(os.path.dirname(os.path.abspath(__file__)), "recettes-claude-etapes.py"))
_et = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_et)
for d in D:
    d["title"] = d["n"] + " *"
    d["src"] = SRC
    d["mat"], d["steps"] = _et.S[d["id"]]   # étapes détaillées (17/10, demande d'Antho)


def md(d):
    rows = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in d["ing"])
    steps = "\n".join(f"{k}. {s}" for k, s in enumerate(d["steps"], 1))
    bal = "\n".join(f"- {b}" for b in d["bal"])
    return f"""# {d['title']}

- **Source** : {d['src']}
- **Portions** : 2 personnes, 1 repas{' (à doubler pour deux repas)' if 'r' in d['kind'] else ''}
- **Temps** : {d['t']}
- **Catégorie** : {d['cat']}
- **Allergènes courants** : {d['allerg']}
- **Matériel** : {d['mat']}

## Ingrédients (2 personnes, 1 repas)

| Ingrédient | Quantité | Rayon |
|---|---|---|
{rows}

## Étapes

{steps}

## Préparation du dimanche

- **Ce qui se fait le dimanche** : {d['sunday']}
- **Conservation** : {d['keep']}
- **Réchauffage** : {d['heat']}

## Équilibre (remarques Claude)

{bal}
"""


if __name__ == "__main__":
    assert len(D) == 30 and len({d["id"] for d in D}) == 30 and len({d["slug"] for d in D}) == 30
    if sys.argv[1] == "md":
        for d in D:
            open(f"/mnt/project-files/recettes/{d['slug']}.md", "w", encoding="utf-8").write(md(d))
        print("écrit", len(D))
    else:
        R = {}
        for d in D:
            x = {"n": d["n"] + " *"}
            if d["v"]: x["v"] = 1
            for f in d["kind"]: x[f] = 1
            x["i"] = d["i"]
            R[d["id"]] = x
        out = dict(R=R, Q={d["id"]: d["Q"] for d in D}, PL={d["id"]: d["P"] for d in D}, SL={d["id"]: d["slug"] for d in D},
                   KP={d["id"]: d["keep_js"] for d in D if "keep_js" in d},
                   RC={d["id"]: {"t": d["t"], "ing": [[a, b] for a, b, c in d["ing"]], "steps": [f"{k}. {s}" for k, s in enumerate(d["steps"], 1)],
                                 "keep": ["Conservation : " + d["keep"], "Réchauffage : " + d["heat"]]} for d in D})
        print(json.dumps(out, ensure_ascii=False))
