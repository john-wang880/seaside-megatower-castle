"""Terrain-supported western approach; preserve prior scene and all source meshes."""
import argparse,bpy,bmesh,hashlib,json,math,sys
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True);p.add_argument('--trees',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath);out=Path(a.output).resolve();assert out!=source.resolve();assert not any(o.name.startswith('V009 |') for o in bpy.data.objects)
col=bpy.data.collections.new('REFINEMENT | v009 western woodland approach');bpy.context.scene.collection.children.link(col)
ground=bpy.data.objects['V002 | western headland with solid rock shore'];inv=ground.matrix_world.inverted();mat=bpy.data.objects['Western citadel_West_Cool weathered limestone'].data.materials[0]
def terrain(x,y):
 h,v,n,i=ground.ray_cast(inv@Vector((x,y,80)),inv.to_3x3()@Vector((0,0,-1)));assert h;return (ground.matrix_world@v).z

def mesh(name,vs,fs,materials=None):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
 for m in (materials if materials is not None else [mat]):me.materials.append(m)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);col.objects.link(ob);return ob

def extrude(name,profile,y0,y1):
 n=len(profile);return mesh(name,[(x,y,z) for y in (y0,y1) for x,z in profile],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])

xs=[-90+i for i in range(19)]+[-71.2];bottom=[(x,min(terrain(x,y) for y in (36.1,36.4,37.2,38,38.8,39.6,39.9))-.35) for x in reversed(xs)]
top=[]
for i in range(9):
 z=25.8+.2*i;top.extend([(-90+2*i,z),(-88+2*i,z)])
top.append((-71.2,27.4));body=extrude('V009 | nine broad western approach treads',top+bottom,36.4,39.6)
# Low continuous protective sidewalls; end at the existing portal face.
rail_top=[(-90,26.45),(-72,28.15),(-71.3,28.15)]
for label,y0,y1 in [('south',36.1,36.4),('north',39.6,39.9)]:extrude('V009 | '+label+' approach parapet',rail_top+[(x,z) for x,z in bottom if x<=-71.3],y0,y1)
# Terrain-following entry apron, triangulated grid. Its west edge blends into
# real terrain while east edge meets the first riser at z25.6, not a floating box.
xx=[-91.5,-91.0,-90.5,-90];yy=[36.4,37.2,38,38.8,39.6];vs=[]
for layer in (0,1):
 for x in xx:
  for y in yy:
   g=terrain(x,y);t=(x+91.5)/1.5;z=(1-t)*(g+.055)+t*25.6
   vs.append((x,y,z if layer else g-.35))
nx,ny=len(xx),len(yy);N=nx*ny;fs=[]
for i in range(nx-1):
 for j in range(ny-1):
  k=i*ny+j
  for off in (0,N):fs.extend([(off+k,off+k+ny,off+k+ny+1),(off+k,off+k+ny+1,off+k+1)])
edge=[i*ny for i in range(nx)]+[(nx-1)*ny+j for j in range(1,ny)]+[i*ny+ny-1 for i in reversed(range(nx-1))]+[j for j in reversed(range(1,ny-1))]
for k,i in enumerate(edge):j=edge[(k+1)%len(edge)];fs.append((i,j,N+j,N+i))
apron=mesh('V009 | terrain-following woodland entry apron',vs,fs)
# Remove complete intersecting tree groups only; preserve original vegetation
# as hidden editable source meshes. Explicit surveyed ranges are part of report.
vegetation=[]
for spec in json.loads(Path(a.trees).read_text()):
 src=bpy.data.objects[spec['object']];me=src.data;removed=set()
 for first,last in spec['ranges']:removed.update(range(first,last))
 assert all(all(i in removed for i in p.vertices) or all(i not in removed for i in p.vertices) for p in me.polygons)
 keep=[p for p in me.polygons if not any(i in removed for i in p.vertices)]
 ob=mesh(spec['replacement'],[tuple(v.co) for v in me.vertices],[tuple(p.vertices) for p in keep],list(me.materials));ob.matrix_world=src.matrix_world.copy()
 for p,old in zip(ob.data.polygons,keep):p.material_index=old.material_index;p.use_smooth=old.use_smooth
 src.hide_render=True;src.hide_set(True);vegetation.append({**spec,'removed_faces':len(me.polygons)-len(keep)})
# Retain original lighting/cameras/world and never overwrite source.
bpy.context.preferences.filepaths.use_scripts_auto_execute=False;bpy.context.scene.render.filepath='//preview.png'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
r={'version':'v009','runtime':bpy.app.version_string,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'treads':9,'rise':.2,'clear_width':3.2,'gate_elevation':27.4,'vegetation':vegetation,'scope':'Western terrain-to-gate approach only. Eastern inner courtyard route remains unfinished.'}
Path(a.report).write_text(json.dumps(r,indent=2));print('V009_BUILD_OK',json.dumps(r))
