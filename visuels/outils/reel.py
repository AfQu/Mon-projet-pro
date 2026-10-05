"""Reel motion design Affaires Québec — copie adaptée du skill aq-creation-contenu
(signature remontée hors des 250 px du bas, assets de visuels/assets).
 (1080x1920, 30 i/s, H.264 + AAC).

Usage :
  python3 visuels/outils/reel.py scenes.json sortie.mp4

scenes.json = liste de scènes (4 s chacune par défaut, clé "duree" pour changer) :
[
  {"type": "titre", "lignes": ["On arrive."], "sous": ["Le pont entre votre vision", "et la réalité locale"], "filet": true},
  {"type": "titre", "lignes": ["Un projet", "d'entreprise", "au Québec ?"], "sous": ["Structure  ·  financement  ·  réseau", "Nous ouvrons les bonnes portes."]},
  {"type": "pile", "mots": ["Structurer.", "Financer.", "Démontrer."], "pied": "affairesquebec.ca"},
  {"type": "logo", "accroche": "QUELQUE CHOSE COMMENCE", "petit": "RENDEZ-VOUS LE", "grand": "JJ.MM.AA", "note": "19 h · heure de Montréal · en ligne"}
]
Formes ajoutées pour varier : "compteur" (chiffre qui défile), "liste" (cases cochées une à une),
  "machine" (question tapée, curseur, puis réponse), "mythe" (idée reçue barrée, puis la réalité).
  Exemples : {"type": "compteur", "prefixe": "Plus de", "valeur": 450, "label": ["conseillers", "dans les MRC"], "source": "Source : …"}
             {"type": "liste", "titre": "…", "items": ["…", "…"]}
             {"type": "machine", "surtitre": "QUESTION", "texte": "…", "reponse": "…"}
             {"type": "mythe", "mythe": "…", "realite": "…"}
Transitions (clé "transition" de la scène qui arrive) : volet (défaut), fondu, glisse, cercle, coupe. Musique : musique.py (synthétisée, libre de droits).
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
SANS = os.path.join(ASSETS, "fonts", "DMSans[opsz,wght].ttf")
LOGO = Image.open(os.path.join(ASSETS, "logo-3-2-fond-sombre.png"))
MARK = Image.open(os.path.join(ASSETS, "symbole-or.png"))

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
    L = int(880 * eo((t - 0.2) / 1.2)); ImageDraw.Draw(img).line([((W - L) / 2, 1540), ((W + L) / 2, 1540)], fill=DIM, width=2)
    reveal(img, "AFFAIRES QUÉBEC", font("n", 34), 1580, eo((t - 0.6) / 0.8), spacing=14)

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
    elif ty in NOUVELLES:
        NOUVELLES[ty](img, sc, lt)

# ---------- Formes supplémentaires (pour varier les Reels) ----------
TXT = (232, 228, 220)

def wrap(txt, f, maxw):
    """Coupe un texte en lignes ; les espaces insécables gardent les mots ensemble."""
    d = ImageDraw.Draw(Image.new("RGB", (10, 10))); lignes, cur = [], ""
    for mot in txt.split(" "):
        essai = (cur + " " + mot).strip()
        if d.textlength(essai, font=f) <= maxw or not cur: cur = essai
        else: lignes.append(cur); cur = mot
    lignes.append(cur); return lignes

def gauche(img, txt, f, x, y, p, color=TXT):
    """Texte aligné à gauche qui glisse depuis la gauche en apparaissant."""
    if p <= 0: return
    a = int(255 * cl(p * 1.4)); dx = int((1 - eo(p)) * -60)
    ImageDraw.Draw(img).text((x + dx, y), txt, font=f, fill=color + (a,))

def s_compteur(img, sc, lt):
    """Grand chiffre qui défile jusqu'à sa valeur, puis son explication."""
    if sc.get("prefixe"): reveal(img, sc["prefixe"], font("n", 50, 500), 520, (lt - 0.1) / 0.5, color=TXT)
    if lt > 0:
        val = int(round(sc["valeur"] * eo((lt - 0.3) / 1.4)))
        txt = f"{val:,}".replace(",", " ") + sc.get("suffixe", "")
        f = font("s", 300); d = ImageDraw.Draw(img)
        d.text(((W - d.textlength(txt, font=f)) / 2, 600), txt, font=f, fill=GOLD + (int(255 * cl(lt / 0.3)),))
    filet(img, 1000, (lt - 1.6) / 0.5, w=160, th=3)
    for k, l in enumerate(sc.get("label", [])):
        reveal(img, l, font("n", 48, 500 if k == 0 else 400), 1050 + k * 70, (lt - 1.8 - 0.3 * k) / 0.6, color=TXT if k else GOLD)
    if sc.get("source"): reveal(img, sc["source"], font("n", 28), 1420, (lt - 2.6) / 0.6, color=DIM)

