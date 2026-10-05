"""Musique d'ambiance synthétisée (libre de droits), 120 BPM.
Usage : python3 musique.py <durée_s> "[4,8,12]" sortie.wav
(les coupures reçoivent un souffle ; la dernière coupure reçoit un impact grave)"""
import numpy as np, wave
import sys,json
T=float(sys.argv[1]) if len(sys.argv)>1 else 16.0
CUTS=json.loads(sys.argv[2]) if len(sys.argv)>2 else [4,8,12]
OUT=sys.argv[3] if len(sys.argv)>3 else "musique.wav"
IMPACT=CUTS[-1] if CUTS else None
SR=44100; N=int(SR*T); t=np.arange(N)/SR
out=np.zeros(N); BPM=120; beat=60/BPM
def note(m): return 440*2**((m-69)/12)
def add(sig,start):
    i=int(start*SR); j=min(N,i+len(sig)); out[i:j]+=sig[:j-i]
chords=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]  # Am F C G
# pad
for bar in range(int(T/2)):
    ch=chords[bar%4]; s=bar*2*beat; d=2*beat
    tt=np.arange(int(d*SR))/SR; env=np.minimum(1,tt/0.4)*np.minimum(1,(d-tt)/0.3)
    sig=sum(np.sin(2*np.pi*note(m)*tt)+0.3*np.sin(2*np.pi*2*note(m)*tt+0.3)+0.25*np.sin(2*np.pi*note(m)*1.003*tt) for m in ch)
    add(0.05*sig*env,s)
    # bass
    for b in range(4):
        tb=np.arange(int(beat*SR))/SR; eb=np.exp(-tb*5)
        add(0.22*np.sin(2*np.pi*note(ch[0]-24)*tb)*eb,s+b*beat)
    # arp 8ths
    if bar>=1 and bar<int(T/2)-1:
        seq=[ch[0]+12,ch[1]+12,ch[2]+12,ch[1]+12]
        for k in range(8):
            tp=np.arange(int(0.3*SR))/SR; ep=np.exp(-tp*14)
            m=seq[k%4]; add(0.07*(np.sin(2*np.pi*note(m)*tp)+0.4*np.sin(2*np.pi*2*note(m)*tp))*ep,s+k*beat/2)
# drums from 2s to 15s
rng=np.random.default_rng(1)
for b in range(int(T/beat)):
    s=b*beat
    if 2<=s<T-1:
        tk=np.arange(int(0.3*SR))/SR; f=50+100*np.exp(-tk*30)
        add(0.5*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tk*9),s)
        th=np.arange(int(0.05*SR))/SR; nz=rng.standard_normal(len(th)); nz=np.diff(np.concatenate([[0],nz]))
        add(0.05*nz*np.exp(-th*80),s+beat/2)
# whooshes before cuts
for c in CUTS:
    L=int(0.6*SR); tw=np.arange(L)/SR; nz=rng.standard_normal(L)
    k=np.linspace(1,40,L).astype(int); sm=np.array([nz[max(0,i-k[i]):i+1].mean() for i in range(L)])
    env=np.sin(np.pi*tw/0.6)**2; add(0.35*sm*env/np.abs(sm).max(),c-0.45)
# impact at logo
ti=np.arange(int(2.5*SR))/SR; f=40+60*np.exp(-ti*8)
if IMPACT: add(0.6*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-ti*1.6),IMPACT)
# master
fade=np.ones(N); fl=int(1.2*SR); fade[-fl:]=np.linspace(1,0,fl); out*=fade
out=np.tanh(out*1.2); out/=np.abs(out).max()*1.1
d=(out*32767).astype(np.int16)
w=wave.open(OUT,"wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes()); w.close()
print("ok")
