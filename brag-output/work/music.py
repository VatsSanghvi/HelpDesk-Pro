import numpy as np, wave
SR=44100; DUR=22.5; N=int(SR*DUR); BPM=120; BEAT=60/BPM
rng=np.random.default_rng(7)
def buf(): return np.zeros(N)
def at(sig,t,dst,g=1.0):
    i=int(t*SR); 
    if i>=N: return
    n=min(len(sig),N-i); dst[i:i+n]+=sig[:n]*g
def env(n,a,d,s=0.0,r=None):
    t=np.arange(n)/SR; e=np.minimum(1,t/max(a,1e-4))
    return e*np.exp(-t/d) if s==0 else e*(s+(1-s)*np.exp(-t/d))
hz=lambda m:440*2**((m-69)/12)
def lp(x,a): # one-pole lowpass, a in (0,1)
    y=np.empty_like(x); acc=0.0
    for i in range(len(x)): acc+=a*(x[i]-acc); y[i]=acc
    return y
def lpf(x,fc): 
    from math import exp,pi
    a=1-np.exp(-2*np.pi*fc/SR); 
    # vectorised via scipy-free IIR using cumulative trick (approx with repeated convolution)
    return lp(x,a)
# --- instruments ---
def pad_note(m,dur,g=0.12):
    n=int(dur*SR); t=np.arange(n)/SR; f=hz(m)
    x=sum(np.sin(2*np.pi*f*(1+d)*t+ph) for d,ph in [(0,0),(0.003,1.3),(-0.004,2.1)])/3
    x+=0.25*np.sin(2*np.pi*2*f*t)
    a=np.minimum(1,t/0.35)*np.minimum(1,(dur-t)/0.5).clip(0,1)
    return x*a*g
def pluck(m,g=0.10,dec=0.22):
    n=int(0.6*SR); t=np.arange(n)/SR; f=hz(m)
    x=np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*2*f*t)*np.exp(-t/0.05)+0.15*np.sin(2*np.pi*3*f*t)*np.exp(-t/0.03)
    return x*env(n,0.003,dec)*g
def bell(m,g=0.18):
    n=int(2.2*SR); t=np.arange(n)/SR; f=hz(m)
    x=np.sin(2*np.pi*f*t+1.2*np.sin(2*np.pi*f*3.5*t)*np.exp(-t/0.4))
    return x*env(n,0.002,0.7)*g
def kick(g=0.55):
    n=int(0.35*SR); t=np.arange(n)/SR; f=48+90*np.exp(-t/0.035)
    ph=2*np.pi*np.cumsum(f)/SR; return np.sin(ph)*env(n,0.001,0.12)*g
def bass(m,dur,g=0.22):
    n=int(dur*SR); t=np.arange(n)/SR; f=hz(m)
    x=np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t)+0.1*np.sin(2*np.pi*3*f*t)
    a=np.minimum(1,t/0.006)*np.exp(-t/0.25)*np.minimum(1,(dur-t)/0.02).clip(0,1)
    return x*a*g
noise=lambda n: rng.standard_normal(n)
def hat(g=0.035):
    n=int(0.06*SR); x=noise(n); x=x-lpf(x,6000); return x*env(n,0.001,0.018)*g
def clap(g=0.09):
    n=int(0.25*SR); x=noise(n); x=lpf(x,3500)-lpf(x,900)
    e=np.zeros(n); 
    for o in [0,0.011,0.022]: i=int(o*SR); e[i:]+=np.exp(-np.arange(n-i)/SR/0.012)
    e+=0.6*np.exp(-np.arange(n)/SR/0.08)
    return x*e*g
def tick(f=2400,g=0.05): # mouse click / key
    n=int(0.03*SR); t=np.arange(n)/SR; x=np.sin(2*np.pi*f*t)+0.5*noise(n)*np.exp(-t/0.003)
    return x*env(n,0.0005,0.006)*g
def whoosh(dur=0.45,g=0.07,up=True):
    n=int(dur*SR); x=noise(n); t=np.arange(n)/SR
    # sweep filter by crossfading two bands
    lo=lpf(x,700); hi=lpf(x,4000)-lo
    k=(t/dur) if up else 1-(t/dur)
    y=lo*(1-k)+hi*k; a=np.sin(np.pi*np.clip(t/dur,0,1))**2
    return y*a*g
