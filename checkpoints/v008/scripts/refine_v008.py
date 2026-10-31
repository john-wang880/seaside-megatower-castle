"""Rock-supported eastern bridge approach, built additively from verified v007."""
import argparse,bpy,bmesh,hashlib,json,math,sys
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath);out=Path(a.output).resolve();assert out!=source.resolve();assert not any(o.name.startswith('V008 |') for o in bpy.data.objects)
bpy.context.preferences.filepaths.use_scripts_auto_execute=False
col=bpy.data.collections.new('REFINEMENT | v008 rock-supported eastern approach');bpy.context.scene.collection.children.link(col)
ground=bpy.data.objects['Castle headland | level courtyard and broken coastal escarpment'];inv=ground.matrix_world.inverted()
mat=bpy.data.objects['Western citadel_West_Cool weathered limestone'].data.materials[0]

def terrain(x,y):
 hit,loc,n,idx=ground.ray_cast(inv@Vector((x,y,80)),(inv.to_3x3()@Vector((0,0,-1))).normalized());assert hit,(x,y)
 return (ground.matrix_world@loc).z

def mesh(name,verts,faces):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(mat);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);col.objects.link(ob);return ob

def extrude(name,profile,y0,y1):
 n=len(profile);verts=[(x,y,z) for y in (y0,y1) for x,z in profile]
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,verts,faces)

xs=[-16+i for i in range(12)]+[-3.3]
y0,y1=35.7,40.3
# Below the lowest sampled rock across the complete width; no unsupported sliver.
rock=[]
for x in xs:
 zz=[terrain(x,y) for y in (35.3,35.7,36.8,38,39.2,40.3,40.7)]
 rock.append({'x':x,'ground_min':min(zz),'ground_max':max(zz),'footing_z':min(zz)-.35})
# 11 broad shallow treads (0.1818 rise), then a level outer landing.
top=[]
for i in range(11):
 z=27.0+(i+1)*2/11
 top.extend([(-16+i,z),(-15+i,z)])
top.append((-3.3,29.0))
bottom=[(r['x'],r['footing_z']) for r in reversed(rock)]
body=extrude('V008 | eastern stepped approach embedded in rock',top+bottom,y0,y1)
# Shallow continuous stone parapets with sloping cap avoid trip-height zigzags.
# Deliberately stop at outer landing; the castle interior route is not fabricated.
rail_top=[(-16,28.08),(-5,29.9),(-3.3,29.9)]
rails=[]
for label,ya,yb in [('south',35.3,35.7),('north',40.3,40.7)]:
 rails.append(extrude('V008 | '+label+' approach parapet',rail_top+bottom,ya,yb))
# Thin segmented tread caps, restrained gaps, reused scene stone material.
F=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
vs=[];fs=[]
for i in range(11):
 x0=-16+i+.025;x1=-15+i-.025;z=27+(i+1)*2/11
 for j in range(3):
  ya=y0+j*(y1-y0)/3+.012;yb=y0+(j+1)*(y1-y0)/3-.012
  k=len(vs);vs.extend([(x0,ya,z-.045),(x1,ya,z-.045),(x1,yb,z-.045),(x0,yb,z-.045),(x0,ya,z+.012),(x1,ya,z+.012),(x1,yb,z+.012),(x0,yb,z+.012)]);fs.extend(tuple(k+t for t in f) for f in F)
caps=mesh('V008 | individually jointed limestone tread caps',vs,fs)
# Open the existing tapered gallery foundation; adding stairs inside a solid wall
# is not an acceptable approach. Retain the original object as a hidden source.
def plain_mesh(name,verts,faces,materials):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 for m in materials:me.materials.append(m)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);col.objects.link(ob);return ob

def components(me):
 adj=[[] for _ in me.vertices]
 for e in me.edges:
  a,b=e.vertices;adj[a].append(b);adj[b].append(a)
 done=set()
 for seed in range(len(adj)):
  if seed in done:continue
  ids=set();q=[seed]
  while q:
   i=q.pop()
   if i in ids:continue
   ids.add(i);q.extend(j for j in adj[i] if j not in ids)
  done.update(ids);yield ids

