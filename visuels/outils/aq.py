#!/usr/bin/env python3
"""Rendu des visuels réseaux sociaux d'Affaires Québec.

Usage :
    python3 visuels/outils/aq.py rendre visuels/2026-S41/contenu/s41-01-trois-portes.json
    python3 visuels/outils/aq.py apercu visuels/2026-S41

Chaque fichier de contenu (JSON) décrit un visuel ou un carrousel : format, gabarit
de chaque slide et textes. Les textes sont écrits avec des espaces ordinaires :
typo() pose les espaces insécables françaises. Après le rendu, chaque PNG passe
un contrôle automatique (dimensions, marge de 88 px, mots orphelins, espaces).
"""
import html
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

OUTILS = Path(__file__).resolve().parent
ASSETS = OUTILS.parent / "assets"
CHROMIUM = "/opt/pw-browsers/chromium"
MARGE = 88

FORMATS = {
    "post": (1080, 1350),
    "story": (1080, 1920),
    "linkedin": (1200, 1200),
    "couverture-linkedin": (1128, 191),
    "banniere-linkedin": (1584, 396),
    "evenement-facebook": (1920, 1005),
}

NBSP, NNBSP = "\u00a0", "\u202f"


# ---------- Typographie ----------

def typo(s):
    """Pose les espaces insécables françaises dans un texte saisi avec des espaces ordinaires."""
    if not s or "http" in s:
        return s
    s = s.replace("'", "’")
    s = re.sub(r"\s*([:%$])(?=\s|$|<)", NBSP + r"\1", s)
    s = re.sub(r"\s*([;?!])", NNBSP + r"\1", s)
    s = re.sub(r"«\s*", "«" + NBSP, s)
    s = re.sub(r"\s*»", NBSP + "»", s)
    s = re.sub(r"(\d) (\d{3})\b", r"\1" + NNBSP + r"\2", s)
    s = re.sub(r"(\d) (h|ans|entreprises|octobre|novembre|décembre)\b", r"\1" + NBSP + r"\2", s)
    s = re.sub(r"\b(n°|J-) ?(\d)", r"\1\2", s)
    s = s.replace(" →", NBSP + "→").replace(" —", NBSP + "—")
    return s


def t(s):
    """Texte prêt pour le HTML : typographie, puis échappement (sauf <strong>/<br>)."""
    s = html.escape(typo(s), quote=False)
    return re.sub(r"&lt;(/?(?:strong|br|em))&gt;", r"<\1>", s)


# ---------- Gabarits (style éditorial) ----------

def g_couverture(d):
    return f"""
    <div class="corps">
      {f'<div class="surtitre">{t(d["surtitre"])}</div>' if d.get("surtitre") else ""}
      <h1 class="titre {d.get("taille", "xl")}">{t(d["titre"])}</h1>
      {f'<p class="sous-titre">{t(d["sous_titre"])}</p>' if d.get("sous_titre") else ""}
    </div>"""


def g_texte(d):
    paras = "".join(f'<p class="texte">{t(p)}</p>' for p in d.get("paragraphes", []))
    return f"""
    <div class="corps">
      {f'<div class="surtitre">{t(d["surtitre"])}</div>' if d.get("surtitre") else ""}
      <h2 class="titre {d.get("taille", "l")}">{t(d["titre"])}</h2>
      {f'<p class="sous-titre or">{t(d["sous_titre"])}</p>' if d.get("sous_titre") else ""}
      <div class="court"></div>
      {paras}
    </div>"""


def g_porte(d):
    items = "".join(f'<li data-n="{i:02d}">{t(x)}</li>' for i, x in enumerate(d["items"], 1))
    return f"""
    <div class="corps">
      <div class="surtitre">{t(d["surtitre"])}</div>
      <h2 class="titre {d.get("taille", "xl")}">{t(d["titre"])}</h2>
      <p class="chapeau">{t(d["chapeau"])}</p>
      <ul class="liste">{items}</ul>
    </div>"""


