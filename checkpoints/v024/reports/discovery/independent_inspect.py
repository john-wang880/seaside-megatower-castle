import bpy,json,hashlib,collections,itertools
from pathlib import Path
P=Path('work/rear_surface_qa_v023'); src=Path('work/v023/castle_v023.blend');h=hashlib.sha256(src.read_bytes()).hexdigest();assert h=='c4b1dda3b8f70e4c8cb0171834b2150b6d7610f6296847362fd204b2dfa7ad51'
bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False)
o=bpy.data.objects['V008 | gallery with genuine eastern approach portal'];dg=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(dg);em=eo.to_mesh()
def components(m):
 p=list(range(len(m.vertices)))
 def root(i):
  while p[i]!=i:p[i]=p[p[i]];i=p[i]
  return i
 for e in m.edges:
  a,b=map(root,e.vertices);p[max(a,b)]=min(a,b)
 groups=collections.defaultdict(list)
 for v in m.vertices:groups[root(v.index)].append(v.index)
 fs=collections.defaultdict(list)
 for f in m.polygons:fs[root(f.vertices[0])].append(f)
 out={}
 for seed,ids in groups.items():
  vs=[list(o.matrix_world@m.vertices[i].co) for i in ids];lo=[min(v[k] for v in vs) for k in range(3)];hi=[max(v[k] for v in vs) for k in range(3)];edges=collections.Counter(tuple(sorted(e))for f in fs[seed] for e in f.edge_keys)
  out[seed]={'seed':seed,'indices':ids,'bounds':[lo,hi],'vertices':len(ids),'faces':len(fs[seed]),'closed':all(v==2 for v in edges.values()),'box_corners':len(ids)==8 and set(map(tuple,vs))==set(itertools.product(*zip(lo,hi))),'materials':sorted(set(f.material_index for f in fs[seed])),'face_ids':[f.index for f in fs[seed]]}
 return out,root
raw,rr=components(o.data);ev,er=components(em)
F=[]
for f in em.polygons:
 if f.normal.y<.99999:continue
 vs=[o.matrix_world@em.vertices[i].co for i in f.vertices];lo=[min(v[k]for v in vs)for k in range(3)];hi=[max(v[k]for v in vs)for k in range(3)]
 if not(lo[0]<35 and hi[0]>-15 and 52<=lo[1]<=67 and lo[2]<90 and hi[2]>35):continue
 assert len(vs)==4 and hi[1]-lo[1]<1e-7
 assert set((v.x,v.z)for v in vs)==set(itertools.product((lo[0],hi[0]),(lo[2],hi[2])))
 F.append((f.index,er(f.vertices[0]),lo,hi,f.material_index))
pairs=[]
for a,b in itertools.combinations(F,2):
 if a[1]==b[1] or a[2][1]!=b[2][1]:continue
 dx=min(a[3][0],b[3][0])-max(a[2][0],b[2][0]);dz=min(a[3][2],b[3][2])-max(a[2][2],b[2][2])
 if dx>0 and dz>0:pairs.append({'faces':[a[0],b[0]],'seeds':[a[1],b[1]],'area':dx*dz,'y':a[2][1],'same_material':a[4]==b[4]})
seeds=sorted({s for p in pairs for s in p['seeds']});mapping=[]
for s in seeds:
 e=ev[s];matches=[r for r in raw.values() if r['bounds']==e['bounds']];assert len(matches)==1
 mapping.append({'evaluated':e,'raw':matches[0]})
mods=[]
for m in o.modifiers:
 d={'name':m.name,'type':m.type}
 for k in ['width','segments','limit_method','angle_limit','use_clamp_overlap','affect','show_render','show_viewport']:
  if hasattr(m,k):d[k]=getattr(m,k)
 mods.append(d)
groups=[];remaining=set(seeds)
while remaining:
 g={remaining.pop()};change=True
 while change:
  change=False
  for p in pairs:
   if g.intersection(p['seeds']) and not set(p['seeds'])<=g:g.update(p['seeds']);change=True
 remaining-=g;groups.append({'seeds':sorted(g),'pairs':sum(set(p['seeds'])<=g for p in pairs),'plane_y':sorted({p['y']for p in pairs if set(p['seeds'])<=g})})
materials=[]
for m in o.data.materials:
 materials.append({'name':m.name,'links':[(l.from_node.type,l.from_socket.name,l.to_node.type,l.to_socket.name)for l in m.node_tree.links] if m.use_nodes else []})
report={'source_sha256':h,'source_unchanged':hashlib.sha256(src.read_bytes()).hexdigest()==h,'object':o.name,'modifiers':mods,'groups':groups,'pairs':pairs,'mapping':mapping,'materials':materials,'object_matrix':[list(r)for r in o.matrix_world],'mesh_users':o.data.users,'vertex_groups':[v.name for v in o.vertex_groups]}
(P/'independent.json').write_text(json.dumps(report,indent=2));eo.to_mesh_clear();print('INDEPENDENT',len(pairs),'pairs',len(seeds),'components','groups',groups,'mods',mods)
