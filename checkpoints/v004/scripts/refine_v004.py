"""Rebuild selective front and side fenestration from the sealed v003 checkpoint.
Run Blender with --disable-autoexec. Output must differ from input.
Original objects are retained hidden; the independent v004 collection is replaceable.
No external assets or embedded scripts. Window voids are actual boolean recesses.
"""
import argparse,bpy,bmesh,hashlib,json,math,os,sys
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=os.path.abspath(bpy.data.filepath);output=os.path.abspath(a.output)
if source==output:raise RuntimeError('Never overwrite the loaded checkpoint.')
NAME='REFINEMENT | v004 varied tower fenestration';PREFIX='V004 | '
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
 o=bpy.data.objects.new(PREFIX+name,me);c.objects.link(o);o['refinement_version']='v004';return o

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


class BasisBatch(Batch):
 def __init__(self,name):super().__init__(name);self.basis=None
 def add(self,v,f,mat):
  if self.basis:
   origin,u,inward=self.basis
   v=[origin+u*x+inward*d+Vector((0,0,z)) for x,d,z in v]
  super().add(v,f,mat)

def face_basis(w):
 if w['face']=='front':return Vector((0,w['plane'],0)),Vector((1,0,0)),Vector((0,1,0))
 return Vector((w['plane'],0,0)),Vector((0,1,0)),Vector((-1,0,0))

main_src,main=duplicate('V003 | main shaft with four genuine recessed lancets','main shaft selective front and east-facing windows')
west_src,west=duplicate('V003 | western monolith with four genuine recessed lancets','west shaft selective front and east-facing windows')
recess_src,recess=duplicate('V003 | western existing recesses opened at sample windows','west old recess strips opened for selected upper and lower windows')
windows=[]
def window(tower,face,x,width,bottom,shoulder,apex,plane,depth,group):
 windows.append(dict(tower=tower,face=face,x=x,width=width,bottom=bottom,shoulder=shoulder,apex=apex,plane=plane,front=0,back=depth,group=group))
for x in [32.5,38.1]:
 for b,sh,ap in [(90.8,97.2,99.8),(106.3,113.1,115.7)]:window('main','front',x,3.55,b,sh,ap,28.8,2.25,'lower two-tier group')
 window('main','front',x,3.30,166.0,172.0,174.5,28.8,2.25,'single pair below crown')
for b,sh,ap in [(129.4,135.7,138.3),(143.2,150.1,152.7)]:window('main','east',44.0,3.60,b,sh,ap,53.05,2.25,'one sparse east-side column')
for x in [-137.0,-128.9]:
 window('west','front',x,2.80,85.8,92.0,94.5,86.0,2.20,'single lower pair')
 window('west','front',x,2.90,147.0,153.3,155.8,86.0,2.20,'single upper pair')
for b,sh,ap in [(108.2,114.4,116.8),(122.4,128.8,131.2)]:window('west','east',100.0,2.80,b,sh,ap,-120.10,2.10,'one sparse east-side column')

