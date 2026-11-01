import bpy,numpy as np,json,collections,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('work/conifer_specialist');repaired=set(json.loads((P/'transport_repaired_components.json').read_text())['tube_vertex_starts']);mapping=json.loads((P/'component_contact_mapping.json').read_text())['wood_components'];wood=bpy.data.objects['CONCEPT | tapering connected boughs and shoots'].data;fol=bpy.data.objects['CONCEPT | radial articulated needle sprays'].data
wood.calc_loop_triangles();tt=collections.defaultdict(list)
for t in wood.loop_triangles:tt[t.polygon_index].append(tuple(t.vertices))
source=Path('work/v019_qa/validate_new_geometry.py').read_text();exec(source[source.index('DIRS='):source.index('comps=[];')])
comps=[];badneedle=[];tested=0
for row in mapping:
 start=row['vertex_start']
 if start not in repaired:continue
 end=start+row['vertex_count'];vs=[v.co.copy() for v in wood.vertices[start:end]];faces=[[i-start for i in wood.polygons[f].vertices] for f in range(row['face_start'],row['face_start']+row['face_count'])];tris=[[i-start for i in t] for f in range(row['face_start'],row['face_start']+row['face_count']) for t in tt[f]];s=solid(vs,faces,tris,str(start));s['meta']=row;comps.append(s)
 for b in range(row['needle_blade_start'],row['needle_blade_start']+row['needle_blade_count']):
  tested+=1;r=exact_triangle_parity(fol.vertices[b*5].co,s)
  if r['state']!='inside':badneedle.append({'blade':b,'tube':start,'result':r})
foldsource=Path('work/v019_qa/audit_tube_folds.py').read_text();exec(foldsource[foldsource.index('folds=[]'):foldsource.index('out={')])
oldpath=P/'pre_frame_repair/isolated_conifer.blend';names=[wood.name,fol.name]
with bpy.data.libraries.load(str(oldpath.resolve()),link=False) as (src,dst):dst.meshes=names
comparisons={}
for now,old in zip([wood,fol],dst.meshes):
 assert len(now.vertices)==len(old.vertices) and len(now.polygons)==len(old.polygons)
 a=np.empty(len(now.vertices)*3,dtype=np.float32);b=a.copy();now.vertices.foreach_get('co',a);old.vertices.foreach_get('co',b);a=a.reshape(-1,3);b=b.reshape(-1,3);d=np.linalg.norm(a.astype(float)-b.astype(float),axis=1);changed=np.flatnonzero(d>0);allowed=set()
 for row in mapping:
  if row['vertex_start'] not in repaired:continue
  if now==wood:allowed.update(range(row['vertex_start'],row['vertex_start']+row['vertex_count']))
  else:allowed.update(range(row['needle_blade_start']*5,(row['needle_blade_start']+row['needle_blade_count'])*5))
 outside=sorted(set(changed)-allowed);assert not outside,(now.name,outside[:10])
 assert all(list(f.vertices)==list(g.vertices) and f.material_index==g.material_index for f,g in zip(now.polygons,old.polygons))
 comparisons[now.name]={'changed_vertices':len(changed),'max_displacement_m':float(d.max()),'rms_displacement_m':float(np.sqrt(np.mean(d*d))),'outside_repaired_components_changed':len(outside),'topology_and_material_indices_exact':True}
oldfolds={x['wood_start'] for x in json.loads(Path('work/v019_qa/tube_folds.json').read_text())['folded_components']};assert oldfolds<=repaired
report={'asset_sha256':hashlib.sha256((P/'isolated_conifer.blend').read_bytes()).hexdigest(),'previous_asset_sha256':hashlib.sha256(oldpath.read_bytes()).hexdigest(),'legacy_reference_switch_components':len(repaired),'includes_all_11_independently_folded':oldfolds<=repaired,'changed_tubes':sorted(repaired),'unchanged_tubes':3199-len(repaired),'changed_tube_triangle_crossings':folds,'exact_parity_needle_roots_tested':tested,'needle_failures':badneedle,'geometry_comparison':comparisons,'scope':'Uses independent validator algorithms on all47 reference-switch components; full independent reintegrated-candidate rerun remains required.'};(P/'frame_repair_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not folds and not badneedle
