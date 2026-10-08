#!/usr/bin/env python3
"""Reel « vidéo » Affaires Québec : vrais plans vidéo (banque libre de droits ou tournage),
étalonnage chaud, lent zoom, textes animés aux couleurs de la charte, transitions variées,
musique libre de droits et carton de fin AQ (reel.py).

Usage :
    python3 visuels/outils/reel_video.py scenario.json sortie.mp4

scenario.json :
{
  "plans": [
    {"clip": "clips/boutique.mp4", "debut": 1.5, "duree": 3.2,
     "texte": "Près de *16 000* entreprises cherchent une relève", "style": "accroche",
     "transition": "fade"},
    {"clip": "clips/atelier.mp4", "duree": 3.0, "texte": "Des clients. Une équipe. *Déjà là.*",
     "style": "soustitre", "transition": "slideleft"}
  ],
  "outro": "visuels/outils/exemples/outro-video.json"
}
- style : « accroche » (Caslon, grand, centré haut) ou « soustitre » (DM Sans gras, bas, bandeau).
- *mot* : mot affiché en or.
- x : position du recadrage vertical dans l'image (0 = gauche, 0,5 = centre, 1 = droite).
- Les bleus et cyans sont désaturés automatiquement (charte : jamais de bleu).
- transition : type xfade de ffmpeg vers ce plan (fade, slideleft, slideup, circleopen, wipeleft, smoothleft…).
Le texte reste hors des 250 px du haut et du bas (zones des boutons Instagram).
Toujours regarder des images clés avant de livrer.
"""
import json, os, re, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "assets", "fonts")
W, H, FPS = 1080, 1920, 30
OR = (227, 167, 60); BLANC = (245, 242, 236); NOIR = (35, 31, 32)
XF = 0.5  # durée des transitions (s)


def sh(*cmd):
    subprocess.run(cmd, check=True)


def police(nom, taille, poids=None):
    f = ImageFont.truetype(os.path.join(FONTS, nom), taille)
    if poids is not None:
        try: f.set_variation_by_axes([14, poids] if "DMSans" in nom else [poids])
        except Exception: pass
    return f


def segments(txt):
    """'a *b* c' -> [('a ', False), ('b', True), (' c', False)]"""
    out = []
    for i, part in enumerate(re.split(r"\*", txt)):
        if part: out.append((part, i % 2 == 1))
    return out


def lignes(txt, f, maxw):
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    mots = [(m, gold) for seg, gold in segments(txt) for m in seg.split(" ") if m]
    res, cur = [], []
    for m in mots:
        essai = " ".join(x for x, _ in cur + [m])
        if cur and d.textlength(essai, font=f) > maxw:
            res.append(cur); cur = [m]
        else:
            cur.append(m)
    if cur: res.append(cur)
    return res


