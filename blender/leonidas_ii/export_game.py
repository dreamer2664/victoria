"""Bounded-memory glTF 2.0 writer for the procedural GAME detail build.

1 LII_GAME_DETAIL=1 blender -b -P blender/leonidas_ii/build.py
2 blender -b exports/leonidas_ii/build/Aurelian_Game_Source.blend -P .../export_game.py
3 python3 tools/package_leonidas_ii.py

All mesh nodes have their own geometric centre, <=18,000 triangles, real
UV/normal attributes and a separate mover/name contract. No operator silently
scales locations twice. GLB is metric / Y-up / -Z bow / load waterline origin.
The Studio installer measures calibration markers to resolve importer units.
Repeated identical geometry is reused by content hash, not merely named alike.
"""
import sys,json,math,struct,hashlib,time,collections
from pathlib import Path
import bpy,bmesh,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
GAME=ROOT/'exports'/'leonidas_ii'/'build';OUT=ROOT/'exports'/'leonidas_ii';MAT=ROOT/'reference'/'leonidas_ii'/'materials'
DATA=json.loads((GAME/'build_data.json').read_text());SOURCE=ROOT/'models'/'leonidas_ii'/'Aurelian_1889.blend'
R=np.array([[0,-1,0],[0,0,1],[-1,0,0]],dtype=np.float32)
WL=np.array([0,-6.5,0],np.float32);BUDGET=18000
G={'asset':{'version':'2.0','generator':'victoria LEONIDAS-II explicit spatial exporter'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'buffers':[{}],'bufferViews':[],'accessors':[],'materials':[],'images':[],'textures':[],'samplers':[{'magFilter':9729,'minFilter':9987,'wrapS':33071,'wrapT':33071}]}
B=bytearray();CACHE={};NODES=[];QA=[];DEDUPE=collections.Counter();start=time.time()
def raw(blob,target=None,stride=None):
 while len(B)%4:B.append(0)
 view={'buffer':0,'byteOffset':len(B),'byteLength':len(blob)}
 if target:view['target']=target
 if stride:view['byteStride']=stride
 i=len(G['bufferViews']);G['bufferViews'].append(view);B.extend(blob);return i

def accessor(view,count,typ,component=5126,offset=0,minimum=None,maximum=None):
 a={'bufferView':view,'byteOffset':offset,'componentType':component,'count':count,'type':typ}
 if minimum is not None:a['min']=list(map(float,minimum));a['max']=list(map(float,maximum))
 i=len(G['accessors']);G['accessors'].append(a);return i

def texture(file):
 image=len(G['images']);G['images'].append({'name':file.stem,'mimeType':'image/png','bufferView':raw(file.read_bytes())});tx=len(G['textures']);G['textures'].append({'source':image,'sampler':0});return {'index':tx}
base=texture(MAT/'Aurelian_basecolor.png');normal=texture(MAT/'Aurelian_normal.png');mr=texture(GAME/'Aurelian_metalrough.png');emission=texture(MAT/'Aurelian_emission.png');sign=texture(MAT/'Aurelian_signs.png')
G['materials']=[
 {'name':'Aurelian_OriginalPBR_Atlas','pbrMetallicRoughness':{'baseColorTexture':base,'metallicRoughnessTexture':mr,'metallicFactor':1.,'roughnessFactor':1.},'normalTexture':{**normal,'scale':.4},'emissiveTexture':emission,'emissiveFactor':[1,1,1],'doubleSided':False},
 {'name':'Aurelian_WindowGlass','pbrMetallicRoughness':{'baseColorFactor':[.24,.39,.38,.38],'metallicFactor':0.,'roughnessFactor':.12},'alphaMode':'BLEND','doubleSided':True},
 {'name':'Aurelian_Incandescent','pbrMetallicRoughness':{'baseColorFactor':[1,.8,.46,1],'metallicFactor':0.,'roughnessFactor':.4},'emissiveFactor':[1,.63,.26]},
 {'name':'Aurelian_CompartmentPlaques','pbrMetallicRoughness':{'baseColorTexture':sign,'metallicFactor':0.,'roughnessFactor':.42},'doubleSided':True}]
MATIDS={m['name']:i for i,m in enumerate(G['materials'])}

def node(name,rows,tris,mat,meta):
 # Re-centre every spatial mesh, preserve explicit global node translation.
 ids=np.unique(tris.ravel());sub=rows[ids].copy();lookup=np.empty(len(rows),np.uint32);lookup[ids]=np.arange(len(ids),dtype=np.uint32);indices=lookup[tris].astype('<u4')
 centre=(sub[:,:3].min(0)+sub[:,:3].max(0))*.5;sub[:,:3]-=centre
 source_xyz=sub[:,:3].copy()
 sub[:,:3]=np.round(sub[:,:3],4);sub[:,3:6]=np.round(sub[:,3:6],4);sub[:,6:]=np.round(sub[:,6:],6);sub=sub.astype('<f4')
 # A few narrow cross-section cap triangles lose their tiny real curvature
 # on a 0.1 mm compression grid. Restore SOURCE precision for every copy of
 # each affected geometric vertex, rather than leaving zero-area triangles,
 # deleting a cap, or inventing arbitrary epsilon offsets. This preserves
 # closed boundaries and moves points <0.087 mm from the compressed grid.
 pp=sub[indices,:3].astype(np.float64);area=np.linalg.norm(np.cross(pp[:,1]-pp[:,0],pp[:,2]-pp[:,0]),axis=1);small=area<=1e-12;protected=0
 if small.any():
  _,group=np.unique(source_xyz,axis=0,return_inverse=True);keep=np.isin(group,group[indices[small].ravel()]);protected=int(keep.sum());sub[keep,:3]=source_xyz[keep]
 # Extremely thin shell reveals and sharp pipe turns must not interpolate
 # a smoothed corner normal into the OPPOSITE face hemisphere. Geometry,
 # UVs, winding, dimensions and triangle count stay unchanged; split only
 # the offending shading corners and use their actual geometric normal.
 # Do this after final position rounding, before constructing tangents.
 pp=sub[indices,:3].astype(np.float64);fn=np.cross(pp[:,1]-pp[:,0],pp[:,2]-pp[:,0]);flen=np.linalg.norm(fn,axis=1);assert np.all(flen>1e-12),(name,'degenerate after source-precision restore',int((flen<=1e-12).sum()));fn/=flen[:,None]
 opposing=np.sum(sub[indices,3:6]*fn[:,None,:],axis=2)<.001;corrected=int(opposing.sum())
 if corrected:
  expanded=sub[indices.ravel()].copy();normal=expanded[:,3:6];normal[opposing.ravel()]=np.round(np.repeat(fn,3,axis=0)[opposing.ravel()],4)
  sub,remap=np.unique(expanded,axis=0,return_inverse=True);indices=remap.reshape(-1,3).astype('<u4')
 # np.unique order is position-sorted, so normalize vertex order after
 # translation as well before using a geometry content hash.
 order=np.lexsort(tuple(sub[:,i] for i in reversed(range(8))));inv=np.empty(len(order),np.uint32);inv[order]=np.arange(len(order),dtype=np.uint32);sub=sub[order];indices=inv[indices]
 # Explicit orthogonal tangent basis from final glTF positions/UVs. UV
 # seams are already split in rows. Degenerate cap UVs receive an orthogonal
 # fallback; no runtime-dependent tangent generation is left to importers.
 xyz=sub[:,:3];uv=sub[:,6:8];nrm=sub[:,3:6];q=indices
 e1=xyz[q[:,1]]-xyz[q[:,0]];e2=xyz[q[:,2]]-xyz[q[:,0]];d1=uv[q[:,1]]-uv[q[:,0]];d2=uv[q[:,2]]-uv[q[:,0]];den=d1[:,0]*d2[:,1]-d1[:,1]*d2[:,0];rec=np.zeros_like(den);ok=np.abs(den)>1e-12;rec[ok]=1/den[ok]
 sd=(e1*d2[:,1,None]-e2*d1[:,1,None])*rec[:,None];td=(e2*d1[:,0,None]-e1*d2[:,0,None])*rec[:,None];t=np.zeros_like(xyz);bt=np.zeros_like(xyz)
 for corner in range(3):np.add.at(t,q[:,corner],sd);np.add.at(bt,q[:,corner],td)
 t-=nrm*np.sum(nrm*t,axis=1,keepdims=True)/np.maximum(np.sum(nrm*nrm,axis=1,keepdims=True),1e-20);length=np.linalg.norm(t,axis=1);bad=length<1e-8
 if bad.any():
  axis=np.tile([1,0,0],(bad.sum(),1)).astype(np.float32);nn=nrm[bad];axis[np.abs(nn[:,0])>.8]=[0,1,0];t[bad]=np.cross(nn,axis);length=np.linalg.norm(t,axis=1)
 t/=np.maximum(length[:,None],1e-20);hand=np.where(np.sum(np.cross(nrm,t)*bt,axis=1)<0,-1.,1.)
 # Match the precision of the final position/normal attributes. Quantising
 # these unit vectors suppresses sub-pixel numerical noise and ZIP entropy;
 # components remain float32 and within glTF unit/orthogonality tolerances.
 sub=np.column_stack((sub,np.round(t,4),hand)).astype('<f4')
 vb=sub.tobytes();ib=indices.tobytes();key=hashlib.sha256(bytes([mat])+vb+ib).hexdigest()
 if key in CACHE:mi=CACHE[key];DEDUPE['reused_nodes']+=1
 else:
  v=raw(vb,34962,48);iv=raw(ib,34963)
  attrs={'POSITION':accessor(v,len(sub),'VEC3',offset=0,minimum=sub[:,:3].min(0),maximum=sub[:,:3].max(0)),'NORMAL':accessor(v,len(sub),'VEC3',offset=12),'TEXCOORD_0':accessor(v,len(sub),'VEC2',offset=24),'TANGENT':accessor(v,len(sub),'VEC4',offset=32)}
  mi=len(G['meshes']);G['meshes'].append({'name':name,'primitives':[{'attributes':attrs,'indices':accessor(iv,indices.size,'SCALAR',5125),'material':mat,'mode':4}]});CACHE[key]=mi
  DEDUPE['unique_triangles']+=len(tris)
 ni=len(G['nodes']);G['nodes'].append({'name':name,'mesh':mi,'translation':list(map(float,centre)),'extras':meta});G['scenes'][0]['nodes'].append(ni)
 NODES.append(dict(name=name,triangles=len(tris),vertices=len(sub),geometry_sha256=key,mesh=mi,centre_m=list(map(float,centre)),normal_fallback_corners=corrected,source_precision_vertices=protected,**meta));return ni

# True closed cross-section hull slices; never cut a triangle list into
# visually adjoining but individually open half-primitives.
def hull_slices(ob):
 ob.data.calc_loop_triangles()
 if len(ob.data.loop_triangles)<=BUDGET:return [ob]
 coords=[v.co.x for v in ob.data.vertices];cut=(min(coords)+max(coords))/2;pieces=[]
 for aft in (True,False):
  bm=bmesh.new();bm.from_mesh(ob.data)
  result=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000002,plane_co=(cut,0,0),plane_no=(1,0,0),clear_outer=aft,clear_inner=not aft)
  border=[e for e in bm.edges if e.is_boundary]
  if border:
   caps=bmesh.ops.holes_fill(bm,edges=border,sides=0).get('faces',[]);uv=bm.loops.layers.uv.active
   if uv:
    for f in caps:
     for loop in f.loops:loop[uv].uv=(.04,.96)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  me=bpy.data.meshes.new(ob.name+('_A' if aft else '_F'));bm.to_mesh(me);bm.free();me.materials.append(ob.data.materials[0]);me.update()
  child=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(child);child.matrix_world=ob.matrix_world.copy()
  for k in ob.keys():child[k]=ob[k]
  pieces.extend(hull_slices(child))
  if child not in pieces:bpy.data.objects.remove(child,do_unlink=True)
 return pieces