def s_liste(img, sc, lt):
    """Une seule scène : un titre, puis des cases cochées une à une."""
    ft = font("s", sc.get("taille", 96)); fi = font("n", 46)
    lt_titre = wrap(sc["titre"], ft, 900)
    haut = len(lt_titre) * ft.size * 1.02 + 90 + sum(len(wrap(x, fi, 760)) * 60 + 54 for x in sc["items"])
    y = int(max(330, 900 - haut / 2))
    for k, l in enumerate(lt_titre):
        reveal(img, l, ft, y, (lt - 0.1 - 0.3 * k) / 0.6); y += int(ft.size * 1.02)
    y += 90; d = ImageDraw.Draw(img)
    for i, item in enumerate(sc["items"]):
        st = 0.9 + sc.get("rythme", 0.8) * i; p = (lt - st) / 0.5
        lignes = wrap(item, fi, 760)
        if p > 0:
            a = int(255 * cl(p * 1.5)); c = 46
            d.rectangle([110, y + 8, 110 + c, y + 8 + c], outline=GOLD + (a,), width=4)
            q = eo((lt - st - 0.35) / 0.35)
            if q > 0:  # coche tracée en deux segments
                x0, y0 = 120, y + 32; x1, y1 = 131, y + 44; x2, y2 = 150, y + 18
                k1 = cl(q * 2); d.line([(x0, y0), (x0 + (x1 - x0) * k1, y0 + (y1 - y0) * k1)], fill=GOLD + (255,), width=6)
                if q > .5:
                    k2 = cl(q * 2 - 1); d.line([(x1, y1), (x1 + (x2 - x1) * k2, y1 + (y2 - y1) * k2)], fill=GOLD + (255,), width=6)
        for k, l in enumerate(lignes):
            gauche(img, l, fi, 196, y + k * 60, p)
        y += len(lignes) * 60 + 54

def s_machine(img, sc, lt):
    """Question tapée à la machine (curseur clignotant), puis la réponse."""
    f = font("s", sc.get("taille", 104)); lignes = wrap(sc["texte"], f, 880); fr = font("n", 50)
    haut = 120 + len(lignes) * f.size * 1.08 + 70 + len(wrap(sc.get("reponse", ""), fr, 880)) * 68
    y0 = int(max(330, 900 - haut / 2))
    if sc.get("surtitre"): reveal(img, sc["surtitre"], font("n", 34), y0, lt / 0.5, spacing=12)
    n = int(max(0, lt - 0.5) * sc.get("cps", 22)); d = ImageDraw.Draw(img); y = y0 + 120; reste = n; fin = (110, y)
    for l in lignes:
        part = l[:max(0, reste)]; reste -= len(l) + 1
        if part:
            d.text((100, y), part, font=f, fill=GOLD + (255,)); fin = (100 + d.textlength(part, font=f), y)
        y += int(f.size * 1.08)
    total = sum(len(l) + 1 for l in lignes); fini = 0.5 + total / sc.get("cps", 22)
    if lt < fini + 1.2 and int(lt * 2.4) % 2 == 0:
        d.rectangle([fin[0] + 8, fin[1] + 18, fin[0] + 14, fin[1] + f.size], fill=GOLD + (255,))
    y += 70
    for k, l in enumerate(wrap(sc.get("reponse", ""), fr, 880)):
        gauche(img, l, fr, 100, y + k * 68, (lt - fini - 0.3 - 0.2 * k) / 0.5)

