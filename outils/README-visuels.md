# visuels.py : schémas d'article (style emmanuelmichel.fr)

`python3 outils/visuels.py data.json sortie.webp` → WebP de 1500 px de large, hauteur automatique.
Champs communs : `type`, `pastille` (SEO, GEO…), `titre`, `sous_titre` (optionnel), `source` (pied de page, optionnel).
- `steps` : `items`: [{titre, texte, tags[], badge}] (le dernier numéro est noir)
- `compare` : `colonnes`: [..], `lignes`: [[..]], `colonne_mise_en_avant`: index
- `bars` : `unite`, `barres`: [{label, valeur, note, couleur: noir|jaune, affichage}]
- `timeline` : `evenements`: [{date, titre, texte, badge, tags[]}]
- `annotated` : `fenetre`: {style: clair|sombre, titre, lignes: [{texte, surligne, repere}], puces[]}, `reperes`: [{n, titre, texte}]
*mot* dans un texte = gras. Aucune donnée inventée : chaque chiffre vient d'une source lue.

# vignette.py : image à la une (1200x675)
`python3 outils/vignette.py data.json image-une-<slug>.webp` (champs : categorie, titre, mode table|serp|ai, header, highlight, ai_text, chips).

Format mobile : canevas de 450 px (rendu 1350 px), police 18 px. Aperçu `<fichier>.mobile.png` à 300 px de large : le texte doit y rester lisible.
Limites : 5 éléments, tableau de 3 colonnes et 5 lignes au plus, cellule de 28 caractères au plus, texte d'élément de 90 caractères au plus.
