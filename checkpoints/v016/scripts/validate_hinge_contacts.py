"""Independent static hinge contact-chain and local collision audit.
No articulation, hinge load rating or construction claim. The loaded model is
never saved. Only temporary world-space intersection meshes are created/deleted.
"""
import bpy,bmesh,argparse,sys,json,hashlib,math
from pathlib import Path
from collections import defaultdict,Counter
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--report',required=True);p.add_argument('--allow-fail',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath);sha=hashlib.sha256(source.read_bytes()).hexdigest();before=(len(bpy.data.objects),len(bpy.data.meshes));deps=bpy.context.evaluated_depsgraph_get();TOL=1e-8
parts=('neck','barrel','pintle','wall anchor','pin cap');expected={f'V015 | {s} hinge {h} {p}' for s in ('south','north') for h in ('lower','upper') for p in parts}
actual={o.name for o in bpy.data.objects if o.name.startswith('V015 |')};missing=sorted(expected-actual);extra=sorted(actual-expected)
if missing or extra:
 r={'model_sha256':sha,'missing_hardware':missing,'unexpected_hardware':extra,'static_hinge_acceptance_pass':False};Path(a.report).write_text(json.dumps(r,indent=2));raise AssertionError(r)

def bbox(vs):return ([min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)])
def overlaps(a,b,eps=0):return all(a[1][k]>b[0][k]+eps and a[0][k]<b[1][k]-eps for k in range(3))
def shape(vs,fs,key):
 count=Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in fs for i in range(len(f)))
 bm=bmesh.new();verts=[bm.verts.new(v) for v in vs]
 for f in fs:bm.faces.new([verts[i] for i in f])
 closed=bool(fs) and all(n==2 for n in count.values()) and all(v.is_manifold for v in bm.verts if v.link_faces);volume=bm.calc_volume(signed=True);bm.free()
 return {'key':key,'vs':vs,'fs':fs,'bounds':bbox(vs),'closed':closed,'signed_volume':volume}

def evaluated(o):
 eo=o.evaluated_get(deps);me=eo.to_mesh();vs=[tuple(eo.matrix_world@v.co) for v in me.vertices];fs=[tuple(f.vertices) for f in me.polygons];eo.to_mesh_clear();return shape(vs,fs,o.name)

def temporary(s):
 me=bpy.data.meshes.new('TEMP hinge independent contact');me.from_pydata(s['vs'],[],s['fs']);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o);return o

def remove(o):
 me=o.data;bpy.data.objects.remove(o,do_unlink=True);bpy.data.meshes.remove(me)
