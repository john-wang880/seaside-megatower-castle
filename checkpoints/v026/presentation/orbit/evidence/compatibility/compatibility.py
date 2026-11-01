import bpy,json,hashlib,sys,itertools,collections
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path('work/orbit_v026');hist=P/'historical/checkpoints/v016/presentation/orbit';src=Path('work/v026/castle_v026.blend');sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();H=sha(src);assert H=='efcd894acdc045a30f845f05267662957b656bc7fe0ee4cf48c05fc798b610ee';plan=json.loads((hist/'final_plan.json').read_text());oldpath=json.loads((hist/'path_plan.json').read_text());assert len(plan['frames'])==96
sys.path.insert(0,str(Path('work/v023_path_conformance/scripts').resolve()));from deep_snapshot import primitive,tree_snapshot,digest

def lightstate():
 s=bpy.context.scene
 return {'world':{'name':s.world.name,'properties':primitive(s.world),'nodes':tree_snapshot(s.world.node_tree)},'lights':{o.name:{'object':primitive(o),'matrix':[list(r)for r in o.matrix_world],'data':primitive(o.data),'nodes':tree_snapshot(o.data.node_tree)if o.data.use_nodes else None}for o in s.objects if o.type=='LIGHT'}}
def props(o):
 d={}
 for p in o.bl_rna.properties:
  if p.identifier!='rna_type'and p.type in{'BOOLEAN','INT','FLOAT','STRING','ENUM'}:
   v=getattr(o,p.identifier);d[p.identifier]=list(v)if getattr(p,'is_array',False)else sorted(v)if isinstance(v,set)else v
 return d
bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);s=bpy.context.scene;lighting=lightstate();actualcycles=props(s.cycles);actualview=props(s.view_settings);dg=bpy.context.evaluated_depsgraph_get();skip=['cloud','air perspective','forest','woodland','meadow','grass','wildflower','traveler','footpath','limestone chips','surf','foam','ocean','headland','sea stack','coastal rock','conifer'];groups={k:[]for k in['main_architecture','offshore_architecture','coastal_rock']};names=[]
for o in s.objects:
 if o.type!='MESH'or o.hide_render:continue
 name=o.name.lower();coast=name.startswith('v008 | coastal rock')
 if not coast and any(x in name for x in skip):continue
 eo=o.evaluated_get(dg);me=eo.to_mesh()
 for v in me.vertices:
  q=eo.matrix_world@v.co;k='coastal_rock'if coast else'offshore_architecture'if q.x>100 and q.y>170 else'main_architecture';groups[k].append(q.copy())
 names.append(o.name);eo.to_mesh_clear()
bounds={};corners={}
for k,vs in groups.items():
 lo=[min(v[i]for v in vs)for i in range(3)];hi=[max(v[i]for v in vs)for i in range(3)];bounds[k]={'min':lo,'max':hi,'evaluated_vertex_count':len(vs)};corners[k]=[Vector(v)for v in itertools.product(*zip(lo,hi))]
c=bpy.data.objects.new('READONLY original orbit camera',bpy.data.cameras.new('READONLY original orbit camera'));s.collection.objects.link(c);s.camera=c;s.render.resolution_x=960;s.render.resolution_y=694;s.render.resolution_percentage=100
vols=set()
for o in s.objects:
 if o.type=='MESH':
  mats=[x.material for x in o.material_slots if x.material]
  if mats and all(m.use_nodes and any(n.type=='OUTPUT_MATERIAL'and n.is_active_output and n.inputs['Volume'].is_linked and not n.inputs['Surface'].is_linked for n in m.node_tree.nodes)for m in mats):vols.add(o.name)
def ray(origin,target):
 d=(target-origin).normalized();a=origin.copy()
 for _ in range(40):
  ok,q,n,fi,o,_=s.ray_cast(dg,a,d)
  if not ok:return None
  if not o.hide_render and o.name not in vols:return {'object':o.name,'face':fi,'position':list(q),'distance_to_target':(q-target).length,'before_target':(q-origin).length<(target-origin).length-.01}
  a=q+d*.001
 return None
