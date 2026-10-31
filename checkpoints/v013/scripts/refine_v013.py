import bpy,math,argparse,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True);p.add_argument('--power-scale',type=float,default=1);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath);sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert not any(o.name.startswith('V013 |') for o in bpy.data.objects)
metal=bpy.data.materials.new('V013 | dark forged lantern iron');metal.use_nodes=True;n=metal.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(.055,.045,.035,1);n.inputs['Metallic'].default_value=.85;n.inputs['Roughness'].default_value=.4
ember=bpy.data.materials.new('V013 | warm lantern flame');ember.use_nodes=True;n=ember.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(1,.34,.055,1);n.inputs['Emission Color'].default_value=(1,.38,.075,1);n.inputs['Emission Strength'].default_value=4
made=[]
def finish(o,name,mat):
 o.name='V013 | '+name;o.data.name=o.name+' mesh';o.data.materials.append(mat);made.append(o.name);return o
def rod(name,a,b,r):
 vec=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=vec.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.rotation_euler=vec.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,name,metal)
def box(name,loc,scale):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,name,metal)
# Surface-mounted, narrow cages outside the previously checked central walking prism.
fixtures=[('entrance',(0,36.79,31.05),(0,36.61,31.05),42),('turn',(5.21,38.65,30.95),(5.39,38.65,30.95),36),('corridor',(5.21,43.5,30.83),(5.39,43.5,30.83),34),('stair',(5.21,49.4,32.08),(5.39,49.4,32.08),40)]
for name,loc,mount,power in fixtures:
 x,y,z=loc;mx,my,mz=mount
 box(name+' mounting plate',mount,(.09,.025,.30) if name=='entrance' else (.025,.09,.30))
 rod(name+' wall arm',mount,(x,y,z+.19),.018)
 for dz in(-.16,.16):
  bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.105,depth=.025,location=(x,y,z+dz));finish(bpy.context.object,name+(' lower cup' if dz<0 else ' hood rim'),metal)
 bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=.11,radius2=.035,depth=.09,location=(x,y,z+.215));finish(bpy.context.object,name+' rain hood',metal)
 for i in range(4):
  t=math.pi/4+i*math.pi/2;dx=.082*math.cos(t);dy=.082*math.sin(t);rod(name+' cage upright '+str(i),(x+dx,y+dy,z-.15),(x+dx,y+dy,z+.15),.009)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=(x,y,z));o=bpy.context.object;o.scale=(.025,.025,.055);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);# Primitive UV-sphere polygon iteration is not repeat-stable; canonicalize cycles.
 old_mesh=o.data;verts=[tuple(v.co) for v in old_mesh.vertices];faces=[]
 for poly in old_mesh.polygons:
  f=list(poly.vertices);start=f.index(min(f));faces.append(tuple(f[start:]+f[:start]))
 new_mesh=bpy.data.meshes.new('Deterministic flame');new_mesh.from_pydata(verts,[],sorted(faces));new_mesh.update();o.data=new_mesh;bpy.data.meshes.remove(old_mesh)
 finish(o,name+' luminous flame',ember);o.visible_shadow=False
 light=bpy.data.lights.new('V013 | '+name+' practical warm source','POINT');light.energy=power*a.power_scale;light.color=(1,.58,.25);light.shadow_soft_size=.035;o=bpy.data.objects.new(light.name,light);bpy.context.scene.collection.objects.link(o);o.location=loc;made.append(o.name)
output=Path(a.output).resolve();output.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
Path(a.report).write_text(json.dumps({'version':'v013','source_sha256':sha,'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'new_objects':made,'fixtures':[{'name':n,'location':l,'wall_mount':m,'watts':w*a.power_scale} for n,l,m,w in fixtures],'scope':'Four physical iron wall-lantern fixtures and local warm point sources. Original lights/world/exposure/cameras and all source meshes untouched. Small emissive visible flame mesh has shadow visibility disabled so collocated point source is not artificially occluded; iron cage casts real shadows. No glass or volumetric flame simulation.'},indent=2))
