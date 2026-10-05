# Assets — visuels réseaux sociaux AQ

## Polices (Google Fonts, licence OFL — voir `fonts/OFL-*.txt`)
- `fonts/LibreCaslonDisplay-Regular.ttf` — titres éditoriaux
- `fonts/DMSans[opsz,wght].ttf`, `fonts/DMSans-Italic[opsz,wght].ttf` — textes courants
- `fonts/Figtree[wght].ttf` — style équipe (800)

## Logos — À FOURNIR (ne jamais redessiner)
- [x] `logo-3-2-fond-sombre.png` — arche or + texte blanc
- [x] `logo-3-1-fond-sombre.png` — arche contour
- [x] `symbole-or.png`
- [x] `symbole-noir.png`

Format souhaité : PNG fond transparent, au moins 2000 px de large (le filigrane est affiché à 420 px, la bannière LinkedIn à 1584 px).

> Mise à jour : les 4 logos sont fournis par le skill `aq-creation-contenu` (copie dans `.claude/skills/`).

## Produire un visuel
```
python3 visuels/outils/aq.py rendre visuels/2026-S41/contenu/s41-01-trois-portes.json
python3 visuels/outils/aq.py apercu visuels/2026-S41
```
Le contenu de chaque visuel est un JSON dans `<semaine>/contenu/` ; les gabarits sont dans `visuels/outils/` (`aq.css` + `aq.py`).
