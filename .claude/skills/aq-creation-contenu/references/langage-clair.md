# Langage clair — règles pour toutes les publications AQ

Adopté par Rénald le 26 octobre 2026. Base : norme internationale **ISO 24495-1:2023 (langage clair)**, complétée par quelques règles du **FALC** (Facile à lire et à comprendre) et des **WCAG** (accessibilité numérique). Objectif : le lecteur trouve l'information, la comprend et sait quoi faire **du premier coup**, y compris s'il lit le français comme deuxième langue, s'il est dyslexique ou s'il lit sur téléphone.

Ces règles s'appliquent aux visuels (carrousels, stories, Reels, bannières) **et** aux légendes. Elles ne changent pas le ton : AQ reste sobre et professionnel, on simplifie la forme, pas le fond.

## 1. Phrases et mots

- **Une idée par phrase.** Viser 15 mots, **jamais plus de 20** dans un visuel ; 25 au maximum dans une légende.
- **Voix active, sujet clair :** « Le conseiller t'oriente » plutôt que « Une orientation est assurée par le conseiller ».
- **Verbes plutôt que noms abstraits :** « pour financer ton projet » plutôt que « en vue du financement de ton projet ».
- **Mots courants.** Un mot technique nécessaire (repreneuriat, cédant, MRC) est expliqué la première fois, en quelques mots.
- **Toujours le même mot pour la même chose** (ne pas alterner repreneur / acheteur / successeur).
- **Pas de double négation**, pas de parenthèses imbriquées, pas de « etc. » (on liste ou on coupe).
- **Une instruction = un verbe à l'impératif** au début : « Appelle », « Inscris-toi », « Prépare ».

## 2. Sigles et noms d'organismes

- **Chaque sigle est développé à sa première apparition** dans le visuel et dans la légende : « la MRC (municipalité régionale de comté) », « les SADC (Sociétés d'aide au développement des collectivités) ».
- Exceptions admises sans développement : AQ (après « Affaires Québec » une première fois), PME, TPS, TVQ.
- Un nom d'organisme est suivi de **ce qu'il fait pour le lecteur** (« Repreneuriat Québec : te met en relation avec des cédants »).

## 3. Chiffres

- **Un chiffre important a un repère** : comparaison, unité ou image mentale. « 12 % des emplois, contre 7 % au Québec » ; « environ 1 emploi sur 8 ».
- **Au plus 2 chiffres par slide**, et un seul chiffre vedette.
- Montants avec l'unité et l'espace insécable : « 34,59 $ », « 6 M$ » expliqué une fois en « 6 millions de dollars ».
- Dates complètes et sans ambiguïté : « vendredi 23 octobre 2026, 19 h (heure de Montréal) ».

## 4. Structure

- **Le plus important d'abord** : titre = le message, pas le thème (« Reprendre une entreprise : 4 étapes avant toute offre » plutôt que « Le repreneuriat »).
- **Listes de 3 à 5 éléments**, jamais plus de 5 par slide.
- **Une slide = une idée** ; le dernier élément d'un carrousel dit quoi faire ensuite.
- Légendes : 1re ligne = le message ; paragraphes de 1 à 3 phrases ; listes à puces pour les étapes.

## 5. Forme visuelle (lisibilité, dyslexie)

- Texte courant en **DM Sans** (sans empattement) ; la Caslon reste réservée aux titres courts.
- **Taille minimale** : 30 px pour le texte courant sur un visuel 1080 px de large, 26 px pour une source ou une mention ; sous-titres de Reel 60 px au moins.
- **Aligné à gauche** ou centré pour les titres courts ; **jamais justifié** ; **pas de mot coupé** en fin de ligne.
- **Pas de phrase entière en majuscules** ni en italique. Les surtitres en petites capitales espacées restent admis car ils font 2 à 4 mots ; au-delà, écrire en casse normale.
- **Contraste** d'au moins 4,5 pour 1 (critère WCAG) : texte #E8E4DC ou or #E3A73C sur fond #231F20 conviennent ; sur une vidéo, toujours un dégradé sombre sous le texte.
- Interligne d'au moins 1,3 pour le texte courant.

## 6. Vidéo et audio

- Tout ce qui est dit est **écrit à l'écran** (sous-titres ou texte du plan).
- Un texte de Reel reste à l'écran **au moins 3 secondes**, et environ 1 seconde par tranche de 4 mots.
- Pas plus de 2 lignes de sous-titre à la fois.

## 7. Images et accessibilité des publications

- Chaque publication a un **texte alternatif** (champ « alt » de Facebook, Instagram et LinkedIn) : 1 ou 2 phrases qui disent ce que montre l'image et le message clé. Il est rédigé dans `legendes.md` sous un titre « Texte alternatif ».
- Les émojis ne remplacent pas un mot et restent rares (0 à 2), en fin de phrase.
- Hashtags en « CamelCase » pour les lecteurs d'écran : #EntrepreneuriatImmigrant, pas #entrepreneuriatimmigrant.

## 8. Vérification

- `python3 visuels/outils/clair.py <contenu.json ou legendes.md>` signale les phrases trop longues, les sigles non développés, les slides trop chargées et les majuscules prolongées. Corriger chaque alerte ou noter pourquoi elle est acceptable.
- Relire en se posant 3 questions : *Qu'est-ce que le lecteur doit retenir ? Que doit-il faire ? Le comprendrait-il s'il lisait le français depuis 2 ans ?*

## Exemples

| À éviter | En langage clair |
| --- | --- |
| « Le volet 3 du PEQ-E impose un accompagnement par un OSR avec offre de service. » | « Le Programme des entrepreneurs a un volet pour reprendre une entreprise. Tu dois être accompagné par un organisme spécialisé en repreneuriat. » |
| « La construction pèse 12,0 % de l'emploi régional. » | « Dans Lanaudière, 12 % des emplois sont dans la construction. C'est presque le double du Québec (7 %). » |
| « Contacte la MRC. » | « Appelle le Réseau accès PME de ta MRC (municipalité régionale de comté). C'est gratuit. » |
