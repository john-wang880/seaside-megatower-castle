"""Rebuild two restrained facade sample bays from the sealed v002 checkpoint.
Run Blender with --disable-autoexec. Output must differ from input.
Original objects are retained hidden; the independent v003 collection is replaceable.
No external assets or embedded scripts. Window voids are actual boolean recesses.
"""
import argparse,bpy,bmesh,hashlib,json,math,os,sys
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=os.path.abspath(bpy.data.filepath);output=os.path.abspath(a.output)
if source==output:raise RuntimeError('Never overwrite the loaded checkpoint.')
NAME='REFINEMENT | v003 two facade sample bays';PREFIX='V003 | '
old=bpy.data.collections.get(NAME)
if old:
 for o in list(old.objects):
  data=o.data if o.type=='MESH' else None
  bpy.data.objects.remove(o,do_unlink=True)
  if data and data.users==0:bpy.data.meshes.remove(data)
 bpy.data.collections.remove(old)
c=bpy.data.collections.new(NAME);bpy.context.scene.collection.children.link(c)
M={'wall':bpy.data.materials['Citadel • deep slate ashlar'],'trim':bpy.data.materials['V002 | subdued crown cornice stone'],'body':bpy.data.materials['Citadel • aged gallery grey'],'dark':bpy.data.materials['Citadel • aperture darkness'],'glass':bpy.data.objects['Citadel | muted window panes'].data.materials[0]}

def finish(name,v,f,mats,mi=None):
 me=bpy.data.meshes.new(PREFIX+name);me.from_pydata(v,[],f);me.update()
 for m in mats:me.materials.append(m)
 if mi:
  for p,i in zip(me.polygons,mi):p.material_index=i
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 o=bpy.data.objects.new(PREFIX+name,me);c.objects.link(o);o['refinement_version']='v003';return o

class Batch:
 def __init__(self,name):self.name=name;self.v=[];self.f=[];self.mats=[];self.mi=[]
 def add(self,v,f,mat):
  if mat not in self.mats:self.mats.append(mat)
  off=len(self.v);self.v.extend([tuple(p) for p in v]);self.f.extend([tuple(i+off for i in p) for p in f]);self.mi.extend([self.mats.index(mat)]*len(f))
 def box(self,x,y,z,w,d,h,mat):
  a,b,e=w/2,d/2,h/2;v=[(x-a,y-b,z-e),(x+a,y-b,z-e),(x+a,y+b,z-e),(x-a,y+b,z-e),(x-a,y-b,z+e),(x+a,y-b,z+e),(x+a,y+b,z+e),(x-a,y+b,z+e)]
  self.add(v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
 def polygon(self,poly,x,y0,y1,mat):
  n=len(poly);v=[(x+u,y,z) for y in [y0,y1] for u,z in poly];f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];self.add(v,f,mat)
 def ring(self,outer,inner,x,y0,y1,mat):
  n=len(outer);assert n==len(inner)
  v=[(x+u,y,z) for y in [y0,y1] for loop in [outer,inner] for u,z in loop];f=[]
  for i in range(n):
   j=(i+1)%n;f.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
  self.add(v,f,mat)
 def reveal(self,outer,inner,x,y0,y1,mat):
  n=len(outer)
  def expand(loop):
   cz=sum(z for u,z in loop)/len(loop)
   return [(u+(.045 if u>0 else -.045 if u<0 else 0),z+(.045 if z>cz else -.045)) for u,z in loop]
  # A very thin closed lining, not an open single-sided ribbon.
  v=[(x+u,y,z) for y,loop in [(y0,outer),(y0,expand(outer)),(y1,inner),(y1,expand(inner))] for u,z in loop];f=[]
  for i in range(n):
   j=(i+1)%n;f.extend([(i,j,2*n+j,2*n+i),(n+i,3*n+i,3*n+j,n+j),(i,n+i,n+j,j),(2*n+i,2*n+j,3*n+j,3*n+i)])
  self.add(v,f,mat)
 def finish(self):return finish(self.name,self.v,self.f,self.mats,self.mi)

def arch(width,bottom,shoulder,apex,steps=10):
 h=width/2;r=apex-shoulder
 left=[(h+width*math.cos(math.pi-i/steps*math.pi/3),shoulder+r*math.sin(math.pi-i/steps*math.pi/3)/(math.sqrt(3)/2)) for i in range(steps+1)]
 return [(-h,bottom)]+left+[(-x,z) for x,z in left[-2::-1]]+[(h,bottom)]