# --- arrangement ---
music=buf(); drums=buf(); sfx=buf(); verb_send=buf()
chords=[[53,57,60,64],[48,52,55,59],[50,53,57,60],[46,50,53,57]]  # Fmaj7 Cmaj7 Dm7 Bbmaj7
roots=[41,36,38,34]
BAR=4*BEAT
nb=int(np.ceil(DUR/BAR))
for b in range(nb):
    t0=b*BAR; ch=chords[b%4]
    if t0>=DUR: break
    endt=min(BAR,DUR-t0)
    pg=0.10 if t0<3.5 else (0.08 if t0<19 else 0.11)
    for m in ch: at(pad_note(m+12,endt+0.4,pg),t0,music); at(pad_note(m+12,endt+0.4,pg*0.5),t0,verb_send)
    # arpeggio 16ths
    arp=[ch[0]+24,ch[2]+24,ch[1]+24,ch[3]+24,ch[2]+24,ch[1]+24,ch[3]+24,ch[2]+24]
    for s in range(16):
        ts=t0+s*BEAT/4
        if ts>=DUR: break
        if ts<1.0 or ts>=19.0: continue
        g=0.035 if ts<3.5 else 0.05
        acc=1.0 if s%4==0 else 0.7
        p=pluck(arp[s%8],g*acc); at(p,ts,music); at(p*0.6,ts,verb_send)
    # groove
    for bt in range(4):
        tb=t0+bt*BEAT
        if tb<3.5 or tb>=19.0: 
            if 2.0<=tb<3.5: at(hat(0.02),tb+BEAT/2,drums)
            continue
        at(kick(),tb,drums)
        if bt in(1,3): at(clap(),tb,drums); at(clap(0.05),tb,verb_send)
        at(hat(),tb+BEAT/2,drums); at(hat(0.018),tb+BEAT/4,drums); at(hat(0.018),tb+3*BEAT/4,drums)
        r=roots[b%4]
        at(bass(r,BEAT/2*0.95),tb,music); at(bass(r+12 if bt%2 else r,BEAT/2*0.95,0.16),tb+BEAT/2,music)
# riser into the drop
n=int(1.0*SR); t=np.arange(n)/SR; x=noise(n); r=(lpf(x,900)*(1-t)+(x-lpf(x,2500))*t)*(t**2)*0.06
at(r,2.5,sfx)
# reveal impact + chime (in key)
at(kick(0.7),3.5,drums); 
for m,dt in [(77,0),(81,0.09),(84,0.18),(88,0.27)]: b_=bell(m,0.07); at(b_,3.5+dt,music); at(b_,3.5+dt,verb_send)
# outro chord bell
for m,dt in [(65,0),(72,0.06),(77,0.12),(81,0.18)]: b_=bell(m,0.08); at(b_,19.0+dt,music); at(b_*1.2,19.0+dt,verb_send)
at(kick(0.5),19.0,drums)
# typing clicks at real capture changes
def typeFrame(t):
    if t<0.45: return 0
    if t<0.62: return 1
    if t<0.8: return 2
    if t<1.72: return 3+min(14,int((t-0.8)/0.92*15))
    if t<2.62: return 18+min(12,int((t-1.72)/0.9*13))
    return 31
last=0
for f in range(int(3.3*30)):
    t=f/30; k=typeFrame(t)
    if k!=last and k>=3:
        for j in range(2): at(tick(1800+rng.integers(0,900),0.018),t+j*0.028,sfx)
    last=k
for c in [0.45,0.62,0.8,1.74,2.96,15.82,16.82,17.82]: at(tick(2200,0.05),c,sfx); at(tick(1100,0.03),c+0.004,sfx)
for tw,up in [(3.2,True),(6.4,True),(8.45,True),(10.95,True),(13.95,True),(18.55,False)]:
    w=whoosh(0.5,0.05,up); at(w,tw,sfx); at(w*0.8,tw,verb_send)
# reverb (shared space)
irn=int(1.6*SR); ir=noise(irn)*np.exp(-np.arange(irn)/SR/0.45); ir=lpf(ir,5000); ir/=np.sqrt((ir**2).sum())
L=1<<int(np.ceil(np.log2(N+irn)))
wet=np.fft.irfft(np.fft.rfft(verb_send+0.3*sfx,L)*np.fft.rfft(ir,L),L)[:N]*0.35
# sidechain duck music under kick
duck=np.ones(N)
for b in range(int(DUR/BEAT)):
    tb=b*BEAT
    if 3.5<=tb<19.0 or abs(tb-19.0)<1e-6:
        i=int(tb*SR); n=min(int(0.25*SR),N-i); duck[i:i+n]=1-0.35*np.exp(-np.arange(n)/SR/0.08)
mix=music*duck+drums+sfx*0.9+wet*duck
# master: gentle high-shelf tame, soft clip, fades
mix=mix-0.15*(mix-lpf(mix,9000))
fin=int(0.03*SR); mix[:fin]*=np.linspace(0,1,fin)
fo=int(2.2*SR); mix[-fo:]*=np.linspace(1,0,fo)**1.5
mix=np.tanh(mix*1.4)/np.tanh(1.4)
mix=mix/np.max(np.abs(mix))*0.89
# stereo: slight width via delayed copy of wet
d=int(0.011*SR); wetd=np.concatenate([np.zeros(d),wet[:-d]])*duck
Lc=mix+0.12*wet; Rc=mix+0.12*wetd
st=np.stack([Lc,Rc],1); st=st/np.max(np.abs(st))*0.89
with wave.open('music.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype('<i2').tobytes())
print('ok', st.shape)
