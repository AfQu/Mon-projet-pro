#!/usr/bin/env python3
"""Montage d'une vidéo face caméra (Rouba, Rénald) aux couleurs d'Affaires Québec.

Usage :
    python3 visuels/outils/montage.py brute.mp4 sortie.mp4 --nom "Rouba Hamadi" \
        --fonction "Co-fondatrice et présidente" [--script script.md] [--modele medium] [--mots mots.json] [--sans-coupe]

Étapes :
  1. recadrage 1080 × 1920, 30 i/s ;
  2. transcription mot à mot en français (faster-whisper, modèle « small », exécuté ici :
     la vidéo ne quitte pas l'environnement). Avec --mots, on fournit les mots déjà minutés ;
  3. suppression des silences de plus de 0,6 s, détectés dans le son (sauf --sans-coupe) ;
  4. sous-titres incrustés : 3 ou 4 mots à la fois, DM Sans, mot prononcé en or,
     placés au-dessus des 250 px du bas (zone des boutons Instagram) ;
  5. bandeau « L'ÉQUIPE » + nom + fonction (style équipe de la charte) de 0,8 s à 4,5 s ;
  6. carton de fin animé (reel.py, scène logo) ajouté à la suite.
Écrit aussi sortie.srt (sous-titres bruts, utiles pour relire ou corriger) et sortie-mots.json.
Toujours regarder quelques images de la vidéo finale et relire le .srt avant de livrer.
"""
import argparse, json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
FONTS = os.path.join(ASSETS, "fonts")
W, H, FPS = 1080, 1920, 30
OR = "E3A73C"
SILENCE_MAX = 0.6       # au-delà, on coupe
MARGE_COUPE = 0.12      # on garde un peu d'air autour de chaque prise de parole


def sh(*cmd):
    subprocess.run(cmd, check=True)


def duree(fichier):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", fichier],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


LEXIQUE = ("Affaires Québec, Rouba Hamadi, Rénald Rabathaly, Réseau accès PME, PME MTL, SADC, CAE, MRC, "
           "Entreprendre ici, Futurpreneur, Equifax, TransUnion, ISDE, Statistique Canada, Registraire des entreprises, "
           "MEIE, MIFI, IDÉ Trois-Rivières, Mauricie, bailleur de fonds, mise de fonds, plan d'affaires.")


def transcrire(fichier, script=None, modele="small"):
    """Transcription locale ; le lexique et le script lu orientent la reconnaissance des noms propres."""
    from faster_whisper import WhisperModel
    invite = LEXIQUE + (" " + " ".join(script.split())[-600:] if script else "")
    m = WhisperModel(modele, device="cpu", compute_type="int8")
    segments, _ = m.transcribe(fichier, language="fr", word_timestamps=True, vad_filter=True, initial_prompt=invite)
    mots = []
    for s in segments:
        for w in s.words:
            txt = w.word.strip()
            if not txt:
                continue
            if mots and txt in "?!:;":
                mots[-1]["mot"] += "\u00a0" + txt; continue
            # « s' » + « y » ou « 'y » : on recolle au mot précédent, sans espace
            if mots and (txt.startswith("'") or txt.startswith("’") or mots[-1]["mot"].endswith(("'", "’"))) or (mots and not w.word.startswith(" ")):
                mots[-1]["mot"] += txt.replace("'", "’"); mots[-1]["fin"] = round(w.end, 3)
            else:
                mots.append({"mot": txt.replace("'", "’"), "debut": round(w.start, 3), "fin": round(w.end, 3)})
    return mots


