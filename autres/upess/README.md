# UPES — spoken word (hors Affaires Québec)

- `upess-spoken-word.mp3` : 35 s, voix de synthèse Piper « SIWIS » (licence CC BY 4.0, mention à garder) + percussions synthétisées (tibwa, tanbou, claps, coup final), -14 LUFS.
- `mix.py` : script de génération (texte, graphies phonétiques « Upèsse », « Une-sa », placement et mixage). Le chemin du modèle de voix est à adapter.
- `upess-spoken-word-musique.mp3` (26 nov.) : même voix, traitée (égalisation, compression légère, petite réverbération), sur la musique instrumentale fournie par Rénald (WhatsApp du 26 nov., 16 h 30), baissée automatiquement sous la voix, fondu final de 3,5 s, -14 LUFS. Les percussions synthétisées ne sont plus utilisées dans cette version.
- `upess-video.mp4` (26 nov.) : vidéo 9:16, 35 s, sur `upess-spoken-word-musique.mp3`. Script `video/video.py` (logo et affiche fournis par Rénald dans `video/`). Déroulé : logo (intro), un mot par frappe, photo de l'affiche avec « Nos droits · Nos acquis · Notre dignité », tuiles « Écouter · Dialoguer · Proposer », « TOUT MOUN CÉ MOUN », élections du 3 au 10 décembre 2026, « Votez UPES-UNSA, ba nou fos la ! » et logo. Sous-titres complets en bas.
- 26 nov. (correction) : « UPES » (et non UPESS) dans tous les textes ; « Toutt moun » dans le script de voix pour faire prononcer le T de « Tout moun cé moun ».
- 26 nov. (correction 2) : « touss » dans le script de voix pour faire entendre le S de « tous les mêmes essentiels » ; phrases de voix figées (fichiers réutilisés), vidéo recalée par la fonction warp() de video.py.

## Version 2 (27 nov.) : chanson complète
- `upes-chanson-v2.mp3` (81 s) et `upes-video-v2.mp4` (9:16, 81 s) : nouveau texte (couplets 1 et 2, refrain), voix SIWIS sur la musique fournie, chœur « UPES ! » et « Votez UPES-UNSA » à 3 voix (SIWIS + UPMC, licence CC BY-SA 4.0 pour UPMC).
- Prononciations : « Upèsse », « touss », « Toutt moun sé moun », « ba nou fosse la », « Une-sa ». Affichage : UPES (pas UPESS).
- Scripts : `video/voix_v2.py` (voix, phrases en cache, texte dans `video/lignes.json`), `video/video_v2.py` (images, calées sur `video/segments.json`).