def g_evenement(d):
    return f"""
    <div class="corps">
      <div class="surtitre">{t(d["surtitre"])}</div>
      <h2 class="titre {d.get("taille", "m")}">{t(d["titre"])}</h2>
      <div class="evenement">
        <div class="jour">{t(d["jour"])}</div>
        <div class="heure">{t(d["heure"])}</div>
        {f'<div class="lieu">{t(d["lieu"])}</div>' if d.get("lieu") else ""}
      </div>
      <div class="appel">{t(d["appel"])}</div>
    </div>"""


GABARITS = {"couverture": g_couverture, "texte": g_texte, "porte": g_porte, "evenement": g_evenement}
AVEC_LOGO = {"evenement"}  # slides qui portent le logo complet : pas de filigrane


def page_html(slide, n, total, fmt):
    w, h = FORMATS[fmt]
    gabarit = slide["gabarit"]
    logo = gabarit in AVEC_LOGO
    filigrane = "" if logo else f'<img class="filigrane" src="../assets/symbole-or.png" alt="" style="--echelle:{w / 1080}">'
    pagination = f"{n}/{total}" + ("" if n == total else NBSP + "→")
    if logo:
        pied = '<div class="pied avec-logo"><img class="logo" src="../assets/logo-3-2-fond-sombre.png" alt="Affaires Québec">'
    else:
        pied = '<div class="pied"><span class="signature">Affaires Québec</span>'
    pied += f'<span class="pagination">{pagination}</span></div>' if total > 1 else "</div>"
    classes = "slide ed" + (" centre" if slide.get("centre") else "")
    return f"""<!doctype html><html lang="fr-CA"><head><meta charset="utf-8">
<link rel="stylesheet" href="aq.css"><style>.slide{{width:{w}px;height:{h}px}}</style></head>
<body><div class="{classes}">{filigrane}{GABARITS[gabarit](slide)}{pied}</div></body></html>"""


# ---------- Contrôle qualité dans la page ----------

QA_JS = """
(m) => {
  const W = innerWidth, H = innerHeight, pb = [];
  const ignore = el => el.closest('.filigrane');
  // 1. Texte et images dans la zone sûre (marge m)
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) {
    if (!node.textContent.trim()) continue;
    const r = document.createRange(); r.selectNodeContents(node);
    for (const q of r.getClientRects()) {
      if (q.left < m - 1 || q.right > W - m + 1 || q.top < m - 1 || q.bottom > H - m + 1)
        pb.push(`texte hors marge (${Math.round(q.left)},${Math.round(q.top)},${Math.round(q.right)},${Math.round(q.bottom)}) : « ${node.textContent.trim().slice(0, 40)} »`);
    }
  }
  document.querySelectorAll('img').forEach(i => {
    if (ignore(i)) return;
    const q = i.getBoundingClientRect();
    if (q.left < m - 1 || q.right > W - m + 1 || q.top < m - 1 || q.bottom > H - m + 1) pb.push(`image hors marge : ${i.getAttribute('src')}`);
  });
  // 2. Mots orphelins : dernière ligne d'un bloc réduite à un seul mot
  document.querySelectorAll('h1,h2,p,li,.jour,.heure,.lieu,.appel').forEach(el => {
    const mots = [];
    const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = tw.nextNode())) {
      const re = /[^ \\n]+/g; let x;
      while ((x = re.exec(n.textContent))) {
        const r = document.createRange(); r.setStart(n, x.index); r.setEnd(n, x.index + x[0].length);
        const q = r.getClientRects()[0]; if (q) mots.push({ m: x[0], y: Math.round(q.top) });
      }
    }
    const lignes = [...new Set(mots.map(o => o.y))];
    if (lignes.length > 1) {
      const der = mots.filter(o => o.y === lignes[lignes.length - 1]);
      if (der.length === 1) pb.push(`mot orphelin « ${der[0].m} » dans « ${el.textContent.trim().slice(0, 50)} »`);
    }
  });
  // 3. Polices réellement chargées
  for (const f of ['400 40px Caslon', '400 40px "DM Sans"'])
    if (!document.fonts.check(f)) pb.push('police non chargée : ' + f);
  return pb;
}
"""

ESPACES_MANQUANTES = re.compile(r"(?<![\u00a0\u202f])[:;?!%$»](?=\s|$)|«(?![\u00a0])")


