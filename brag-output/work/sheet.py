import sys,glob
from PIL import Image,ImageDraw
fs=sorted(glob.glob('stills/s_*.jpg'),key=lambda f:float(f[9:-4]))
sel=sys.argv[1].split(',') if len(sys.argv)>1 else None
if sel: fs=[f for f in fs if f[9:-4] in sel]
W,H=960,540; cols=2; rows=(len(fs)+1)//2
out=Image.new('RGB',(W*cols,H*rows),'white')
for i,f in enumerate(fs):
    im=Image.open(f).resize((W,H)); d=ImageDraw.Draw(im); d.rectangle([0,0,90,28],fill='red'); d.text((6,6),f[9:-4],fill='white')
    out.paste(im,((i%cols)*W,(i//cols)*H))
out.save(sys.argv[2] if len(sys.argv)>2 else 'sheet.jpg',quality=80)
