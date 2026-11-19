"""Verify every embedded image and offline responsive gallery interaction.
Run AFTER real individual-image review and make_leonidas_render_gallery.py.
Requires Pillow, Playwright and its Chromium headless shell/system libraries.
These are byte/UI tests, never automatic visual, model or Studio acceptance.
"""
from pathlib import Path
from html.parser import HTMLParser
import base64,hashlib,io,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];DOC=ROOT/'docs/leonidas_ii';REND=ROOT/'renders/leonidas_ii'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
page=DOC/'EVIDENCE_INDEX.html';manifest=json.loads((DOC/'RENDER_GALLERY.json').read_text());review=DOC/'FINAL_RENDER_REVIEW.json'
assert manifest['sha256']==H(page) and manifest['final_review_sha256']==H(review)
assert manifest['source_sha256']==H(ROOT/'models/leonidas_ii/Aurelian_1889.blend')
assert not manifest['captions'] and not manifest['external_resources'] and not manifest['display_resizing']

class Cards(HTMLParser):
 def __init__(self):super().__init__();self.cards=[];self.current=None;self.in_title=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);assert tag not in ('p','figcaption','footer'),('Unexpected caption element',tag)
  for k in ('src','href','srcset'):assert not a.get(k,'').startswith(('https:','http:','//')),('External dependency',tag,k)
  if tag=='article':self.current=dict(title='');self.cards.append(self.current)
  elif self.current is not None and tag=='img':self.current.update(src=a['src'],alt=a['alt'],pixels=[int(a['width']),int(a['height'])])
  elif self.current is not None and tag=='button':self.current['index']=int(a['data-index'])
  elif self.current is not None and tag=='h2':self.in_title=True
 def handle_endtag(self,tag):
  if tag=='h2':self.in_title=False
  if tag=='article':self.current=None
 def handle_data(self,data):
  if self.current is not None and self.in_title:self.current['title']+=data

parsed=Cards();parsed.feed(page.read_text());rows=manifest['images'];disk={str(p.relative_to(ROOT)) for p in REND.rglob('*.jpg') if 'build' not in p.relative_to(REND).parts}
assert len(parsed.cards)==len(rows)==len(disk)==manifest['counts']['total']==272 and {r['file'] for r in rows}==disk
stems={Path(r['file']).stem for r in rows};rooms=json.loads((ROOT/'exports/leonidas_ii/build_data.json').read_text())['rooms']
assert {'Room_'+r['id'] for r in rooms}=={n for n in stems if n.startswith('Room_')}
for field,prefix,count in (('room_surveys','Room_',203),('crew_details','Supplement_',2),('micro_details','Micro_',9),('refinement_details','Detail_',7)):
 assert manifest['counts'][field]==sum(n.startswith(prefix) for n in stems)==count
assert manifest['counts']['major']==51
review_rows={r['file']:r for r in json.loads(review.read_text())['images']};assert set(review_rows)==disk
for i,(card,row) in enumerate(zip(parsed.cards,rows)):
 assert card['index']==i and card['title']==card['alt']==row['title'] and card['pixels']==row['pixels']
 assert card['src'].startswith('data:image/webp;base64,')
 blob=base64.b64decode(card['src'].partition(',')[2],validate=True)
 assert hashlib.sha256(blob).hexdigest()==row['display_sha256'] and len(blob)==row['display_bytes']
 with Image.open(io.BytesIO(blob)) as im:assert im.format=='WEBP' and list(im.size)==row['pixels']
 original=ROOT/row['file'];assert H(original)==row['sha256']
 with Image.open(original) as im:
  native=im.convert('RGB');manual=review_rows[row['file']]
  assert manual.get('pixel_association')=='VISIBLE_FILENAME_AND_SHA256_STRIP_WITH_BIT_IDENTICAL_NATIVE_RENDER_BODY' and manual.get('decoded_rgb_sha256')==hashlib.sha256(native.tobytes()).hexdigest()
  out=io.BytesIO();native.save(out,'WEBP',quality=80,method=6)
 assert out.getvalue()==blob,('Embedded data is not exact native-dimension encoding of the stated original',row['file'])
print('ALL EMBEDDED IMAGES VERIFIED',len(rows),flush=True)

