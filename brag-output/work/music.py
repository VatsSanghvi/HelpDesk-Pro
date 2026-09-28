# Soundtrack for the v2 cut (30.6s, 100 BPM, beat = 0.6s), synthesized from scratch.
# Sections follow the edit: stabs on the cold-open cuts -> light groove -> lift at Power BI
# -> breakdown under the insight -> resolves on F under the end card. No samples, no booms.
import numpy as np, wave
SR=44100; DUR=30.6; N=int(SR*DUR); BEAT=0.6; BAR=4*BEAT; PICK=0.6   # bars start at 0.6 + 2.4k
rng=np.random.default_rng(11)
def buf(): return np.zeros(N)
def at(sig,t,dst,g=1.0):
    i=int(round(t*SR))
    if i>=N or i<0: return
    n=min(len(sig),N-i); dst[i:i+n]+=sig[:n]*g
def env(n,a,d):
    t=np.arange(n)/SR; return np.minimum(1,t/max(a,1e-4))*np.exp(-t/d)
hz=lambda m:440*2**((m-69)/12)
def lpf(x,fc):  # one-pole low-pass (vectorised via lfilter-free recursion on chunks is overkill here)
    a=1-np.exp(-2*np.pi*fc/SR); y=np.empty_like(x); acc=0.0
    for i in range(len(x)): acc+=a*(x[i]-acc); y[i]=acc
    return y
noise=lambda n: rng.standard_normal(n)
# ---- instruments ----
def pad_note(m,dur,g):
    n=int(dur*SR); t=np.arange(n)/SR; f=hz(m)
    x=sum(np.sin(2*np.pi*f*(1+d)*t+ph) for d,ph in [(0,0),(0.0035,1.3),(-0.004,2.1)])/3+0.2*np.sin(2*np.pi*2*f*t)
    a=np.minimum(1,t/0.45)*np.clip((dur-t)/0.6,0,1)
    return x*a*g
def pluck(m,g,dec=0.2):
    n=int(0.7*SR); t=np.arange(n)/SR; f=hz(m)
    x=np.sin(2*np.pi*f*t)+0.32*np.sin(2*np.pi*2*f*t)*np.exp(-t/0.05)+0.12*np.sin(2*np.pi*3*f*t)*np.exp(-t/0.03)
    return x*env(n,0.003,dec)*g
def bell(m,g):
    n=int(3.2*SR); t=np.arange(n)/SR; f=hz(m)
    x=np.sin(2*np.pi*f*t+0.9*np.sin(2*np.pi*f*3.5*t)*np.exp(-t/0.35))
    return x*env(n,0.004,1.1)*g
def kick(g):
    n=int(0.32*SR); t=np.arange(n)/SR; f=46+70*np.exp(-t/0.03)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.002,0.11)*g
def bass(m,dur,g):
    n=int(dur*SR); t=np.arange(n)/SR; f=hz(m)
    x=np.sin(2*np.pi*f*t)+0.25*np.sin(2*np.pi*2*f*t)
    return x*np.minimum(1,t/0.008)*np.exp(-t/0.5)*np.clip((dur-t)/0.03,0,1)*g
def hat(g):
    n=int(0.05*SR); x=noise(n); x=x-lpf(x,7000); return x*env(n,0.001,0.014)*g
def clap(g):
    n=int(0.22*SR); x=noise(n); x=lpf(x,3200)-lpf(x,1000)
    e=np.zeros(n)
    for o in [0,0.010,0.020]: i=int(o*SR); e[i:]+=np.exp(-np.arange(n-i)/SR/0.011)
    e+=0.5*np.exp(-np.arange(n)/SR/0.07)
    return x*e*g
def click(g):  # ~150ms soft UI click, in the track's space (not a sharp tick)
    n=int(0.15*SR); t=np.arange(n)/SR
    body=np.sin(2*np.pi*1750*t)*np.exp(-t/0.006)+0.6*np.sin(2*np.pi*880*t)*np.exp(-t/0.018)
    return (body+0.25*lpf(noise(n),4000)*np.exp(-t/0.004))*np.minimum(1,t/0.0008)*g
def whoosh(dur,g):
    n=int(dur*SR); x=noise(n); t=np.arange(n)/SR
    lo=lpf(x,600); hi=lpf(x,3500)-lo; k=t/dur
    return (lo*(1-k)+hi*k)*np.sin(np.pi*k)**2*g