frames=[];points={'main crown front':(35,33.8,185),'bridge central pier':(-40,34.8,20),'west entrance':(-71.4,38,29),'near conifer crown context':(-82,42,30),'offshore marker':(116,190,10)}
for i,f in enumerate(plan['frames']):
 r=f['recipe'];assert all(r[k]==oldpath['frames'][i][k]for k in['location','target','lens','clip_start','clip_end']);c.location=r['location'];c.rotation_euler=(Vector(r['target'])-c.location).to_track_quat('-Z','Y').to_euler()
 for k in ['lens','clip_start','clip_end']:setattr(c.data,k,r[k])
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();projection={}
 for k,vs in corners.items():
  ps=[world_to_camera_view(s,c,q)for q in vs];m=.055 if k=='main_architecture'else.025;projection[k]={'bounds_xy':[[min(q[j]for q in ps),max(q[j]for q in ps)]for j in[0,1]],'margin':m,'fits':all(q.z>0 and m<=q.x<=1-m and m<=q.y<=1-m for q in ps)}
 samples={}
 if f['index']in[1,25,49,72,96]:
  for label,point in points.items():
   q=Vector(point);samples[label]={'target':point,'projection':list(world_to_camera_view(s,c,q)),'first_opaque_hit':ray(c.location,q)}
 frames.append({'index':f['index'],'projection':projection,'finite_target_sightlines':samples})
# Match exact historical effective setting mutations without rendering.
s.render.threads_mode='FIXED';s.render.threads=8;s.render.filepath='UNUSED';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.render.image_settings.compression=15;s.render.use_stamp=False
rend=props(s.render);rend.pop('filepath');checks={'cycles_exact':actualcycles==plan['expected_cycles'],'view_exposure_exact':actualview==plan['expected_view_settings'],'effective_render_except_filepath_exact':rend==plan['expected_render_except_filepath'],'image_settings_exact':props(s.render.image_settings)==plan['expected_image_settings'],'blender_version_exact':bpy.app.version_string==plan['expected_blender_version'],'frame_exact':s.frame_current==plan['source_scene_frame']}
diffs={k:{'current':v,'old':plan['expected_render_except_filepath'].get(k)}for k,v in rend.items()if v!=plan['expected_render_except_filepath'].get(k)}
# Historical recipe binds only world name, not complete light graphs. Compare actual unchanged local v016 baseline as additional explicit evidence.
old=Path('work/v016/castle_v016.blend');oldhash=sha(old);assert oldhash==plan['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(old.resolve()),use_scripts=False);older=lightstate();checks['world_actual_v016_exact']=lighting['world']==older['world'];checks['lights_actual_v016_exact']=lighting['lights']==older['lights'];assert sha(old)==oldhash and sha(src)==H
report={'source_sha256':H,'source_unchanged':True,'old_baseline_sha256':oldhash,'inputs':{str(hist/'final_plan.json'):sha(hist/'final_plan.json'),str(hist/'path_plan.json'):sha(hist/'path_plan.json')},'settings_checks':checks,'render_differences':diffs,'world_light_state_sha256':{'current':digest(lighting),'historical_v016':digest(older)},'bounds':bounds,'selected_objects':names,'all96_framing_pass':all(p['fits']for f in frames for p in f['projection'].values()),'frames':frames,'recommended_single_render_index':49,'limits':'Conservative evaluated selected architectural/coastal-rock/offshore AABB fit, not entire sea/terrain/forest extent. 25 finite target rays at5 original frames, not exhaustive pixel occlusion proof. Conifer additions excluded from architecture bounds; target center hit is context not exact foliage surface certification. Volume containers skipped only for opaque classification; original clouds unchanged. No radius search, pose/quality change, render or model save.'};(P/'compatibility.json').write_text(json.dumps(report,indent=2));new=json.loads(json.dumps(plan));new['source_sha256']=H;(P/'proposed_final_plan.json').write_text(json.dumps(new,indent=2)+'\n');print('CHECKS',checks,'FRAMEPASS',report['all96_framing_pass'],'DIFF',diffs)