def calque_texte(texte, style, chemin):
    """PNG transparent 1080 × 1920 : dégradé de lisibilité + texte."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grad = Image.new("L", (1, H))
    for y in range(H):
        if style == "accroche":
            a = max(0, 1 - y / 1100) * 170 + max(0, (y - 1300) / 620) * 120
        else:
            a = max(0, (y - 900) / 1020) * 210
        grad.putpixel((0, y), int(min(255, a)))
    img.putalpha(grad.resize((W, H)))
    img = Image.composite(Image.new("RGBA", (W, H), NOIR + (255,)), Image.new("RGBA", (W, H), (0, 0, 0, 0)), img.getchannel("A"))
    d = ImageDraw.Draw(img)
    if style == "accroche":
        f = police("LibreCaslonDisplay-Regular.ttf", 104); interligne = 112; y = 330
    else:
        f = police("DMSans[opsz,wght].ttf", 62, 700); interligne = 80
    ls = lignes(texte, f, 900)
    if style != "accroche":
        y = 1640 - len(ls) * interligne
    for ligne in ls:
        largeur = d.textlength(" ".join(m for m, _ in ligne), font=f)
        x = (W - largeur) / 2
        for k, (mot, gold) in enumerate(ligne):
            mot_aff = mot + (" " if k < len(ligne) - 1 else "")
            d.text((x + 3, y + 3), mot_aff, font=f, fill=(0, 0, 0, 160))  # ombre douce pour la lisibilité
            d.text((x, y), mot_aff, font=f, fill=(OR if gold else BLANC) + (255,))
            x += d.textlength(mot_aff, font=f)
        y += interligne
    img.save(chemin)


def plan(p, i, tmp):
    """Un plan : recadrage vertical, étalonnage, lent zoom, texte en fondu."""
    dur = float(p["duree"]); out = os.path.join(tmp, f"plan{i:02d}.mp4")
    png = os.path.join(tmp, f"texte{i:02d}.png"); calque_texte(p.get("texte", ""), p.get("style", "soustitre"), png)
    z = 0.06 / max(dur, 0.1)  # zoom progressif de 6 % sur la durée du plan
    vf = (f"[0:v]trim=start={p.get('debut', 0)}:duration={dur},setpts=PTS-STARTPTS,fps={FPS},"
          f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}:(iw-{W})*{p.get('x', 0.5)}:(ih-{H})/2,"
          f"scale=w='iw*(1+{z}*t)':h='ih*(1+{z}*t)':eval=frame,crop={W}:{H},"
          "huesaturation=colors=c+b:saturation=-1:strength=6,unsharp=5:5:0.6,"  # charte : jamais de bleu
          "eq=saturation=0.82:contrast=1.06:brightness=-0.02,colorbalance=rs=0.05:gs=0.01:bs=-0.06,"
          "vignette=PI/5[v];"
          f"[1:v]format=rgba,fade=in:st=0.15:d=0.45:alpha=1[t];[v][t]overlay=0:0,format=yuv420p[o]")
    sh("ffmpeg", "-y", "-v", "error", "-i", p["clip"], "-loop", "1", "-t", str(dur), "-i", png,
       "-filter_complex", vf, "-map", "[o]", "-an", "-c:v", "libx264", "-crf", "18", "-r", str(FPS), out)
    return out


def main(scenario, sortie):
    sc = json.load(open(scenario, encoding="utf-8"))
    tmp = tempfile.mkdtemp()
    fichiers = [plan(p, i, tmp) for i, p in enumerate(sc["plans"])]
    durees = [float(p["duree"]) for p in sc["plans"]]
    outro = os.path.join(tmp, "outro.mp4")
    sh(sys.executable, os.path.join(HERE, "reel.py"), sc.get("outro", os.path.join(HERE, "exemples", "outro-video.json")), outro)
    fichiers.append(outro); durees.append(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", outro], capture_output=True, text=True).stdout))
    transitions = [p.get("transition", "fade") for p in sc["plans"][1:]] + ["fade"]
    entrees = sum((["-i", f] for f in fichiers), [])
    chaine, prec, t = [], "[0:v]", 0.0
    for k in range(1, len(fichiers)):
        t += durees[k - 1] - XF
        etiquette = f"[x{k}]"
        chaine.append(f"{prec}[{k}:v]xfade=transition={transitions[k - 1]}:duration={XF}:offset={t:.3f}{etiquette}")
        prec = etiquette
    total = sum(durees) - XF * (len(fichiers) - 1)
    video = os.path.join(tmp, "video.mp4")
    sh("ffmpeg", "-y", "-v", "error", *entrees, "-filter_complex", ";".join(chaine), "-map", prec,
       "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", video)
    coupes = []; t = 0.0
    for dd in durees[:-1]:
        t += dd - XF; coupes.append(round(t + XF / 2, 2))
    wav = os.path.join(tmp, "musique.wav")
    sh(sys.executable, os.path.join(HERE, "musique.py"), str(total), json.dumps(coupes), wav)
    sh("ffmpeg", "-y", "-v", "error", "-i", video, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
       "-shortest", "-movflags", "+faststart", sortie)
    print(f"OK : {sortie} ({total:.1f} s)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
