"""Vidéo UPES-UNSA 9:16 sur la bande-son upess-spoken-word-musique.mp3."""
import math, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "..", "..", "visuels", "assets", "fonts", "Figtree[wght].ttf")
W, H, FPS, T = 1080, 1920, 30, 35.1
# Recalage : instants de début de phrase de la voix pour laquelle les temps ci-dessous ont été écrits (OLD) et de la voix actuelle (NEW)
OLD = [4.8, 7.0, 11.3, 15.8, 20.6, 22.7, 24.4, 25.6, 29.2]
NEW = [4.8, 7.038, 11.409, 15.885, 20.948, 22.967, 24.702, 25.894, 29.584]
def warp(t):
    d = 0.0
    for o, n in zip(OLD, NEW):
        if t >= n - 0.05: d = n - o
    return t - d
NAVY, BLUE, LIGHT, RED, WHITE = (27, 48, 96), (46, 95, 168), (155, 208, 238), (227, 6, 19), (255, 255, 255)
cl = lambda x: max(0.0, min(1.0, x))
def eo(x): x = cl(x); return 1 - (1 - x) ** 3
def back(x): x = cl(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
_F = {}
def F(s, w=800):
    if (s, w) not in _F:
        f = ImageFont.truetype(FONT, s)
        try: f.set_variation_by_axes([w])
        except Exception: pass
        _F[(s, w)] = f
    return _F[(s, w)]
LOGO = Image.open(os.path.join(HERE, "logo.png")).convert("RGBA")
AFF = Image.open(os.path.join(HERE, "affiche.jpg")).convert("RGB")
PHOTO = AFF.crop((440, 250, 1064, 560))  # bandeau des agents
# fond : dégradé marine -> bleu, vague claire animée
BG = Image.new("RGB", (W, H))
d = ImageDraw.Draw(BG)
for y in range(H):
    k = y / H; d.line([(0, y), (W, y)], fill=tuple(int(NAVY[i] + (BLUE[i] - NAVY[i]) * k) for i in range(3)))
def fond(t):
    img = BG.copy().convert("RGBA"); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    for j, (amp, base, a) in enumerate([(40, 1500, 40), (55, 1580, 28)]):
        pts = [(x, base + amp * math.sin(x / 170 + t * (0.9 + 0.3 * j) + j)) for x in range(0, W + 20, 20)]
        dl.polygon(pts + [(W, H), (0, H)], fill=LIGHT + (a,))
    img.alpha_composite(lay); return img
def texte(img, s, size, cx, cy, p, color=WHITE, slam=True, w=800, shadow=True):
    """Mot qui « frappe » : grossit puis se pose, avec ombre."""
    if p <= 0: return
    f = F(size, w); dd = ImageDraw.Draw(img); tw = dd.textlength(s, font=f)
    sc = 1 + 0.45 * (1 - back(p / 0.35)) if slam else 1
    a = int(255 * cl(p / 0.12))
    tmp = Image.new("RGBA", (int(tw) + 60, size + 80), (0, 0, 0, 0)); dt = ImageDraw.Draw(tmp)
    if shadow: dt.text((34, 44), s, font=f, fill=(0, 0, 0, int(a * 0.45)))
    dt.text((30, 36), s, font=f, fill=color + (a,))
    if sc != 1: tmp = tmp.resize((int(tmp.width * sc), int(tmp.height * sc)), Image.LANCZOS)
    img.alpha_composite(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)))
def ajuste(s, maxw, start):
    dd = ImageDraw.Draw(Image.new("RGB", (5, 5))); z = start
    while dd.textlength(s, font=F(z)) > maxw and z > 40: z -= 4
    return z
