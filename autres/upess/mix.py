import json, subprocess, numpy as np
SR=44100; V="/tmp/claude-0/-home-user-Mon-projet-pro/8da80b25-d863-58f1-800d-0061204bdeb6/scratchpad/voix/fr_FR-siwis-medium.onnx"
rng=np.random.default_rng(7)
def tts(t,ls,name):
    subprocess.run(["python3","-m","piper","-m",V,"-f",name,"--length-scale",str(ls),"--sentence-silence","0.45"],input=t.encode(),capture_output=True,check=True)
    a=np.frombuffer(subprocess.run(["ffmpeg","-loglevel","error","-i",name,"-ar",str(SR),"-ac","1","-f","f32le","-"],capture_output=True).stdout,np.float32).copy()
    nz=np.where(np.abs(a)>0.01)[0]; return a[max(0,nz[0]-400):nz[-1]+2000]
def env(n,d): return np.exp(-np.arange(n)/(d*SR))
def bp_noise(n,lo,hi):
    x=rng.standard_normal(n); X=np.fft.rfft(x); f=np.fft.rfftfreq(n,1/SR); X[(f<lo)|(f>hi)]=0; return np.fft.irfft(X,n)
def tibwa(acc):
    n=int(0.05*SR); t=np.arange(n)/SR
    s=0.6*np.sin(2*np.pi*1750*t)*env(n,0.012)+0.5*bp_noise(n,2500,6000)*env(n,0.006)
    return s/np.abs(s).max()*(0.55 if acc else 0.32)
def bass():
    n=int(0.5*SR); t=np.arange(n)/SR; f=55+45*np.exp(-t/0.04)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.18)+0.25*bp_noise(n,80,400)*env(n,0.03)
    return s/np.abs(s).max()*0.9
def slap():
    n=int(0.2*SR); t=np.arange(n)/SR
    s=0.6*np.sin(2*np.pi*230*t)*env(n,0.05)+0.7*bp_noise(n,500,3500)*env(n,0.02)
    return s/np.abs(s).max()*0.5
def clap():
    n=int(0.25*SR); s=np.zeros(n)
    for k,o in enumerate([0,0.011,0.022]):
        i=int(o*SR); m=int(0.06*SR); s[i:i+m]+=bp_noise(m,900,3200)*env(m,0.01)*(0.7 if k<2 else 1)
    s[int(0.03*SR):]+=bp_noise(n-int(0.03*SR),900,3200)*env(n-int(0.03*SR),0.06)*0.5
    return s/np.abs(s).max()*0.55
def final():
    n=int(3.0*SR); t=np.arange(n)/SR; f=45+60*np.exp(-t/0.05)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.7)+0.5*bp_noise(n,60,300)*env(n,0.15)+0.35*bp_noise(n,3000,9000)*env(n,0.9)
    return s/np.abs(s).max()
def add(buf,x,t,g=1.0):
    i=int(t*SR); j=min(len(buf),i+len(x)); buf[i:j]+=g*x[:j-i]
# voix
L=[("Collègues de l'Espace Sud…",1.0),
   ("Titulaires ou contractuels, nous avons tous les mêmes essentiels :",0.95),
   ("Nos droits. Nos acquis. Notre dignité.",1.1),
   ("L'Upèsse remonte vos doléances, dialogue avec l'autorité, et reste à vos côtés.",0.93),
   ("Tout moun, sé moun !",0.95),
   ("Du trois au dix décembre,",0.9),
   ("ba nou fosse la !",0.9),
   ("votez Upèsse, Une-sa !",0.88),
   ("Upèsse : Union des Personnels de l'Espace Sud.",1.15)]
vx=[tts(t,ls,f"v{i}.wav") for i,(t,ls) in enumerate(L)]
gains=[1.0,1.0,1.0,1.05,1.1,1.2,1.25,1.3,1.0]
BEAT=0.6; STEP=BEAT/4; BAR=16*STEP
# placement
t=3*BAR/1.0*0+ 2*BAR  # intro tibwa 2 mesures
starts=[]; cur=2*BAR
starts.append(cur); cur+=len(vx[0])/SR+0.9
tan_in=cur-0.3
for i in [1,2,3,4]:
    starts.append(cur); cur+=len(vx[i])/SR+(0.7 if i!=2 else 0.9)
build=cur-0.2
for i in [5,6,7]:
    starts.append(cur); cur+=len(vx[i])/SR+0.35
fin=cur+0.25
starts.append(fin+1.6)
T=starts[-1]+len(vx[8])/SR+2.5
buf_v=np.zeros(int(T*SR)+SR); buf_p=np.zeros_like(buf_v)
for s,x,g in zip(starts,vx,gains): add(buf_v,x,s,g)
pat_t=[1,0,1,1,1,0,1,0,1,0,1,1,1,0,1,0]
b=0.0
while b<fin:
    for k in range(16):
        tt=b+k*STEP
        if tt>=fin: break
        if pat_t[k]: add(buf_p,tibwa(k%4==0),tt)
        if tt>=tan_in:
            if k in (0,6,10): add(buf_p,bass(),tt)
            if k in (4,12,14): add(buf_p,slap(),tt)
        if tt>=build:
            if k in (4,12): add(buf_p,clap(),tt)
            if tt>=fin-BAR and k in (0,2,6,8,10,14): add(buf_p,clap(),tt,0.7)
    b+=BAR
add(buf_p,final(),fin,1.0)
# tibwa léger sous la dernière phrase, puis fondu
b=fin+1.4
for k in range(int((T-b)/STEP)):
    if pat_t[k%16]: add(buf_p,tibwa(False),b+k*STEP,0.5*max(0,1-k*STEP/(T-b)))
w0=__import__('wave').open('voix_seule.wav','wb'); w0.setnchannels(1); w0.setsampwidth(2); w0.setframerate(SR); w0.writeframes((np.clip(buf_v/np.abs(buf_v).max()*0.9,-1,1)*32767).astype(np.int16).tobytes()); w0.close()
open('duree.txt','w').write(str(T))
# ducking
e=np.abs(buf_v); win=int(0.15*SR); e=np.convolve(e,np.ones(win)/win,"same"); duck=1-0.45*np.clip(e/0.05,0,1)
mix=buf_v*1.0+buf_p*0.55*duck
mix=mix/np.abs(mix).max()*0.9
import wave
w=wave.open("upess.wav","wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes()); w.close()
print("durée",round(T,1),"s ; voix aux", [round(s,1) for s in starts])
