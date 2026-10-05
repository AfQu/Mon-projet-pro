# Routine hebdomadaire — lot de publications AQ

Exécutée automatiquement chaque jeudi vers 17 h 45 (heure de Montréal). Elle prépare les publications **du vendredi au jeudi suivants**. Rénald valide et programme ; **la routine ne publie jamais**.

## 1. Préparer l'environnement
```
pip install -q pillow playwright numpy
apt-get install -y -q hunspell hunspell-fr   # correcteur fr_CA
git fetch origin claude/wonderful-bell-06kyk8 && git checkout claude/wonderful-bell-06kyk8 && git pull
```
Chromium est déjà installé (`/opt/pw-browsers/chromium`, utilisé par `visuels/outils/aq.py`). ffmpeg est dans le PATH.

## 2. Lire avant de produire
1. `visuels/PLAN.md` (charte, ligne éditoriale, visuels prévus, accords).
2. Le skill `.claude/skills/aq-creation-contenu/` (SKILL.md et `references/`).
3. Les semaines déjà produites (`visuels/2026-S*/legendes.md`) pour ne pas se répéter et respecter les proportions des piliers.

## 3. Choisir le contenu de la période
- D'abord les visuels du `PLAN.md` dont la date tombe dans la période et qui ne sont pas bloqués (⛔).
- Compléter selon la trame du skill : au plus **1 publication de fil par jour et par plateforme**, 3 à 5 stories, 1 à 2 posts LinkedIn (vouvoiement).
- Respecter les piliers (30/30/20/20) et le plafond financement (25 %) sur le cumul du trimestre.
- Chaque contenu apporte une valeur concrète et vérifiable (organismes, outils, programmes, étapes nommés).

## 4. Produire
- Contenu en JSON dans `visuels/<semaine>/contenu/`, rendu avec `python3 visuels/outils/aq.py rendre <json>` ; Reels avec `visuels/outils/reel.py`.
- Le rendu doit afficher `OK` partout. Regarder ensuite **chaque** image (et des images clés des Reels) : le contrôle automatique ne remplace pas l'œil.
- Correcteur : `hunspell -i utf-8 -d fr_CA -l` sur tous les textes et légendes.
- Légendes dans `legendes.md`, sources dans `sources.md`, planche `apercu.png` régénérée.

## 5. Livrer
1. Dossier `visuels/<semaine>/publication/<AAAA-MM-JJ>/` (date du vendredi) : un sous-dossier par jour et par plateforme, images numérotées, `legende.txt`, et `programme.md` (heure, plateforme, fichier, légende, gestes à faire dans l'appli).
2. Un zip de ce dossier (ignoré par git).
3. Commit et push sur `claude/wonderful-bell-06kyk8`.
4. Envoyer à Rénald (SendUserFile, statut « proactive ») : le zip, `apercu.png` et `programme.md`.
5. Message final de 10 lignes maximum : ce qui est prêt, puis **au plus 5 points à valider** (chiffres, accords, photos manquantes).

## Règles d'autonomie
**La routine décide seule :** sujets, textes, mise en page, ordre et horaires proposés, dans le cadre ci-dessus.

**Elle signale sans bloquer :** tout chiffre ou critère de programme (Rénald le vérifie avant de publier), les sujets proches de l'immigration (statut, permis).

**Elle ne fait jamais :**
- publier, programmer ou répondre sur un réseau social ;
- nommer un client ou citer un témoignage sans accord noté dans `PLAN.md` ;
- inventer un chiffre, une date ou une citation ;
- donner un avis individuel juridique ou d'immigration (toujours « selon ta situation, valide avec un conseiller ») ;
- générer ou retoucher une photo de personne, redessiner le logo, sortir de la charte ;
- mentionner l'inscription au webinaire après le 23 octobre 2026.

**Si quelque chose bloque** (photo, accord, source introuvable) : produire tout le reste, et lister le manque dans le message final.