def tuile(img, s, cx, cy, p, col):
    if p <= 0: return
    dy = int((1 - back(p / 0.5)) * -500); w, h = 860, 190
    lay = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.rounded_rectangle([14, 16, w + 14, h + 16], 18, fill=(0, 0, 0, 90))
    dl.rounded_rectangle([0, 0, w, h], 18, fill=col + (255,), outline=(235, 235, 235, 255), width=6)
    f = F(ajuste(s, w - 80, 110)); tw = dl.textlength(s, font=f)
    dl.text(((w - tw) / 2, h / 2 - f.size * 0.62), s, font=f, fill=WHITE + (255,))
    img.alpha_composite(lay, (int(cx - w / 2), int(cy - h / 2 + dy)))
def logo(img, cx, cy, wl, p, pulse=0.0):
    if p <= 0: return
    s = (0.6 + 0.4 * back(p / 0.7)) * (1 + pulse); lw = int(wl * s); lh = int(LOGO.height * lw / LOGO.width)
    L = LOGO.resize((lw, lh), Image.LANCZOS); L.putalpha(L.getchannel("A").point(lambda v: int(v * cl(p / 0.25))))
    img.alpha_composite(L, (int(cx - lw / 2), int(cy - lh / 2)))
SOUS = [(4.55, 6.6, "Collègues de l'Espace Sud…"), (6.75, 11.0, "Titulaires ou contractuels, nous avons tous les mêmes essentiels :"),
        (11.2, 15.7, "nos droits… nos acquis… notre dignité."), (15.85, 20.45, "L'UPES remonte vos doléances, dialogue avec l'autorité, et reste à vos côtés."),
        (20.55, 22.5, "Tout moun cé moun !"), (22.6, 23.85, "Du 3 au 10 décembre,"), (23.9, 25.55, "ba nou fos la :"), (25.6, 28.8, "votez UPES-UNSA !"),
        (29.05, 33.2, "UPES. Union des Personnels de l'Espace Sud.")]
def sous_titre(img, t):
    for a, b, s in SOUS:
        if a <= t < b:
            f = F(44, 600); dd = ImageDraw.Draw(img); mots = s.split(); lignes, cur = [], ""
            for m in mots:
                e = (cur + " " + m).strip()
                if dd.textlength(e, font=f) <= 900: cur = e
                else: lignes.append(cur); cur = m
            lignes.append(cur); y = 1630 - 30 * (len(lignes) - 1)
            al = cl((t - a) / 0.15) * cl((b - t) / 0.15)
            for l in lignes:
                tw = dd.textlength(l, font=f); pad = 18
                box = Image.new("RGBA", (int(tw) + 2 * pad, 64), (10, 20, 45, int(185 * al))); img.alpha_composite(box, (int((W - tw) / 2 - pad), y - 6))
                ImageDraw.Draw(img).text(((W - tw) / 2, y), l, font=f, fill=WHITE + (int(255 * al),)); y += 66
