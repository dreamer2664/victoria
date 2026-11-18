"""Independent signed-component / exported-normal audit of the OWN GLBs.

Actual archived regional hashes are checked against their manifest first.
Positions are welded by exact exported coordinate, not a broad tolerance.
A positive connected-component volume does not prove no self-intersection,
correct naval thickness, physical pressure boundaries or Studio ingestion.
"""
from pathlib import Path
import json,mmap,struct,hashlib,sys,tarfile
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
ROOT=Path(__file__).resolve().parents[1];EX=ROOT/'exports/leonidas_ii';KIT=EX/'build/Roblox_Import_Kit';DOC=ROOT/'docs/leonidas_ii'
M=json.loads((EX/'game_manifest.json').read_text());K=json.loads((EX/'IMPORT_KIT_MANIFEST.json').read_text());names={n['name']:n for n in M['nodes'] if n['kind']!='calibration'}
# Independent re-checks must also work after regenerable build/ has expired.
# Restore only missing exact named GLBs from our archived kit, never perform
# unrestricted tar extraction or rebuild/rewrite the delivered master.
missing={b['file']:b for b in K['batches'] if not(KIT/b['file']).is_file()}
if missing:
 KIT.mkdir(parents=True,exist_ok=True)
 with tarfile.open(EX/'Aurelian_Roblox_Import_Kit.tar.xz','r:xz') as archive:
  for member in archive:
   if not member.isfile() or not member.name.startswith('Aurelian_Import_Kit/'):continue
   rel=member.name.removeprefix('Aurelian_Import_Kit/')
   if rel not in missing:continue
   b=missing[rel];assert Path(rel).name==rel and 0<member.size==b['bytes']<20*1024*1024
   blob=archive.extractfile(member).read(b['bytes']+1);assert len(blob)==b['bytes'] and hashlib.sha256(blob).hexdigest()==b['sha256']
   (KIT/rel).write_bytes(blob);print('RESTORED EXACT ARCHIVED GLB',rel,flush=True)
 assert all((KIT/f).is_file() for f in missing),'Archive did not contain the expected regional set'
seen=set();rows=[]
for batch in K['batches']:
 file=KIT/batch['file'];assert hashlib.sha256(file.read_bytes()).hexdigest()==batch['sha256']
 with file.open('rb') as f:
  mm=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ);jl=struct.unpack_from('<I',mm,12)[0];g=json.loads(mm[20:20+jl]);base=20+jl+8
  def acc(i,width):
   a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];dt=np.dtype('<f4' if a['componentType']==5126 else '<u4' if a['componentType']==5125 else '<u2');offset=base+v.get('byteOffset',0)+a.get('byteOffset',0)
   return np.ndarray((a['count'],width),dtype=dt,buffer=mm,offset=offset,strides=(v.get('byteStride',width*dt.itemsize),dt.itemsize)).copy()
  for node in g['nodes']:
   name=node['name']
   if name not in names:continue
   key=names[name]['geometry_sha256']
   if key in seen:continue
   seen.add(key);p=g['meshes'][node['mesh']]['primitives'][0]
   xyz=acc(p['attributes']['POSITION'],3).astype(np.float64);norm=acc(p['attributes']['NORMAL'],3).astype(np.float64);tri=acc(p['indices'],1).reshape(-1,3).astype(np.int64)
   vv,inv=np.unique(xyz,axis=0,return_inverse=True);tt=inv[tri]
   graph=coo_matrix((np.ones(len(tt)*3,np.uint8),(tt.ravel(),tt[:,[1,2,0]].ravel())),shape=(len(vv),len(vv))).tocsr();nc,labels=connected_components(graph,directed=False)
   points=xyz[tri];areas=np.cross(points[:,1]-points[:,0],points[:,2]-points[:,0]);area=np.linalg.norm(areas,axis=1);volumes=np.einsum('ij,ij->i',points[:,0],np.cross(points[:,1],points[:,2]))/6
   signed=np.bincount(labels[tt[:,0]],weights=volumes,minlength=nc)
   # Exact-coordinate welding can merge touching closed solids. Such edges
   # can have >2 uses, so record those contacts separately rather than calling
   # every one a hole. There must be no ODD unpaired uses, and the directed
   # edge uses must cancel. This is not a proof of a two-manifold union.
   ee=tt.ravel();ends=tt[:,[1,2,0]].ravel();lo=np.minimum(ee,ends);hi=np.maximum(ee,ends);keys=lo*len(vv)+hi
   _,ei,ec=np.unique(keys,return_inverse=True,return_counts=True);winding=np.bincount(ei,weights=np.where(ee<ends,1,-1));collapsed=ee==ends
   odd_edges=int((ec%2!=0).sum());winding_errors=int((winding!=0).sum());contact_edges=int((ec>2).sum())
   dot=np.einsum('ij,ij->i',areas,norm[tri].mean(axis=1));flipped=(dot < -.05*area)
   corner_dot=np.einsum('ij,ikj->ik',areas,norm[tri])/np.maximum(area[:,None],1e-20)
   rows.append(dict(name=name,geometry_sha256=key,components=nc,negative_components=int((signed < -1e-10).sum()),near_zero_components=int((np.abs(signed)<=1e-10).sum()),min_component_signed_volume_m3=float(signed.min()),gross_signed_volume_m3=float(signed.sum()),triangles=len(tri),normal_disagreement_triangles=int(flipped.sum()),opposing_normal_corners=int((corner_dot < -1e-4).sum()),degenerate_area_triangles=int((area<=1e-12).sum()),odd_unpaired_welded_edges=odd_edges,inconsistent_edge_winding=winding_errors,coincident_contact_edges=contact_edges,collapsed_triangle_edges=int(collapsed.sum())))
  mm.close()
 print('AUDITED',batch['file'],len(rows),flush=True)
summary={k:sum(r[k] for r in rows) for k in ('components','negative_components','near_zero_components','normal_disagreement_triangles','opposing_normal_corners','degenerate_area_triangles','odd_unpaired_welded_edges','inconsistent_edge_winding','coincident_contact_edges','collapsed_triangle_edges','triangles')};summary['unique_visual_meshes']=len(rows)
report=dict(schema='victoria.leonidas-ii.component-volume-audit/1.2',source_sha256=M['source_sha256'],auditor_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),game_manifest_sha256=hashlib.sha256((EX/'game_manifest.json').read_bytes()).hexdigest(),kit_manifest_sha256=hashlib.sha256((EX/'IMPORT_KIT_MANIFEST.json').read_bytes()).hexdigest(),regional_files=[dict(file=b['file'],sha256=b['sha256']) for b in K['batches']],scope='Exact exported-coordinate connected components; signed volumes / geometric face versus exported corner normals. Coincident contacts may have more than two edge uses. No odd unpaired uses and balanced winding are checked, not a two-manifold Boolean union, self-intersection, physical pressure boundaries, universal watertightness, or Studio acceptance.',summary=summary,rows=rows)
(DOC/'COMPONENT_VOLUME_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n');print('COMPONENT AUDIT',json.dumps(summary))
gates=('negative_components','near_zero_components','normal_disagreement_triangles','opposing_normal_corners','degenerate_area_triangles','odd_unpaired_welded_edges','inconsistent_edge_winding','collapsed_triangle_edges')
sys.exit(1 if any(summary[k] for k in gates) else 0)
