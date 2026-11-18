"""Actual-image evidence index and native-resolution six-room review pages.
No rendering/generation of ship content, resizing/upscaling of deliverable
JPGs, or automatic visual approval. Contact sheets are excluded scratch.
"""
from pathlib import Path
import json,base64,io,html,hashlib,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shipdesign.leonidas_ii import ROOMS,DECKS
OUT=ROOT/'renders/leonidas_ii';DOC=ROOT/'docs/leonidas_ii';WORK=OUT/'build/review';WORK.mkdir(parents=True,exist_ok=True)
register=json.loads((OUT/'all_cameras.json').read_text());by={Path(r['file']).stem:r for r in register}
SOURCE_HASH=hashlib.sha256((ROOT/'models/leonidas_ii/Aurelian_1889.blend').read_bytes()).hexdigest();RENDERER_HASH=hashlib.sha256((ROOT/'blender/leonidas_ii/render.py').read_bytes()).hexdigest()
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
except OSError:font=ImageFont.load_default()
# 2 x 3, each survey at its ORIGINAL 640 x 480 pixels. The tiny heading
# bars do not obscure any image content. Open these to inspect every room.
reviewed=[]
for page,start in enumerate(range(0,len(ROOMS),6),1):
 rows=ROOMS[start:start+6]
 # Only assemble COMPLETE pages from exact registered final JPGs. This
 # allows review during later serial render batches without promoting raw,
 # missing or stale pixels to a seemingly finished native review page.
 entries=[by.get('Room_'+room['id']) for room in rows]
 if not all(r and r.get('source_sha256')==SOURCE_HASH and r.get('renderer_sha256')==RENDERER_HASH and Path(r['file']).suffix=='.jpg' and (ROOT/r['file']).exists() and r.get('sha256')==hashlib.sha256((ROOT/r['file']).read_bytes()).hexdigest() for r in entries):continue
 sheet=Image.new('RGB',(1280,1560),'#eee8dc');draw=ImageDraw.Draw(sheet);ids=[]
 for i,room in enumerate(rows):
  name='Room_'+room['id'];r=by.get(name)
  if not r:continue
  image=Image.open(ROOT/r['file']).convert('RGB');assert image.size==(640,480)
  x=(i%2)*640;y=(i//2)*520;sheet.paste(image,(x,y+40));text=room['id']+' / '+room['deck'].upper()+' / '+room['name']
  draw.text((x+10,y+8),text[:77],font=font,fill='#17313b');ids.append(room['id'])
 sheet.save(WORK/f'Rooms_{page:02}.jpg',quality=93,subsampling=0)
 reviewed.append(dict(page=page,file=str((WORK/f'Rooms_{page:02}.jpg').relative_to(ROOT)),room_ids=ids))
(WORK/'sheet_index.json').write_text(json.dumps(reviewed,indent=2))
if '--sheets-only' in sys.argv:
 print('Wrote',len(reviewed),'native six-room sheets. Approval still requires opening them.');sys.exit(0)
room_lookup={r['id']:r for r in ROOMS}
def enc(text):return html.escape(str(text),quote=True)
def category(r):
 name=Path(r['file']).stem
 if name.startswith('Room_'):return 'Room surveys'
 if r.get('supplementary') or name.startswith('Supplement_'):return 'Correction details'
 if name.startswith('Exterior_'):return 'Exterior'
 if name.startswith('Plan_') or name=='Engineering_Structural_Skeleton':return 'Decks & structure'
 if name.startswith(('Machinery_','Engineering_')):return 'Machinery'
 return 'Interiors'
cards=[]
groups=['Exterior','Interiors','Machinery','Decks & structure','Correction details','Room surveys']
ordered=sorted(register,key=lambda r:(groups.index(category(r)),r.get('room_id') or '',r['file']))
for r in ordered:
 path=ROOT/r['file']
 assert path.is_file() and path.suffix=='.jpg' and r.get('source_sha256')==SOURCE_HASH and r.get('renderer_sha256')==RENDERER_HASH and r.get('sha256')==hashlib.sha256(path.read_bytes()).hexdigest(),('Only exact current-source final JPGs may enter the gallery',r['file'])
 im=Image.open(path).convert('RGB');im.thumbnail((620,390),Image.Resampling.LANCZOS);buf=io.BytesIO();im.save(buf,'JPEG',quality=80,optimize=True)
 uri='data:image/jpeg;base64,'+base64.b64encode(buf.getvalue()).decode();cat=category(r);room=r.get('room_id');deck=room_lookup.get(room,{}).get('deck','')
 tag='ROOF-OFF DIAGNOSTIC' if Path(r['file']).stem.startswith('Room_') else 'TECHNICAL CUTAWAY' if r['cutaway'] else 'ACTUAL MODEL VIEW'
 caption=enc(r['title']);name=Path(r['file']).stem
 cards.append(f'<article data-group="{enc(cat)}" data-search="{enc((name+" "+r["title"]+" "+deck).lower())}"><img loading="lazy" src="{uri}" alt="{caption}"><div class="caption"><small>{tag} · {r["pixels"][0]} × {r["pixels"][1]}</small><h3>{caption}</h3><p>{enc(name)} {("· "+deck.upper()) if deck else ""}</p><code>{enc(r["file"])}</code></div></article>')
source=hashlib.sha256((ROOT/'models/leonidas_ii/Aurelian_1889.blend').read_bytes()).hexdigest();major=sum(category(r) not in ('Room surveys','Correction details') for r in register);rooms=sum(category(r)=='Room surveys' for r in register);supplementary=sum(category(r)=='Correction details' for r in register)
review_file=DOC/'VISUAL_REVIEW.json';review=json.loads(review_file.read_text()) if review_file.exists() else {};review_matches=review.get('source_sha256')==source
review_summary=(str(len(review.get('major_images',[])))+'/51 major views, '+str(len(review.get('room_surveys',[])))+'/203 surveys and '+str(len(review.get('supplementary_images',[])))+'/2 supplementary correction details recorded in the manual review register; status: '+str(review.get('status','NOT_RECORDED'))+'.') if review_matches else 'No matching current-source manual review register. Image presence is not visual acceptance.'
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>SS Aurelian · actual-model evidence</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f3f0e9;color:#1e333d;font:16px/1.5 system-ui,Arial,sans-serif}header{background:#142c37;color:#f5f0e5;padding:52px max(24px,5vw) 36px}header small{color:#d6b77b;letter-spacing:.2em;font-weight:700}h1{font:600 clamp(36px,5vw,66px)/1.05 Georgia,serif;margin:18px 0}header p{max-width:850px;color:#c9d4d7;margin:18px 0}.status{display:inline-block;color:#f3dfb0;border:1px solid #977c4b;border-radius:3px;padding:6px 10px;font-size:13px}.numbers{display:flex;gap:38px;flex-wrap:wrap;margin-top:28px}.numbers b{font-size:28px;display:block;color:white}.numbers span{color:#b9cacc;font-size:13px}.source{font-size:11px;overflow-wrap:anywhere;color:#9db1b7;margin-top:22px}nav{position:sticky;top:0;z-index:2;background:#f3f0e9f5;border-bottom:1px solid #d5d3c9;padding:15px max(24px,5vw);display:flex;gap:8px;align-items:center;flex-wrap:wrap}button,input{font:inherit;font-size:13px;padding:9px 12px;border:1px solid #bdc3be;background:transparent;color:#193b49;border-radius:3px}button{cursor:pointer}button[aria-pressed=true]{background:#193b49;color:white;border-color:#193b49}input{margin-left:auto;min-width:225px}main{padding:30px max(24px,5vw) 70px}.note{margin:0 0 24px;font-size:13px;color:#5c696b}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:24px}article{background:#fffdf8;border:1px solid #dedbd2;border-radius:4px;overflow:hidden}article[hidden]{display:none}article img{display:block;width:100%;aspect-ratio:1.59;object-fit:contain;background:#53646b}.caption{padding:17px 18px 21px}h3{font:600 21px/1.3 Georgia,serif;margin:8px 0}small{font-size:10px;letter-spacing:.08em;color:#916d2d;font-weight:700}.caption p{font-size:12px;color:#56696e;margin:6px 0}.caption code{font-size:10px;color:#6a7778;overflow-wrap:anywhere}footer{padding:24px 5vw;background:#dfe4df;font-size:12px;color:#435b63}@media(max-width:600px){header{padding-top:32px}.grid{grid-template-columns:1fr}input{width:100%;margin:0}.numbers{gap:22px}nav{position:relative}}</style>
<header><small>OPERATION VICTORIA / LEONIDAS-II</small><h1>SS Aurelian, 1889</h1><span class="status">REVIEW CANDIDATE · ROBLOX STUDIO ACCEPTANCE UNVERIFIED</span><p>Actual Cycles images of the delivered editable model. No concept imagery, museum plan tracings or simulated gameplay screenshots. Cutaways and roof-off surveys are explicitly identified.</p><div class="numbers"><div><b>MAJOR_COUNT</b><span>major / technical views</span></div><div><b>ROOM_COUNT</b><span>physical-space surveys</span></div><div><b>SUPPLEMENTARY_COUNT</b><span>additional correction details</span></div><div><b>166 m</b><span>length overall</span></div><div><b>7</b><span>deck datums</span></div></div><div class="source">MASTER SHA-256 · SOURCE_HASH</div></header>
<nav><button aria-pressed="true" data-filter="All">All views</button><button data-filter="Exterior">Exterior</button><button data-filter="Interiors">Interiors</button><button data-filter="Machinery">Machinery</button><button data-filter="Decks &amp; structure">Decks &amp; structure</button><button data-filter="Correction details">Correction details</button><button data-filter="Room surveys">203-room survey</button><input type="search" placeholder="Find a space, deck or image…" aria-label="Search evidence"></nav><main><p class="note"><strong>MANUAL_REVIEW_SUMMARY</strong> These are embedded index thumbnails, not replacements for the full-resolution JPGs. Full image paths and their original pixel dimensions appear on every card. Source/processing/camera metadata: renders/leonidas_ii/all_cameras.json. Up to 12 adaptive samples for major views / 6 for surveys, conventional OIDN and a temporary 1K texture cache leave softness/noise; original delivered 2K maps are unchanged. Visual review does not certify hidden geometry, live avatars or performance.</p><section class="grid">CARDS</section></main><footer>Project-derived fictional single-screw Atlantic liner. Built: 628 passenger sleeping positions (including 114 modeled convertible settee berths, not additional permanent beds; conversion/live sleeping unimplemented) + 117 crew berths; 900/196 planning targets not achieved. Three boat sockets only; no full eleven-boat inventory or joint boat/port approval. Read DELIVERY_REPORT.md and ROBLOX_INSTALL_AND_TEST.md before installation.</footer><script>let group='All';const buttons=[...document.querySelectorAll('button')],input=document.querySelector('input'),cards=[...document.querySelectorAll('article')];function filter(){const q=input.value.toLowerCase();for(const c of cards)c.hidden=!(group==='All'||c.dataset.group===group)||!c.dataset.search.includes(q)}for(const b of buttons)b.onclick=()=>{group=b.dataset.filter;for(const a of buttons)a.setAttribute('aria-pressed',a===b?'true':'false');filter()};input.oninput=filter;</script></html>'''
page=page.replace('MAJOR_COUNT',str(major)).replace('ROOM_COUNT',str(rooms)).replace('SUPPLEMENTARY_COUNT',str(supplementary)).replace('SOURCE_HASH',source).replace('MANUAL_REVIEW_SUMMARY',enc(review_summary)).replace('CARDS','\n'.join(cards))
(DOC/'EVIDENCE_INDEX.html').write_text(page)
# During rendering camera_register is the latest batch. At a gallery
# checkpoint expose the verified cumulative set there too, without changing
# any camera/source/pixel records or automatically approving an image.
(OUT/'camera_register.json').write_text(json.dumps(register,indent=2))
print('Wrote evidence index:',major,'major /',rooms,'surveys /',supplementary,'supplementary details; contact pages:',len(reviewed))
