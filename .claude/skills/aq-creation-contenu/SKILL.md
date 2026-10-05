---
name: aq-creation-contenu
description: Création de contenu pour Affaires Québec (AQ), cabinet-conseil qui accompagne les entrepreneurs issus de l'immigration et les organismes de développement économique au Québec. Utilise ce skill dès qu'il est question de publications Instagram, Facebook ou LinkedIn d'AQ, de légendes, de hashtags, de stories, de bulles « À la une », de Reels ou vidéos motion design, de visuels (posts, couvertures, bannières d'événement), de calendrier éditorial, d'idées de posts, de publicité Meta ou de promotion d'un événement AQ, même si l'utilisateur ne dit pas « skill » ni « Affaires Québec » explicitement (ex. « écris-moi la légende du post 3 », « donne-moi des idées de posts », « fais un Reel », « ajuste le ton »).
---

# Création de contenu — Affaires Québec

Ce skill encode la ligne éditoriale, l'identité visuelle et les méthodes validées avec Rey (Rénald Rabathaly, co-fondateur et directeur des opérations d'AQ). Rouba Hamadi est co-fondatrice et présidente.

## 1. Positionnement : la règle qui prime sur tout

AQ vend **la structure et le réseau** qui propulsent un projet, pas le style de vie d'entrepreneur. AQ n'est pas un coach business façon influenceur.

- Ton **institutionnel, sobre, crédible** : vouvoiement, peu d'émojis (0 à 2), pas de promesses de liberté, de richesse ou de « vie de rêve ».
- On parle de **méthode** (Structurer · Financer · Démontrer), de **financement**, de **réseau institutionnel** (organismes de développement économique, bailleurs de fonds, municipalités).
- Crédibilité par les faits : expérience dans l'écosystème (Entreprendre ici, IDÉ Trois-Rivières), collaborations (MEIE, Ville de Montréal, MIFI), résultats clients.
- À éviter : scripts de coach (« douleur → projection → réponds GO »), urgence artificielle, superlatifs, « machine à RDV ».

Si une demande pousse vers un ton coach ou lifestyle, propose la version institutionnelle et explique brièvement pourquoi.

## 1 bis. Angle par défaut : les problématiques des clients

Les posts partent des **problèmes concrets que vivent nos clients**, puis montrent comment la méthode et le réseau d'AQ y répondent. C'est ce qui prouve notre expertise sans nous mettre en avant de façon gratuite.

Structure : **Constat** (le problème, concret et reconnaissable) → **Pourquoi** (la cause dans le système québécois) → **Ce qui aide** (méthode, ressource, réseau ; un conseil utile même sans nous) → **Appel à l'action** sobre.
Banque de problématiques et règles : `references/problematiques.md`. Viser au moins la moitié du calendrier sur cet angle.

## 2. Publics

1. Entrepreneurs issus de l'immigration au Québec (projet, démarrage, croissance).
2. Organismes, municipalités, pôles de développement local qui soutiennent ces entrepreneurs (offre institutionnelle : études diagnostiques, cartographie des services, co-construction de programmes).

L'audience est **au Québec**, même si Rey publie depuis la Martinique : heures, pubs et références sont réglées sur Montréal.

## 3. Flux de travail

1. Identifier le livrable : légende, visuel, story, Reel, calendrier, pub, page (bio, À propos).
2. Lire la référence utile :
   - `references/marque.md` : couleurs, polices, logos, gabarits visuels.
   - `references/plateformes.md` : dimensions, différences Instagram / Facebook, réglages, pubs.
   - `references/legendes.md` : structures de légendes, hashtags, exemples validés.
   - `references/problematiques.md` : problèmes des clients (entrepreneurs et organismes) et comment les traiter en post.
   - `references/calendrier.md` : méthode de lancement, trame hebdomadaire, promotion d'un événement.
   - `references/persuasion.md` : principes de persuasion compatibles avec le ton AQ.
3. Produire, puis passer la checklist (section 5).
4. Sortie mobile : Rey travaille sur téléphone, donc des réponses courtes, sans préambule, qui tiennent sur un écran, avec 5 tâches au maximum à la fois.

## 4. Vidéo Reel motion design

Script : `scripts/reel_motion.py` (Pillow + ffmpeg). Il génère un MP4 1080 × 1920 à 30 i/s avec des transitions en volet or, des révélations de texte en masque et une musique synthétisée libre de droits (`scripts/musique.py`). Les scènes se définissent dans un JSON (voir l'en-tête du script). Contrôle toujours quelques images clés avant de livrer.

## 5. Checklist avant de livrer

- [ ] Ton institutionnel (pas de lifestyle ni de script de coach).
- [ ] Faits vérifiés, sans rien inventer : chiffres, années d'expérience, noms de clients.
- [ ] Témoignage ou nom de client seulement avec son accord (ex. G&M Agence, Le Pôle).
- [ ] Heure indiquée en « heure de Montréal » quand il y a une date ; aucune date passée ou périmée.
- [ ] L'angle part d'un problème client quand c'est possible.
- [ ] Légende adaptée à la plateforme (Instagram : « lien en bio » ; Facebook : lien direct, 1 ou 2 hashtags).
- [ ] Visuel aux bonnes dimensions, fautes et doubles espaces vérifiés, pas de texte fantôme.

## 6. Points ouverts à signaler si pertinents

- Expérience de Rouba : 10 ans (proposition au Pôle) ou 15 ans (site) → à harmoniser ; ne pas chiffrer tant que ce n'est pas tranché.
- Compteurs du site affairesquebec.ca affichés à « 0 » → à vérifier avant de s'en servir comme preuve.
- Téléphone public : numéro martiniquais (+596) ; un numéro 514/438 inspirerait plus confiance au Québec.