def topology(o):
 bm=bmesh.new();bm.from_mesh(o.data);r={'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges)};bm.free();return r

def duplicate(n,label):
 src=bpy.data.objects[n];src.hide_render=False;src.hide_viewport=False
 o=bpy.data.objects.new(PREFIX+label,src.data.copy());o.data.name=PREFIX+label+' mesh';o.matrix_world=src.matrix_world.copy();c.objects.link(o);o['source_object']=n
 src.hide_render=True;src.hide_viewport=True;return src,o

main_src,main=duplicate('Citadel | monumental shadowed tower','main shaft with four genuine recessed lancets')
west_src,west=duplicate('Western citadel_West_Ancient monolith','western monolith with four genuine recessed lancets')
recess_src,recess=duplicate('Western citadel_West_Deep architectural recess','western existing recesses opened at sample windows')

windows=[]
for x in [32.5,38.1]:
 for b,sh,ap in [(129.4,135.7,138.3),(143.2,150.1,152.7)]:windows.append(dict(tower='main',x=x,width=3.55,bottom=b,shoulder=sh,apex=ap,front=28.8,back=31.05))
for x in [-137.0,-128.9]:
 for b,sh,ap in [(108.2,114.4,116.8),(122.4,128.8,131.2)]:windows.append(dict(tower='west',x=x,width=3.0,bottom=b,shoulder=sh,apex=ap,front=86.0,back=88.2))

for tower,targets in [('main',[main]),('west',[west,recess])]:
 cut=Batch(tower+' temporary cutters')
 for w in windows:
  if w['tower']!=tower:continue
  cut.polygon(arch(w['width'],w['bottom'],w['shoulder'],w['apex']),w['x'],w['front']-2.0,w['back'],M['wall'])
 cutter=cut.finish()
 for obj in targets:
  bpy.context.view_layer.objects.active=obj;obj.select_set(True)
  mod=obj.modifiers.new('True deep lancet voids','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
  bpy.ops.object.modifier_apply(modifier=mod.name);obj.select_set(False)
 cutter_mesh=cutter.data;bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.meshes.remove(cutter_mesh)

stone=Batch('two facade samples stone reveals and restrained frames')
tracery=Batch('two facade samples recessed mullions and tracery')
glass=Batch('two facade samples deep muted glazing')
structure=Batch('two facade samples secondary structural divisions')
for w in windows:
 x,fw,b,sh,ap,y,back=(w[k] for k in ['x','width','bottom','shoulder','apex','front','back'])
 # Opening is cut behind the original facade. The inner throat tapers to emphasize real wall thickness.
 outer=arch(fw,b,sh,ap);inner=arch(fw-.40,b+.18,sh-.12,ap-.25)
 stone.reveal(outer,inner,x,y-.015,back-.20,M['body'])
 # Narrow masonry surround, rather than another massive facade frame.
 frame_outer=arch(fw+.66,b-.28,sh,ap+.44)
 stone.ring(frame_outer,outer,x,y-.48,y+.05,M['trim'])
 # A separate internal roll sits about 1.6 units behind the outer face.
 inside=arch(fw-.58,b+.26,sh-.17,ap-.40)
 tracery.ring(inner,inside,x,back-.46,back-.22,M['body'])
 glass.polygon(inner,x,back-.12,back-.045,M['glass'])
 iw=fw-.64;center_bottom=b+.30;small_sh=sh-.75;small_ap=ap-1.05
 # Two subordinate lancets and a central stone mullion, recessed behind the main arch.
 for dx in [-iw/4,iw/4]:
  sw=iw/2-.10
  out=arch(sw,center_bottom,small_sh,small_ap);inn=arch(sw-.16,center_bottom+.08,small_sh,small_ap-.13)
  tracery.ring(out,inn,x+dx,back-.60,back-.34,M['body'])
 tracery.box(x,back-.49,(center_bottom+small_sh)/2,.18,.30,small_sh-center_bottom,M['trim'])
 # A single low crossbar supports glazing panes; restrained visible human-scale detail.
 tracery.box(x,back-.48,b+3.1,iw,.19,.12,M['body'])
 # Two-tier sloping sill and its small supporting shoulders.
 structure.box(x,y-.35,b-.42,fw+.9,1.02,.28,M['trim'])
 structure.box(x,y-.08,b-.68,fw+.52,.58,.22,M['body'])
 for dx in [-fw/2+.18,fw/2-.18]:structure.box(x+dx,y-.10,b-.92,.38,.54,.35,M['body'])

# Secondary rhythm is inset behind the existing tall primary ribs. Broad wall fields remain.
rib_specs=[('main',35.3,28.55,124.45,162.78,141.05,12.1),('west',-132.95,85.78,104.65,136.65,120.1,13.4)]
for tower,x,y,z0,z1,belt,width in rib_specs:
 structure.box(x,y,(z0+z1)/2,.36,.52,z1-z0,M['body'])
 structure.box(x,y-.05,belt,width,.67,.33,M['body'])
 structure.box(x,y-.17,belt+.20,width+.18,.82,.12,M['trim'])

rib_contact_checks=[]
for tower,x,y,z0,z1,belt,width in rib_specs:
 obj=main if tower=='main' else bpy.data.objects['Western citadel_West_Sunlit ivory carved stone']
 for end,z,d in [('lower',z0,-1),('upper',z1,1)]:
  hit,loc,normal,index=obj.ray_cast(Vector((x,y,z-d)),Vector((0,0,d)))
  overlap=(loc.z-z) if d<0 else (z-loc.z)
  if not hit or overlap<=0:raise RuntimeError('Secondary rib does not meet actual cornice geometry.')
  rib_contact_checks.append({'tower':tower,'end':end,'rib_endpoint_z':z,'actual_cornice_surface_z':round(loc.z,5),'embedded_contact_depth':round(overlap,5)})
added=[stone.finish(),tracery.finish(),glass.finish(),structure.finish()]
for obj in [main,west,recess]:
 bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()

# Evidence: ray casts through window centers must hit their actual recessed backing walls.
void_checks=[]
for w in windows:
 o=main if w['tower']=='main' else west
 origin=Vector((w['x'],w['front']-4,w['bottom']+3.8));hit,loc,normal,index=o.ray_cast(origin,Vector((0,1,0)))
 depth=(loc.y-w['front']) if hit else None
 if not hit or abs(depth-(w['back']-w['front']))>.02:raise RuntimeError('Window void failed actual-depth check: '+str(w))
 void_checks.append({'tower':w['tower'],'x':w['x'],'bottom':w['bottom'],'actual_wall_recess_depth':round(depth,3),'backing_wall_hit':True})

s=bpy.context.scene;s['v003_scope']='Two facade sample bands only; true recessed lancets and subordinate divisions. No lighting, height or silhouette changes.'
s.render.filepath='//previews/v003_two_sample_bays.png';s.render.use_stamp=False
for key in ['use_stamp_filename','use_stamp_date','use_stamp_time']:
 if hasattr(s.render,key):setattr(s.render,key,False)
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
os.makedirs(os.path.dirname(output),exist_ok=True)
report={'version':'v003 sample pass','source_filename':os.path.basename(source),'source_sha256':hashlib.sha256(open(source,'rb').read()).hexdigest(),'output_filename':os.path.basename(output),'scope':'Main front central panel z124.45–162.78; west front middle band z104.65–136.65; no expansion yet','visual_revision':'Secondary ribs extended into existing floor cornices, with isolated end caps removed after actual preview critique','window_count':len(windows),'windows':windows,'true_void_ray_checks':void_checks,'secondary_rib_actual_surface_contact_checks':rib_contact_checks,'source_objects_retained_hidden':[main_src.name,west_src.name,recess_src.name],'replacement_meshes':{o.name:topology(o) for o in [main,west,recess]},'added_objects':{o.name:topology(o) for o in added},'lighting_world_exposure_changed':False,'tower_heights_and_outer_primary_ribs_changed':False,'images':len(bpy.data.images),'libraries':len(bpy.data.libraries),'texts':len(bpy.data.texts),'autoexec_enabled':bpy.context.preferences.filepaths.use_scripts_auto_execute,'status':'Sample geometry awaiting same-camera visual review; not whole-tower completion.'}
bpy.ops.wm.save_as_mainfile(filepath=output,compress=True);report['output_sha256']=hashlib.sha256(open(output,'rb').read()).hexdigest()
with open(a.report,'w',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
