"""Build the requested title-only, completely offline gallery of ALL finals.

Native-pixel WebP display copies are encoded from exact registered final JPGs;
no resizing, generated content, remote dependencies or automatic visual approval.
Original JPGs/camera/source hashes stay in the separate machine-readable index.
Run only after the individual image review has been recorded:
  python3 tools/make_leonidas_render_gallery.py
The default file replaces the superseded evidence index, not the render files.
"""
from pathlib import Path
import sys,json,html,hashlib,base64,io,re
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shipdesign.leonidas_ii import ROOMS,DECKS
RENDER=ROOT/'renders/leonidas_ii';DOC=ROOT/'docs/leonidas_ii'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
MAJOR_TITLES={
 'Exterior_Bow_Port':'Port Bow','Exterior_Stern_Starboard':'Starboard Stern','Exterior_Broadside_Port':'Port Broadside','Exterior_Overhead':'Upper Decks',
 'Machinery_Engine_Aisle':'Engine Room','Engineering_Engine_Cutaway':'Triple-Expansion Engine — Cutaway','Engineering_Crossheads_ValveGear':'Crossheads and Valve Gear — Cutaway',
 'Machinery_Stokehold':'Middle Stokehold','Machinery_Stokehold_After':'After Stokehold','Machinery_Stokehold_Forward':'Forward Stokehold',
 'Engineering_Stern_Aperture':'Propeller and Rudder — Dry Inspection','Machinery_Shaft_Alley':'Shaft Alley','Machinery_Steam_Steering':'Steam Steering Room',
 'Machinery_Dynamos_And_Switchboard':'Dynamos and Switchboards','Machinery_Feed_Pumps':'Feed Pumps','Engineering_Structural_Skeleton':'Keel and Framing — Cutaway',
 'Interior_Dining_First':'First-Class Dining Saloon','Interior_Library':'Library','Interior_Smoking':'Smoking Room','Interior_Music':'Music Room','Interior_Writing':'Writing Room',
 'Interior_Grand_Stair':'Grand Stair — Cutaway','Interior_Dining_Second':'Second-Class Dining Saloon','Interior_Second_Lounge':'Second-Class Lounge',
 'Interior_Cabin_First':'First-Class Cabin','Interior_Cabin_Second':'Second-Class Cabin','Interior_Third_Class':'Third-Class Accommodation','Interior_Crew':'Crew Accommodation',
 'Interior_Captain':"Captain’s Cabin",'Interior_Officer':"Officer’s Cabin",'Interior_Wheelhouse':'Wheelhouse','Interior_Chart_Signals':'Chart and Signals Room',
 'Interior_Galley':'Galley','Interior_Bakery':'Bakery','Interior_Pantry':'Pantry','Interior_Bath':'Bathroom','Interior_Lavatory':'Lavatory','Interior_Hospital':'Hospital',
 'Interior_Purser':"Purser’s Office",'Interior_Mail':'Mail Room','Interior_Barber':'Barber Shop','Interior_Cargo':'Cargo Hold','Interior_Cold_Store':'Cold Store','Interior_Bar':'Bar',
 'Supplement_Crew_Mess_Port':'Port Crew Mess — Cutaway','Supplement_Crew_Mess_Starboard':'Starboard Crew Mess — Cutaway',
 'Detail_Exterior_Bridge':'Bridge and Officer Deckhouses','Detail_Exterior_Promenade':'After Deckhouse and Rigging','Detail_Promenade_Bench':'Promenade Bench',
 'Detail_Mast_Ladder':'Foremast Ladder','Detail_Funnel_Ladder':'Funnel Ladder','Detail_Lifebuoy_Hook':'Lifebuoy Bracket','Detail_Wheelhouse_Framing':'Wheelhouse Ceiling and Controls',
}

MICRO_NAMES={'Micro_Dining_Tableware','Micro_Dining_Underside','Micro_Piano_Stool_Feet','Micro_Pantry_Crockery','Micro_Bunk_Ladder','Micro_Door_Hinge_Closed','Micro_Door_Hinge_Open','Micro_Hospital_Trolley','Micro_Thrust_Bearings'}
IDENTITY_KEYS=('file','sha256','source_sha256','renderer_sha256','pixels','cycles_samples','room_id','cutaway','detail_driver','detail_driver_sha256','supplementary')
def expected_major():return set(MAJOR_TITLES)-{k for k in MAJOR_TITLES if k.startswith(('Supplement_','Detail_'))}|{'Plan_'+d for d in DECKS}
def expected_all():return expected_major()|{'Room_'+r['id'] for r in ROOMS}|{k for k in MAJOR_TITLES if k.startswith(('Supplement_','Detail_'))}|MICRO_NAMES

