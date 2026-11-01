import bpy,json,hashlib,collections,time
from pathlib import Path
from mathutils import Vector
P=Path('work/gallery_support_graph_v018');SHA='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd';src=Path(bpy.data.filepath);assert hashlib.sha256(src.read_bytes()).hexdigest()==SHA
spec=json.load(open('work/gallery_arcade_audit_v018/components_extended.json'));targetspec=next(x for x in spec if x['object']=='V006 | main facade with one short jointed rib sample');targetname=targetspec['object'];dg=bpy.context.evaluated_depsgraph_get();region=targetspec['region']
def overlap(a,b,pad=0):return all(a[0][k]<=b[1][k]+pad and b[0][k]<=a[1][k]+pad for k in range(3))
def components(o):
 eo=o.evaluated_get(dg);me=eo.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
 try:
  me.calc_loop_triangles();vs=[list(eo.matrix_world@v.co) for v in me.vertices];parent=list(range(len(vs)))
  def root(i):
   while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
   return i
  for e in me.edges:
   a,b=map(root,e.vertices);parent[b]=a
  groups=collections.defaultdict(list)
  for i in range(len(vs)):groups[root(i)].append(i)
  tris=collections.defaultdict(list)
  for t in me.loop_triangles:tris[root(t.vertices[0])].append(list(t.vertices))
  result=[]
  for key,ids in groups.items():
   pts=[vs[i] for i in ids];bb=[[min(v[k] for v in pts) for k in range(3)],[max(v[k] for v in pts) for k in range(3)]];mapping={v:i for i,v in enumerate(ids)};tt=[[mapping[i] for i in t] for t in tris[key]]
   if not tt:continue
   counts=collections.Counter(tuple(sorted((t[j],t[(j+1)%3]))) for t in tt for j in range(3));result.append({'object':o.name,'seed':min(ids),'bounds':bb,'vertices':pts,'triangles':tt,'closed':all(n==2 for n in counts.values()),'vertex_count':len(ids),'signature':hashlib.sha256(json.dumps(sorted(pts)).encode()).hexdigest()})
  return result
 finally:eo.to_mesh_clear()
target=bpy.data.objects[targetname];assert not target.modifiers
raw=components(target);targets=[c for c in raw if overlap(c['bounds'],region)];assert len(targets)==430
assert {c['seed'] for c in targets}=={c['seed'] for c in targetspec['components']}
for c in targets:
 old=next(x for x in targetspec['components'] if x['seed']==c['seed']);assert c['vertex_count']==old['vertices'] and all(abs(c['bounds'][j][k]-old['bounds'][j][k])<1e-5 for j in range(2) for k in range(3));c['target']=True
boxes=[c['bounds'] for c in targets];union=[[min(bb[0][k] for bb in boxes) for k in range(3)],[max(bb[1][k] for bb in boxes) for k in range(3)]]
allc=list(raw);objects=[];excluded=[]
for o in bpy.context.scene.objects:
 if o==target or o.type!='MESH' or o.hide_render or o.hide_viewport or not o.visible_get():continue
 if o.name.startswith(('Air perspective','Volume cloud','Open sea','Distant ocean')):excluded.append(o.name);continue
 eo=o.evaluated_get(dg);corners=[eo.matrix_world@Vector(v) for v in eo.bound_box];bb=[[min(v[k] for v in corners) for k in range(3)],[max(v[k] for v in corners) for k in range(3)]]
 if not overlap(bb,union,2):continue
 cs=components(o);kept=[c for c in cs if any(overlap(c['bounds'],b,2) for b in boxes)];allc.extend(kept);objects.append({'object':o.name,'evaluated_components':len(cs),'near_target_full_bounds':len(kept),'modifiers':[m.type for m in o.modifiers]})
# Keep full source-object components too: possible indirect same-object support chains.
keys={(c['object'],c['seed']) for c in targets}
for c in allc:c['target']=(c['object'],c['seed']) in keys
r={'source_sha256':SHA,'source_unchanged':hashlib.sha256(src.read_bytes()).hexdigest()==SHA,'target_count':430,'target_full_bounds_union':union,'components':allc,'objects':objects,'excluded_named_nonstructural':excluded,'scope':'Full evaluated components, never clipped to inspection box. Other-object components selected by proximity to every full target AABB; unresolved chains beyond this neighborhood need expansion, not floating verdict.'};(P/'geometry.json').write_text(json.dumps(r));print(json.dumps({k:v for k,v in r.items() if k!='components'},indent=2))