def frame(t):
    img = fond(t)
    if t < 6.6:  # 1. intro tibwa -> logo
        pulse = 0.025 * max(0, 1 - ((t % 0.6) / 0.2)) if t > 1.0 else 0
        logo(img, W / 2, 820, 760, t - 0.3, pulse)
    elif t < 11.0:  # 2. un mot par frappe
        for i, (s, t0, col) in enumerate([("TITULAIRES", 6.78, WHITE), ("CONTRACTUELS", 7.78, LIGHT), ("MÊMES ESSENTIELS", 9.64, WHITE)]):
            z = ajuste(s, 980, 150); texte(img, s, z, W / 2, 620 + i * 280, t - t0, col)
        if t > 9.64: ImageDraw.Draw(img).rectangle([W / 2 - 160, 1310, W / 2 + 160, 1320], fill=RED)
    elif t < 15.7:  # 3. photo des agents + droits
        k = (t - 11.0) / 4.7; z = (W + 160) / PHOTO.width * (1 + 0.1 * k); pw = int(PHOTO.width * z * 1.0); ph = int(PHOTO.height * z)
        P = PHOTO.resize((pw, ph), Image.LANCZOS); x0 = int((W - pw) / 2 - 140 * k)
        img.paste(P, (x0 + 70, 230)); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); do = ImageDraw.Draw(ov)
        for y in range(230 + ph - 300, 230 + ph): do.line([(0, y), (W, y)], fill=NAVY + (int(255 * (y - (230 + ph - 300)) / 300),))
        img.alpha_composite(ov)
        for i, (s, t0, col) in enumerate([("Nos droits", 11.22, WHITE), ("Nos acquis", 12.6, LIGHT), ("Notre dignité", 14.02, WHITE)]):
            texte(img, s, 120, W / 2, 1020 + i * 160, t - t0, col)
    elif t < 20.45:  # 4. break : trois tuiles
        for i, (s, t0, col) in enumerate([("ÉCOUTER", 16.14, RED), ("DIALOGUER", 17.7, (120, 185, 225)), ("PROPOSER", 19.04, BLUE)]):
            tuile(img, s, W / 2, 560 + i * 270, t - t0, col)
    elif t < 22.5:  # 5. climax
        p = t - 20.58
        if 0 <= p < 0.12: img.alpha_composite(Image.new("RGBA", (W, H), WHITE + (int(255 * (1 - p / 0.12)),)))
        sh = 18 * math.exp(-p * 5) * math.sin(p * 60) if p > 0 else 0
        for i, (s, col) in enumerate([("TOUT", WHITE), ("MOUN", RED), ("CÉ", WHITE), ("MOUN !", RED)]):
            texte(img, s, 230, W / 2 + sh, 470 + i * 250, p - 0.08 * i, col)
    elif t < 23.85:  # 6. montée : élections
        texte(img, "ÉLECTIONS", 150, W / 2, 620, t - 22.64, WHITE)
        texte(img, "PROFESSIONNELLES", ajuste("PROFESSIONNELLES", 980, 120), W / 2, 790, t - 22.73, WHITE)
        texte(img, "du 3 au 10", 120, W / 2, 1010, t - 22.9, LIGHT)
        texte(img, "décembre 2026", 120, W / 2, 1150, t - 23.4, LIGHT)
    else:  # 7. outro
        if t < 28.9:
            texte(img, "ba nou fos la !", 120, W / 2, 470, t - 23.92, LIGHT)
            texte(img, "VOTEZ", 190, W / 2, 760, t - 25.66, WHITE)
            texte(img, "UPES-UNSA", ajuste("UPES-UNSA", 1000, 190), W / 2, 960, t - 25.9, RED)
            if t > 26.2: ImageDraw.Draw(img).rectangle([W / 2 - 300, 1090, W / 2 + 300, 1100], fill=WHITE)
        else:
            logo(img, W / 2, 800, 720, t - 29.0)
            texte(img, "Votez UPES-UNSA", 84, W / 2, 1330, t - 29.5, WHITE, slam=False)
            texte(img, "du 3 au 10 décembre 2026", 64, W / 2, 1430, t - 29.9, LIGHT, slam=False, w=700)
    # éclair blanc sur chaque changement de scène
    for c in (6.6, 11.0, 15.7, 22.5, 23.85, 28.9):
        if 0 <= t - c < 0.1: img.alpha_composite(Image.new("RGBA", (W, H), WHITE + (int(200 * (1 - (t - c) / 0.1)),)))
    sous_titre(img, t)
    if t > T - 1.5: img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * cl((t - (T - 1.5)) / 1.5)))))
    if t < 0.4: img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - t / 0.4)))))
    return img.convert("RGB")
if __name__ == "__main__":
    audio, out = sys.argv[1], sys.argv[2]; tmp = tempfile.mkdtemp()
    if len(sys.argv) > 3:
        for s in sys.argv[3:]: frame(float(s)).save(os.path.join(HERE, f"apercu_{s}.png"))
        sys.exit()
    for i in range(int(T * FPS)): frame(warp(i / FPS)).save(f"{tmp}/{i:04d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/%04d.png", "-i", audio, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    print("OK", out)