def main():
 source=sha(ROOT/'models/leonidas_ii/Aurelian_1889.blend');renderer=sha(ROOT/'blender/leonidas_ii/render.py')
 rows=[]
 for p in sorted(RENDER.rglob('all_cameras.json')):
  if 'build' in p.relative_to(RENDER).parts:continue
  rows.extend(json.loads(p.read_text()))
 by={}
 for r in rows:
  p=ROOT/r['file'];assert p.is_file() and p.suffix=='.jpg',('Missing final JPG',r['file'])
  assert r.get('source_sha256')==source and r.get('renderer_sha256')==renderer,('Stale source/renderer',r['file'])
  assert r.get('sha256')==sha(p),('Image hash changed',r['file'])
  assert list(Image.open(p).size)==r['pixels'],('Native pixel dimensions changed',r['file'])
  for key in ('detail_driver','detail_driver_sha256'):
   if key=='detail_driver' and r.get(key):assert r.get('detail_driver_sha256')==sha(ROOT/r[key]),('Stale detail driver',r['file'])
  previous=by.get(r['file']);assert previous is None or previous==r,('Conflicting duplicate image registration',r['file'])
  by[r['file']]=r
 assert by,'No final renders found'
 stems={Path(r['file']).stem for r in by.values()};required=expected_all();assert len(required)==272,'Required-view contract changed; reconcile the delivery target explicitly'
 assert required<=stems,('Gallery is incomplete',sorted(required-stems))
 on_disk={str(p.relative_to(ROOT)) for p in RENDER.rglob('*.jpg') if 'build' not in p.relative_to(RENDER).parts}
 assert set(by)==on_disk,('Unregistered or missing final render',sorted(on_disk-set(by)),sorted(set(by)-on_disk))
 review=json.loads((DOC/'FINAL_RENDER_REVIEW.json').read_text());opened=review.get('images',[])
 assert review.get('source_sha256')==source and review.get('renderer_sha256')==renderer and not review.get('blocking_issues') and review.get('status')=='ALL_FINAL_RENDERS_INDIVIDUALLY_REVIEWED_WITH_LIMITATIONS','Individual final review is incomplete'
 seen={v['file']:v for v in opened}
 assert len(opened)==len(seen)==len(by) and set(seen)==set(by),'Review does not cover every final render exactly once'
 assert all(all(v.get(k)==by[p].get(k) for k in IDENTITY_KEYS) and v.get('status') in ('REVIEWED','REVIEWED_WITH_LIMITATIONS') and v.get('observation') and v.get('pixel_association')=='VISIBLE_FILENAME_AND_SHA256_STRIP_WITH_BIT_IDENTICAL_NATIVE_RENDER_BODY' for p,v in seen.items()),'Stale or incomplete individual review record, renderer/camera-driver identity or exact-file pixel association'
 rooms={r['id']:r for r in ROOMS}
 def group(r):
  n=Path(r['file']).stem
  return 0 if n.startswith('Exterior_') else 1 if n.startswith('Interior_') else 2 if n.startswith(('Machinery_','Engineering_')) else 3 if n.startswith('Plan_') else 5 if n.startswith('Room_') else 4
 def title(r):
  n=Path(r['file']).stem
  if n in MAJOR_TITLES:return MAJOR_TITLES[n]
  if n.startswith('Plan_'):return r.get('short_title') or n[5:].title()+' Deck — Cutaway'
  if n.startswith('Room_'):
   rid=n[5:];room=rooms[rid];name=room['name']
   name=re.sub(r'(?i)\b(first|second|third) class\b',lambda m:m.group(1).title()+'-Class',name)
   name=re.sub(r'\s+'+re.escape(rid)+r'\b','',name).strip()
   return rid+' · '+name+' — Roof Off'
  assert r.get('short_title'),('Add a short descriptive title',n)
  return r['short_title']
 ordered=sorted(by.values(),key=lambda r:(group(r),r.get('room_id') if group(r)==5 else '',r['file']))
 articles=[];manifest=[]
 for i,r in enumerate(ordered):
  p=ROOT/r['file'];im=Image.open(p).convert('RGB');original_size=im.size
  assert seen[r['file']].get('decoded_rgb_sha256')==hashlib.sha256(im.tobytes()).hexdigest(),('Pixel-association body no longer matches original',r['file'])
  b=io.BytesIO();im.save(b,'WEBP',quality=80,method=6)
  blob=b.getvalue();assert Image.open(io.BytesIO(blob)).size==original_size
  label=title(r);escaped=html.escape(label,quote=True);uri='data:image/webp;base64,'+base64.b64encode(blob).decode()
  articles.append(f'<article><button class="open" type="button" data-index="{i}" aria-label="{escaped}"><img loading="lazy" decoding="async" src="{uri}" width="{im.width}" height="{im.height}" alt="{escaped}"></button><h2>{html.escape(label)}</h2></article>')
  manifest.append(dict(file=r['file'],title=label,sha256=r['sha256'],pixels=r['pixels'],source_sha256=source,display_format='WebP80, original pixel dimensions; conventional display compression only',display_sha256=hashlib.sha256(blob).hexdigest(),display_bytes=len(blob)))
 page='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>SS Aurelian — All Renders</title><style>
