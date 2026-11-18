"""Original deterministic tileable-ish PBR atlas + compartment sign atlas.
Run with system Python (Pillow/numpy), then build the Blender scene.
Nothing here downloads or invents historical photographs.
"""
from pathlib import Path
import sys, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from shipdesign.leonidas_ii import ROOMS
OUT=ROOT/'reference'/'leonidas_ii'/'materials';OUT.mkdir(parents=True,exist_ok=True)
# name, sRGB base, roughness, metallic, pattern
PALETTE=[
 ('Hull',(26,31,32),.52,.55,'metal'),('Oxide',(112,44,35),.72,.12,'paint'),('Ivory',(227,221,200),.58,0,'paint'),('White',(235,232,214),.66,0,'paint'),
 ('Teak',(145,104,62),.55,0,'wood'),('Oak',(158,119,72),.43,0,'wood'),('Mahogany',(90,41,27),.32,0,'wood'),('Walnut',(81,61,40),.42,0,'wood'),
 ('Brass',(183,139,60),.25,.92,'metal'),('Steel',(128,140,140),.28,.95,'metal'),('Iron',(44,54,53),.56,.7,'metal'),('Copper',(160,86,47),.33,.88,'metal'),
 ('Funnel',(203,158,87),.58,.12,'paint'),('Soot',(16,19,19),.91,0,'grain'),('Engine',(49,86,76),.40,.5,'paint'),('Lagging',(178,173,151),.91,0,'fabric'),
 ('Leather',(76,42,28),.43,0,'leather'),('LeatherGreen',(30,64,48),.46,0,'leather'),('Velvet',(97,35,34),.91,0,'fabric'),('GoldCloth',(170,132,59),.86,0,'fabric'),
 ('Linen',(222,215,190),.93,0,'fabric'),('Mattress',(163,165,141),.91,0,'stripe'),('Carpet',(97,46,38),.96,0,'carpet'),('Rubber',(72,76,62),.78,0,'rubber'),
 ('Tile',(201,211,204),.38,0,'tile'),('Porcelain',(234,232,211),.22,0,'grain'),('Marble',(192,190,167),.31,0,'marble'),('Rope',(153,134,94),.94,0,'rope'),
 ('BookRed',(112,46,38),.58,0,'book'),('BookBlue',(37,61,74),.58,0,'book'),('BookGreen',(59,77,45),.58,0,'book'),('Paper',(218,203,163),.88,0,'paper'),
 ('Coal',(28,30,29),.98,0,'grain'),('Firebrick',(134,67,44),.9,0,'brick'),('Canvas',(185,172,137),.9,0,'fabric'),('Chart',(208,198,159),.88,0,'chart'),
 ('Bulb',(255,222,150),.25,0,'grain'),('Red',(148,43,34),.4,.1,'paint'),('Green',(25,98,68),.4,.1,'paint'),('Black',(22,24,23),.7,0,'grain'),
]
N=256;SIZE=2048
base=np.zeros((SIZE,SIZE,3),np.uint8);rough=np.zeros((SIZE,SIZE),np.uint8);metal=np.zeros_like(rough);normal=np.zeros((SIZE,SIZE,3),np.uint8)
rng=np.random.default_rng(1889);y,x=np.mgrid[0:N,0:N];u=x/N;v=y/N
metadata={}
for i,(name,col,r,m,pattern) in enumerate(PALETTE):
 noise=rng.normal(0,1,(N,N));low=np.array(Image.fromarray(np.uint8(np.clip(128+noise*18,0,255))).filter(ImageFilter.GaussianBlur(3)),float)-128
 height=noise*.25;delta=low*.28
 if pattern=='wood':
  fibres=rng.normal(0,1,N*4)
  fibres=np.convolve(fibres,np.ones(5)/5,mode='same')
  warp=(v*N*3.8+3*np.sin(u*math.tau*1.4+v*6)+1.4*np.sin(u*math.tau*6))%(N*4-1)
  grain=np.interp(warp.ravel(),np.arange(N*4),fibres).reshape(N,N)
  delta+=grain*9+np.sin(v*math.tau*5+np.sin(u*8)*.6)*1.6;height+=grain*.6
 elif pattern in ('fabric','stripe','rope'):
  weave=(np.sin(u*math.tau*95)+np.sin(v*math.tau*95));delta+=weave*3;height+=weave*2
  if pattern=='stripe':delta+=np.where((x//22)%2,13,-13)
  if pattern=='rope':delta+=np.sin((u+v)*math.tau*13)*9
 elif pattern=='leather':
  delta+=low*.7;height+=low*.3
 elif pattern=='carpet':
  a=(np.abs(u-.5)+np.abs(v-.5));motif=(np.sin(a*math.tau*4)>0)*12
  delta+=motif+np.cos(u*math.tau*3)*np.cos(v*math.tau*3)*9;height+=motif*.09
 elif pattern=='rubber':
  motif=(np.abs(np.abs(u-.5)+np.abs(v-.5)-.32)<.027)|(x<5)|(y<5);delta+=motif*24;height+=motif*4
 elif pattern=='tile':
  grout=(x%64<3)|(y%64<3);delta-=grout*38;height-=grout*7
  delta+=(((x//64+y//64)%2)*2-1)*7
 elif pattern=='marble':delta-=np.exp(-np.sin(u*21+v*9+np.sin(v*13))**2*100)*29
 elif pattern=='brick':
  grout=(y%64<5)|((x+(y//64%2)*48)%96<5);delta-=grout*32;height-=grout*6
 elif pattern=='book':
  delta+=(y<14)*18+(y>240)*13
 elif pattern in ('paper','chart'):
  delta+=(np.sin(v*200)*1.4)
 elif pattern=='metal':delta+=np.sin(v*math.tau*98)*1.6;height+=np.sin(v*math.tau*98)*.2
 # leave a 4px gutter by clamping the patch; UVs never sample its neighbors
 rgb=np.uint8(np.clip(np.array(col)[None,None,:]+delta[:,:,None],0,255))
 gy,gx=np.gradient(height/18);n=np.dstack((-gx,-gy,np.ones_like(gx)));n/=np.linalg.norm(n,axis=2)[:,:,None]
 nn=np.uint8(np.clip((n*.5+.5)*255,0,255));rr=np.uint8(np.clip(r*255+noise*1.3+np.abs(delta)*.18,0,255));mm=np.full((N,N),round(m*255),np.uint8)
 if name=='Chart':
  im=Image.fromarray(rgb);d=ImageDraw.Draw(im)
  for j in range(15):
   pts=[(k*8,int(70+j*5+math.sin(k*.4+j)*9)) for k in range(33)];d.line(pts,fill=(125,136,113),width=1)
  d.line([(26,200),(63,168),(124,130),(190,54),(224,31)],fill=(164,81,58),width=2);d.ellipse((180,175,225,220),outline=(92,88,63),width=2);d.line((202,165,202,229),fill=(92,88,63));d.line((171,197,234,197),fill=(92,88,63));rgb=np.asarray(im)
 if pattern=='book':
  im=Image.fromarray(rgb);d=ImageDraw.Draw(im)
  for yy in [24,32,195,203,222]:d.line((9,yy,246,yy),fill=(177,146,77),width=2)
  rgb=np.asarray(im)
 row,colidx=divmod(i,8);sl=(slice(row*N,(row+1)*N),slice(colidx*N,(colidx+1)*N))
 base[sl]=rgb;rough[sl]=rr;metal[sl]=mm;normal[sl]=nn
 metadata[name]={'tile':i,'column':colidx,'row':row,'srgb':list(col),'roughness':r,'metallic':m,'pattern':pattern}
for name,arr in [('basecolor',base),('roughness',rough),('metallic',metal),('normal',normal)]:Image.fromarray(arr).save(OUT/f'Aurelian_{name}.png',optimize=True)
emission=np.zeros_like(base);emission[4*256:5*256,4*256:5*256]=[255,203,120]
Image.fromarray(emission).save(OUT/'Aurelian_emission.png',optimize=True)
(OUT/'atlas.json').write_text(json.dumps(metadata,indent=2))
# 256 sign cells. A real raster atlas, never a font dependency in the viewer.
signs=Image.new('RGB',(2048,2048),(78,49,28));d=ImageDraw.Draw(signs)
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
try:font=ImageFont.truetype(fontpath,18);small=ImageFont.truetype(fontpath,11)
except OSError:font=ImageFont.load_default();small=font
index={}
for i,r in enumerate(ROOMS):
 col,row=i%8,i//8;xx,yy=col*256,row*64
 d.rounded_rectangle((xx+3,yy+3,xx+252,yy+60),4,fill=(71,45,27),outline=(186,150,79),width=2)
 title=r['name'];title=title if len(title)<33 else title[:30]+'…'
 d.text((xx+128,yy+19),r['id'].replace('_',' ').upper(),font=font,fill=(234,213,151),anchor='mm')
 d.text((xx+128,yy+43),title,font=small,fill=(222,204,158),anchor='mm')
 index[r['id']]={'cell':i,'title':r['name']}
signs.save(OUT/'Aurelian_signs.png',optimize=True)
(OUT/'signs.json').write_text(json.dumps(index,indent=2))
print('Wrote six original PBR/sign/emission atlases to',OUT)