def cut_components(src,cutter,groups,label):
 me=src.data;removed=set().union(*groups);kept=[p for p in me.polygons if not all(i in removed for i in p.vertices)]
 verts=[tuple(v.co) for v in me.vertices];faces=[tuple(p.vertices) for p in kept];material_ids=[p.material_index for p in kept];inverse=src.matrix_world.inverted()
 for group in groups:
  order=sorted(group);mapping={v:i for i,v in enumerate(order)};old=[p for p in me.polygons if all(i in group for i in p.vertices)]
  piece=plain_mesh('TEMP cutter operand',[tuple(src.matrix_world@me.vertices[i].co) for i in order],[[mapping[i] for i in p.vertices] for p in old],list(me.materials))
  for p,q in zip(piece.data.polygons,old):p.material_index=q.material_index
  # Original decorative rock blades have an open buried underside. Close only
  # selected operands before boolean excavation; untouched rocks stay unchanged.
  bm=bmesh.new();bm.from_mesh(piece.data)
  boundary=[e for e in bm.edges if e.is_boundary]
  if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges)
  bm.to_mesh(piece.data);bm.free()
  bpy.context.view_layer.objects.active=piece;piece.select_set(True)
  mod=piece.modifiers.new('Local excavation','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name)
  bm=bmesh.new();bm.from_mesh(piece.data);assert not any(not e.is_manifold for e in bm.edges),(src.name,min(group),len(bm.edges),sum(not e.is_manifold for e in bm.edges));bm.free()
  off=len(verts);verts.extend(tuple(inverse@v.co) for v in piece.data.vertices);faces.extend(tuple(off+i for i in p.vertices) for p in piece.data.polygons);material_ids.extend(p.material_index for p in piece.data.polygons)
  m=piece.data;bpy.data.objects.remove(piece,do_unlink=True);bpy.data.meshes.remove(m)
 replacement=src.copy();replacement.name=label;replacement.data=bpy.data.meshes.new(label);replacement.data.from_pydata(verts,[],faces);replacement.data.update()
 for m in me.materials:replacement.data.materials.append(m)
 for p,idx in zip(replacement.data.polygons,material_ids):p.material_index=idx
 col.objects.link(replacement);replacement.hide_render=False;replacement.hide_set(False);src.hide_render=True;src.hide_set(True)
 return {'source':src.name,'replacement':replacement.name,'components_cut':len(groups),'untouched_faces':len(kept),'source_modifiers_preserved':[m.type for m in replacement.modifiers]}

cross=[(35.5,26.7),(40.5,26.7),(40.5,31.0)]
for i in range(1,25):
 t=math.pi*i/24;cross.append((38+2.5*math.cos(t),31+2*math.sin(t)))
n=len(cross);verts=[(x,y,z) for x in (-17.0,-3.2) for y,z in cross];faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
cutter=plain_mesh('TEMP gallery arch cutter',verts,faces,[])
gallery=bpy.data.objects['Citadel | secondary keep and galleries'];group=next(g for g in components(gallery.data) if 3888 in g);assert len(group)==8
excavation=[cut_components(gallery,cutter,[group],'V008 | gallery with genuine eastern approach portal')]
m=cutter.data;bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.meshes.remove(m)
# Trim only intersecting rock components within the path volume; rock outside
# this corridor and the broad underlying terrain are unchanged.
cutter=plain_mesh('TEMP tread rock clearance',[(-16.1,35.6,27),(-3.2,35.6,27),(-3.2,40.4,27),(-16.1,40.4,27),(-16.1,35.6,35),(-3.2,35.6,35),(-3.2,40.4,35),(-16.1,40.4,35)],F,[])
rocks=bpy.data.objects['Slanting slate ribs, coastal blade-rocks and tidal reefs'];groups=[]
for group in components(rocks.data):
 pts=[rocks.matrix_world@rocks.data.vertices[i].co for i in group];lo=[min(v[k] for v in pts) for k in range(3)];hi=[max(v[k] for v in pts) for k in range(3)]
 if all(hi[k]>v for k,v in enumerate((-16.1,35.6,27))) and all(lo[k]<v for k,v in enumerate((-3.2,40.4,35))):groups.append(group)
excavation.append(cut_components(rocks,cutter,groups,'V008 | coastal rock blades locally excavated for approach'))
m=cutter.data;bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.meshes.remove(m)
# Portal voussoirs follow the real tapered front plane rather than floating.
vs=[];fs=[]
for i in range(15):
 t0=math.pi*i/15+.006;t1=math.pi*(i+1)/15-.006;pts=[]
 for depth in (-.12,.12):
  for radius,height,t in [(2.5,2,t0),(2.74,2.24,t0),(2.74,2.24,t1),(2.5,2,t1)]:
   z=31+height*math.sin(t);y=38+radius*math.cos(t);x=-15.85+(z-23.4)*(.071347)+depth;pts.append((x,y,z))
 k=len(vs);vs.extend(pts);fs.extend(tuple(k+j for j in f) for f in F)
mesh('V008 | tapered gallery portal arch stones',vs,fs)

# Externally check real tread/landing surfaces against terrain at dense samples.
clear=[]
for i in range(11):
 x=-15.5+i;z=27+(i+1)*2/11+.012
 for y in (35.8,36.9,38,39.1,40.2):
  g=terrain(x,y);clear.append({'x':x,'y':y,'tread_z':z,'ground_z':g,'clearance':z-g})
assert min(r['clearance'] for r in clear)>0, min(r['clearance'] for r in clear)
bpy.context.scene.render.filepath='//preview.png';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
r={'version':'v008','source':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'runtime':bpy.app.version_string,'model_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'excavation':excavation,'new_objects':[o.name for o in col.objects],'rise':2.0,'treads':11,'nominal_riser':2/11,'clear_width':4.6,'rock_footing_samples':rock,'tread_ground_samples':clear,'original_data_unchanged':True,'limits':'Outer bridge-to-rock approach only. Castle interior entrance and western approach remain unfinished. No real-world engineering certification.'}
Path(a.report).write_text(json.dumps(r,indent=2));print('V008_OK',len(clear))
