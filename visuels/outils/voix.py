#!/usr/bin/env python3
"""Voix off synthétisée pour un Reel motion design (Piper, voix française « siwis », licence CC BY 4.0).

Usage :
    python3 visuels/outils/voix.py scenes.json reel.mp4 sortie.mp4 [modele.onnx]

Chaque scène peut avoir une clé "voix" : liste de répliques {"t": 0.2, "texte": "…", "dit": "…"}.
  t     = départ en secondes depuis le début de la scène ;
  texte = ce qui est dit (doit aussi être écrit à l'écran : règle langage clair) ;
  dit   = graphie phonétique facultative pour corriger la prononciation (ex. « bizness »).
La musique d'origine est baissée sous la voix (sidechain), puis le tout est normalisé à -14 LUFS.
Installation : pip install piper-tts ; modèle fr_FR-siwis-medium.onnx (+ .onnx.json) depuis
huggingface.co/rhasspy/piper-voices (fr/fr_FR/siwis/medium). Mention : voix « SIWIS » (CC BY 4.0).
"""
import json, os, subprocess, sys, tempfile, wave
import numpy as np

SR = 22050

def synth(modele, texte, out, vitesse):
    subprocess.run([sys.executable, "-m", "piper", "-m", modele, "-f", out, "--length-scale", str(vitesse)],
                   input=texte.encode(), check=True, capture_output=True)
    w = wave.open(out); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a

def main(scenes_path, video, sortie, modele=None):
    modele = modele or os.environ.get("AQ_VOIX", "fr_FR-siwis-medium.onnx")
    scenes = json.load(open(scenes_path)); T = sum(float(s.get("duree", 4)) for s in scenes)
    piste = np.zeros(int((T + 1) * SR), np.float32); tmp = tempfile.mkdtemp(); t0 = 0.0
    for i, sc in enumerate(scenes):
        for k, r in enumerate(sc.get("voix", [])):
            a = synth(modele, r.get("dit", r["texte"]), f"{tmp}/{i}_{k}.wav", r.get("vitesse", 0.92))
            d = int((t0 + r["t"]) * SR); piste[d:d + len(a)] += a[:len(piste) - d]
            fin = t0 + r["t"] + len(a) / SR
            if fin > t0 + float(sc.get("duree", 4)) + 0.2:
                print(f"ATTENTION scène {i + 1} : la voix déborde ({fin - t0:.1f} s pour {sc.get('duree')} s)")
        t0 += float(sc.get("duree", 4))
    w = wave.open(f"{tmp}/voix.wav", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(piste, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    filtre = ("[1:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume=1.6,asplit=2[v][sc];"
              "[0:a]volume=0.8[m];[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[md];"
              "[md][v]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", f"{tmp}/voix.wav", "-filter_complex", filtre,
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", sortie], check=True)
    print(f"OK : {sortie}")

if __name__ == "__main__":
    main(*sys.argv[1:5])
