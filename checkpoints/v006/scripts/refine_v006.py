"""Two short stonework samples on existing facade ribs; no global facade replacement.

Keeps original objects/meshes/materials and replaces only one isolated cuboid component
in each duplicate. Original tilted end surfaces are interpolated, not flattened.
"""
import argparse,array,bmesh,bpy,hashlib,json,os,sys
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=bpy.data.filepath;output=os.path.abspath(a.output)
if os.path.realpath(source)==os.path.realpath(output):raise RuntimeError('Output must differ from input')
bpy.context.preferences.filepaths.use_scripts_auto_execute=False
NAME='REFINEMENT | v006 two short rib stonework samples'
if NAME in bpy.data.collections:
 for obj in list(bpy.data.collections[NAME].objects):
  data=obj.data;bpy.data.objects.remove(obj,do_unlink=True)
  if data.users==0:bpy.data.meshes.remove(data)
 bpy.data.collections.remove(bpy.data.collections[NAME])
for m in list(bpy.data.materials):
 if m.name.startswith('V006 |') and not m.users:bpy.data.materials.remove(m)
col=bpy.data.collections.new(NAME);bpy.context.scene.collection.children.link(col)
FACES=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]

def topo(mesh):
 bm=bmesh.new();bm.from_mesh(mesh);r={'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges)};bm.free();return r

def component_ids(mesh,box):
 lo,hi=box
 candidates={v.index for v in mesh.vertices if all(lo[j]-.005<=v.co[j]<=hi[j]+.005 for j in range(3))}
 adjacency={v.index:set() for v in mesh.vertices}
 for e in mesh.edges:
  x,y=e.vertices;adjacency[x].add(y);adjacency[y].add(x)
 seen=set()
 for seed in sorted(candidates):
  if seed in seen:continue
  queue=[seed];group=set()
  while queue:
   i=queue.pop()
   if i in group:continue
   group.add(i);queue.extend(adjacency[i]-group)
  seen|=group
  if len(group)!=8:continue
  pts=[mesh.vertices[i].co for i in group]
  bounds=([min(v[j] for v in pts) for j in range(3)],[max(v[j] for v in pts) for j in range(3)])
  if all(abs(bounds[k][j]-box[k][j])<.005 for k in [0,1] for j in range(3)):return sorted(group)
 raise RuntimeError('Exact independent eight-vertex rib component not found')

def local_stone(original,tower):
 m=bpy.data.materials[original].copy();m.name='V006 | '+tower+' sampled rib stone without competing fine brick grid'
 t=m.node_tree
 if 'Brick Texture' in t.nodes:
  b=t.nodes['Brick Texture'];mean=tuple((b.inputs['Color1'].default_value[i]+b.inputs['Color2'].default_value[i])*.5 for i in range(4))
  for key in ['Color1','Color2','Mortar']:b.inputs[key].default_value=mean
  b.inputs['Mortar Size'].default_value=0
  t.nodes['Bump'].inputs['Strength'].default_value=0
  t.nodes['Bump.001'].inputs['Strength'].default_value=.08;t.nodes['Bump.001'].inputs['Distance'].default_value=.006
 else:
  t.nodes['Bump'].inputs['Strength'].default_value=.08;t.nodes['Bump'].inputs['Distance'].default_value=.012
 return m

def joint_stone(original,tower):
 src=bpy.data.materials[original];m=bpy.data.materials.new('V006 | '+tower+' lightly recessed joint backing');m.use_nodes=True
 n=m.node_tree.nodes.get('Principled BSDF');rgb=tuple(float(x)*.74 for x in src.diffuse_color[:3]);n.inputs['Base Color'].default_value=(*rgb,1);n.inputs['Roughness'].default_value=.92;n.inputs['Specular IOR Level'].default_value=.2;m.diffuse_color=(*rgb,1);return m

def add_piece(target,coords,mat_index,bevel=0):
 b=bmesh.new();vs=[b.verts.new(p) for p in coords]
 for f in FACES:b.faces.new([vs[i] for i in f])
 bmesh.ops.recalc_face_normals(b,faces=list(b.faces))
 if bevel:bmesh.ops.bevel(b,geom=list(b.edges),offset=bevel,offset_type='OFFSET',segments=1,profile=.5,affect='EDGES',clamp_overlap=True)
 bmesh.ops.recalc_face_normals(b,faces=list(b.faces));b.verts.ensure_lookup_table()
 assert not any(not e.is_manifold for e in b.edges)
 remap={v:target.verts.new(v.co) for v in b.verts}
 for f in b.faces:
  nf=target.faces.new([remap[v] for v in f.verts]);nf.material_index=mat_index;nf.smooth=False
 stats={'vertices':len(b.verts),'faces':len(b.faces),'boundary_edges':0,'nonmanifold_edges':0};b.free();return stats

configs=[
 {'tower':'main','object':'Citadel | carved ivory tracery','box':((44.14,26.5,64.8),(45.06,27.7,180.0)),'cuts':[125.62,127.78,129.94,132.10,134.26,136.42],'bevel':.010,'joint_width':.018,'core_inset':(.028,.035)},
 {'tower':'west','object':'Western citadel_West_Sunlit ivory carved stone','box':((-126.7134,84.575,78.31952),(-125.5266,85.625,167.024)),'cuts':[137.95,139.85,141.75,143.65,145.55,147.45],'bevel':.010,'joint_width':.018,'core_inset':(.028,.035)}
]
checks=[]
for cfg in configs:
 src=bpy.data.objects[cfg['object']]
 assert all(abs(src.matrix_world[i][j]-(1 if i==j else 0))<1e-7 for i in range(4) for j in range(4)), 'Unexpected source transform'
 ids=component_ids(src.data,cfg['box']);pts=[src.data.vertices[i].co.copy() for i in ids];old_faces=[p for p in src.data.polygons if any(i in ids for i in p.vertices)]
 assert len(old_faces)==6 and all(set(p.vertices)<=set(ids) for p in old_faces)
 old_index=old_faces[0].material_index;assert all(p.material_index==old_index for p in old_faces)
 material=src.data.materials[old_index];stone=local_stone(material.name,cfg['tower']);mortar=joint_stone(material.name,cfg['tower'])
 bottom=sorted(pts,key=lambda v:v.z)[:4];top=sorted(pts,key=lambda v:v.z)[4:]
 # Consistent counter-clockwise rings, matching each upper corner in XY to its original lower corner.
 cx=sum(v.x for v in bottom)/4;cy=sum(v.y for v in bottom)/4
 bottom=sorted(bottom,key=lambda v: __import__('math').atan2(v.y-cy,v.x-cx))
 top=[min(top,key=lambda v:(v.x-q.x)**2+(v.y-q.y)**2) for q in bottom]
 z0=sum(v.z for v in bottom)/4;z1=sum(v.z for v in top)/4;H=z1-z0
 def ring(z,inset=(0,0)):
  t=(z-z0)/H;res=[]
  for lo,hi in zip(bottom,top):
   v=lo.lerp(hi,t);v.x+=inset[0] if v.x<cx else -inset[0];v.y+=inset[1] if v.y<cy else -inset[1];res.append(v)
  return res
 def piece(lo,hi,inset=(0,0)):return ring(lo,inset)+ring(hi,inset)
 obj=src.copy();obj.data=src.data.copy();obj.name='V006 | '+cfg['tower']+' facade with one short jointed rib sample';obj.data.name=obj.name+' mesh';col.objects.link(obj);obj.hide_render=False;obj.hide_viewport=False
 obj.data.materials.append(stone);si=len(obj.data.materials)-1;obj.data.materials.append(mortar);mi=len(obj.data.materials)-1
 bm=bmesh.new();bm.from_mesh(obj.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in ids],context='VERTS')
 cuts=cfg['cuts'];pieces=[]
 # Unchanged original rib below/above. End surfaces retain the original tiny tilt.
 pieces.append(add_piece(bm,piece(z0,cuts[0]),old_index));pieces.append(add_piece(bm,piece(cuts[-1],z1),old_index))
 # Full-length inset backing prevents transparent slits and supports all stone courses.
 pieces.append(add_piece(bm,piece(cuts[0]-.01,cuts[-1]+.01,cfg['core_inset']),mi))
 stones=[]
 for i,(lo,hi) in enumerate(zip(cuts[:-1],cuts[1:])):
  a0=lo+(cfg['joint_width']/2 if i else 0);a1=hi-(cfg['joint_width']/2 if i<len(cuts)-2 else 0)
  stats=add_piece(bm,piece(a0,a1),si,cfg['bevel']);stones.append({'nominal_z_bottom':a0,'nominal_z_top':a1,'bevel':cfg['bevel'],**stats})
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();obj.data.update()
 src.hide_render=True;src.hide_viewport=True
 t=topo(obj.data);base_top=topo(src.data);assert t['boundary_edges']==base_top['boundary_edges']==0 and t['nonmanifold_edges']==base_top['nonmanifold_edges']==0
 # Rays at the middle of each visible front joint must hit the inset backing, never the empty far side.
 gaps=[];yfront=min(v.y for v in bottom)
 for z in cuts[1:-1]:
  # Original end tilt remains in all interpolated cuts; sample the front plane's true Z.
  truez=ring(z)[0].z;hit,loc,n,face=obj.ray_cast(Vector((cx,yfront-1,truez)),Vector((0,1,0)))
  assert hit and abs(loc.y-(yfront+cfg['core_inset'][1]))<.0002,(cfg['tower'],z,hit,loc)
  gaps.append({'nominal_z':z,'front_surface_y':yfront,'actual_joint_backing_y':loc.y,'backing_recess':loc.y-yfront,'material_index':obj.data.polygons[face].material_index})
  assert obj.data.polygons[face].material_index==mi
 # At every block middle the outer front remains exactly on the original envelope.
 outer=[]
 for lo,hi in zip(cuts[:-1],cuts[1:]):
  z=(lo+hi)*.5;hit,loc,n,face=obj.ray_cast(Vector((cx,yfront-1,z)),Vector((0,1,0)));assert hit and abs(loc.y-yfront)<.0002
  outer.append({'z':z,'actual_front_y':loc.y})
 checks.append({'tower':cfg['tower'],'source_object':src.name,'replacement_object':obj.name,'source_component_vertices':ids,'source_component_bounds':cfg['box'],'original_material':material.name,'sample_stone_material':stone.name,'joint_backing_material':mortar.name,'sample_nominal_z_range':[cuts[0],cuts[-1]],'original_end_tilt_preserved':True,'stones':stones,'joint_width':cfg['joint_width'],'joint_backing_ray_checks':gaps,'stone_front_envelope_ray_checks':outer,'lower_and_upper_continuations_touch_sample_end_faces':True,'core_overlaps_continuations_each_end':.01,'source_topology':base_top,'replacement_topology':t,'visible_face_increase':t['faces']-base_top['faces']})
s=bpy.context.scene;s['v006_scope']='Two short sample lengths only; genuine bevelled stones and recessed continuous joint backing. Remaining ribs are retained as comparison. No lighting change.';s.render.filepath='//previews/v006_rib_samples.png';s.render.use_stamp=False
for k in ['use_stamp_filename','use_stamp_date','use_stamp_time']:
 if hasattr(s.render,k):setattr(s.render,k,False)
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
report={'version':'v006 two short actual stonework samples','source_filename':os.path.basename(source),'source_sha256':hashlib.sha256(open(source,'rb').read()).hexdigest(),'output_filename':os.path.basename(output),'samples':checks,'new_stone_count':sum(len(q['stones']) for q in checks),'total_visible_face_increase':sum(q['visible_face_increase'] for q in checks),'lights_world_exposure_unchanged':True,'status':'Awaiting actual near/macro render review; not project completion.'}
os.makedirs(os.path.dirname(output),exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=output,compress=True);report['output_sha256']=hashlib.sha256(open(output,'rb').read()).hexdigest()
with open(a.report,'w',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