for label,obj,chosen in [('main',main,[w for w in windows if w['tower']=='main']),('west',west,[w for w in windows if w['tower']=='west']),('west recess',recess,[w for w in windows if w['tower']=='west' and w['face']=='front'])]:
 cut=BasisBatch(label+' temporary cutters')
 for w in chosen:
  cut.basis=face_basis(w);cut.polygon(arch(w['width'],w['bottom'],w['shoulder'],w['apex']),w['x'],-2.0,w['back'],M['wall'])
 cutter=cut.finish();bpy.context.view_layer.objects.active=obj;obj.select_set(True)
 mod=obj.modifiers.new('Selective true deep window voids','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.ops.object.modifier_apply(modifier=mod.name);obj.select_set(False)
 data=cutter.data;bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.meshes.remove(data)
stone=BasisBatch('varied facade groups stone reveals and restrained frames')
tracery=BasisBatch('varied facade groups recessed mullions and tracery')
glass=BasisBatch('varied facade groups deep muted glazing')
structure=BasisBatch('varied facade groups secondary structural divisions')
for w in windows:
 for batch in [stone,tracery,glass,structure]:batch.basis=face_basis(w)
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


structure.basis=None
rib_contact_checks=[]
for group,zlo_probe,zhi_probe,upper_obj,belt in [('main lower',87,122,main,105.25),('main upper',165,178,bpy.data.objects['V002 | main crown masonry and terraces'],None)]:
 x,y=35.3,28.55
 hit,lo,n,i=main.ray_cast(Vector((x,y,zlo_probe)),Vector((0,0,-1)))
 if not hit:raise RuntimeError('Missing lower cornice contact for '+group)
 hit,hi,n,i=upper_obj.ray_cast(Vector((x,y,zhi_probe)),Vector((0,0,1)))
 if not hit:raise RuntimeError('Missing upper cornice contact for '+group)
 z0,z1=lo.z-.055,hi.z+.055
 structure.box(x,y,(z0+z1)/2,.36,.52,z1-z0,M['body'])
 if belt:
  structure.box(x,y-.05,belt,12.1,.67,.33,M['body']);structure.box(x,y-.17,belt+.20,12.28,.82,.12,M['trim'])
 rib_contact_checks.append({'group':group,'actual_lower_surface_z':lo.z,'actual_upper_surface_z':hi.z,'rib_z0':z0,'rib_z1':z1,'overlap_each_end':.055})
added=[stone.finish(),tracery.finish(),glass.finish(),structure.finish()]
for obj in [main,west,recess]:
 bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()

void_checks=[]
for w in windows:
 obj=main if w['tower']=='main' else west
 origin,u,inward=face_basis(w);start=origin+u*w['x']-inward*4+Vector((0,0,w['bottom']+3.8))
 hit,loc,n,i=obj.ray_cast(start,inward)
 actual=(loc-(origin+u*w['x'])).dot(inward) if hit else None
 if not hit or abs(actual-w['back'])>.025:raise RuntimeError('Selected window void failed actual depth check: '+str(w))
 void_checks.append({'tower':w['tower'],'face':w['face'],'group':w['group'],'center_u':w['x'],'bottom':w['bottom'],'actual_depth':round(actual,4)})
checks={o.name:topology(o) for o in [main,west,recess]+added}
if any(r['boundary_edges'] or r['nonmanifold_edges'] for r in checks.values()):raise RuntimeError('Non-manifold generated geometry: '+str(checks))

s=bpy.context.scene;s['v004_scope']='Selective front bands and single sparse side columns. Rear and additional side wall fields remain quiet. No lighting or silhouette change.'
s.render.filepath='//previews/v004_varied_tower_windows.png';s.render.use_stamp=False
for key in ['use_stamp_filename','use_stamp_date','use_stamp_time']:
 if hasattr(s.render,key):setattr(s.render,key,False)
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
report={'version':'v004 selective expansion','source_filename':os.path.basename(source),'source_sha256':hashlib.sha256(open(source,'rb').read()).hexdigest(),'output_filename':os.path.basename(output),'new_window_count':len(windows),'v003_existing_windows_retained':8,'total_refined_windows':8+len(windows),'windows':windows,'actual_void_depth_checks':void_checks,'new_rib_contacts':rib_contact_checks,'mesh_topology':checks,'source_objects_retained_hidden':[main_src.name,west_src.name,recess_src.name],'lights_world_exposure_unchanged':True,'tower_silhouettes_unchanged':True,'images':len(bpy.data.images),'libraries':len(bpy.data.libraries),'texts':len(bpy.data.texts),'status':'Awaiting actual render review; not project completion.'}
os.makedirs(os.path.dirname(output),exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=output,compress=True);report['output_sha256']=hashlib.sha256(open(output,'rb').read()).hexdigest()
with open(a.report,'w',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
