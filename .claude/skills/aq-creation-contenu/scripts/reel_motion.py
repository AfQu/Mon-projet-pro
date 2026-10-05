"""Reel motion design Affaires Québec (1080x1920, 30 i/s, H.264 + AAC).

Usage :
  python3 reel_motion.py scenes.json sortie.mp4

scenes.json = liste de scènes (4 s chacune par défaut, clé "duree" pour changer) :
[
  {"type": "titre", "lignes": ["On arrive."], "sous": ["Le pont entre votre vision", "et la réalité locale"], "filet": true},
  {"type": "titre", "lignes": ["Un projet", "d'entreprise", "au Québec ?"], "sous": ["Structure  ·  financement  ·  réseau", "Nous ouvrons les bonnes portes."]},
  {"type": "pile", "mots": ["Structurer.", "Financer.", "Démontrer."], "pied": "affairesquebec.ca"},
  {"type": "logo", "accroche": "QUELQUE CHOSE COMMENCE", "petit": "RENDEZ-VOUS LE", "grand": "JJ.MM.AA", "note": "19 h · heure de Montréal · en ligne"}
]
Transitions : volet or diagonal entre les scènes. Musique : musique.py (synthétisée, libre de droits).
Dépendances : Pillow, ffmpeg. Toujours contrôler quelques images clés avant de livrer.
"""
import json, math, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
W, H, FPS = 1080, 1920, 30
BG = (35, 31, 32); GOLD = (228, 168, 58); DIM = (150, 120, 60); SUB = (228, 168, 58)
BEAT = 0.5
SERIF = os.path.join(ASSETS, "fonts", "LibreCaslonDisplay-Regular.ttf")
SANS = os.path.join(ASSETS, "fonts", "DMSans-Variable.ttf")
LOGO = Image.open(os.path.join(ASSETS, "logos", "logo-3-2-fond-sombre.png"))
MARK = Image.open(os.path.join(ASSETS, "logos", "symbole-or.png"))