def s_mythe(img, sc, lt):
    """Idée reçue barrée d'un trait or, puis la réalité."""
    fm = font("n", 56); lm = wrap(sc["mythe"], fm, 860); fr = font("s", sc.get("taille", 92)); lr = wrap(sc["realite"], fr, 900)
    haut = 80 + len(lm) * 74 + 100 + 80 + len(lr) * fr.size * 1.04
    y0 = int(max(330, 900 - haut / 2))
    reveal(img, sc.get("label_mythe", "IDÉE REÇUE"), font("n", 34), y0, lt / 0.5, spacing=12, color=DIM)
    d = ImageDraw.Draw(img); y = y0 + 80
    barre = eo((lt - 1.4) / 0.6)
    for k, l in enumerate(lm):
        a = int(255 * cl((lt - 0.3) / 0.5) * (1 - 0.45 * barre)); w = d.textlength(l, font=fm); x = (W - w) / 2
        d.text((x, y), l, font=fm, fill=TXT + (a,))
        bk = cl(barre * len(lm) - k)
        if bk > 0: d.line([(x - 10, y + 38), (x - 10 + (w + 20) * bk, y + 38)], fill=GOLD + (255,), width=6)
        y += 74
    y += 100
    reveal(img, sc.get("label_realite", "EN RÉALITÉ"), font("n", 34), y, (lt - 2.2) / 0.5, spacing=12); y += 80
    for k, l in enumerate(lr):
        reveal(img, l, fr, y, (lt - 2.6 - 0.3 * k) / 0.6); y += int(fr.size * 1.04)

NOUVELLES = {"compteur": s_compteur, "liste": s_liste, "machine": s_machine, "mythe": s_mythe}

def transition(img, kind, u):
    """Transitions variées : volet (or diagonal), fondu, glisse (panneau vertical), cercle, coupe (sèche)."""
    d = ImageDraw.Draw(img)
    if kind == "volet":
        x = int(-W * 1.3 + eio(u) * W * 2.6); sk = 260
        d.polygon([(x, 0), (x + W + sk, 0), (x + W, H), (x - sk, H)], fill=GOLD)
        d.polygon([(x + W + sk, 0), (x + W + sk + 90, 0), (x + W + 90, H), (x + W, H)], fill=BG)
    elif kind == "fondu":
        img.alpha_composite(Image.new("RGBA", (W, H), BG + (int(255 * (1 - abs(2 * u - 1))),)))
    elif kind == "glisse":
        top = int(H - eio(u) * 2 * H)
        d.rectangle([0, top, W, top + H], fill=BG)
        d.rectangle([0, top, W, top + 6], fill=GOLD); d.rectangle([0, top + H - 6, W, top + H], fill=GOLD)
    elif kind == "cercle":
        R = int(math.hypot(W, H) / 2) + 10; cx, cy = W // 2, H // 2
        m = Image.new("L", (W, H), 0); dm = ImageDraw.Draw(m)
        r = int(R * eio(cl(u * 2))); dm.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
        if u > .5:
            h = int(R * eio(cl(u * 2 - 1))); dm.ellipse([cx - h, cy - h, cx + h, cy + h], fill=0)
        img.paste(Image.new("RGBA", (W, H), GOLD + (255,)), (0, 0), m)
    # "coupe" : rien, coupure franche


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
        for k, c in enumerate(cuts, 1):
            u = (t - (c - 0.3)) / 0.6
            if 0 <= u <= 1: transition(img, scenes[k].get("transition", "volet"), u)
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
