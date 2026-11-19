"""Prepare unambiguous INTERNAL native-pixel review copies, never a gallery.

Usage: python3 tools/prepare_leonidas_review_images.py [stem-prefix ...]
All output is excluded scratch under renders/leonidas_ii/build/exact-review.
Each original final JPEG is decoded without resizing into a lossless PNG with
its filename/hash strip ABOVE the untouched native render body. Equality is
reopened and verified byte-for-byte. This resolves parallel viewer result-order
ambiguity; it performs NO visual inspection, approval or note generation.
The user-facing title-only gallery always encodes the unlabelled final JPGs.
"""
from pathlib import Path
import hashlib,json,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
RENDER=ROOT/'renders/leonidas_ii';OUT=RENDER/'build/exact-review'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 source=H(ROOT/'models/leonidas_ii/Aurelian_1889.blend');renderer=H(ROOT/'blender/leonidas_ii/render.py')
 # Pillow's bundled/default font is available if the optional system font is not.
 font_path=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
 font=ImageFont.truetype(str(font_path),18) if font_path.exists() else ImageFont.load_default(size=18)
 small=ImageFont.truetype(str(font_path),13) if font_path.exists() else ImageFont.load_default(size=13)
 rows=[]
 for reg in sorted(RENDER.rglob('all_cameras.json')):
  if 'build' in reg.relative_to(RENDER).parts:continue
  for row in json.loads(reg.read_text()):
   if not row.get('sha256') or row.get('source_sha256')!=source or row.get('renderer_sha256')!=renderer:continue
   p=ROOT/row['file'];stem=p.stem
   if len(sys.argv)>1 and not any(stem.startswith(v) for v in sys.argv[1:]):continue
   if row.get('detail_driver') and row['detail_driver_sha256']!=H(ROOT/row['detail_driver']):continue
   assert H(p)==row['sha256'],('Changed original',p)
   with Image.open(p) as im:orig=im.convert('RGB')
   w,h=orig.size;assert row['pixels']==[w,h]
   proof=Image.new('RGB',(w,h+58),'#102633');proof.paste(orig,(0,58));draw=ImageDraw.Draw(proof)
   draw.text((10,4),stem,font=font,fill='white');draw.text((10,31),'SHA256 '+row['sha256'][:24]+'  |  native pixels below',font=small,fill='#b8dfd5')
   out=OUT/(stem+'.png');proof.save(out)
   with Image.open(out) as check:assert check.crop((0,58,w,h+58)).tobytes()==orig.tobytes()
   rows.append(dict(file=row['file'],sha256=row['sha256'],labelled_copy=str(out.relative_to(ROOT)),labelled_sha256=H(out),native_pixels=[w,h],strip_height=58,decoded_rgb_sha256=hashlib.sha256(orig.tobytes()).hexdigest()))
 index=OUT/'index.json';prior={v['file']:v for v in json.loads(index.read_text())} if index.exists() else {};prior.update({v['file']:v for v in rows});index.write_text(json.dumps(sorted(prior.values(),key=lambda v:v['file']),indent=2)+'\n')
 print('Native-pixel identity-labelled review copies prepared:',len(rows),'; no visual approval inferred.')

if __name__=='__main__':main()
