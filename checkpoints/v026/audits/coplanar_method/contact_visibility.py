import sys
if sys.flags.optimize:raise RuntimeError('Optimized Python unsupported')
import sys
sys.dont_write_bytecode=True
import bpy,json,argparse,hashlib,collections
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent));from surface_partition import *
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--contacts',required=True);p.add_argument('--receipt',action='append',required=True);p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();d=json.loads(Path(a.contacts).read_text());assert sha(a.model)==d['model_sha256']and not Path(a.report).exists();bpy.ops.wm.open_mainfile(filepath=str(Path(a.model).resolve()),use_scripts=False);dg=bpy.context.evaluated_depsgraph_get();geo={};trees=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH'or o.hide_render:continue
 if not any(s.material and(not s.material.use_nodes or any(n.type=='OUTPUT_MATERIAL'and n.is_active_output and n.inputs['Surface'].is_linked for n in s.material.node_tree.nodes))for s in o.material_slots):continue
 eo=o.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();vs=[eo.matrix_world@v.co for v in me.vertices];ts=[tuple(t.vertices)for t in me.loop_triangles]
 if vs and ts:
  geo[o.name]=[[tuple(vs[k])for k in t]for t in ts] if any(o.name==r['union']or any(c['object']==o.name for c in r['contacts'])for r in d['results'])else None
  trees.append((o.name,BVHTree.FromPolygons(vs,ts,all_triangles=True)))
 eo.to_mesh_clear()
receipts=[(p,json.loads(Path(p).read_text()))for p in a.receipt];rows=[]
selection=[]
for result in d['results']:
 groups=collections.defaultdict(list)
 for c in result['contacts']:
  key=(c['object'],tuple(round(v,4)for v in c['normal']),round(c['plane_offset'],4),c['same_facing']);groups[key].append(c)
 chosen=[c for group in groups.values()for c in sorted(group,key=lambda x:x['area'],reverse=True)[:2]]
 selection.append({'union':result['union'],'full_contact_pairs':len(result['contacts']),'sampled_pairs':len(chosen),'selection':'Two largest pair patches per neighbor object, rounded plane/normal and orientation class. Rounding only groups sample strata, not geometric contact tests.'})
 for c in chosen:
  t=geo[result['union']][c['union_triangle']];q=geo[c['object']][c['neighbor_triangle']];n,offset=plane(t);qn,qd=plane(q)
  if dot(n,qn)<0:q=list(reversed(q))
  hit=[sub(v,mul(n,dot(n,v)-offset))for v in q]
  for x,y in zip(t,t[1:]+t[:1]):
   outward=cross(sub(y,x),n);hit=clip(hit,outward,dot(outward,x))
   if not hit:break
  assert hit and area(hit)>1e-10;point=tuple(sum(v[k]for v in hit)/len(hit)for k in range(3))
  points=[point]+[tuple((point[k]+v[k])/2 for k in range(3))for v in hit]
  for sample_index,point in enumerate(points):
   for receipt,rd in receipts:
    cam=rd['settings']['camera']['matrix_world'];camera_data=rd['settings']['camera']['data'];render=rd['settings']['render'];local=Matrix(cam).inverted()@Vector(point);tx=camera_data['sensor_width']/(2*camera_data['lens']);ty=tx*render['resolution_y']/render['resolution_x'];in_frame=local.z<0 and abs(local.x/(-local.z)/tx)<=1 and abs(local.y/(-local.z)/ty)<=1;origin=Vector([cam[i][3]for i in range(3)]);vec=Vector(point)-origin;dist=vec.length;direction=vec.normalized();hits=[]
    for name,bvh in trees:
     loc,normal,index,distance=bvh.ray_cast(origin,direction,dist+.001)
     if loc is not None:hits.append((distance,name,index))
    hits.sort();nearest=hits[0]if hits else None;facing=dot(n,sub(tuple(origin),point))>0
    rows.append({'union':result['union'],'neighbor':c['object'],'neighbor_polygon':c['neighbor_polygon'],'normal':n,'plane_offset':offset,'sample':point,'sample_index':sample_index,'inside_camera_frame':in_frame,'receipt':receipt,'camera_height':origin.z,'outward_front_facing':facing,'distance_to_contact':dist,'nearest_hit':nearest,'nearer_occluder':bool(nearest and nearest[0]<dist-.001),'contact_at_first_surface':bool(nearest and abs(nearest[0]-dist)<=.001),'scope':'Clipped-contact centroid and halfway-to-vertex samples; finite area-stratified points, not exhaustive pixel visibility proof.'})
assert sha(a.model)==d['model_sha256'];Path(a.report).write_text(json.dumps({'model_sha256':d['model_sha256'],'inputs':{p:sha(p)for p in [a.contacts,*a.receipt]},'source_unchanged':True,'selection':selection,'samples':rows,'scope':'Read-only actual evaluated surface raycasts from recorded cameras to finite overlap centroids. No render, no universal hidden/exposed claim; material transparency and pixel filtering not simulated.'},indent=2));print('VISIBILITY SAMPLES',len(rows))
