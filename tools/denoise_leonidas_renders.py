"""Standalone Intel Open Image Denoise pass after Blender has EXITED.
Avoid simultaneous geometry + OIDN memory on the 1.9GiB build host.
Actual Cycles pixels only; no image generation, upscaling or geometry edits.
Final JPEG copies bound repository size. Raw PNGs remain in render build/.
LD_LIBRARY_PATH=<Blender>/lib python3 tools/denoise_leonidas_renders.py
"""
from pathlib import Path
import os,sys,ctypes as C,json,hashlib,shutil
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'renders'/'leonidas_ii';RAW=OUT/'build'/'raw';RAW.mkdir(parents=True,exist_ok=True)
lib=C.CDLL(os.getenv('OIDN_LIBRARY','/var/tmp/blender/lib/libOpenImageDenoise.so.2'))
def function(name,restype,args):
 f=getattr(lib,name);f.restype=restype;f.argtypes=args;return f
new=function('oidnNewDevice',C.c_void_p,[C.c_int]);setint=function('oidnSetDeviceInt',None,[C.c_void_p,C.c_char_p,C.c_int]);commitd=function('oidnCommitDevice',None,[C.c_void_p]);error=function('oidnGetDeviceError',C.c_int,[C.c_void_p,C.POINTER(C.c_char_p)]);newf=function('oidnNewFilter',C.c_void_p,[C.c_void_p,C.c_char_p]);image=function('oidnSetSharedFilterImage',None,[C.c_void_p,C.c_char_p,C.c_void_p,C.c_int,C.c_size_t,C.c_size_t,C.c_size_t,C.c_size_t,C.c_size_t]);boolf=function('oidnSetFilterBool',None,[C.c_void_p,C.c_char_p,C.c_bool]);commitf=function('oidnCommitFilter',None,[C.c_void_p]);execute=function('oidnExecuteFilter',None,[C.c_void_p]);releasef=function('oidnReleaseFilter',None,[C.c_void_p]);released=function('oidnReleaseDevice',None,[C.c_void_p])
dev=new(1);assert dev;setint(dev,b'numThreads',2);commitd(dev)
def check():
 message=C.c_char_p();code=error(dev,C.byref(message));assert code==0,(code,message.value)
def persist(done):
 for name in ('camera_register.json','all_cameras.json'):
  p=OUT/name
  if not p.exists():continue
  regs=json.loads(p.read_text());updates={r['raw']:r for r in done}
  for r in regs:
   key=str(Path(r['file']).relative_to(Path('renders/leonidas_ii')))
   if key in updates:r['file']=str(Path('renders/leonidas_ii')/updates[key]['final']);r['postprocess']=updates[key]['processing'];r['sha256']=updates[key]['sha256']
  p.write_text(json.dumps(regs,indent=2))
 p=OUT/'postprocess_register.json';old=json.loads(p.read_text()) if p.exists() else [];by={r['final']:r for r in old}
 for r in done:by[r['final']]=r
 p.write_text(json.dumps(list(by.values()),indent=2))

PENDING=OUT/'build'/'pending'
check();files=list(OUT.glob('*.png'))+list((OUT/'rooms').glob('*.png'))+list(PENDING.rglob('*.png'));done=[]
for file in sorted(files):
 if file.name.startswith('Preview_'):continue
 registered_raw=file.relative_to(OUT);relative=file.relative_to(PENDING) if file.is_relative_to(PENDING) else registered_raw;raw=RAW/relative;raw.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(file,raw)
 im=Image.open(raw).convert('RGB');arr=np.ascontiguousarray(np.asarray(im,dtype=np.float32)/255);result=np.empty_like(arr);h,w=arr.shape[:2]
 # Full-resolution OIDN can exceed this host's 1.9GiB even without Blender.
 # Fixed 384px cores + 80px real-pixel halo bound filter memory. Cropping
 # writes the original full pixel grid, never an upscaled small render.
 core,pad=384,80
 for yy in range(0,h,core):
  for xx in range(0,w,core):
   x0,x1=max(0,xx-pad),min(w,xx+core+pad);y0,y1=max(0,yy-pad),min(h,yy+core+pad)
   padding=((max(0,pad-yy),max(0,yy+core+pad-h)),(max(0,pad-xx),max(0,xx+core+pad-w)),(0,0))
   tile=np.ascontiguousarray(np.pad(arr[y0:y1,x0:x1],padding,mode='edge'));filtered=np.empty_like(tile);th,tw=tile.shape[:2];fil=newf(dev,b'RT')
   image(fil,b'color',tile.ctypes.data,3,tw,th,0,12,tw*12);image(fil,b'output',filtered.ctypes.data,3,tw,th,0,12,tw*12);boolf(fil,b'hdr',False);boolf(fil,b'srgb',True);commitf(fil);check();execute(fil);check();releasef(fil)
   ch,cw=min(core,h-yy),min(core,w-xx);result[yy:yy+ch,xx:xx+cw]=filtered[pad:pad+ch,pad:pad+cw]
 out=Image.fromarray(np.clip(result*255+.5,0,255).astype(np.uint8));jpg=OUT/relative.with_suffix('.jpg');jpg.parent.mkdir(parents=True,exist_ok=True);out.save(jpg,quality=94,subsampling=0,optimize=True)
 file.unlink();done.append(dict(raw=str(registered_raw),final=str(jpg.relative_to(OUT)),width=w,height=h,sha256=hashlib.sha256(jpg.read_bytes()).hexdigest(),processing='Cycles actual source geometry; tiled standalone OIDN 2 CPU, 384px core/80px halo; JPEG94, no resize'))
 persist(done)
 print('DENOISED',jpg.name,flush=True)
released(dev)
print('POSTPROCESS COMPLETE',len(done))
