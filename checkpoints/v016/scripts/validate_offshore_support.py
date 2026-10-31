"""Independent exact closed-solid static offshore support audit; never saves model."""
import bpy,bmesh,argparse,sys,json,hashlib,math
from pathlib import Path
from collections import defaultdict,Counter
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--report',required=True);p.add_argument('--baseline',required=True);p.add_argument('--allow-fail',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
canonical=Path(a.baseline);canonical_sha=hashlib.sha256(canonical.read_bytes()).hexdigest();assert canonical_sha=='578ff47936800fe2a651237b609d95090cd97fefa686a208f8215d57628ac389'
source=Path(bpy.data.filepath);sha=hashlib.sha256(source.read_bytes()).hexdigest();before=(len(bpy.data.objects),len(bpy.data.meshes));deps=bpy.context.evaluated_depsgraph_get();TOL=1e-8;cache={}
axes=[Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))]
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
def triangle_box(vs,bb):
 center=(Vector(bb[0])+Vector(bb[1]))*.5;half=(Vector(bb[1])-Vector(bb[0]))*.5;v=[Vector(q)-center for q in vs];edges=[v[1]-v[0],v[2]-v[1],v[0]-v[2]]
 for axis in axes+[edges[0].cross(edges[1])]+[e.cross(q) for e in edges for q in axes]:
  if axis.length<1e-10:continue
  axis=axis.normalized();q=[point.dot(axis) for point in v];radius=sum(half[k]*abs(axis[k]) for k in range(3))
  if min(q)>radius+2e-5 or max(q)<-radius-2e-5:return False
 return True