*{box-sizing:border-box}html{color-scheme:dark}body{margin:0;background:#101719;color:#ece9df;font:16px/1.4 system-ui,-apple-system,Segoe UI,Arial,sans-serif}header{padding:48px 4vw 36px;border-bottom:1px solid #364044}h1{max-width:1760px;margin:0 auto;font:400 clamp(32px,4vw,60px)/1.1 Georgia,serif;letter-spacing:-.025em}main{max-width:1900px;margin:auto;padding:30px 4vw 70px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:36px 28px}article{min-width:0}button{font:inherit;color:inherit;cursor:pointer}button.open{display:block;width:100%;padding:0;border:0;background:#192326;border-radius:3px;overflow:hidden}button.open:focus-visible{outline:2px solid #cdb580;outline-offset:6px}article img{display:block;width:100%;height:auto;aspect-ratio:1.6;object-fit:contain}h2{font:400 19px/1.35 Georgia,serif;letter-spacing:.01em;margin:13px 0 0}dialog{position:fixed;inset:0;width:100vw;height:100dvh;max-width:none;max-height:none;border:0;margin:0;padding:54px 58px 65px;background:#080e10f8;color:#f3f0e7}dialog::backdrop{background:#080e10}dialog[open]{display:flex;align-items:center;justify-content:center}dialog img{display:block;max-width:100%;max-height:calc(100dvh - 140px);width:auto;height:auto;margin:auto;object-fit:contain}dialog h2{text-align:center;position:absolute;left:50px;right:50px;bottom:24px;margin:0}dialog button{position:absolute;z-index:3;background:#1c292dbf;border:1px solid #6b777b;border-radius:50%;width:44px;height:44px;line-height:1}#close{top:12px;right:16px;font-size:26px}#previous{left:10px;top:48%;font-size:22px}#next{right:10px;top:48%;font-size:22px}@media(min-width:1500px){main{gap:44px 34px}h2{font-size:21px}}@media(max-width:760px){header{padding:32px 5vw 25px}main{grid-template-columns:1fr;padding:22px 5vw 45px;gap:28px}h2{font-size:18px}dialog{padding:58px 12px 80px}dialog h2{left:35px;right:35px;font-size:17px}dialog button{width:44px;height:44px}#previous{left:4px}#next{right:4px}}@media(prefers-reduced-motion:no-preference){button.open img{transition:opacity .18s}button.open:hover img{opacity:.88}}
</style></head><body><header><h1>SS Aurelian</h1></header><main>ARTICLES</main>
<dialog aria-labelledby="image-title"><button id="close" type="button" aria-label="Close">×</button><button id="previous" type="button" aria-label="Previous render">←</button><img id="expanded" alt=""><button id="next" type="button" aria-label="Next render">→</button><h2 id="image-title"></h2></dialog>
<script>const cards=[...document.querySelectorAll('article')],dialog=document.querySelector('dialog'),expanded=document.querySelector('#expanded'),label=document.querySelector('#image-title');let index=0,last=null;function display(i){index=(i+cards.length)%cards.length;let c=cards[index],im=c.querySelector('img');expanded.src=im.src;expanded.alt=im.alt;label.textContent=c.querySelector('h2').textContent}for(const b of document.querySelectorAll('.open'))b.addEventListener('click',()=>{last=b;display(Number(b.dataset.index));dialog.showModal()});document.querySelector('#close').onclick=()=>dialog.close();document.querySelector('#previous').onclick=()=>display(index-1);document.querySelector('#next').onclick=()=>display(index+1);dialog.addEventListener('close',()=>{expanded.removeAttribute('src');if(last)last.focus()});document.addEventListener('keydown',e=>{if(!dialog.open)return;if(e.key==='ArrowLeft'){e.preventDefault();display(index-1)}if(e.key==='ArrowRight'){e.preventDefault();display(index+1)}});dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});</script></body></html>'''.replace('ARTICLES','\n'.join(articles))
 assert not re.search(r'<(?:p|figcaption|footer)\b',page,re.I),'Only short titles, never captions'
 assert not re.search(r'(?:src|href)=["\']https?://',page),'Gallery must work offline'
 output=DOC/'EVIDENCE_INDEX.html';output.write_text(page)
 report=dict(schema='victoria.leonidas-ii.title-only-render-gallery/1.0',file=str(output.relative_to(ROOT)),sha256=sha(output),bytes=output.stat().st_size,source_sha256=source,renderer_sha256=renderer,builder_sha256=sha(Path(__file__)),final_review_sha256=sha(DOC/'FINAL_RENDER_REVIEW.json'),images=manifest,counts=dict(total=len(manifest),major=len(expected_major()),room_surveys=len(ROOMS),crew_details=sum(n.startswith('Supplement_') for n in stems),micro_details=sum(n.startswith('Micro_') for n in stems),refinement_details=sum(n.startswith('Detail_') for n in stems)),captions=False,external_resources=False,display_resizing=False)
 (DOC/'RENDER_GALLERY.json').write_text(json.dumps(report,indent=2)+'\n')
 print('TITLE-ONLY OFFLINE GALLERY',len(manifest),'renders,',output.stat().st_size,'bytes')

if __name__=='__main__':main()