# ---- arrangement ----
music=buf(); drums=buf(); sfx=buf(); send=buf()
CH={'F':[53,57,60,64],'C':[48,52,55,62],'Dm':[50,53,57,60],'Bb':[46,50,53,57]}
RT={'F':41,'C':36,'Dm':38,'Bb':34}
PROG=['F','C','Dm','Bb','F','C','Dm','Bb','F','Bb','C']        # bars 0..10 (0.6s .. 27.0s)
# pad from the very first frame (pickup shares bar 0's F)
for k,c in enumerate(PROG):
    t0=PICK+k*BAR; st=0.0 if k==0 else t0; dur=(t0+BAR)-st
    g=0.075 if t0<13.2 else (0.065 if t0<24.0 else 0.085)
    for m in CH[c]: at(pad_note(m+12,dur+0.5,g),st,music); at(pad_note(m+12,dur+0.5,g*0.6),st,send)
    arp=[CH[c][0]+24,CH[c][2]+24,CH[c][1]+24,CH[c][3]+24]
    for s in range(8):                       # 8th-note arpeggio
        ts=t0+s*BEAT/2
        if ts<1.2 or ts>=27.0: continue
        if 24.0<=ts<27.0 and s%2: continue   # breakdown: quarters only
        g=0.028 if ts<13.2 else 0.038
        p=pluck(arp[s%4],g*(1.0 if s%2==0 else 0.75)); at(p,ts,music); at(p*0.7,ts,send)
    for b in range(4):                       # drums + bass
        tb=t0+b*BEAT
        if tb<1.2 or tb>=27.0: continue
        r=RT[c]
        if tb<13.2:                          # groove A: half-time, airy
            if b in (0,2): at(kick(0.42),tb,drums); at(bass(r,1.1,0.2),tb,music)
            at(hat(0.016),tb+BEAT/2,drums)
        elif tb<24.0:                        # groove B: lift for Power BI onwards
            at(kick(0.46),tb,drums)
            if b in (1,3): at(clap(0.07),tb,drums); at(clap(0.04),tb,send)
            at(hat(0.022),tb+BEAT/2,drums); at(hat(0.01),tb+BEAT/4,drums); at(hat(0.01),tb+3*BEAT/4,drums)
            at(bass(r,BEAT/2*0.95,0.2),tb,music); at(bass(r+12 if b%2 else r,BEAT/2*0.95,0.13),tb+BEAT/2,music)
        else:                                # breakdown under the insight
            if b==0: at(bass(r,2.2,0.16),tb,music)
# cold-open stabs, one per micro-cut (Fmaj7 rising)
for m,tc in [(77,0.0),(81,0.3),(84,0.6),(88,0.9)]:
    p=pluck(m,0.07,0.25); at(p,tc,music); at(p*0.8,tc,send)
# resolution under the end card (27.0): Fmaj9, soft bell, low F — no impact hit
for m in [53,57,60,64,67]: at(pad_note(m+12,3.8,0.085),27.0,music); at(pad_note(m+12,3.8,0.06),27.0,send)
at(bass(29,3.4,0.2),27.0,music)
for m,dt in [(65,0),(69,0.07),(72,0.14),(76,0.21)]: b_=bell(m,0.05); at(b_,27.0+dt,music); at(b_,27.0+dt,send)
# gentle lift into the resolve
n=int(0.8*SR); tt=np.arange(n)/SR; x=noise(n); at(((x-lpf(x,1800))*(tt/0.8)**2)*0.022,26.2,sfx)
# the one UI click: Submit
at(click(0.09),3.9,sfx); at(click(0.03),3.9,send)
# soft whooshes, peaking on the major transitions only
for tw,g in [(13.2,0.045),(18.0,0.04),(24.0,0.028),(27.0,0.035)]:
    w=whoosh(0.7,g); at(w,tw-0.35,sfx); at(w*0.8,tw-0.35,send)
# shared room
irn=int(1.8*SR); ir=noise(irn)*np.exp(-np.arange(irn)/SR/0.5); ir=lpf(ir,5500); ir/=np.sqrt((ir**2).sum())
L=1<<int(np.ceil(np.log2(N+irn)))
wet=np.fft.irfft(np.fft.rfft(send+0.25*sfx,L)*np.fft.rfft(ir,L),L)[:N]*0.32
# light sidechain under the kick
duck=np.ones(N)
for k in range(int(DUR/BEAT)+1):
    tb=k*BEAT
    if 1.2<=tb<27.0:
        i=int(tb*SR); n=min(int(0.22*SR),N-i)
        if n>0: duck[i:i+n]=1-0.28*np.exp(-np.arange(n)/SR/0.07)
mix=music*duck+drums+sfx+wet*duck
mix=mix-0.12*(mix-lpf(mix,9000))
fo=int(1.4*SR); mix[-fo:]*=np.linspace(1,0,fo)**1.6
mix=np.tanh(mix*1.3)/np.tanh(1.3); mix=mix/np.max(np.abs(mix))*0.89
d=int(0.012*SR); wetd=np.concatenate([np.zeros(d),wet[:-d]])*duck
st=np.stack([mix+0.1*wet*duck,mix+0.1*wetd],1); st=st/np.max(np.abs(st))*0.89
with wave.open('music.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype('<i2').tobytes())
print('ok',st.shape)
