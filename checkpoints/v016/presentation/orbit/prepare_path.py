import bpy,json,hashlib,math,itertools
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
root=Path('work/orbit_v016');source=Path(bpy.data.filepath);sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha=='d44a4cdecd11dab152fd656c624755369e575a0f342e2eb0bc2460475c6f65eb'
s=bpy.context.scene;s.render.resolution_x=640;s.render.resolution_y=462;s.render.resolution_percentage=100
skip=['cloud','air perspective','forest','woodland','meadow','grass','wildflower','traveler','footpath','limestone chips','surf','foam','ocean','headland','sea stack','coastal rock']
deps=bpy.context.evaluated_depsgraph_get();groups={'main_architecture':[],'offshore_architecture':[],'coastal_rock':[]};names=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render:continue
 name=o.name.lower();coast=name.startswith('v008 | coastal rock')
 if not coast and any(x in name for x in skip):continue
 e=o.evaluated_get(deps);mesh=e.to_mesh()
 for v in mesh.vertices:
  p=e.matrix_world@v.co
  group='coastal_rock' if coast else ('offshore_architecture' if p.x>100 and p.y>170 else 'main_architecture')
  groups[group].append(p.copy())
 names.append(o.name);e.to_mesh_clear()
bounds={};corners={}
for key,ps in groups.items():
 assert ps,key
 lo=[min(p[i] for p in ps) for i in range(3)];hi=[max(p[i] for p in ps) for i in range(3)]
 bounds[key]={'min':lo,'max':hi,'evaluated_vertex_count':len(ps)}
 corners[key]=[Vector(p) for p in itertools.product(*zip(lo,hi))]
c=bpy.data.objects.new('Orbit feasibility',bpy.data.cameras.new('Orbit feasibility'));s.collection.objects.link(c);s.camera=c;c.data.lens=40;c.data.clip_start=.05;c.data.clip_end=3000
target=Vector((-35,35,85));radius=580
for trial in range(20):
 frames=[];ok=True
 for i in range(96):
  t=i/95;u=t*t*(3-2*t);theta=math.radians(-93+40*u);loc=Vector((target.x+radius*math.cos(theta),target.y+radius*math.sin(theta),45))
  c.location=loc;c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();projection={}
  for key,ps in corners.items():
   q=[world_to_camera_view(s,c,p) for p in ps];margin=.055 if key=='main_architecture' else .025
   fit=all(p.z>0 and margin<=p.x<=1-margin and margin<=p.y<=1-margin for p in q);ok=ok and fit
   projection[key]={'bounds_xy':[[min(p[j] for p in q),max(p[j] for p in q)] for j in (0,1)],'minimum_margin_required':margin,'fits':fit}
  frames.append({'frame':i+1,'seconds':i/12,'location':list(loc),'target':list(target),'lens':40,'clip_start':.05,'clip_end':3000,'projection':projection})
 if ok:break
 radius*=1.05
assert ok,'Could not fit conservative asset bounds'
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
(root/'path_plan.json').write_text(json.dumps({'source_sha256':sha,'kind':'40 degree front-facing partial exterior arc, not 360 orbit','fps':12,'frame_count':96,'duration_seconds':8,'camera_radius':radius,'target':list(target),'camera_z':45,'angle_degrees':[-93,-53],'motion':'smoothstep angle; real Blender camera position each frame','bounds':bounds,'selected_objects':names,'proof':'Conservative AABB corners of evaluated selected geometry at all96 planned camera positions; projection fit does not prove occlusion-free rays. Sea/forest/background extent excluded.','frames':frames,'source_saved':False},indent=2))
indices=[0,24,48,71,95];views={f'key_{i+1:03d}':{k:v for k,v in frames[i].items() if k in ('location','target','lens','clip_start','clip_end')} for i in indices}
(root/'keyframes.json').write_text(json.dumps({'source_sha256':sha,'views':views},indent=2));print(json.dumps({'radius':radius,'bounds':bounds,'frames':96,'all_fit':ok}))