names={k:'V016 | offshore '+v for k,v in {'core':'terrain-following stair core','landing':'upper landing','arrival':'final arrival step','support':'final step support'}.items()}
missing=[n for n in names.values() if n not in bpy.data.objects];assert not missing,missing
hardware={k:evaluated(bpy.data.objects[n]) for k,n in names.items()}
# Union AABB contains every possible source contact. Cull evaluated, never raw modifier bounds.
allbb=([min(s['bounds'][0][k] for s in hardware.values()) for k in range(3)],[max(s['bounds'][1][k] for s in hardware.values()) for k in range(3)])
source_components={};nonmesh=[];scanned=[]
for o in list(bpy.context.scene.objects):
 if o.hide_render or o.hide_get() or o.name in names.values():continue
 if o.type!='MESH':
  if o.type not in ('CAMERA','LIGHT','EMPTY'):nonmesh.append([o.name,o.type])
  continue
 scanned.append(o.name);eo=o.evaluated_get(deps)
 if not overlaps(bbox([eo.matrix_world@Vector(v) for v in eo.bound_box]),allbb,-2e-5):continue
 me=eo.to_mesh();vs=[tuple(eo.matrix_world@v.co) for v in me.vertices];parent=list(range(len(vs)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for e in me.edges:
  u,v=map(find,e.vertices)
  if u!=v:parent[v]=u
 groups=defaultdict(list)
 for f in me.polygons:groups[find(f.vertices[0])].append(tuple(f.vertices))
 for fs in groups.values():
  ids=sorted({i for f in fs for i in f});bb=bbox([vs[i] for i in ids])
  if not overlaps(bb,allbb,-2e-5):continue
  remap={old:i for i,old in enumerate(ids)};key=o.name+'#'+str(ids[0]);s=shape([vs[i] for i in ids],[tuple(remap[i] for i in f) for f in fs],key);s['source_object']=o.name;s['seed']=ids[0];source_components[key]=s
 eo.to_mesh_clear()
ash='V012 | legacy ashlar with buried-route clearance#';rock='Western citadel_West_Sea stack basalt#0';plinth=ash+'5704';upper=ash+'5712';stairs=[ash+str(i) for i in range(5824,5881,8)]
required=[('core',s) for s in stairs]+[('core',rock),('core',plinth),('landing','core'),('landing',stairs[0]),('arrival','landing'),('arrival','support'),('arrival',upper),('support','core'),('support',plinth),('support','landing'),('support',upper)]
allowed={frozenset(pair) for pair in required};allsh=hardware|source_components
checks=[]
for left,right in required:
 if left not in allsh or right not in allsh:q={'closed':False,'volume':None,'missing_operand':True}
 else:q=intersection(allsh[left],allsh[right])
 checks.append({'left':left,'right':right,**q,'pass':positive(q)})
unexpected=[];uncertain=[];contacts=[];openchecks=[];fluid_contacts=[]
for k,h in hardware.items():
 for sk,s in source_components.items():
  if not overlaps(h['bounds'],s['bounds'],-2e-5):continue
  if not s['closed']:
   me=bpy.data.meshes.new('TEMP open offshore surface');me.from_pydata(s['vs'],[],s['fs']);me.update();me.calc_loop_triangles();hits=sum(triangle_box([s['vs'][i] for i in t.vertices],h['bounds']) for t in me.loop_triangles);bpy.data.meshes.remove(me)
   row={'hardware':k,'source':sk,'surface_aabb_triangle_hits':hits};openchecks.append(row)
   if hits:
    if s['source_object'] in ('Open sea | rippled three-dimensional water surface','Distant ocean to the horizon'):
     water=bpy.data.objects[s['source_object']];materials=[m.name if m else None for m in water.data.materials]
     if s['source_object']=='Distant ocean to the horizon':
      assert materials==['North sea | teal depth and crossing wavelets'] and abs(s['bounds'][0][2]+.432)<2e-5 and abs(s['bounds'][1][2]+.432)<2e-5,'Unrecognized horizon sheet geometry/material'
     fluid_contacts.append({**row,'classification':'intentional nonstructural fluid surface; never a support link','bounds':s['bounds'],'materials':materials})
    else:uncertain.append(row)
   continue
  q=intersection(h,s);row={'left':k,'right':sk,**q}
  if not q['closed']:uncertain.append(row)
  elif positive(q):
   row['allowed']=frozenset((k,sk)) in allowed;contacts.append(row)
   if not row['allowed']:unexpected.append(row)
keys=list(hardware)
for i,k in enumerate(keys):
 for j in keys[i+1:]:
  q=intersection(hardware[k],hardware[j]);row={'left':k,'right':j,**q}
  if not q['closed']:uncertain.append(row)
  elif positive(q):
   row['allowed']=frozenset((k,j)) in allowed;contacts.append(row)
   if not row['allowed']:unexpected.append(row)
limits={'core':([113.85,184.50,-10],[118.15,191.80,6.20]),'landing':([113.75,190.10,6.084],[118.25,191.80,6.444]),'arrival':([113.75,191.75,6.264],[114.75,192.40,6.624]),'support':([113.85,191.75,5.70],[114.65,192.40,6.30])}
topology=[]
for k,s in hardware.items():
 o=bpy.data.objects[names[k]];lo,hi=limits[k];bb=s['bounds'];bounded=all(bb[0][i]>=lo[i]-2e-5 and bb[1][i]<=hi[i]+2e-5 for i in range(3))
 topology.append({'part':k,'bounds':bb,'closed':s['closed'],'signed_volume':s['signed_volume'],'visible':not o.hide_render and not o.hide_get(),'materials':[m.name if m else None for m in o.data.materials],'within_agreed_bounds':bounded})
# Controls prove required chain fails if core omitted, and geometry-disconnected
# copy cannot satisfy a stair/core positive volume check. No source mutation.
missing_core=not all(x in (set(allsh)-{'core'}) and y in (set(allsh)-{'core'}) for x,y in required)
s=hardware['core'];moved=shape([(x+1000,y,z) for x,y,z in s['vs']],s['fs'],'NEGATIVE detached core');detached=not positive(intersection(moved,allsh[stairs[0]]))
r={'canonical_v015_sha256':canonical_sha,'canonical_v015_bytes_unchanged':canonical_sha==hashlib.sha256(canonical.read_bytes()).hexdigest(),'source_sha256':sha,'source_unchanged':sha==hashlib.sha256(source.read_bytes()).hexdigest(),'temporary_datablocks_cleaned':before==(len(bpy.data.objects),len(bpy.data.meshes)),'scope':'Static closed-positive-volume geometric support connectivity only; no walkability, dynamic simulation or structural/load claim. Exact component-specific intended contacts, no prefix exemption.','volume_threshold':TOL,'scanned_visible_mesh_objects':scanned,'visible_nonmesh_geometry':nonmesh,'source_component_count':len(source_components),'required_contacts':checks,'new_part_topology_bounds':topology,'all_positive_contacts':contacts,'unexpected_intersections':unexpected,'uncertain':uncertain,'open_surface_checks':openchecks,'nonstructural_fluid_contacts':fluid_contacts,'negative_controls':{'missing_core_rejected':missing_core,'detached_core_rejected':detached},'allowed_pairs':[sorted(q) for q in allowed]}
r['pass']=all(q['pass'] for q in checks) and all(q['closed'] and q['signed_volume']>TOL and q['visible'] and q['within_agreed_bounds'] and q['materials']==['West_Ashlar stone variation'] for q in topology) and not unexpected and not uncertain and not nonmesh and missing_core and detached and r['source_unchanged'] and r['temporary_datablocks_cleaned'] and r['canonical_v015_bytes_unchanged']
Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps({'pass':r['pass'],'required_failures':[q for q in checks if not q['pass']],'unexpected':unexpected,'uncertain':uncertain,'topology':topology},indent=2))
if not a.allow_fail:assert r['pass'],'Inspect independent support report'