obs=[]
for ob in list(bpy.context.scene.objects):
 if ob.type!='MESH':continue
 if ob.name=='Hull_Shell_New':obs.extend(hull_slices(ob))
 else:obs.append(ob)
for i,ob in enumerate(sorted(obs,key=lambda o:o.name)):
 me=ob.data;me.calc_loop_triangles();V=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',V);V=V.reshape(-1,3)
 world=np.asarray(ob.matrix_world,dtype=np.float32);V=V@world[:3,:3].T+world[:3,3];V=V@R.T+WL
 loops=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',loops)
 norms=np.empty(len(me.loops)*3,np.float32);me.corner_normals.foreach_get('vector',norms);norms=norms.reshape(-1,3)
 norms=norms@np.linalg.inv(world[:3,:3])@R.T;norms/=np.maximum(np.linalg.norm(norms,axis=1,keepdims=True),1e-20)
 uv=np.empty(len(me.loops)*2,np.float32);me.uv_layers[0].data.foreach_get('uv',uv);uv=uv.reshape(-1,2);uv[:,1]=1-uv[:,1]
 attrs=np.column_stack((V[loops],norms,uv));rows,inv=np.unique(attrs,axis=0,return_inverse=True)
 tl=np.empty(len(me.loop_triangles)*3,np.int32);me.loop_triangles.foreach_get('loops',tl);tri=inv[tl].reshape(-1,3).astype(np.uint32)
 points=rows[tri,:3];area2=np.linalg.norm(np.cross(points[:,1]-points[:,0],points[:,2]-points[:,0]),axis=1)
 qa=dict(name=ob.name,triangles=len(tri),zero_area_triangles=int((area2<1e-11).sum()),finite=bool(np.isfinite(rows).all()),uv_outside_01=int(((uv<0)|(uv>1)).any(axis=1).sum()))
 edges=collections.Counter()
 for face in me.polygons:
  ids=list(face.vertices)
  for a,b in zip(ids,ids[1:]+ids[:1]):edges[tuple(sorted((a,b)))]+=1
 qa['boundary_edges']=sum(v==1 for v in edges.values());qa['nonmanifold_edges']=sum(v>2 for v in edges.values())
 QA.append(qa);assert qa['finite'],ob.name
 # Remove only true zero-area triangles from GAME exports; master retained.
 tri=tri[area2>=1e-11]
 if not len(tri):continue
 meta=dict(kind=ob.get('LII_kind',''),room=ob.get('LII_room',''),deck=ob.get('LII_deck',''),source_object=ob.name,mover=ob.get('LII_mover',''))
 mat=MATIDS.get(me.materials[0].name,0)
 chunks=[tri]
 if len(tri)>BUDGET:
  original=loops[tl].reshape(-1,3);parent=list(range(len(V)))
  def find(a):
   while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
   return a
  for a,b,c in original:
   a,b,c=find(int(a)),find(int(b)),find(int(c));parent[b]=a;parent[c]=a
  components={}
  for it,a in enumerate(original[:,0]):components.setdefault(find(int(a)),[]).append(it)
  chunks=[];bucket=[];count=0
  for comp in components.values():
   assert len(comp)<=BUDGET,(ob.name,'closed component over budget',len(comp))
   if count+len(comp)>BUDGET and bucket:chunks.append(tri[bucket]);bucket=[];count=0
   bucket.extend(comp);count+=len(comp)
  if bucket:chunks.append(tri[bucket])
 for j,chunk in enumerate(chunks):
  name=ob.name+(f'_G{j+1:02}' if len(chunks)>1 else '');node(name,rows,chunk,mat,meta)
 if i%150==0:print('EXPORTED',i,ob.name,round(time.time()-start,1),'seconds',flush=True)