def plages_son(fichier, total):
    """Plages à garder : tout sauf les silences de plus de SILENCE_MAX (détectés dans le son par ffmpeg)."""
    err = subprocess.run(["ffmpeg", "-v", "info", "-i", fichier, "-af", f"silencedetect=noise=-35dB:d={SILENCE_MAX}",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    debuts = [float(x.split("silence_start: ")[1].split()[0]) for x in err.splitlines() if "silence_start: " in x]
    fins = [float(x.split("silence_end: ")[1].split()[0]) for x in err.splitlines() if "silence_end: " in x]
    fins += [total] * (len(debuts) - len(fins))
    plages, t = [], 0.0
    for d, f in zip(debuts, fins):
        a, b = d + MARGE_COUPE, f - MARGE_COUPE
        if b - a > 0.05:
            if a > t: plages.append((t, a))
            t = b
    if total > t: plages.append((t, total))
    return plages or [(0.0, total)]


def recaler(mots, plages):
    """Temps des mots après suppression des silences (un temps tombé dans un silence est ramené à sa bordure)."""
    def nouveau(t):
        acc = 0.0
        for a, b in plages:
            if t < a: return acc
            if t <= b: return acc + (t - a)
            acc += b - a
        return acc
    out = []
    for m in mots:
        d, f = nouveau(m["debut"]), nouveau(m["fin"])
        if f - d > 0.01:
            out.append({**m, "debut": round(d, 3), "fin": round(f, 3)})
    return out


def blocs(mots, n=4):
    """Groupes de 3-4 mots, coupés aussi après une ponctuation forte."""
    g, cur = [], []
    for m in mots:
        cur.append(m)
        if len(cur) >= n or m["mot"][-1:] in ".?!,;:":
            g.append(cur); cur = []
    if cur:
        g.append(cur)
    return g


def temps_ass(t):
    h, r = divmod(max(0.0, t), 3600); m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def ecrire_ass(mots, chemin):
    entete = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: AQ,DM Sans,66,&H00DCE4E8,&H00DCE4E8,&H00201F23,&H96201F23,1,0,0,0,100,100,0,0,1,5,0,2,110,110,430,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lignes = []
    or_ass = "&H" + OR[4:6] + OR[2:4] + OR[0:2] + "&"   # BGR
    for g in blocs(mots):
        for i, m in enumerate(g):
            fin = g[i + 1]["debut"] if i + 1 < len(g) else m["fin"] + 0.15
            texte = " ".join((f"{{\\c{or_ass}}}{x['mot']}{{\\c&HDCE4E8&}}" if j == i else x["mot"]) for j, x in enumerate(g))
            lignes.append(f"Dialogue: 0,{temps_ass(m['debut'])},{temps_ass(fin)},AQ,,0,0,0,,{texte}")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(entete + "\n".join(lignes) + "\n")


def ecrire_srt(mots, chemin):
    def ts(t):
        h, r = divmod(t, 3600); m, s = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
    with open(chemin, "w", encoding="utf-8") as f:
        for k, g in enumerate(blocs(mots), 1):
            f.write(f"{k}\n{ts(g[0]['debut'])} --> {ts(g[-1]['fin'])}\n{' '.join(m['mot'] for m in g)}\n\n")


def bandeau(nom, fonction, chemin):
    """Style équipe : étiquette or « L'ÉQUIPE » (Figtree 800), nom blanc Figtree 800, fonction en or."""
    def figtree(taille, poids):
        f = ImageFont.truetype(os.path.join(FONTS, "Figtree[wght].ttf"), taille)
        try: f.set_variation_by_axes([poids])
        except Exception: pass
        return f
    img = Image.new("RGBA", (W, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    fe, fn, ff = figtree(26, 800), figtree(58, 800), figtree(34, 600)
    largeur = max(d.textlength(nom, font=fn), d.textlength(fonction, font=ff)) + 100
    d.rectangle([88, 40, 88 + largeur, 270], fill=(35, 31, 32, 235))
    d.rectangle([88, 40, 96, 270], fill=(227, 167, 60, 255))
    d.text((130, 62), "L'ÉQUIPE", font=fe, fill=(227, 167, 60, 255))
    d.text((128, 104), nom, font=fn, fill=(255, 255, 255, 255))
    d.text((130, 186), fonction, font=ff, fill=(227, 167, 60, 255))
    img.save(chemin)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brute"); ap.add_argument("sortie")
    ap.add_argument("--nom", required=True); ap.add_argument("--fonction", required=True)
    ap.add_argument("--mots", help="JSON de mots minutés (sinon transcription automatique)")
    ap.add_argument("--sans-coupe", action="store_true")
    ap.add_argument("--script", help="script lu (Markdown ou texte) pour guider la transcription")
    ap.add_argument("--modele", default="small", help="small (rapide) ou medium (plus précis, plus lent)")
    ap.add_argument("--outro", default=os.path.join(HERE, "exemples", "outro-video.json"))
    a = ap.parse_args()
    tmp = tempfile.mkdtemp()

    # 1. recadrage vertical
    norm = os.path.join(tmp, "norm.mp4")
    sh("ffmpeg", "-y", "-v", "error", "-i", a.brute, "-vf",
       f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
       "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-ar", "48000", "-ac", "2", norm)

    # 2. mots
    script = open(a.script, encoding="utf-8").read() if a.script else None
    mots = json.load(open(a.mots, encoding="utf-8")) if a.mots else transcrire(norm, script, a.modele)
    total = duree(norm)

    # 3. coupe des silences
    plages = [(0.0, total)] if a.sans_coupe else plages_son(norm, total)
    mots = recaler(mots, plages)
    coupe = os.path.join(tmp, "coupe.mp4")
    sel = "+".join(f"between(t,{x:.3f},{y:.3f})" for x, y in plages)
    sh("ffmpeg", "-y", "-v", "error", "-i", norm,
       "-vf", f"select='{sel}',setpts=N/FRAME_RATE/TB", "-af", f"aselect='{sel}',asetpts=N/SR/TB",
       "-c:v", "libx264", "-crf", "18", "-c:a", "aac", coupe)

    # 4-5. sous-titres + bandeau
    base = os.path.splitext(a.sortie)[0]
    ass = os.path.join(tmp, "st.ass"); ecrire_ass(mots, ass); ecrire_srt(mots, base + ".srt")
    json.dump(mots, open(base + "-mots.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    png = os.path.join(tmp, "bandeau.png"); bandeau(a.nom, a.fonction, png)
    habille = os.path.join(tmp, "habille.mp4")
    sh("ffmpeg", "-y", "-v", "error", "-i", coupe, "-loop", "1", "-t", "6", "-i", png, "-filter_complex",
       "[1:v]format=rgba,fade=in:st=0.8:d=0.4:alpha=1,fade=out:st=4.2:d=0.4:alpha=1[b];"
       f"[0:v][b]overlay=0:1100:shortest=0:eof_action=pass[v1];"
       f"[v1]subtitles={ass}:fontsdir={FONTS}[v]",
       "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "18", "-c:a", "aac", habille)

    # 6. carton de fin
    outro = os.path.join(tmp, "outro.mp4")
    sh(sys.executable, os.path.join(HERE, "reel.py"), a.outro, outro)
    sh("ffmpeg", "-y", "-v", "error", "-i", habille, "-i", outro, "-filter_complex",
       "[0:v]setsar=1[a];[1:v]setsar=1[b];[0:a]aresample=48000,aformat=channel_layouts=stereo[x];"
       "[1:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.6[y];[a][x][b][y]concat=n=2:v=1:a=1[v][au]",
       "-map", "[v]", "-map", "[au]", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.sortie)
    print(f"OK : {a.sortie} ({duree(a.sortie):.1f} s) ; sous-titres : {base}.srt — relire avant publication")


if __name__ == "__main__":
    main()