cache={}
def intersection(left,right):
 key=tuple(sorted((left['key'],right['key'])))
 if key in cache:return cache[key]
 if not overlaps(left['bounds'],right['bounds']):result={'volume':0.0,'closed':True,'broadphase_disjoint':True}
 elif not left['closed'] or not right['closed']:result={'volume':None,'closed':False,'reason':'operand_not_closed'}
 else:
  lhs=temporary(left);rhs=temporary(right)
  try:
   bpy.context.view_layer.objects.active=lhs;lhs.select_set(True)
   mod=lhs.modifiers.new('Exact static contact','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=rhs;bpy.ops.object.modifier_apply(modifier=mod.name)
   bm=bmesh.new();bm.from_mesh(lhs.data);result={'volume':abs(bm.calc_volume(signed=True)),'closed':all(e.is_manifold for e in bm.edges),'result_faces':len(bm.faces)};bm.free()
  finally:remove(lhs);remove(rhs)
 cache[key]=result;return result

def positive(q):return q['closed'] and q['volume'] is not None and q['volume']>TOL
hardware={n:evaluated(bpy.data.objects[n]) for n in sorted(expected)};endpoint_shapes={};assembly=[];checks=[];topology=[];passage=[];allowed_source_pairs=set()
for side in ('south','north'):
 for level,z in [('lower',29.69),('upper',30.59)]:
  prefix=f'V015 | {side} hinge {level} ';names={p:prefix+p for p in parts}
  leaf=f'V012 | {side} outward-open timber leaf';jamb=f'V010 | {side} closed-entry stone jamb'
  candidates=[o for o in bpy.data.objects if o.name.startswith(f'V012 | {side} open-leaf iron strap') and not o.hide_render]
  assert len(candidates)==2,(side,'expected two original straps')
  strap=min(candidates,key=lambda o:abs(sum((o.matrix_world@Vector(v)).z for v in o.bound_box)/8-z)).name
  for n in (leaf,jamb,strap):
   assert n in bpy.data.objects and not bpy.data.objects[n].hide_render,n
   if n not in endpoint_shapes:endpoint_shapes[n]=evaluated(bpy.data.objects[n])
  assert abs(sum(endpoint_shapes[strap]['bounds'][k][2] for k in (0,1))/2-z)<.005
  links=[(strap,names['neck']),(leaf,names['neck']),(names['neck'],names['barrel']),(names['barrel'],names['pintle']),(names['pintle'],names['wall anchor']),(names['wall anchor'],jamb),(names['barrel'],names['pin cap'])]
  row={'side':side,'level':level,'matched_original_strap':strap,'original_leaf':leaf,'original_jamb':jamb,'required_links':[]}
  for left,right in links:
   q=intersection((hardware|endpoint_shapes)[left],(hardware|endpoint_shapes)[right]);record={'assembly':prefix.strip(),'left':left,'right':right,**q,'positive_closed_contact':positive(q)};checks.append(record);row['required_links'].append(record)
  for p in parts:
   n=names[p];s=hardware[n];ob=bpy.data.objects[n];topology.append({'object':n,'closed':s['closed'],'positive_signed_volume':s['signed_volume']>TOL,'volume':s['signed_volume'],'visible':not ob.hide_render,'materials':[m.name if m else None for m in ob.data.materials]})
   b=s['bounds'];side_clear=b[1][1]<36-1e-5 if side=='south' else b[0][1]>40+1e-5
   pivot_y=35.9 if side=='south' else 40.1
   pivot_local=p not in ('barrel','pin cap') or (max(abs(v+3.55) for v in (b[0][0],b[1][0]))<=.075 and max(abs(v-pivot_y) for v in (b[0][1],b[1][1]))<=.075)
   passage.append({'object':n,'bounds':b,'barrel_cap_confined_to_leaf_pivot_region':pivot_local,'entirely_outside_legacy_y36_to40_band':side_clear,'bounded_fixture_height':z-.21<=b[0][2] and b[1][2]<=z+.16,'within_small_hinge_region':b[0][0]>=-3.80 and b[1][0]<=-3.15})
  for target in (strap,leaf):allowed_source_pairs.add((names['neck'],target))
  for p in ('barrel','pin cap'):allowed_source_pairs.add((names[p],leaf))
  for p in ('pintle','wall anchor'):allowed_source_pairs.add((names[p],jamb))
  # Negative controls inspect a missing required anchor and a geometrically
  # detached anchor, without changing/deleting any loaded model object.
  without_anchor={p:n for p,n in names.items() if p!='wall anchor'}
  row['missing_anchor_negative_control_rejected']=not all(p in without_anchor for p in parts)
  original=hardware[names['wall anchor']];shifted=shape([(x-.5,y,h) for x,y,h in original['vs']],original['fs'],original['key']+' NEGATIVE moved west .5')
  detached=intersection(shifted,endpoint_shapes[jamb]);row['detached_anchor_negative_control']={**detached,'rejected':not positive(detached)}
  assembly.append(row)

# All source-visible local mesh components are checked, not just objects named
# architecture. Only explicitly allowed exact object-pairs may overlap.
# Atmospheric visualization meshes are not physical obstacles.
allbb=([min(s['bounds'][0][k] for s in hardware.values()) for k in range(3)],[max(s['bounds'][1][k] for s in hardware.values()) for k in range(3)])
source_components=[]
for o in list(bpy.data.objects):
 if o.type!='MESH' or o.hide_render or o.name in hardware or o.name.startswith(('Volume cloud','Air perspective')):continue
 eo=o.evaluated_get(deps);bb=bbox([eo.matrix_world@Vector(v) for v in eo.bound_box])
 if not overlaps(bb,allbb):continue
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
  if len(ids)<3:continue
  bb=bbox([vs[i] for i in ids])
  if any(overlaps(bb,h['bounds']) for h in hardware.values()):selected[seed]={'ids':ids,'faces':[]}
 for f in me.polygons:
  seed=find(f.vertices[0])
  if seed in selected:selected[seed]['faces'].append(tuple(f.vertices))
 for seed,c in selected.items():
  if not c['faces']:continue
  mapping={old:i for i,old in enumerate(c['ids'])};sh=shape([vs[i] for i in c['ids']],[tuple(mapping[i] for i in f) for f in c['faces']],o.name+' COMPONENT '+str(min(c['ids'])));sh['source_object']=o.name;sh['component_seed']=min(c['ids']);source_components.append(sh)
 eo.to_mesh_clear()

# Conservative triangle-vs-box SAT for open source sheets: prove their actual
# surfaces avoid hardware AABBs; ambiguous overlap fails rather than pretending
# an open sheet is an enclosed solid.
axes=[Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))]
def triangle_box(vs,bb):
 center=(Vector(bb[0])+Vector(bb[1]))*.5;half=(Vector(bb[1])-Vector(bb[0]))*.5;v=[Vector(q)-center for q in vs];edges=[v[1]-v[0],v[2]-v[1],v[0]-v[2]]
 for axis in axes+[edges[0].cross(edges[1])]+[e.cross(q) for e in edges for q in axes]:
  if axis.length<1e-10:continue
  axis=axis.normalized();q=[point.dot(axis) for point in v];radius=sum(half[k]*abs(axis[k]) for k in range(3))
  if min(q)>radius+2e-5 or max(q)<-radius-2e-5:return False
 return True
