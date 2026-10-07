# Routine hebdomadaire — lot de publications AQ

Exécutée automatiquement chaque jeudi vers 17 h 45 (heure de Montréal). Elle prépare les publications **du vendredi au jeudi suivants**. Rénald valide et programme ; **la routine ne publie jamais**.

## 1. Préparer l'environnement
```
pip install -q pillow playwright numpy faster-whisper
apt-get install -y -q hunspell hunspell-fr   # correcteur fr_CA
git fetch origin claude/wonderful-bell-06kyk8 && git checkout claude/wonderful-bell-06kyk8 && git pull
```
Chromium est déjà installé (`/opt/pw-browsers/chromium`, utilisé par `visuels/outils/aq.py`). ffmpeg est dans le PATH.

## 2. Lire avant de produire
1. `visuels/PLAN.md` (charte, ligne éditoriale, visuels prévus, accords).
2. Le skill `.claude/skills/aq-creation-contenu/` (SKILL.md et `references/`).
3. `visuels/publie.md` : ce qui est déjà publié (ne jamais le reproposer ; tenir compte des écarts avec les programmes).
4. Les semaines déjà produites (`visuels/2026-S*/legendes.md`) pour ne pas se répéter et respecter les proportions des piliers.

## 3. Choisir le contenu de la période
- D'abord les visuels du `PLAN.md` dont la date tombe dans la période et qui ne sont pas bloqués (⛔).
- Compléter selon la trame du skill : au plus **1 publication de fil par jour et par plateforme**, 3 à 5 stories, 1 à 2 posts LinkedIn (vouvoiement).
- Respecter les piliers (30/30/20/20) et la **rotation des 6 sujets** de `PLAN.md` : réseautage et accès au marché en priorité, puis repreneuriat, régions et secteurs, ressources institutionnelles, démarrage. **Financement et crédit : au plus 1 contenu de fil par semaine.**
- Avant de choisir, compter les sujets des 4 dernières semaines (`publie.md`, `legendes.md`) et rattraper les sujets en retard.
- Placer les mots-clés de `PLAN.md` (« reprendre une entreprise Québec », « réseau d'affaires immigrant », « s'installer en région Québec ») dans les accroches et les légendes quand le sujet s'y prête.
- Dans `programme.md`, indiquer pour chaque contenu son sujet (1 à 6), et le décompte de la semaine.
- Chaque contenu apporte une valeur concrète et vérifiable (organismes, outils, programmes, étapes nommés).

## 3 bis. Vidéos face caméra (Rouba, Rénald)
- Au plus **1 vidéo face caméra par semaine**, en alternant Rouba et Rénald (pilier « Visages »).
- **Date de publication : au plus tôt le dimanche**, soit 3 jours après la livraison du jeudi, pour laisser le temps d'enregistrer. Jamais le vendredi ni le samedi qui suivent la livraison.
- Livrer pour chaque vidéo un fichier `script-<AAAA-MM-JJ>-<prénom>.md` dans le dossier du lot, avec :
  1. l'objectif et le message clé, en une phrase ;
  2. la durée cible (30 à 60 s) ;
  3. l'**accroche des 3 premières secondes**, à dire face caméra ;
  4. le texte complet, en phrases courtes, lisible au prompteur (environ 130 mots par minute) ;
  5. les consignes de tournage : vertical 9:16, face à une fenêtre, fond neutre (sans bleu), téléphone à hauteur des yeux, regarder l'objectif, 2 prises ;
  6. la date limite d'envoi de la vidéo (la veille de la publication) ;
  7. la légende Instagram/Facebook (et LinkedIn si pertinent).
- Fournir aussi la **couverture du Reel** (texte seul si aucune photo n'est disponible).
- Dans `programme.md` et dans le message final, mettre en tête : « Vidéo à tourner : <sujet>, par <prénom>, à envoyer avant le <date> ».
- Quand la vidéo brute arrive (déposée dans la session) : `python3 visuels/outils/montage.py brute.mp4 finale.mp4 --nom "Rouba Hamadi" --fonction "Cofondatrice et présidente" --script script-<date>-<prénom>.md` (le script lu guide la transcription ; `--modele medium` si le son est difficile). Le script recadre en 1080 × 1920, transcrit en français sur place (faster-whisper ; la vidéo ne sort pas de l'environnement), coupe les silences de plus de 0,6 s (détectés dans le son), incruste les sous-titres (mot prononcé en or, au-dessus des 250 px du bas), ajoute le bandeau « L'ÉQUIPE » et le carton de fin.
- **Relire `finale.srt`** : la transcription se trompe surtout sur les noms propres (organismes, programmes, sigles). Corriger les mots dans `finale-mots.json`, puis relancer avec `--mots finale-mots.json`.
- Regarder des images clés (début avec bandeau, milieu, carton de fin) avant de livrer, et fournir la couverture.

## 3 ter. Varier les Reels en motion design
- Moteur : `visuels/outils/reel.py`. Formes disponibles : `titre`, `pile`, `compteur` (chiffre qui défile), `liste` (cases cochées dans une seule scène), `machine` (question tapée puis réponse), `mythe` (idée reçue barrée puis la réalité), `logo`. Transitions : `volet`, `fondu`, `glisse`, `cercle`, `coupe`. Exemple complet : `visuels/outils/exemples/reel-formes.json`.
- Chaque Reel dure de 12 à 20 s, mélange **au moins 3 formes différentes** et **au moins 2 types de transitions**, sans enchaîner plus de 2 scènes de la même forme.
- **Changer de forme d'ouverture à chaque Reel** (ex. : idée reçue, puis chiffre clé, puis question tapée, puis checklist). Le format « titre puis titre puis titre » ne doit pas revenir deux fois de suite.
- Consigner chaque Reel dans `visuels/reels-journal.md` (date, sujet, forme d'ouverture, formes et transitions utilisées) et le lire avant d'en concevoir un nouveau.
- Alterner les semaines : Reel en motion design ou vidéo face caméra en vedette.

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
