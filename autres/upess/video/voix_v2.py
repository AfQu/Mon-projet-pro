"""Voix UPES v2 : une phrase par entrée de lignes.json, mise en cache par texte ; chœur = 3 voix superposées."""
import hashlib, json, os, subprocess, numpy as np
SR = 44100
V = "/tmp/claude-0/-home-user-Mon-projet-pro/8da80b25-d863-58f1-800d-0061204bdeb6/scratchpad/voix/"
VOIX = {"f": ["-m", V + "fr_FR-siwis-medium.onnx"], "h1": ["-m", V + "fr_FR-upmc-medium.onnx", "-s", "1"], "f2": ["-m", V + "fr_FR-upmc-medium.onnx", "-s", "0"]}
def tts(txt, ls, voix="f"):
    h = hashlib.md5(f"{voix}|{ls}|{txt}".encode()).hexdigest()[:12]; f = f"cache/{h}.wav"
    if not os.path.exists(f):
        subprocess.run(["python3", "-m", "piper", *VOIX[voix], "-f", f, "--length-scale", str(ls), "--sentence-silence", "0.4"], input=txt.encode(), capture_output=True, check=True)
    a = np.frombuffer(subprocess.run(["ffmpeg", "-loglevel", "error", "-i", f, "-ar", str(SR), "-ac", "1", "-f", "f32le", "-"], capture_output=True).stdout, np.float32).copy()
    nz = np.where(np.abs(a) > 0.01)[0]; return a[max(0, nz[0] - 300):nz[-1] + 1500]
L = json.load(open("lignes.json")); t = 4.5; segs = []; parts = []
for l in L:
    a = tts(l["dit"], l["ls"])
    if l.get("choeur"):
        b = tts(l["dit"], l["ls"], "h1"); c = tts(l["dit"], l["ls"], "f2"); n = max(len(a), len(b) + 900, len(c) + 1600)
        m = np.zeros(n, np.float32); m[:len(a)] += 1.0 * a; m[700:700 + len(b)] += 0.38 * b; m[1500:1500 + len(c)] += 0.32 * c; a = m / np.abs(m).max() * 0.95
    parts.append((t, a)); segs.append({"debut": round(t, 3), "fin": round(t + len(a) / SR, 3), "aff": l["aff"]}); t += len(a) / SR + l["pause"]
T = t; buf = np.zeros(int(T * SR) + SR, np.float32)
for s, a in parts: i = int(s * SR); buf[i:i + len(a)] += a
buf = buf / np.abs(buf).max() * 0.9
import wave
w = wave.open("voix_seule.wav", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((buf * 32767).astype(np.int16).tobytes()); w.close()
json.dump({"duree": round(T, 2), "segments": segs}, open("segments.json", "w"), ensure_ascii=False, indent=1)
print("durée", round(T, 1))
