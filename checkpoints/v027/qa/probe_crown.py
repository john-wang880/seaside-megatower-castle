import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector,Matrix
sys.dont_write_bytecode=True
import argparse
p=argparse.ArgumentParser()
for k in ['candidate','candidate-sha','receipt','pixels','seating-report','report']:p.add_argument('--'+k,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(a.candidate).resolve();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(source);assert before==a.candidate_sha;assert not Path(a.report).exists()
receiptpath=Path(a.receipt);receipt=json.loads(receiptpath.read_text());pixels=json.loads(Path(a.pixels).read_text());assert pixels['image_sha256']==receipt['image_sha256'];assert receipt['source_sha256_before']==receipt['source_sha256_after']=='37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255'
cam=receipt['settings']['camera'];m=Matrix(cam['matrix_world']);origin=m.translation;w,h=pixels['resolution'];bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();lights=[o for o in bpy.data.objects if o.type=='LIGHT'and not o.hide_render];hidden_render_only=[o.name for o in bpy.data.objects if o.hide_render and o.visible_get()];assert not hidden_render_only,hidden_render_only

def cast(start,direction,distance=100):
 hit,p,n,face,o,matrix=scene.ray_cast(deps,start,direction,distance=distance)
 if not hit:return {'hit':False}
 eo=o.evaluated_get(deps);material=eo.material_slots[eo.data.polygons[face].material_index].material if eo.type=='MESH'and face<len(eo.data.polygons)else None
 return {'hit':True,'object':o.name,'point':list(p),'normal':list(n),'face':face,'distance':(p-start).length,'material':material.name if material else None}
rows=[]
for row in pixels['samples']:
 x,y=row['pixel'];u=2*(x+.5)/w-1;v=1-2*(y+.5)/h;d=(m.to_3x3()@Vector([u*cam['data']['sensor_width']/(2*cam['data']['lens']),v*cam['data']['sensor_width']/(2*cam['data']['lens'])*h/w,-1])).normalized();hit=cast(origin,d);result={**row,'ray_direction':list(d),'first_hit':hit}
 if hit['hit']:
  p=Vector(hit['point']);n=Vector(hit['normal']);shadow=[]
  for light in lights:
   delta=light.matrix_world.translation-p
   if delta.length>30:continue
   start=p+n*.0001;ld=light.matrix_world.translation-start;oc=cast(start,ld.normalized(),max(0,ld.length-.001));shadow.append({'light':light.name,'light_type':light.data.type,'distance':ld.length,'toward_light_first_hit':oc})
  result['nearby_light_center_visibility']=shadow
  if hit['object']=='V012 | entrance hall ceiling lining':result['down_from_ceiling']=cast(p+Vector([0,0,-.0001]),Vector([0,0,-1]),1.0)
 rows.append(result)
# Original actual crown seating geometry, not image black-pixel inference.
seat=json.loads(Path(a.seating_report).read_text());crowns=[x for x in seat['witnesses']if x['label'].endswith(' crown')];assert len(crowns)==3 and all(x['pass']for x in crowns);assert sha(source)==before
out={'pass_all_pixels_hit_geometry':all(x['first_hit']['hit']for x in rows),'pass':all(x['first_hit']['hit']for x in rows),'source_sha256':before,'archived_actual_image_source_sha256':receipt['source_sha256_before'],'receipt_sha256':sha(receiptpath),'image_sha256':pixels['image_sha256'],'camera':cam,'rays':rows,'crowns':crowns,'source_unchanged':True,'rendered':False,'saved':False,'scope':'Finite exact camera pixel-center geometry rays and nearby-light center visibility. Cycles area-light sampling, indirect illumination, material microtexture, denoising and antialiasing are not reproduced; this is not a radiometric causal decomposition. Actual surface hits distinguish solid/haunch views from missing roof; independent seating/coplanar proofs remain necessary.'};Path(a.report).write_text(json.dumps(out,indent=2));print('RAYS',len(rows),out['pass_all_pixels_hit_geometry'])
