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
 # Authored coordinated textiles / wall coverings, NOT random per-object hues.
 ('CabinBlue',(184,196,193),.79,0,'wallpaper'),('CabinSage',(193,201,174),.79,0,'wallpaper'),
 ('ClothBlue',(45,70,89),.92,0,'brocade'),('ClothSage',(87,107,77),.93,0,'brocade'),('ClothPlum',(102,62,78),.93,0,'brocade'),
 ('SagePaint',(137,158,143),.68,0,'paint'),('LibraryWall',(109,133,112),.88,0,'wallpaper'),
 ('WritingWall',(212,196,190),.90,0,'wallpaper'),('MusicWall',(227,222,205),.87,0,'wallpaper'),('SmokingWall',(142,127,92),.89,0,'wallpaper'),
 ('CarpetNavy',(40,60,71),.97,0,'carpet'),('CarpetSage',(88,106,81),.97,0,'carpet'),('CarpetWine',(104,52,55),.97,0,'carpet'),
 ('Parquet',(126,91,57),.52,0,'parquet'),('Grating',(56,62,59),.73,.5,'grating'),('Bread',(169,119,59),.92,0,'grain'),
 ('Enamel',(221,228,218),.34,.05,'paint'),('Dial',(228,221,196),.42,.05,'dial'),('TelegraphDial',(224,217,192),.44,.05,'telegraph'),
 ('Notice',(218,209,179),.89,0,'notice'),('Seascape',(152,168,166),.9,0,'seascape'),
 ('WeatheredTeak',(129,108,76),.70,0,'wood'),('BilliardBaize',(41,89,65),.96,0,'fabric'),('DeckCanvas',(207,196,166),.93,0,'fabric'),
]
assert len(PALETTE)==64, 'The single 8x8 material atlas must never overflow.'
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
  delta+=grain*4+np.sin(v*math.tau*5+np.sin(u*8)*.6)*.7;height+=grain*.28
 elif pattern in ('fabric','stripe','rope','brocade'):
  weave=(np.sin(u*math.tau*95)+np.sin(v*math.tau*95));delta+=weave*3;height+=weave*2
  if pattern=='stripe':delta+=np.where((x//22)%2,13,-13)
  if pattern=='rope':delta+=np.sin((u+v)*math.tau*13)*9
  if pattern=='brocade':
   ornament=np.cos(u*math.tau*4)*np.cos(v*math.tau*4);delta+=np.where(ornament>.58,7,0);height+=np.where(ornament>.58,.6,0)
 elif pattern=='leather':
  delta+=low*.7;height+=low*.3
 elif pattern=='carpet':
  a=(np.abs(u-.5)+np.abs(v-.5));motif=(np.sin(a*math.tau*4)>0)*5
  delta+=motif+np.cos(u*math.tau*3)*np.cos(v*math.tau*3)*3;height+=motif*.09
 elif pattern=='rubber':
  motif=(np.abs(np.abs(u-.5)+np.abs(v-.5)-.32)<.027)|(x<5)|(y<5);delta+=motif*24;height+=motif*4
 elif pattern=='tile':
  grout=(x%64<3)|(y%64<3);delta-=grout*38;height-=grout*7
  delta+=(((x//64+y//64)%2)*2-1)*7
 elif pattern=='wallpaper':
  stem=np.cos(u*math.tau*8+np.sin(v*math.tau*4)*.6)
  delta+=np.where(stem>.94,-5,0)+np.cos(v*math.tau*4)*1.2;height+=stem*.08
 elif pattern=='parquet':
  # Narrow herringbone staves and fine seams, not giant swirling wood.
  X=x+y;Y=y-x;bands=(X//22+Y//66)%2
  grain=np.sin((np.where(bands,X,Y))*1.7)*1.4
  joint=(X%22<1)|(Y%66<1);delta+=bands*9-4+grain-joint*24;height-=joint*1.5
 elif pattern=='grating':
  hole=(x%32>9)&(y%32>9);delta-=hole*28;height-=hole*8
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
 if pattern in ('dial','telegraph','notice','seascape'):
  im=Image.fromarray(rgb);d=ImageDraw.Draw(im)
  try:facefont=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',14);tiny=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',10)
  except OSError:facefont=ImageFont.load_default();tiny=facefont
  if pattern in ('dial','telegraph'):
   d.ellipse((13,13,243,243),outline=(65,59,45),width=2)
   for j in range(60):
    a=j*math.tau/60;r0=92 if j%5==0 else 101
    d.line((128+r0*math.sin(a),128-r0*math.cos(a),128+110*math.sin(a),128-110*math.cos(a)),fill=(45,47,43),width=2 if j%5==0 else 1)
   if pattern=='dial':
    for j in range(1,13):
     a=j*math.tau/12;d.text((128+78*math.sin(a),128-78*math.cos(a)),str(j),font=facefont,fill=(35,38,35),anchor='mm')
    d.line((128,128,177,88),fill=(29,33,31),width=4);d.line((128,128,99,62),fill=(29,33,31),width=3)
   else:
    for j,txt in enumerate(('FULL','HALF','SLOW','STOP','SLOW','HALF','FULL')):
     a=(-110+j*220/6)*math.pi/180;d.text((128+75*math.sin(a),128-75*math.cos(a)),txt,font=tiny,fill=(49,47,41),anchor='mm')
    d.text((63,195),'ASTERN',font=tiny,fill=(112,48,37),anchor='mm');d.text((187,195),'AHEAD',font=tiny,fill=(37,71,49),anchor='mm')
   d.ellipse((121,121,135,135),fill=(53,53,44))
  elif pattern=='notice':
   d.rectangle((13,13,243,243),outline=(107,88,56),width=3);d.text((128,35),'AURELIAN',font=facefont,fill=(52,59,48),anchor='mm')
   d.text((128,63),'SHIP NOTICES',font=tiny,fill=(70,64,49),anchor='mm')
   for j,length in enumerate((190,177,192,163,185,175,193,157)):
    yy=93+j*15;d.line((31,yy,31+length,yy),fill=(139,130,105),width=2)
  else:
   # Original stylised marine picture for framed joinery, no photo claim.
   d.rectangle((0,126,255,255),fill=(76,111,119));d.polygon([(0,166),(45,158),(97,174),(161,155),(255,163),(255,181),(0,187)],fill=(115,144,145))
   d.polygon([(59,154),(187,154),(170,172),(80,169)],fill=(58,54,45));d.line((127,42,127,156),fill=(57,62,56),width=3)
   d.polygon([(124,54),(124,142),(71,142)],fill=(213,207,181));d.polygon([(132,70),(132,144),(175,144)],fill=(222,214,189))
   d.ellipse((169,32,196,59),fill=(222,211,172))
  rgb=np.asarray(im)
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
