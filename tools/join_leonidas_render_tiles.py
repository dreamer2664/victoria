"""Join overlapping CAMERA BORDER renders, not generated images/upscaling.
Invocation: python3 .../join_leonidas_render_tiles.py <json-manifest>
"""
from pathlib import Path
import sys,json
from PIL import Image
p=Path(sys.argv[1]);data=json.loads(p.read_text());canvas=Image.new('RGB',data['size'])
for t in data['tiles']:
 im=Image.open(t['file']).convert('RGB');x0,y0,x1,y1=t['box'];ox,oy=t['source_origin'];w,h=x1-x0,y1-y0
 # Pixel boxes are full-frame top-left coordinates. Rendering keeps padding
 # around the tile so denoising is not asked to extrapolate at the join.
 xx,yy=x0-ox,y0-oy;canvas.paste(im.crop((xx,yy,xx+w,yy+h)),(x0,y0))
canvas.save(data['output'],optimize=True)