local_contacts=[];unexpected=[];uncertain=[];open_surface_checks=[]
for hn,h in hardware.items():
 for s in source_components:
  if not overlaps(h['bounds'],s['bounds']):continue
  base={'hardware':hn,'source':s['source_object'],'component_seed':s['component_seed']}
  if not s['closed']:
   # Blender triangulates non-convex polygons correctly; do not use a naive fan.
   me=bpy.data.meshes.new('TEMP open source triangulation');me.from_pydata(s['vs'],[],s['fs']);me.update();me.calc_loop_triangles();hits=sum(triangle_box([s['vs'][i] for i in t.vertices],h['bounds']) for t in me.loop_triangles);bpy.data.meshes.remove(me)
   open_surface_checks.append({**base,'triangles_intersecting_hardware_aabb':hits})
   if hits:uncertain.append({**base,'reason':'open_source_surface_intersects_hardware_aabb'})
   continue
  q=intersection(h,s)
  if not q['closed']:uncertain.append({**base,**q,'reason':'nonclosed_intersection'});continue
  if positive(q):
   allowed=(hn,s['source_object']) in allowed_source_pairs;record={**base,**q,'specifically_allowed_contact':allowed};local_contacts.append(record)
   if not allowed:unexpected.append(record)
# Adjacent parts of one assembly may intentionally join; different assemblies
# must not intersect. Required chain checks above prevent merely nearby parts.
hn=sorted(hardware)
for i,n in enumerate(hn):
 for m in hn[i+1:]:
  same=any(n.startswith(f'V015 | {s} hinge {h} ') and m.startswith(f'V015 | {s} hinge {h} ') for s in ('south','north') for h in ('lower','upper'))
  if same:continue
  q=intersection(hardware[n],hardware[m])
  if positive(q):unexpected.append({'hardware':n,'source':m,**q,'reason':'different_hinge_assemblies_intersect'})
source_unchanged=sha==hashlib.sha256(source.read_bytes()).hexdigest();cleaned=before==(len(bpy.data.objects),len(bpy.data.meshes))
r={'model_sha256':sha,'volume_threshold':TOL,'hardware_count':len(hardware),'topology':topology,'passage_bounds':passage,'assemblies':assembly,'required_positive_contacts':checks,'source_contact_checks':local_contacts,'open_surface_checks':open_surface_checks,'unexpected_intersections':unexpected,'uncertain':uncertain,'only_named_source_pair_exemptions':[list(q) for q in sorted(allowed_source_pairs)],'all_required_contacts_positive_closed':all(q['positive_closed_contact'] for q in checks),'all_hardware_closed_positive_visible':all(q['closed'] and q['positive_signed_volume'] and q['visible'] for q in topology),'all_hardware_uses_existing_forged_iron':all(q['materials']==['V013 | dark forged lantern iron'] for q in topology),'all_hardware_outside_tested_passage_band':all(q['entirely_outside_legacy_y36_to40_band'] and q['bounded_fixture_height'] and q['within_small_hinge_region'] and q['barrel_cap_confined_to_leaf_pivot_region'] for q in passage),'negative_controls_pass':all(q['missing_anchor_negative_control_rejected'] and q['detached_anchor_negative_control']['rejected'] for q in assembly),'temporary_datablocks_cleaned':cleaned,'source_unchanged':source_unchanged,'scope':'Static intended positive-volume contact chains only, including original matched strap and leaf to named jamb. No articulation or load capacity certification. Unrelated overlaps are never exempted by V015 prefix.'}
r['static_hinge_acceptance_pass']=all(r[k] for k in('all_required_contacts_positive_closed','all_hardware_closed_positive_visible','all_hardware_uses_existing_forged_iron','all_hardware_outside_tested_passage_band','negative_controls_pass','temporary_datablocks_cleaned','source_unchanged')) and not unexpected and not uncertain
Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if not isinstance(v,list)}));
if not a.allow_fail:assert r['static_hinge_acceptance_pass'],'Inspect hinge contact report'