# Four genuine tiny calibration meshes. Point markers encode a known 10m
# basis. Do not estimate length from mesh-part centres or import auto-scale.
vv=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],np.float32)*.025
tris=np.array([[0,3,2],[0,2,1],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]],np.uint32)
for nm,c in [('Origin',(0,0,0)),('Forward',(0,0,-10)),('Port',(-10,0,0)),('Up',(0,10,0))]:
 rows=np.column_stack((vv+np.array(c,np.float32),np.tile([0,1,0],(8,1)),np.zeros((8,2)))).astype(np.float32);node('CAL_'+nm,rows,tris,0,{'kind':'calibration','room':'','deck':''})
G['buffers'][0]['byteLength']=len(B)
J=json.dumps(G,separators=(',',':')).encode();J+=b' '*((-len(J))%4);B.extend(b'\0'*((-len(B))%4))
p=GAME/'Aurelian_Game.glb'
with p.open('wb') as f:
 f.write(struct.pack('<4sII',b'glTF',2,12+8+len(J)+8+len(B)));f.write(struct.pack('<I4s',len(J),b'JSON'));f.write(J);f.write(struct.pack('<I4s',len(B),b'BIN\0'));f.write(B)
visual_nodes=[n for n in NODES if n['kind']!='calibration'];visual_meshes={n['mesh']:n['triangles'] for n in visual_nodes}
manifest=dict(schema='victoria.leonidas-ii.game-export/2.2',exporter_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),normal_policy='Split opposing smoothed corners into the geometric face hemisphere before final tangent generation. Retain source float precision only where the 0.1mm compression grid would create a degenerate cap triangle. No authored shape, UV, winding or triangle-count change.',file='Aurelian_Game.glb',format='glTF 2.0 GLB',units='metres',forward='-Z',port='-X',up='+Y',origin='load waterline amidships',source=str(SOURCE.relative_to(ROOT)),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),lod_method='Regenerate coherent primitives at lower angular tessellation; keep boxes/curves and interface dimensions, omit separate tiny shell rivet heads. No arbitrary global decimation.',counts=dict(mesh_nodes=len(visual_nodes),unique_meshes=len(visual_meshes),placed_triangles=sum(n['triangles'] for n in visual_nodes),unique_triangles=sum(visual_meshes.values()),reused_nodes=len(visual_nodes)-len(visual_meshes),max_node_triangles=max(n['triangles'] for n in visual_nodes),removed_zero_area_triangles=sum(q['zero_area_triangles'] for q in QA),calibration_nodes=4,storage_meshes_including_calibration=len(G['meshes']),corrected_shading_corners=sum(n.get('normal_fallback_corners',0) for n in visual_nodes),source_precision_vertices=sum(n.get('source_precision_vertices',0) for n in visual_nodes)),nodes=NODES,mesh_audit=QA,glb_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),glb_bytes=p.stat().st_size,limitations=['Studio importer/upload is unverified; asset IDs intentionally absent.','No measured Roblox client/server frame-time benchmark.','Detail count still substantial; local distance/deck culling supplied, not a performance guarantee.','Transparent glass uses standard alpha PBR, not Blender transmission.'])
(OUT/'game_manifest.json').write_text(json.dumps(manifest,indent=2));print('GAME EXPORT',json.dumps(manifest['counts']),p.stat().st_size,round(time.time()-start,1),flush=True)
