"""No-resize room inspection sheets; no image generation or approval.
Usage: --register <all_cameras.json> --output <excluded inspection folder>.
Only complete pages of original, exact hash-bound 640x480 final JPGs appear.
"""
from pathlib import Path
import argparse,json,hashlib,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shipdesign.leonidas_ii import ROOMS
p=argparse.ArgumentParser();p.add_argument('--register',required=True);p.add_argument('--output',required=True);a=p.parse_args()
reg=ROOT/a.register;out=ROOT/a.output;out.mkdir(parents=True,exist_ok=True);rows=json.loads(reg.read_text());by={r.get('room_id'):r for r in rows if Path(r['file']).name.startswith('Room_')};ordered=sorted(ROOMS,key=lambda r:r['id']);sheets=[]
H=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
except OSError:font=ImageFont.load_default()
for page,start in enumerate(range(0,len(ordered),6),1):
 rooms=ordered[start:start+6];entries=[by.get(r['id']) for r in rooms]
 if not all(r and Path(r['file']).suffix=='.jpg' and (ROOT/r['file']).is_file() and r.get('pixels')==[640,480] and H(ROOT/r['file'])==r.get('sha256') for r in entries):continue
 assert len({r['source_sha256'] for r in entries})==len({r['renderer_sha256'] for r in entries})==1
 sheet=Image.new('RGB',(1280,1560),'#ede9e0');draw=ImageDraw.Draw(sheet)
 for i,(room,r) in enumerate(zip(rooms,entries)):
  im=Image.open(ROOT/r['file']).convert('RGB');assert im.size==(640,480);x,y=i%2*640,i//2*520
  sheet.paste(im,(x,y+40));draw.text((x+10,y+7),f"{room['id']} / {room['deck'].upper()} / {room['name']}"[:76],font=font,fill='#142e38')
 f=out/f'Sheet_{page:02}.jpg';sheet.save(f,quality=94,subsampling=0,optimize=True)
 sheets.append(dict(page=page,file=str(f.relative_to(ROOT)),sha256=H(f),pixels=[1280,1560],panel_pixels=[640,480],no_resize=True,source_sha256=entries[0]['source_sha256'],renderer_sha256=entries[0]['renderer_sha256'],inputs=[dict(room=r['room_id'],file=r['file'],sha256=r['sha256']) for r in entries]))
(out/'pages.json').write_text(json.dumps(dict(status='PAGES_CREATED_NOT_VISUALLY_REVIEWED',register=str(reg.relative_to(ROOT)),pages=sheets),indent=2)+'\n');print('Complete native-size sheets:',len(sheets),'; no approval recorded.')
