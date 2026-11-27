"""Vidéo UPES-UNSA v2 (chanson longue), 9:16, calée sur segments.json (voix_v2.py)."""
import json, math, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
import video as V  # styles et fonctions de la v1
W, H, FPS = V.W, V.H, V.FPS
WHITE, RED, LIGHT, BLUE = V.WHITE, V.RED, V.LIGHT, V.BLUE
SEG = json.load(open(os.path.join(V.HERE, "segments.json"))); S = SEG["segments"]; T = SEG["duree"] + 1.0
def at(i, frac=0.0): s = S[i]; return s["debut"] + (s["fin"] - s["debut"]) * frac
def pos(i, mot):  # instant approximatif d'un mot dans la phrase i
    a = S[i]["aff"].lower(); k = a.find(mot.lower()); return at(i, max(0, k) / max(1, len(a)))
def mots(img, t, items, y0=560, dy=260, size=150):
    for k, (s, t0, col) in enumerate(items):
        V.texte(img, s, V.ajuste(s, 980, size), W / 2, y0 + k * dy, t - t0, col)
def photo(img, t, t0, t1):
    k = (t - t0) / max(0.1, t1 - t0); z = (W + 160) / V.PHOTO.width * (1 + 0.1 * k)
    P = V.PHOTO.resize((int(V.PHOTO.width * z), int(V.PHOTO.height * z)), Image.LANCZOS)
    img.paste(P, (int((W - P.width) / 2 - 140 * k + 70), 230)); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); do = ImageDraw.Draw(ov)
    for y in range(230 + P.height - 300, 230 + P.height): do.line([(0, y), (W, y)], fill=V.NAVY + (int(255 * (y - (230 + P.height - 300)) / 300),))
    img.alpha_composite(ov)
# scènes : (début, fonction)
def sc0(img, t):
    V.logo(img, W / 2, 640, 640, t - 0.3, 0.025 * max(0, 1 - ((t % 0.6) / 0.2)) if t > 1 else 0)
    V.texte(img, "ÉLECTIONS PROFESSIONNELLES", V.ajuste("ÉLECTIONS PROFESSIONNELLES", 980, 80), W / 2, 1110, t - at(0), WHITE)
    V.texte(img, "MARTINIQUE", 90, W / 2, 1220, t - pos(0, "martinique"), LIGHT)
    V.texte(img, "du 3 au 10 décembre 2026", 64, W / 2, 1330, t - pos(0, "du 3"), WHITE, w=700)
def sc1(img, t): mots(img, t, [("L'ESPACE SUD", at(1), WHITE), ("EN AVANT !", pos(1, "en avant"), RED), ("tous ensemble", pos(1, "tous"), LIGHT), ("avec l'UPES", pos(1, "avec"), WHITE)], 520, 230, 150)
def sc2(img, t):
    mots(img, t, [("TOUJOURS PRÉSENTS", at(2), WHITE), ("pour défendre", pos(2, "pour"), LIGHT), ("vos intérêts", pos(2, "vos"), LIGHT)], 500, 200, 130)
    p = t - at(3); sh = 14 * math.exp(-p * 6) * math.sin(p * 60) if p > 0 else 0
    V.texte(img, "UPES !", 260, W / 2 + sh, 1180, p, RED)
def sc3(img, t):
    mots(img, t, [("TITULAIRES", at(4), WHITE), ("CONTRACTUELS", pos(4, "contractuels"), LIGHT), ("MÊMES ESSENTIELS", pos(4, "mêmes"), WHITE)], 600, 280, 150)
def sc4(img, t):
    photo(img, t, at(5), S[6]["fin"])
    for k, (s, t0, col) in enumerate([("Nos droits", pos(5, "nos droits"), WHITE), ("Nos acquis", pos(5, "nos acquis"), LIGHT), ("Notre dignité", pos(5, "notre"), WHITE)]):
        V.texte(img, s, 112, W / 2, 900 + k * 130, t - t0, col)
    V.texte(img, "ENSEMBLE,", 110, W / 2, 1390, t - at(6), RED)
    V.texte(img, "ON VA LES FAIRE RESPECTER !", V.ajuste("ON VA LES FAIRE RESPECTER !", 990, 90), W / 2, 1510, t - pos(6, "on va"), RED)
def sc5(img, t):
    for k, (s, t0, col) in enumerate([("REMONTER", at(7), RED), ("DIALOGUER", pos(7, "dialoguer"), (120, 185, 225)), ("ÉCHANGER", pos(7, "échanger"), BLUE)]):
        V.tuile(img, s, W / 2, 560 + k * 270, t - t0, col)
def sc6(img, t):
    mots(img, t, [("L'UPES", at(8), RED), ("toujours présente", pos(8, "toujours"), WHITE), ("force de proposition", pos(8, "force"), LIGHT)], 480, 220, 150)
    V.texte(img, "à vos côtés", 110, W / 2, 1180, t - at(9), WHITE)
    V.texte(img, "conditions de travail · qualité de vie", V.ajuste("conditions de travail · qualité de vie", 980, 60), W / 2, 1300, t - pos(9, "conditions"), LIGHT, w=700)
def sc7(img, t):
    V.texte(img, "RESPECT", 220, W / 2, 620, t - at(10), WHITE)
    V.texte(img, "de la valeur humaine", 100, W / 2, 820, t - pos(10, "de la"), LIGHT)