def controle_source(slide):
    pb = []
    for k, v in slide.items():
        for s in v if isinstance(v, list) else [v]:
            if isinstance(s, str) and k != "gabarit" and "http" not in s:
                if ESPACES_MANQUANTES.search(typo(s)):
                    pb.append(f"espace insécable manquante dans « {s[:50]} »")
                if "  " in s:
                    pb.append(f"double espace dans « {s[:50]} »")
    return pb


# ---------- Commandes ----------

def rendre(chemin_json):
    src = Path(chemin_json).resolve()
    spec = json.loads(src.read_text(encoding="utf-8"))
    fmt = spec["format"]
    w, h = FORMATS[fmt]
    sortie = src.parent.parent  # contenu/ -> dossier de la semaine
    slides = spec["slides"]
    tmp = OUTILS / ".rendu.html"
    rapport = []
    with sync_playwright() as p:
        nav = p.chromium.launch(executable_path=CHROMIUM)
        page = nav.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        for n, slide in enumerate(slides, 1):
            versions = [("", slide)] + [(f"-{k}", {**slide, **v}) for k, v in slide.get("variantes", {}).items()]
            for suffixe, s in versions:
                nom = f"{spec['id']}-{n:02d}{suffixe}.png" if len(slides) > 1 else f"{spec['id']}{suffixe}.png"
                tmp.write_text(page_html(s, n, len(slides), fmt), encoding="utf-8")
                page.goto(tmp.as_uri())
                page.evaluate("document.fonts.ready")
                pb = page.evaluate(QA_JS, MARGE) + controle_source(s)
                page.screenshot(path=str(sortie / nom), clip={"x": 0, "y": 0, "width": w, "height": h})
                with Image.open(sortie / nom) as im:
                    if im.size != (w, h):
                        pb.append(f"dimensions {im.size} au lieu de {(w, h)}")
                rapport.append((nom, pb))
        nav.close()
    tmp.unlink(missing_ok=True)
    ok = True
    for nom, pb in rapport:
        print(("OK   " if not pb else "À REVOIR ") + nom)
        for x in pb:
            ok = False
            print("     - " + x)
    return ok


def apercu(dossier):
    """Planche contact de tous les PNG d'une semaine, regroupés par visuel."""
    d = Path(dossier)
    pngs = sorted(f for f in d.glob("*.png") if f.name != "apercu.png")
    groupes = {}
    for f in pngs:
        groupes.setdefault(re.sub(r"-\d\d(-\w+)?$", "", f.stem), []).append(f)
    th, gap, lab = 360, 24, 34
    police = ImageFont.truetype(str(ASSETS / "fonts" / "DMSans[opsz,wght].ttf"), 20)
    lignes = []
    for nom, fichiers in groupes.items():
        vignettes = []
        for f in fichiers:
            im = Image.open(f).convert("RGB")
            im.thumbnail((10_000, th))
            vignettes.append((f.stem.replace(nom, "").lstrip("-") or nom, im))
        lignes.append((nom, vignettes))
    largeur = max(sum(v.width + gap for _, v in vs) + gap for _, vs in lignes)
    hauteur = sum(th + 2 * lab + gap for _ in lignes) + gap
    planche = Image.new("RGB", (max(largeur, 800), hauteur), "#151213")
    dr = ImageDraw.Draw(planche)
    y = gap
    for nom, vs in lignes:
        dr.text((gap, y), nom, fill="#E3A73C", font=police)
        x = gap
        for etiquette, v in vs:
            planche.paste(v, (x, y + lab))
            dr.text((x, y + lab + v.height + 6), etiquette, fill="#E8E4DC", font=police)
            x += v.width + gap
        y += th + 2 * lab + gap
    planche.save(d / "apercu.png")
    print(f"{d / 'apercu.png'} : {len(pngs)} visuels")


if __name__ == "__main__":
    cmd, *args = sys.argv[1:]
    if cmd == "rendre":
        sys.exit(0 if all([rendre(a) for a in args]) else 1)
    elif cmd == "apercu":
        for a in args:
            apercu(a)
