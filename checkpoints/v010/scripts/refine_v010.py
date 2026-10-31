"""Repair inherited solid occupancy, local stair-edge terrain and gate vegetation."""
import argparse,bpy,bmesh,hashlib,json,math,sys
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath);out=Path(a.output).resolve();assert out!=source.resolve();assert not any(o.name.startswith('V010 |') for o in bpy.data.objects)
col=bpy.data.collections.new('REFINEMENT | v010 actual entrance clearance');bpy.context.scene.collection.children.link(col)
F=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
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
mat=bpy.data.materials['Citadel • weathered limestone'];wood=bpy.data.materials['Pine bark'];iron=bpy.data.materials['Citadel • deep slate ashlar']
def box(name,x0,x1,y0,y1,z0,z1,material):
 return plain_mesh(name,[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],F,[material])
# Remove only the bounded foundation volume actually overlapping the landing.
cutter=box('TEMP vestibule cutter',-6.25,-3.15,35.55,40.45,28.78,32.3,mat)
foundation=bpy.data.objects['Citadel | rock-set foundations and approach stair'];group=next(g for g in components(foundation.data) if 0 in g);assert len(group)==8
excavation=cut_components(foundation,cutter,[group],'V010 | foundation with clear eastern entrance vestibule')
me=cutter.data;bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.meshes.remove(me)
# Intentionally closed arched door: genuine vestibule, NOT a fictitious through
# route into the unfinished interior. Usable landing stops west of x=-3.5.
cross=[(35.9,29),(40.1,29),(40.1,31)]
for i in range(1,25):
 t=math.pi*i/24;cross.append((38+2.1*math.cos(t),31+1.5*math.sin(t)))
n=len(cross);door=plain_mesh('V010 | deliberately closed eastern timber entry',[(x,y,z) for x in (-3.37,-3.19) for y,z in cross],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],[wood])
# Narrow frame, center seam and iron straps convey the deliberate route end.
for name,y0,y1 in [('south',35.65,35.9),('north',40.1,40.35)]:box('V010 | '+name+' closed-entry stone jamb',-3.49,-3.17,y0,y1,29,31,mat)
vs=[];fs=[]
for i in range(13):
 t0=math.pi*i/13+.006;t1=math.pi*(i+1)/13-.006;pts=[]
 for x in (-3.49,-3.17):
  for radius,rise,t in [(2.1,1.5,t0),(2.35,1.75,t0),(2.35,1.75,t1),(2.1,1.5,t1)]:pts.append((x,38+radius*math.cos(t),31+rise*math.sin(t)))
 k=len(vs);vs.extend(pts);fs.extend(tuple(k+j for j in f) for f in F)
plain_mesh('V010 | closed-entry stone arch',vs,fs,[mat])
box('V010 | double-door central seam',-3.395,-3.375,37.98,38.02,29.02,32.46,iron)
for z in (29.65,30.55):
 for ya,yb in ((36.03,37.93),(38.07,39.97)):box('V010 | entry iron strap',-3.42,-3.395,ya,yb,z,z+.08,iron)
# Local terrain clearance patch coordinates are measured from actual offending
# triangles, not broad remeshing or wholesale coastal flattening.
src=bpy.data.objects['Castle headland | level courtyard and broken coastal escarpment'];new=src.copy();new.name='V010 | headland with local stair-edge clearance';new.data=src.data.copy();new.data.name=new.name;col.objects.link(new);inverse=src.matrix_world.inverted();terrain_edits=[]
for index,target_z in ((5502,27.80),(5758,27.60),(6014,27.60)):
 v=new.data.vertices[index];before=src.matrix_world@v.co;after=before.copy();after.z=target_z;v.co=inverse@after;terrain_edits.append({'vertex':index,'before':list(before),'after':list(after)})
new.data.update();src.hide_render=True;src.hide_set(True)
# A complete tree has low foliage crossing the far side of the western passage.
vegetation=[]
for name,first,last,label in [('V009 | woodland trunks with western approach clearance',98340,98590,'V010 | woodland trunks with gate exit clearance'),('V009 | woodland boughs with western approach clearance',168367,168580,'V010 | woodland boughs with gate exit clearance')]:
 src=bpy.data.objects[name];m=src.data;ids=set(range(first,last));assert all(all(i in ids for i in p.vertices) or all(i not in ids for i in p.vertices) for p in m.polygons)
 kept=[p for p in m.polygons if not any(i in ids for i in p.vertices)];ob=plain_mesh(label,[tuple(v.co) for v in m.vertices],[tuple(p.vertices) for p in kept],list(m.materials));ob.matrix_world=src.matrix_world.copy()
 for p,old in zip(ob.data.polygons,kept):p.material_index=old.material_index;p.use_smooth=old.use_smooth
 src.hide_render=True;src.hide_set(True);vegetation.append({'source':name,'removed_range':[first,last],'removed_faces':len(m.polygons)-len(kept)})
bpy.context.preferences.filepaths.use_scripts_auto_execute=False;bpy.context.scene.render.filepath='//preview.png';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
r={'version':'v010','runtime':bpy.app.version_string,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'foundation_clearance':excavation,'terrain_edits':terrain_edits,'vegetation':vegetation,'scope':'Clear actual eastern entrance vestibule ending at deliberately CLOSED door; no claim of through courtyard route.'};Path(a.report).write_text(json.dumps(r,indent=2));print('V010_BUILD_OK',json.dumps(r))
