"""Open an east-west passage through the western bridgehead; preserve all source data.
Run from verified v006, with --disable-autoexec. No external assets or downloads.
"""
import argparse,bpy,bmesh,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath);out=Path(a.output).resolve()
assert out != source.resolve(), 'Never overwrite source'
assert not any(o.name.startswith('V007 |') for o in bpy.data.objects), 'Build from v006 only'
bpy.context.preferences.filepaths.use_scripts_auto_execute=False
col=bpy.data.collections.new('REFINEMENT | v007 western bridgehead passage');bpy.context.scene.collection.children.link(col)

def mesh_object(name,verts,faces,materials):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);col.objects.link(ob)
 for m in materials:me.materials.append(m)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();return ob

def component_ids(me,seed):
 adj=[[] for _ in me.vertices]
 for e in me.edges:
  x,y=e.vertices;adj[x].append(y);adj[y].append(x)
 ids=set();q=[seed]
 while q:
  x=q.pop()
  if x in ids:continue
  ids.add(x);q.extend(y for y in adj[x] if y not in ids)
 return ids

# The original gate block and adjacent support arch are perpendicular to the bridge.
# A shared true cut along X creates a usable central passage, without moving facades.
yc=38.0;r=2.2;spring=29.05;rise=2.0;floor=27.40
cross=[(yc-r,26.9),(yc+r,26.9),(yc+r,spring)]
for i in range(1,25):
 th=math.pi*i/24;cross.append((yc+r*math.cos(th),spring+rise*math.sin(th)))
verts=[(x,y,z) for x in (-73.0,-55.5) for y,z in cross];n=len(cross)
faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
cut=mesh_object('TEMP passage cutter',verts,faces,[])
src=bpy.data.objects['Western citadel_West_Cool weathered limestone'];me=src.data
ids=component_ids(me,16054)|component_ids(me,17278)
assert len(ids)==62, len(ids)
keep=[f for f in me.polygons if not all(i in ids for i in f.vertices)]
v=[tuple(x.co) for x in me.vertices];fs=[tuple(f.vertices) for f in keep];matids=[f.material_index for f in keep]
inv=src.matrix_world.inverted()
# Boolean each closed component independently: their overlapping assembly must not
# be treated as a single self-intersecting operand.
for seed in (16054,17278):
 selected_ids=component_ids(me,seed);order=sorted(selected_ids);remap={v:i for i,v in enumerate(order)}
 selected=[f for f in me.polygons if all(i in selected_ids for i in f.vertices)]
 part=mesh_object('TEMP gate component',[tuple(src.matrix_world@me.vertices[i].co) for i in order],[[remap[i] for i in f.vertices] for f in selected],list(me.materials))
 for f,old in zip(part.data.polygons,selected):f.material_index=old.material_index
 bpy.context.view_layer.objects.active=part;part.select_set(True)
 mod=part.modifiers.new('Actual bridgehead through passage','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
 bpy.ops.object.modifier_apply(modifier=mod.name)
 offset=len(v);v.extend(tuple(inv@(part.matrix_world@x.co)) for x in part.data.vertices)
 fs.extend(tuple(offset+i for i in f.vertices) for f in part.data.polygons);matids.extend(f.material_index for f in part.data.polygons)
 data=part.data;bpy.data.objects.remove(part,do_unlink=True);bpy.data.meshes.remove(data)
new=mesh_object('V007 | western stonework with actual bridgehead passage',v,fs,list(me.materials));new.matrix_world=src.matrix_world.copy()
for f,idx in zip(new.data.polygons,matids):f.material_index=idx
src.hide_render=True;src.hide_set(True)
for ob in (cut,):
 data=ob.data;bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(data)
# Continuous threshold connects the two cut components to the existing bridge deck.
mat=me.materials[0]
F=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,x0,x1,y0,y1,z0,z1):
 return mesh_object(name,[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],F,[mat])
slab=box('V007 | continuous stone passage threshold',-71.3,-57.6,35.5,40.5,27.16,floor)
# Subtle segmented voussoirs make the eastern portal legible; do not change tower skyline.
vs=[];fs=[]
for i in range(13):
 t0=math.pi*i/13+.008;t1=math.pi*(i+1)/13-.008
 pts=[]
 for x in (-56.54,-56.28):
  for radius,height,theta in [(r,rise,t0),(r+.23,rise+.23,t0),(r+.23,rise+.23,t1),(r,rise,t1)]:pts.append((x,yc+radius*math.cos(theta),spring+height*math.sin(theta)))
 start=len(vs);vs.extend(pts);fs.extend(tuple(start+j for j in f) for f in F)
ring=mesh_object('V007 | eastern portal individual arch stones',vs,fs,[mat])
# Checks operate on the actual resulting modified component, not on intended cutter dimensions.
bm=bmesh.new();bm.from_mesh(new.data)
boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
assert boundary==0 and nonmanifold==0,(boundary,nonmanifold)
# Check unobstructed passage rays in the usable central width, above threshold.
rays=[]
for y in (36.6,38,39.4):
 for z in (27.6,28.4,29.4):
  hit,loc,normal,face=new.ray_cast(inv@Vector((-72,y,z)),inv.to_3x3()@Vector((1,0,0)),distance=16.5)
  rays.append({'y':y,'z':z,'blocked':bool(hit)})
assert not any(x['blocked'] for x in rays),rays
# One pre-existing conifer grew inside the solid gate. Remove this complete tree,
# not just intersecting triangles, retaining untouched forest geometry and source meshes.
vegetation=[]
for name,first,last,newname in [
 ('Woodland tree trunks',13210,13620,'V007 | woodland trunks minus gate-intersecting tree'),
 ('Dense western woodland | irregular three-dimensional needle boughs',47305,47720,'V007 | woodland boughs minus gate-intersecting tree')]:
 original=bpy.data.objects[name];m=original.data;removed=set(range(first,last))
 assert all(all(i in removed for i in p.vertices) or all(i not in removed for i in p.vertices) for p in m.polygons)
 points=[original.matrix_world@m.vertices[i].co for i in removed]
 assert all(-74<v.x<-67 and 33<v.y<40 and 21<v.z<31 for v in points)
 retained=[p for p in m.polygons if not any(i in removed for i in p.vertices)]
 replacement=mesh_object(newname,[tuple(v.co) for v in m.vertices],[tuple(p.vertices) for p in retained],list(m.materials));replacement.matrix_world=original.matrix_world.copy()
 for f,old in zip(replacement.data.polygons,retained):f.material_index=old.material_index;f.use_smooth=old.use_smooth
 original.hide_render=True;original.hide_set(True)
 vegetation.append({'source':name,'removed_vertex_range':[first,last],'removed_faces':len(m.polygons)-len(retained),'retained_faces':len(retained)})
bpy.context.scene.render.filepath='//preview.png'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report={'version':'v007','source_filename':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'runtime':bpy.app.version_string,'modified_source_object':src.name,'original_component_vertices':len(ids),'original_unchanged_faces':len(keep),'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'clear_passage_rays':rays,'threshold_elevation':floor,'scope':'Western gate internal east-west opening and threshold only; western approach stairs and eastern cliff landing remain future work.','vegetation_clearance':vegetation,'new_objects':[o.name for o in col.objects],'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
Path(a.report).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('V007_OK',json.dumps(report))