from playwright.sync_api import sync_playwright
screens=REND/'build/review/gallery';screens.mkdir(parents=True,exist_ok=True);errors=[];external=[];ui=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,args=['--disable-dev-shm-usage'])
 context=browser.new_context(viewport={'width':1440,'height':1000});context.set_offline(True)
 tab=context.new_page();tab.on('pageerror',lambda e:errors.append(str(e)));tab.on('request',lambda r:external.append(r.url) if r.url.startswith(('http:','https:')) else None)
 tab.goto(page.as_uri(),wait_until='domcontentloaded');assert tab.locator('article').count()==len(rows)
 assert tab.evaluate('document.documentElement.scrollWidth<=innerWidth')
 tab.locator('article img').first.evaluate('(im)=>im.decode()')
 tab.screenshot(path=str(screens/'Gallery_Desktop.png'))
 tab.locator('.open').first.click();tab.locator('#expanded').evaluate('(im)=>im.decode()')
 assert tab.locator('dialog').evaluate('(d)=>d.open') and tab.locator('#image-title').inner_text()==rows[0]['title']
 assert tab.locator('#expanded').evaluate('(im)=>[im.naturalWidth,im.naturalHeight]')==rows[0]['pixels']
 for control in ('#next','#previous','#close'):
  box=tab.locator(control).bounding_box();assert box and box['width']>=44 and box['height']>=44
 tab.keyboard.press('ArrowRight');assert tab.locator('#image-title').inner_text()==rows[1]['title']
 tab.keyboard.press('ArrowLeft');assert tab.locator('#image-title').inner_text()==rows[0]['title']
 tab.keyboard.press('ArrowLeft');tab.locator('#expanded').evaluate('(im)=>im.decode()');assert tab.locator('#image-title').inner_text()==rows[-1]['title']
 assert tab.locator('#expanded').evaluate('(im)=>[im.naturalWidth,im.naturalHeight]')==rows[-1]['pixels']
 tab.keyboard.press('Escape');assert not tab.locator('dialog').evaluate('(d)=>d.open')
 assert tab.locator('.open').first.evaluate('(b)=>document.activeElement===b')
 ui.append(dict(viewport=[1440,1000],status='PASS',checks='Offline load, title-only cards, no horizontal overflow, native image decode, modal, next/previous keys, wraparound, Escape and focus return.'))
 tab.set_viewport_size({'width':390,'height':844});tab.reload(wait_until='domcontentloaded');assert tab.evaluate('document.documentElement.scrollWidth<=innerWidth')
 first=tab.locator('article').first.bounding_box();assert first and first['width']<=390 and first['x']>=0
 tab.locator('.open').first.click();tab.locator('#expanded').evaluate('(im)=>im.decode()');assert tab.locator('#image-title').inner_text()==rows[0]['title']
 tab.screenshot(path=str(screens/'Gallery_Mobile_Modal.png'))
 for control in ('#next','#previous','#close'):
  box=tab.locator(control).bounding_box();assert box and box['width']>=44 and box['height']>=44
 tab.locator('#next').click();assert tab.locator('#image-title').inner_text()==rows[1]['title']
 tab.locator('#previous').click();assert tab.locator('#image-title').inner_text()==rows[0]['title']
 tab.locator('#close').click();assert not tab.locator('dialog').evaluate('(d)=>d.open')
 ui.append(dict(viewport=[390,844],status='PASS',checks='Offline mobile single-column layout, no horizontal overflow, modal image and touch-sized next/previous/close controls.'))
 # Match the file viewer's opaque-origin allow-scripts iframe, not only a
 # top-level browser tab. No same-origin/modals/network privilege is added.
 context.close();context=browser.new_context(viewport={'width':390,'height':844});context.set_offline(True)
 tab=context.new_page();tab.on('pageerror',lambda e:errors.append(str(e)));tab.on('request',lambda r:external.append(r.url) if r.url.startswith(('http:','https:')) else None)
 tab.set_content('<!doctype html><html><body style="margin:0"><iframe id="sandbox-preview" name="sandbox-preview" sandbox="allow-scripts" style="display:block;border:0;width:100vw;height:100vh"></iframe></body></html>')
 tab.locator('#sandbox-preview').evaluate('(frame,html)=>frame.srcdoc=html',page.read_text())
 preview=tab.locator('#sandbox-preview').element_handle().content_frame();assert preview is not None
 preview.wait_for_function('typeof cards!=="undefined" && cards.length===272')
 assert preview.locator('article').count()==len(rows) and preview.evaluate('document.documentElement.scrollWidth<=innerWidth')
 preview.locator('.open').first.click();preview.locator('#expanded').evaluate('(im)=>im.decode()')
 assert preview.locator('dialog').evaluate('(d)=>d.open') and preview.locator('#image-title').inner_text()==rows[0]['title']
 tab.screenshot(path=str(screens/'Gallery_Sandboxed_Preview.png'))
 preview.locator('#next').click();assert preview.locator('#image-title').inner_text()==rows[1]['title']
 preview.locator('#close').click();assert not preview.locator('dialog').evaluate('(d)=>d.open')
 assert preview.locator('.open').first.evaluate('(b)=>document.activeElement===b')
 sandboxed_preview=dict(status='PASS',sandbox='allow-scripts',viewport=[390,844],checks='Opaque-origin sandboxed iframe, complete offline gallery, no horizontal overflow, image decode, native dialog, next/close and focus return; no allow-same-origin or allow-modals added.')
 assert not errors and not external,(errors,external)
 browser.close()
report=dict(schema='victoria.leonidas-ii.offline-gallery-tests/1.0',status='STRUCTURE_EMBEDDING_AND_OFFLINE_UI_PASS',gallery_sha256=H(page),manifest_sha256=H(DOC/'RENDER_GALLERY.json'),final_review_sha256=H(review),tester_sha256=H(Path(__file__)),source_sha256=manifest['source_sha256'],images_verified=len(rows),native_encoding_reproduced=True,captions=False,external_requests=external,javascript_errors=errors,ui=ui,sandboxed_preview=sandboxed_preview,screenshots=[str(p.relative_to(ROOT)) for p in sorted(screens.glob('Gallery_*.png'))],limits=__doc__)
(DOC/'RENDER_GALLERY_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print('OFFLINE GALLERY TESTS PASS',len(rows),'exact embedded originals / desktop and mobile; not image/model acceptance.',flush=True)
