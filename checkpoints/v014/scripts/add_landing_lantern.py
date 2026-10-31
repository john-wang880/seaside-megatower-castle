import bpy,argparse,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True);p.add_argument('--power',type=float,default=26);p.add_argument('--y',type=float,default=54.8);p.add_argument('--z',type=float,default=33.1);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath);sha=hashlib.sha256(source.read_bytes()).hexdigest();assert not any(o.name.startswith('V014 |') for o in bpy.data.objects)
y,z=a.y,a.z;shift=Vector((0,y-49.4,z-32.08));original=[o for o in bpy.data.objects if o.name.startswith('V013 | stair ')];assert len(original)==11
wall=bpy.data.objects['V012 | east lined stairwell and terrace guard'];eo=wall.evaluated_get(bpy.context.evaluated_depsgraph_get());inv=eo.matrix_world.inverted();contacts=[]
for probe_z in [z-.15,z,z+.15]:
 h,v,n,i=eo.ray_cast(inv@Vector((5.2,y,probe_z)),(inv.to_3x3()@Vector((1,0,0))).normalized(),distance=.3);assert h;point=eo.matrix_world@v;assert abs(point.x-5.4)<1e-5;contacts.append(list(point))
new=[]
for original_ob in original:
 ob=original_ob.copy();ob.name=original_ob.name.replace('V013 | stair ','V014 | landing marker ')
 if ob.type=='LIGHT':ob.data=original_ob.data.copy();ob.data.name='V014 | low-power landing practical';ob.data.energy=a.power
 bpy.context.scene.collection.objects.link(ob);ob.location+=shift
 new.append({'name':ob.name,'type':ob.type,'data':ob.data.name,'shared_mesh_data_with_source':ob.type=='MESH' and ob.data==original_ob.data})
path=Path(a.output).resolve();bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
Path(a.report).write_text(json.dumps({'source_sha256':sha,'model_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'new_objects':new,'light_power':a.power,'fixture_center':[5.21,y,z],'mount_wall_surface_probes':contacts,'original_4_lamps_unchanged':True,'new_mesh_datablocks':0,'scope':'One low guard-mounted warm landing marker. Ten new mesh instances share existing lantern mesh data; one independent point light. Original four fixtures/powers and environment unchanged.'},indent=2))
