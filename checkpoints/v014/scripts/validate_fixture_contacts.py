"""Read-only exact intersection-volume tests for intended lantern joints/mounts."""
import bpy,bmesh,argparse,sys,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();counts=(len(bpy.data.objects),len(bpy.data.meshes));rows=[]
def intersection(left,right):
 ob=left.copy();ob.data=left.data.copy();bpy.context.scene.collection.objects.link(ob);mod=ob.modifiers.new('TEMP exact contact','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=right
 deps=bpy.context.evaluated_depsgraph_get();eo=ob.evaluated_get(deps);mesh=eo.to_mesh();bm=bmesh.new();bm.from_mesh(mesh);vol=abs(bm.calc_volume(signed=True))*abs(ob.matrix_world.determinant());closed=all(e.is_manifold for e in bm.edges);bm.free();eo.to_mesh_clear();data=ob.data;bpy.data.objects.remove(ob,do_unlink=True);bpy.data.meshes.remove(data);return vol,closed
for name in ['entrance','turn','corridor','stair','landing marker']:
 prefix=('V014 | ' if name=='landing marker' else 'V013 | ')+name+' '
 pairs=[('mounting plate','wall arm'),('wall arm','rain hood'),('rain hood','hood rim')]
 pairs += [(f'cage upright {i}',cap) for i in range(4) for cap in ['lower cup','hood rim']]
 for left,right in pairs:
  v,c=intersection(bpy.data.objects[prefix+left],bpy.data.objects[prefix+right]);rows.append({'fixture':name,'parts':[left,right],'intersection_volume':v,'closed':c,'positive_joint':c and v>1e-10})
 wall={'entrance':'hall south stone lining','turn':'hall east stone lining','corridor':'east north corridor stone lining','stair':'east lined stairwell and terrace guard','landing marker':'east lined stairwell and terrace guard'}[name]
 v,c=intersection(bpy.data.objects[prefix+'mounting plate'],bpy.data.objects['V012 | '+wall]);rows.append({'fixture':name,'parts':['mounting plate',wall],'intersection_volume':v,'closed':c,'positive_joint':c and v>1e-10})
r={'model_sha256':sha,'joint_checks':rows,'all_joints_positive_closed_intersections':all(q['positive_joint'] for q in rows),'temporary_data_cleaned':counts==(len(bpy.data.objects),len(bpy.data.meshes)),'source_unchanged':sha==hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'scope':'Intended mesh joint connectivity and plate-to-wall overlap only; not engineering strength certification. Flame/light intentionally suspended visually inside rigid cage.'};Path(a.report).write_text(json.dumps(r,indent=2));print(r);assert r['all_joints_positive_closed_intersections'] and r['temporary_data_cleaned'] and r['source_unchanged']
