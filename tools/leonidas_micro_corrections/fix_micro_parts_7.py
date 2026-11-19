"""Already-applied one-off exterior/access/deck corrections. Never rerun."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'blender/leonidas_ii'
staged={}
def load(n):return (ROOT/n).read_text()
def sub(s,a,b):
 assert s.count(a)==1,(a[:110],s.count(a))
 return s.replace(a,b)
def stage(n,s):compile(s,str(ROOT/n),'exec');staged[n]=s
s=load('topsides.py')
s=sub(s,"  # Base coaming, stiffening rings, ladder, steam escape pipe and whistle.","  # Four narrow coaming-carried saddles support the actual liner wall\n  # without sealing the open gas passage or relying on a pipe below it.\n  for side in (-1,1):\n   inner.rod((x+side*1.43,0,17.22),(x+side*2.175,0,17.22),.035,'Iron',8)\n   inner.rod((x,side*1.43,17.22),(x,side*2.075,17.22),.035,'Iron',8)\n  # Base coaming, stiffening rings, ladder, steam escape pipe and whistle.")
s=sub(s," for dx in (-.6,.6):m.cylinder((x+dx,0,z+.55),.19,.72,'Engine',16,(1,0,0))", " # Cast feet and a common enclosed reduction case support both steam\n # cylinders and carry the windlass spindle, not two floating cylinders.\n m.box((x,0,z+.66),(.50,.38,.66),'Engine',.025)\n for dx in (-.6,.6):\n  m.box((x+dx,0,z+.375),(.50,.24,.13),'Engine',.012)\n  m.cylinder((x+dx,0,z+.55),.19,.72,'Engine',16,(1,0,0))")
s=sub(s,"  for xa in np.arange(xx-l/2+.12,xx+l/2,.24):m.box", "  # Coaming-fastened ledgers receive every hatch-board end. The former\n  # boards ended 5mm clear of each wall and the battens were 5mm above.\n  for yy in (-w/2+.085,w/2-.085):m.box((xx,yy,12.20),(l-.12,.12,.07),'Oak',.008)\n  for xa in np.arange(xx-l/2+.12,xx+l/2,.24):m.box")
s=sub(s,"m.box((xx,yy,12.34),(l,.065,.055)","m.box((xx,yy,12.3348),(l,.065,.055)")
s=sub(s,"bolts(m,(xx,footy,17.38)","bolts(m,(xx,footy,17.3675)")
s=sub(s,"m.box((xx,footy-side*.12,18.1)","m.box((xx,footy-side*.10,18.1)")
s=sub(s,"a.box((-2,float(yy),z+.085)","a.box((-2,float(yy),z+.0823)")
stage('topsides.py',s)
s=load('structure.py')
s=sub(s," if deck=='orlop':holes += [(-28.5,36.05,-7.9,7.9),(-70,-28.5,-1.5,1.5)]", " if deck=='orlop':holes += [(-28.5,36.05,-7.9,7.9),(-70,-28.5,-1.5,1.5)]\n # The exterior galley flue has a real sleeve opening, not a solid deck\n # intersecting the pipe/lagging. Its fastened coamings are in interiors.py.\n if deck in ('promenade','boat'):holes.append((-39.63,-39.07,-5.08,-4.52))")
s=sub(s,"    if hi0-lo0<.02 or hi1-lo1<.02:continue\n    vv=[(a,lo0,z-.13),(b,lo1,z-.13),(b,hi1,z-.13),(a,hi0,z-.13),(a,lo0,z),(b,lo1,z),(b,hi1,z),(a,hi0,z)]\n    m.add(vv,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'Teak' if z>=8.8 else 'Iron')", "    # Clip a full tapered strip to this transverse cell. Discarding a\n    # cell whenever only ONE end narrowed away left triangular holes\n    # under the stern weather finish. Keep those real triangular panels.\n    poly=[(a,-ba),(b,-bb),(b,bb),(a,ba)]\n    for bound,positive in ((c,True),(d,False)):\n     clipped=[]\n     for A,B in zip(poly,poly[1:]+poly[:1]):\n      ia=A[1]>=bound if positive else A[1]<=bound;ib=B[1]>=bound if positive else B[1]<=bound\n      if ia:clipped.append(A)\n      if ia!=ib:\n       t=(bound-A[1])/(B[1]-A[1]);clipped.append((A[0]+t*(B[0]-A[0]),bound))\n     poly=clipped\n     if not poly:break\n    unique=[]\n    for p in poly:\n     if not unique or math.dist(p,unique[-1])>1e-8:unique.append(p)\n    if len(unique)>1 and math.dist(unique[0],unique[-1])<1e-8:unique.pop()\n    poly=unique;nn=len(poly)\n    if nn<3 or abs(sum(A[0]*B[1]-A[1]*B[0] for A,B in zip(poly,poly[1:]+poly[:1])))<1e-7:continue\n    vv=[(px,py,z+dz) for dz in (-.13,0) for px,py in poly]\n    ff=[tuple(range(nn-1,-1,-1)),tuple(range(nn,2*nn))]+[(j,(j+1)%nn,(j+1)%nn+nn,j+nn) for j in range(nn)]\n    m.add(vv,ff,'Teak' if z>=8.8 else 'Iron')")
stage('structure.py',s)
s=load('interiors.py')
s=sub(s,"   for zz in (14.4,17.2):flue.ring((-39.35,-4.8,zz),.24,.035,'Iron',16,6)", "   for zz in (14.4,17.2):\n    # Finite sleeves bridge the intentional structural opening and seat\n    # against the lagging, not 5mm away from it. No deck caps the flue.\n    for dx in (-.30,.30):flue.box((-39.35+dx,-4.8,zz+.025),(.12,.72,.06),'Iron',.009)\n    for dy in (-.30,.30):flue.box((-39.35,-4.8+dy,zz+.025),(.72,.12,.06),'Iron',.009)\n    flue.ring((-39.35,-4.8,zz+.045),.24,.050,'Iron',16,6)")
stage('interiors.py',s)
s=load('audit_exterior_parts.py')
s=sub(s,"import topsides\nimport interiors", "import topsides\nimport structure\nimport interiors")
s=sub(s,"        topsides.build()", "        structure.build_decks()\n        structure.build_stairs()\n        topsides.build()")
s=sub(s,"Covers topsides, weather roofs/planks, climbing ladders, navigation fixtures,", "Covers structural decks/stairs, topsides, weather roofs/planks, ladders, navigation,")
stage('audit_exterior_parts.py',s)
for n,s in staged.items():(ROOT/n).write_text(s)
print('APPLIED staged correction 7:',', '.join(staged))
