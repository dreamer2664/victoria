"""Pack standard glTF roughness(G)/metalness(B); keep source maps separate."""
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'reference'/'leonidas_ii'/'materials';O=ROOT/'exports'/'leonidas_ii'/'build';O.mkdir(parents=True,exist_ok=True)
r=Image.open(P/'Aurelian_roughness.png').convert('L');m=Image.open(P/'Aurelian_metallic.png').convert('L');Image.merge('RGB',(Image.new('L',r.size,255),r,m)).save(O/'Aurelian_metalrough.png',optimize=True)
print('Packed glTF channel map; no source map overwritten')
