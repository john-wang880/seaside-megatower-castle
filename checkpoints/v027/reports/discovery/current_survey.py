import bpy,json,hashlib,collections
from pathlib import Path
from mathutils import Vector
P=Path('work/interior_ceiling_v026');src=Path('work/v026/castle_v026.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();H=sha(src);assert H=='efcd894acdc045a30f845f05267662957b656bc7fe0ee4cf48c05fc798b610ee';bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();objects=[];geo={}
for o in s.objects:
 if not(o.name.startswith(('V012 | hall ','V012 | entrance hall','V012 | north corridor','V012 | west north corridor','V012 | east north corridor','V013 |','V014 |','V015 |'))or o.name in['V012 | south outward-open timber leaf','V012 | north outward-open timber leaf']or'open-leaf iron strap'in o.name):continue
 r={'name':o.name,'type':o.type,'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'matrix':[list(v)for v in o.matrix_world],'modifiers':[(m.name,m.type)for m in o.modifiers]}
 if o.type=='MESH':
  eo=o.evaluated_get(dg);me=eo.to_mesh();vs=[eo.matrix_world@v.co for v in me.vertices];edges=collections.Counter(tuple(sorted(e))for f in me.polygons for e in f.edge_keys);r.update(bounds=[[min(v[k]for v in vs)for k in range(3)],[max(v[k]for v in vs)for k in range(3)]],vertices=len(vs),polygons=len(me.polygons),mesh_users=o.data.users,material_slots=[{'link':m.link,'material':m.material.name if m.material else None}for m in o.material_slots],edge_usage=dict(collections.Counter(edges.values())));geo[o.name]={'vertices':[list(v)for v in vs],'faces':[list(f.vertices)for f in me.polygons]};eo.to_mesh_clear()
 elif o.type=='LIGHT':r.update(location=list(o.matrix_world.translation),energy=o.data.energy,color=list(o.data.color),light_type=o.data.type)
 objects.append(r)
def ray(origin,direction,distance):
 ok,p,n,f,o,_=s.ray_cast(dg,Vector(origin),Vector(direction),distance=distance)
 return {'object':o.name,'face':f,'point':list(p),'normal':list(n)}if ok else None
samples=[]
for x in[-2.5,-1.8,0,.4,2.6,3.2,4.45]:
 for y in[36.65,37.4,38,38.6,39.35]:
  floor=ray((x,y,29.1),(0,0,-1),.2);ceil=ray((x,y,31.11),(0,0,1),2);samples.append({'xy':[x,y],'floor':floor,'ceiling':ceil,'headroom':ceil['point'][2]-floor['point'][2]if ceil and floor else None})
# Candidate bounding envelopes only, no mesh: three ribs plus high sidebands.
envelopes=[{'label':'rib'+str(i),'bounds':[[x-.14,36.56,32.5],[x+.14,39.44,32.82]]}for i,x in enumerate([-1.8,.4,2.6])]+[{'label':'south high band','bounds':[[-2.5,36.56,32.2],[3.2,36.72,32.5]]},{'label':'north high band','bounds':[[-2.5,39.28,32.2],[3.2,39.44,32.5]]}]
def gap(a,b):return sum(max(a[0][k]-b[1][k],b[0][k]-a[1][k],0)**2 for k in range(3))**.5
conflicts=[]
for e in envelopes:
 for r in objects:
  if r['type']=='MESH' and r['name'].startswith(('V013 |','V014 |','V015 |'))or r['type']=='MESH'and('timber leaf'in r['name']or'open-leaf'in r['name']):conflicts.append({'envelope':e['label'],'object':r['name'],'AABB_separation_lower_bound':gap(e['bounds'],r['bounds'])})
plan=json.loads(Path('checkpoints/v018/presentation/interior_route/final_plan.json').read_text());views={}
for idx in[1,76]:
 r=plan['frames'][idx-1]['recipe'];c=bpy.data.objects.new('READONLY firsthall'+str(idx),bpy.data.cameras.new('READONLY firsthall'+str(idx)));s.collection.objects.link(c);c.location=r['location'];c.rotation_euler=(Vector(r['target'])-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=r['lens'];c.data.sensor_width=plan['sensor_width_mm'];c.data.sensor_fit=plan['sensor_fit'];c.data.clip_start=r['clip_start'];c.data.clip_end=r['clip_end'];bpy.context.view_layer.update();views['frame_'+str(idx).zfill(4)]={**r,'reference_matrix':[list(v)for v in c.matrix_world],'camera_data':{k:getattr(c.data,k)for k in['lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','clip_start','clip_end']}}
report={'source_sha256':H,'source_unchanged':sha(src)==H,'objects':objects,'geometry':geo,'hall_floor_ceiling_probes':samples,'review_envelopes_not_geometry':envelopes,'fixture_door_separations':conflicts,'body_prism':{'floor_z':29,'top_z':31.1,'width_y':[37.4,38.6],'hall_x':[-3.5,4.45],'note':'Historical accepted2.1unit bodyprism, not global2.4measurement or entirevolume recertification'},'limits':'Read-only actual evaluated geometry/finite rays/AABB review envelopes. ZeroAABBdistance is not provenintersection; no candidate, rendering, supportengineering or allroute certification.'};(P/'current_survey.json').write_text(json.dumps(report,indent=2));(P/'views.json').write_text(json.dumps({'source_sha256':H,'source_scene_frame':s.frame_current,'resolution':plan['resolution'],'samples':80,'threads':8,'views':views,'scope':'Exact historical frame1/76 camera poses on current source, not yet rendered'},indent=2));print('DONE',len(objects),min(x['headroom']for x in samples if x['headroom'] is not None),min(x['AABB_separation_lower_bound']for x in conflicts))
