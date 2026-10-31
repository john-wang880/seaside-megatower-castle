"""Independent new landing-marker-versus-closed-architecture volume intersections. Only plate/arm embedding in the named mount wall is allowed. Other overlaps/unknown-open components fail. Not structural certification."""
import bpy,bmesh,argparse,json,sys,hashlib,math
from collections import defaultdict,Counter
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--report',required=True);p.add_argument('--allow-collisions',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath);sha=hashlib.sha256(source.read_bytes()).hexdigest();deps=bpy.context.evaluated_depsgraph_get();before=(len(bpy.data.objects),len(bpy.data.meshes))
def bounds(vs):return ([min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)])
def overlap(a,b):return all(a[1][k]>b[0][k]+1e-6 and a[0][k]<b[1][k]-1e-6 for k in range(3))
def temporary(vs,fs):
 me=bpy.data.meshes.new('TEMP independent door audit');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o);return o

def remove(o):
 me=o.data;bpy.data.objects.remove(o,do_unlink=True);bpy.data.meshes.remove(me)
leaves=[]
for o in bpy.data.objects:
 if o.type=='MESH' and not o.hide_render and o.name.startswith('V014 | landing marker '):
  eo=o.evaluated_get(deps);me=eo.to_mesh();vs=[tuple(eo.matrix_world@v.co) for v in me.vertices];fs=[tuple(p.vertices) for p in me.polygons];leaves.append({'name':o.name,'vertices':vs,'faces':fs,'bounds':bounds(vs)});eo.to_mesh_clear()
assert len(leaves)==10
architecture=[]
for o in list(bpy.data.objects):
 if o.type!='MESH' or o.hide_render or o.name.startswith(('V013 |','V014 |')):continue
 if not any(term in o.name.lower() for term in('citadel','ashlar','limestone','stone','rib facade','foundation','terrace ledges','gallery','galleries','keep','gate','wall','vault','lining','guard','ceiling','stair')):continue
 if any(term in o.name.lower() for term in('footpath','woodland','tree','timber leaf','iron strap')):continue
 eo=o.evaluated_get(deps);bb=bounds([eo.matrix_world@Vector(v) for v in eo.bound_box])
 if not any(overlap(bb,l['bounds']) for l in leaves):continue
 me=eo.to_mesh();vs=[tuple(eo.matrix_world@v.co) for v in me.vertices];parent=list(range(len(vs)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for e in me.edges:
  u,v=map(find,e.vertices)
  if u!=v:parent[v]=u
 groups=defaultdict(list)
 for i in range(len(vs)):groups[find(i)].append(i)
 selected={}
 for seed,ids in groups.items():
  bb=bounds([vs[i] for i in ids])
  if any(overlap(bb,l['bounds']) for l in leaves):selected[seed]={'ids':ids,'bounds':bb,'faces':[]}
 for face in me.polygons:
  seed=find(face.vertices[0])
  if seed in selected:selected[seed]['faces'].append(tuple(face.vertices))
 for seed,q in selected.items():
  ids=q['ids'];mapping={old:i for i,old in enumerate(ids)};faces=[tuple(mapping[i] for i in f) for f in q['faces']]
  count=Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in faces for i in range(len(f)))
  architecture.append({'object':o.name,'seed':min(ids),'vertices':[vs[i] for i in ids],'faces':faces,'bounds':q['bounds'],'closed':bool(faces) and all(n==2 for n in count.values())})
 eo.to_mesh_clear()
checks=[];uncertain=[]
for leaf in leaves:
 cutter=temporary(leaf['vertices'],leaf['faces'])
 try:
  for item in architecture:
   if not overlap(leaf['bounds'],item['bounds']):continue
   detail={'fixture':leaf['name'],'architecture':item['object'],'component_seed':item['seed']}
   if not item['closed']:uncertain.append({**detail,'reason':'architecture_component_not_closed'});continue
   part=temporary(item['vertices'],item['faces'])
   try:
    bpy.context.view_layer.objects.active=part;part.select_set(True)
    mod=part.modifiers.new('Independent door interference volume','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(part.data);volume=abs(bm.calc_volume(signed=True));nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
    checks.append({**detail,'intersection_volume':volume,'intersection_faces':len(part.data.polygons),'result_nonmanifold_edges':nonmanifold})
    if nonmanifold:uncertain.append({**detail,'reason':'intersection_result_not_closed'})
   finally:remove(part)
 finally:remove(cutter)
intentional=[q for q in checks if q['intersection_volume']>1e-8 and q['architecture']=='V012 | east lined stairwell and terrace guard' and any(q['fixture'].endswith(suffix) for suffix in ['mounting plate','wall arm'])]
collisions=[q for q in checks if q['intersection_volume']>1e-8 and q not in intentional];unchanged=sha==hashlib.sha256(source.read_bytes()).hexdigest();cleaned=before==(len(bpy.data.objects),len(bpy.data.meshes))
r={'source_sha256':sha,'fixture_geometry_measurements':[{k:l[k] for k in('name','bounds')} for l in leaves],'checks':checks,'intentional_wall_mount_intersections':intentional,'collisions':collisions,'uncertain':uncertain,'temporary_datablocks_cleaned':cleaned,'source_unchanged':unchanged,'landing_fixture_architecture_clear':not collisions and not uncertain and cleaned and unchanged,'volume_tolerance':1e-8,'scope':__doc__}
Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps(r));
if not a.allow_collisions:assert r['landing_fixture_architecture_clear']