cl = lambda x: max(0, min(1, x))
def eo(x): x = cl(x); return 1 - (1 - x) ** 3
def back(x): x = cl(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def eio(x): x = cl(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
_FC = {}
def font(kind, s, w=400):
    k = (kind, s, w)
    if k not in _FC:
        if kind == "s": _FC[k] = ImageFont.truetype(SERIF, s)
        else:
            f = ImageFont.truetype(SANS, s)
            try: f.set_variation_by_axes([14, w])
            except Exception: pass
            _FC[k] = f
    return _FC[k]

def fit_serif(lines, maxw=960, start=220):
    s = start
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    while s > 80 and max(d.textlength(l, font=font("s", s)) for l in lines) > maxw: s -= 6
    return s

def reveal(img, txt, f, y, p, color=GOLD, spacing=0, scale=1.0):
    if p <= 0: return
    tmp = Image.new("RGBA", (W, 400), (0, 0, 0, 0)); d = ImageDraw.Draw(tmp)
    if spacing:
        ws = [d.textlength(c, font=f) for c in txt]; x = (W - sum(ws) - spacing * (len(txt) - 1)) / 2
        for c, w in zip(txt, ws): d.text((x, 60), c, font=f, fill=color); x += w + spacing
    else:
        d.text(((W - d.textlength(txt, font=f)) / 2, 60), txt, font=f, fill=color)
    bb = tmp.getbbox()
    if not bb: return
    crop = tmp.crop((0, 0, W, bb[3] + 10))
    if scale != 1.0:
        nw, nh = int(W * scale), int(crop.height * scale); r = crop.resize((nw, nh), Image.LANCZOS)
        crop = Image.new("RGBA", (W, nh), (0, 0, 0, 0)); crop.alpha_composite(r, ((W - nw) // 2, 0))
    h = crop.height; off = int((1 - back(p)) * h * 0.9)
    win = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    if abs(off) < h: win.alpha_composite(crop, (0, off))
    win.putalpha(win.getchannel("A").point(lambda v: int(v * cl(p * 1.6))))
    img.alpha_composite(win, (0, int(y - 60)))

def filet(img, y, p, w=520, th=4):
    if p <= 0: return
    L = int(w * eo(p)); ImageDraw.Draw(img).rectangle([(W - L) / 2, y, (W + L) / 2, y + th], fill=GOLD)

def fond(img, t):
    s = 1.0 + 0.012 * t; mw = int(1500 * s); mh = int(MARK.height * mw / MARK.width)
    m = MARK.resize((mw, mh), Image.BILINEAR); m.putalpha(m.getchannel("A").point(lambda v: int(v * 0.07)))
    img.alpha_composite(m, (int(W - mw * 0.62 + t * 6), int(H - mh * 0.72 - t * 8)))

def pied(img, t):
    L = int(880 * eo((t - 0.2) / 1.2)); ImageDraw.Draw(img).line([((W - L) / 2, 1640), ((W + L) / 2, 1640)], fill=DIM, width=2)
    reveal(img, "AFFAIRES QUÉBEC", font("n", 34), 1690, eo((t - 0.6) / 0.8), spacing=14)

def scene(img, sc, lt):
    ty = sc["type"]
    if ty == "titre":
        lignes = sc["lignes"]; s = fit_serif(lignes, start=220 if len(lignes) == 1 else 175)
        lh = int(s * 0.97); y0 = 860 - (len(lignes) * lh) // 2 - 60
        for k, l in enumerate(lignes): reveal(img, l, font("s", s), y0 + k * lh, (lt - 0.2 - BEAT * k) / 0.6)
        yb = y0 + len(lignes) * lh + 60
        if sc.get("filet"): filet(img, yb, (lt - 1.0) / 0.6); yb += 50
        for k, l in enumerate(sc.get("sous", [])):
            reveal(img, l, font("n", 44, 500 if k == 0 else 400), yb + k * 70, (lt - 1.5 - 0.4 * k) / 0.6)
    elif ty == "pile":
        mots = sc["mots"]; s = fit_serif(mots, start=205); y0 = 900 - len(mots) * 100
        for k, m in enumerate(mots):
            st = 0.25 + 0.7 * k
            punch = 1 + 0.07 * math.exp(-(lt - st - 0.45) * 9) if lt > st + 0.45 else 1.0
            reveal(img, m, font("s", s), y0 + k * 200, (lt - st) / 0.55, scale=punch)
        if sc.get("pied"): reveal(img, sc["pied"], font("n", 40), 1400, (lt - 2.5) / 0.6)
    elif ty == "logo":
        if lt > 0.1:
            p = back((lt - 0.1) / 0.8); lw = int(820 * (0.75 + 0.25 * p)); lh = int(LOGO.height * lw / LOGO.width)
            L = LOGO.resize((lw, lh), Image.LANCZOS); L.putalpha(L.getchannel("A").point(lambda v: int(v * cl((lt - 0.1) / 0.4))))
            img.alpha_composite(L, ((W - lw) // 2, int(700 - lh / 2)))
        if sc.get("accroche"): reveal(img, sc["accroche"], font("n", 44), 950, (lt - 1.1) / 0.6, spacing=16)
        filet(img, 1180, (lt - 1.7) / 0.5, w=120, th=3)
        if sc.get("petit"): reveal(img, sc["petit"], font("n", 36), 1240, (lt - 2.0) / 0.6, spacing=14)
        if sc.get("grand"): reveal(img, sc["grand"], font("n", 96, 600), 1305, (lt - 2.4) / 0.6, spacing=20)
        if sc.get("note"): reveal(img, sc["note"], font("n", 38), 1470, (lt - 2.9) / 0.6)

def main(scenes_path, out):
    scenes = json.load(open(scenes_path))
    starts, t = [], 0.0
    for sc in scenes: starts.append(t); t += float(sc.get("duree", 4.0))
    T = t; cuts = starts[1:]
    tmp = tempfile.mkdtemp()
    for i in range(int(T * FPS)):
        t = i / FPS; img = Image.new("RGBA", (W, H), BG + (255,)); fond(img, t)
        n = sum(t >= c for c in cuts); lt = t - starts[n]
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); scene(layer, scenes[n], lt)
        if scenes[n]["type"] != "logo": pied(layer, t)
        img.alpha_composite(layer)
        d = ImageDraw.Draw(img)
        for c in cuts:
            u = (t - (c - 0.3)) / 0.6
            if 0 <= u <= 1:
                x = int(-W * 1.3 + eio(u) * W * 2.6); sk = 260
                d.polygon([(x, 0), (x + W + sk, 0), (x + W, H), (x - sk, H)], fill=GOLD)
                d.polygon([(x + W + sk, 0), (x + W + sk + 90, 0), (x + W + 90, H), (x + W, H)], fill=BG)
        if t > T - 0.6: img.alpha_composite(Image.new("RGBA", (W, H), BG + (int(255 * cl((t - (T - 0.6)) / 0.6)),)))
        img.convert("RGB").save(f"{tmp}/{i:04d}.png")
    wav = os.path.join(tmp, "musique.wav")
    subprocess.run([sys.executable, os.path.join(HERE, "musique.py"), str(T), json.dumps(cuts), wav], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/%04d.png", "-i", wav,
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    print(f"OK : {out} ({T:.1f} s) — images dans {tmp}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
