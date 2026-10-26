#!/usr/bin/env python3
"""Contrôle « langage clair » des publications AQ (voir .claude/skills/aq-creation-contenu/references/langage-clair.md).

Usage :
    python3 visuels/outils/clair.py visuels/2026-S43/contenu/s43-14-fiche-lanaudiere.json
    python3 visuels/outils/clair.py visuels/2026-S43/legendes.md
    python3 visuels/outils/clair.py visuels/2026-S43/contenu/*.json visuels/2026-S43/legendes.md

Signale : phrases trop longues, sigles non développés à leur première apparition, slides trop chargées
(plus de 5 éléments, plus de 2 chiffres), passages en majuscules, « etc. ». Code de sortie 1 s'il y a une alerte.
Les alertes sont des signaux : corriger, ou noter pourquoi l'exception est acceptable.
"""
import json, re, sys

MAX_VISUEL, MAX_LEGENDE = 20, 25
SIGLES_LIBRES = {"AQ", "PME", "TPS", "TVQ", "PDF", "URL", "OK", "FB", "IG", "MP4", "PNG", "QC", "CV"}
CHAMPS_IGNORES = {"id", "gabarit", "format", "pilier", "source", "clip", "transition", "style", "type",
                  "etiquette", "surtitre", "petit", "accroche", "chiffre", "grand"}
RE_SIGLE = re.compile(r"\b([A-ZÀ-Ý][A-ZÀ-Ý0-9]{1,6})\b")
RE_NOMBRE = re.compile(r"\d[\d\s ,.]*\d|\d")


def nettoie(t):
    t = re.sub(r"<[^>]+>", " ", t).replace("*", "").replace(" ", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", t).strip()


def phrases(t):
    return [p.strip() for p in re.split(r"(?<=[.!?…])\s+|\s*•\s*|\s*→\s*|\n", t) if p.strip()]


def mots(p):
    return [m for m in re.split(r"[\s’']+", p) if re.search(r"\w", m)]


class Rapport:
    def __init__(self, nom):
        self.nom, self.alertes, self.vus = nom, [], set()

    def add(self, ou, msg):
        self.alertes.append(f"  - {ou} : {msg}")

    def texte(self, ou, t, maxi):
        t = nettoie(t)
        for p in phrases(t):
            n = len(mots(p))
            if n > maxi:
                self.add(ou, f"phrase de {n} mots (max {maxi}) : « {p[:90]}{'…' if len(p) > 90 else ''} »")
        for m in RE_SIGLE.finditer(t):
            s = m.group(1)
            if s in SIGLES_LIBRES or s in self.vus or not re.search(r"[A-Z]{2}", s):
                continue
            self.vus.add(s)
            avant, apres = t[max(0, m.start() - 2):m.start()], t[m.end():m.end() + 2]
            if not (avant.endswith("(") or apres.startswith(" (") or apres.startswith("(")):
                self.add(ou, f"sigle « {s} » non développé à sa première apparition (ex. « {s} (…) »)")
        if re.search(r"\b(?:[A-ZÀ-Ý]{2,}\s+){3,}[A-ZÀ-Ý]{2,}\b", t):
            self.add(ou, "passage de plus de 3 mots en majuscules")
        if re.search(r"\betc\b", t):
            self.add(ou, "« etc. » : lister ou couper")


def chaines(x, champ=None):
    if isinstance(x, str):
        if champ not in CHAMPS_IGNORES:
            yield x
    elif isinstance(x, list):
        for v in x:
            yield from chaines(v, champ)
    elif isinstance(x, dict):
        for k, v in x.items():
            yield from chaines(v, k)


def controle_json(chemin):
    r = Rapport(chemin)
    d = json.load(open(chemin, encoding="utf-8"))
    pages = d.get("slides") or d.get("plans") or (d if isinstance(d, list) else [d])
    for i, s in enumerate(pages, 1):
        ou = f"slide {i}" if "slides" in d else f"plan {i}"
        for t in chaines(s):
            r.texte(ou, t, MAX_VISUEL)
        items = s.get("items", []) if isinstance(s, dict) else []
        if len(items) > 5:
            r.add(ou, f"{len(items)} éléments (max 5)")
        visibles = " ".join(nettoie(t) for t in chaines(s))
        nombres = [n for n in RE_NOMBRE.findall(visibles) if not re.fullmatch(r"20\d\d|19\d\d|\d", n.strip())]
        if isinstance(s, dict) and s.get("chiffre"):
            nombres.append(s["chiffre"])
        if len(nombres) > 2:
            r.add(ou, f"{len(nombres)} chiffres ({', '.join(n.strip() for n in nombres[:5])}) : 2 au maximum par slide")
    return r


def controle_md(chemin):
    r = Rapport(chemin)
    section = "début"
    for ligne in open(chemin, encoding="utf-8"):
        ligne = ligne.rstrip("\n")
        if ligne.startswith("#"):
            section = ligne.lstrip("# ").strip()
            if ligne.startswith("## "):
                r.vus = set()  # chaque publication est lue séparément
            continue
        if not ligne.strip() or ligne.lstrip().startswith(("Fichier", "|", "Inscription :", "http")) or ligne.startswith("#"):
            continue
        texte = re.sub(r"#\w+", "", re.sub(r"https?://\S+", "", ligne))
        r.texte(section[:40], texte, MAX_LEGENDE)
    return r


def main(chemins):
    total = 0
    for c in chemins:
        r = controle_json(c) if c.endswith(".json") else controle_md(c)
        if r.alertes:
            print(f"À REVOIR {c}")
            print("\n".join(r.alertes))
        else:
            print(f"OK   {c}")
        total += len(r.alertes)
    return 1 if total else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