def sc8(img, t):
    p = t - at(11)
    if 0 <= p < 0.12: img.alpha_composite(Image.new("RGBA", (W, H), WHITE + (int(255 * (1 - p / 0.12)),)))
    sh = 18 * math.exp(-p * 5) * math.sin(p * 60) if p > 0 else 0
    for k, (s, col) in enumerate([("TOUT", WHITE), ("MOUN", RED), ("CÉ", WHITE), ("MOUN !", RED)]):
        V.texte(img, s, 230, W / 2 + sh, 470 + k * 250, p - 0.08 * k, col)
def sc9(img, t):
    photo(img, t, at(12), S[14]["fin"])
    for k, (s, i, col) in enumerate([("Concilier nos vies", 12, WHITE), ("Préserver nos acquis", 13, LIGHT), ("Améliorer notre avenir", 14, WHITE)]):
        V.texte(img, s, V.ajuste(s, 960, 100), W / 2, 980 + k * 150, t - at(i), col)
def sc10(img, t):
    mots(img, t, [("FAITES ENTENDRE", at(15), WHITE), ("VOS VOIX", pos(15, "vos voix"), WHITE), ("ba nou fos la !", pos(15, "ba nou"), RED)], 540, 240, 160)
def sc11(img, t):
    V.texte(img, "DU 3 AU 10", 170, W / 2, 680, t - at(16), WHITE)
    V.texte(img, "DÉCEMBRE 2026", V.ajuste("DÉCEMBRE 2026", 980, 150), W / 2, 880, t - pos(16, "décembre"), LIGHT)
def sc12(img, t):
    V.logo(img, W / 2, 760, 680, t - at(17))
    V.texte(img, "Union des Personnels de l'Espace Sud", V.ajuste("Union des Personnels de l'Espace Sud", 960, 64), W / 2, 1260, t - pos(17, "union"), WHITE, slam=False, w=700)
def sc13(img, t):
    V.texte(img, "VOTEZ", 200, W / 2, 520, t - at(18), WHITE)
    V.texte(img, "UPES-UNSA", V.ajuste("UPES-UNSA", 1000, 200), W / 2, 730, t - pos(18, "upes"), RED)
    V.texte(img, "TERRITORIAUX,", V.ajuste("TERRITORIAUX,", 980, 120), W / 2, 980, t - at(19), WHITE)
    V.texte(img, "ON EST LÀ !", 130, W / 2, 1130, t - pos(19, "on est"), LIGHT)
def sc14(img, t):
    for k, (s, t0, col) in enumerate([("LIBRES ENSEMBLE", at(20), RED), ("UNIS", pos(20, "unis"), (120, 185, 225)), ("SOLIDAIRES", pos(20, "solidaires"), BLUE)]):
        V.tuile(img, s, W / 2, 460 + k * 250, t - t0, col)
    V.texte(img, "Pour nos droits,", 100, W / 2, 1230, t - at(21), WHITE)
    V.texte(img, "pour nos salaires !", 100, W / 2, 1350, t - pos(21, "pour nos salaires"), LIGHT)
def sc15(img, t):
    V.logo(img, W / 2, 760, 700, t - (S[21]["fin"] + 0.3))
    V.texte(img, "Votez UPES-UNSA", 84, W / 2, 1290, t - (S[21]["fin"] + 0.8), WHITE, slam=False)
    V.texte(img, "du 3 au 10 décembre 2026", 64, W / 2, 1390, t - (S[21]["fin"] + 1.1), LIGHT, slam=False, w=700)
SCENES = [(0, sc0), (S[1]["debut"] - 0.2, sc1), (S[2]["debut"] - 0.2, sc2), (S[4]["debut"] - 0.2, sc3), (S[5]["debut"] - 0.2, sc4), (S[7]["debut"] - 0.3, sc5),
          (S[8]["debut"] - 0.2, sc6), (S[10]["debut"] - 0.2, sc7), (S[11]["debut"] - 0.1, sc8), (S[12]["debut"] - 0.2, sc9), (S[15]["debut"] - 0.2, sc10),
          (S[16]["debut"] - 0.15, sc11), (S[17]["debut"] - 0.2, sc12), (S[18]["debut"] - 0.2, sc13), (S[20]["debut"] - 0.2, sc14), (S[21]["fin"] + 0.2, sc15)]
SOUS = [(s["debut"] - 0.05, s["fin"] + 0.25, s["aff"]) for s in S]
def frame(t):
    img = V.fond(t); n = max(k for k, (d, _) in enumerate(SCENES) if t >= d or k == 0); SCENES[n][1](img, t)
    d = SCENES[n][0]
    if n and 0 <= t - d < 0.1: img.alpha_composite(Image.new("RGBA", (W, H), WHITE + (int(200 * (1 - (t - d) / 0.1)),)))
    V.SOUS[:] = SOUS; V.sous_titre(img, t)
    if t > T - 1.5: img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * V.cl((t - (T - 1.5)) / 1.5)))))
    if t < 0.4: img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - t / 0.4)))))
    return img.convert("RGB")
if __name__ == "__main__":
    if sys.argv[1] == "apercu":
        for s in sys.argv[2:]: frame(float(s)).save(os.path.join(V.HERE, f"apercu_{s}.png"))
        sys.exit()
    audio, out = sys.argv[1], sys.argv[2]; tmp = tempfile.mkdtemp()
    for i in range(int(T * FPS)): frame(i / FPS).save(f"{tmp}/{i:05d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/%05d.png", "-i", audio, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "21", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    print("OK", out)
