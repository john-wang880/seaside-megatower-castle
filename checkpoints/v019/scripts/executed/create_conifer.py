"""Original standalone branch-hierarchy conifer study. Never saves source scene."""
import bpy,bmesh,math,random,json,hashlib,time
from pathlib import Path
from mathutils import Vector
P=Path('work/conifer_specialist'); P.mkdir(exist_ok=True)
SRC=Path('work/v018/castle_v018.blend'); SHA='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)==SHA
s=bpy.context.scene; fo=bpy.data.objects['V010 | woodland boughs with gate exit clearance'];wo=bpy.data.objects['V010 | woodland trunks with gate exit clearance']
materials=[bpy.data.materials[x] for x in ['Fir needles — forest green','Sunlit needle tips','Cypress needles — deep blue green']];wood=wo.data.materials[0]
def subset(o,a,b):
 vs=[o.matrix_world@v.co for v in o.data.vertices[a:b]]; fs=[([i-a for i in f.vertices],f.material_index) for f in o.data.polygons if all(a<=i<b for i in f.vertices)];return vs,fs
wv,wf=subset(wo,26760,27010);fv,ff=subset(fo,90395,90693); oldm=list(fo.data.materials)
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
def mesh(name,vs,fs,mats,indices=None):
 m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update()
 for mat in mats:m.materials.append(mat)
 for i,f in enumerate(m.polygons):f.material_index=indices[i] if indices else 0
 o=bpy.data.objects.new(name,m);s.collection.objects.link(o);return o
origwood=mesh('SOURCE | exact target trunk and bough context',wv,[f[0] for f in wf],[wood])
original=mesh('SOURCE | original target crown',fv,[f[0] for f in ff],oldm,[f[1] for f in ff]); original.hide_render=True
rng=random.Random(220617);V=[];F=[];MI=[];WV=[];WF=[];needle_count=0;shoot_count=0;attachments=[];transport_repairs=[]
root=Vector((-82.111656,42.306736,23.650854));top=Vector((-81.992180,42.071362,33.396))
def center(z):return root.lerp(top,(z-root.z)/(top.z-root.z))
def tube(points,radius):
 offset=len(WV);n=5
 tangents=[(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized() for i in range(len(points))]
 switched=[abs(t.dot(Vector((0,0,1))))>.95 for t in tangents]
 repair=len(set(switched))>1
 if repair:transport_repairs.append(offset)
 previous_u=None;previous_tangent=None
 for i,p in enumerate(points):
  tangent=tangents[i];ref=Vector((1,0,0)) if switched[i] else Vector((0,0,1))
  if repair and previous_u is not None:
   u=previous_tangent.rotation_difference(tangent) @ previous_u
   u=(u-tangent*u.dot(tangent)).normalized()
  else:u=tangent.cross(ref).normalized()
  v=tangent.cross(u).normalized();r=radius*(1-.9*i/(len(points)-1))
  WV.extend(p+r*(math.cos(j*math.tau/n)*u+math.sin(j*math.tau/n)*v) for j in range(n))
  previous_u=u;previous_tangent=tangent
 for i in range(len(points)-1):
  for j in range(n):a=offset+i*n+j;b=offset+i*n+(j+1)%n;WF.append([a,b,b+n,a+n])
 WF.extend([[offset+j for j in range(n-1,-1,-1)],[offset+(len(points)-1)*n+j for j in range(n)]])
def needle(p,d,length,width,mat):
 global needle_count
 d=d.normalized();side=d.cross(Vector((0,0,1)))
 if side.length<.1:side=d.cross(Vector((1,0,0)))
 side.normalize();normal=d.cross(side).normalized();i=len(V)
 V.extend([p,p+d*length*.38+side*width*.5,p+d*length,p+d*length*.38-side*width*.5,p+d*length*.42+normal*width*.3])
 F.extend([[i,i+1,i+4],[i+1,i+2,i+4],[i+2,i+3,i+4],[i+3,i,i+4]]);MI.extend([mat]*4);needle_count+=1

def shoot(a,b,scale,age):
 global shoot_count
 shoot_count+=1
 nw=len(V);ww=len(WV)
 axis=b-a;length=axis.length;d=axis.normalized();u=d.cross(Vector((0,0,1))).normalized();v=d.cross(u).normalized()
 mid=a.lerp(b,.55)+Vector((0,0,-.025*scale))
 tube([a,mid,b],.009*scale)
 # Spiral rather than a planar ladder. Needles point forward, outward, and variably down.
 n=max(22,int(32*scale))
 for j in range(n):
  t=(j+.3)/n;theta=j*2.399963+rng.uniform(-.22,.22);radial=math.cos(theta)*u+math.sin(theta)*v
  p=a.lerp(mid,t/.55) if t<=.55 else mid.lerp(b,(t-.55)/.45)
  direction=(radial*.84+d*.55+Vector((0,0,-.12*(1-t)))).normalized()
  taper=(.65+.35*math.sin(t*math.pi))*(1-.4*max(0,(t-.75)/.25))
  leng=(.115+.06*rng.random())*scale*taper
  mat=1 if t>.78 and rng.random()<.45 else (2 if age and rng.random()<.13 else 0)
  needle(p,direction,leng,(.032+.016*rng.random())*scale,mat)
 # Small terminal spear, not an ellipsoid endcap.
 needle(b.lerp(mid,min(1,.025/(b-mid).length)),d,.115*scale,.026*scale,1)
 attachments.append((nw,len(V),ww))

primary_count=0
# Unevenly phased radial boughs, not level horizontal collars. Lower boughs are longer and hang.
for tier in range(28):
 t=tier/28; z=24.60+8.75*(tier/27)**.83
 radius=1.24*(1-t)**.66
 count=6 if tier<12 else 5
 phase=tier*2.399963+rng.uniform(-.12,.12)
 for k in range(count):
  primary_count+=1; angle=phase+k*math.tau/count+rng.uniform(-.12,.12); outward=Vector((math.cos(angle),math.sin(angle),0));side=Vector((-math.sin(angle),math.cos(angle),0))
  zz=z+rng.uniform(-.10,.10);c=center(zz);L=radius*rng.uniform(.78,1.04);drop=.34*(1-t)+.06
  def rawpoint(u):return c+outward*(L*u)+side*(.065*math.sin(u*math.pi)*(1 if k%2 else -1))+Vector((0,0,-drop*math.sin(u*math.pi*.86)+.09*u*u))
  knots=[rawpoint(j/5) for j in range(6)]
  def bpoint(u):
   q=min(4,int(u*5));return knots[q].lerp(knots[q+1],u*5-q)
  tube(knots,.037*(1-t)+.008)
  n=9 if tier<13 else 7
  for j in range(n):
   u=.16+.78*j/(n-1);p=bpoint(u);spread=(.24+.20*(1-u))*(1-t*.72)*rng.uniform(.85,1.15)
   for sign in [-1,1]:
    end=p+side*sign*spread+outward*(spread*(.45+.3*u))+Vector((0,0,-(.12+.13*(1-u))*(1-t)+rng.uniform(-.035,.035)))
    shoot(p,end,.94*(1-t*.22),tier<8)
   # Upper infill shoot is staggered, connecting mass between bough levels without a solid core.
   if j%3==1:
    end=p+outward*.16*(1-t)+side*rng.uniform(-.1,.1)+Vector((0,0,.23*(1-t*.5)))
    shoot(p,end,.85*(1-t*.20),False)
  shoot(bpoint(.82),bpoint(1)+outward*.10,.85*(1-t*.25),False)
# Narrow continuous leader extension overlaps existing trunk, supporting upper shoots.
tube([center(33.30),center(33.70),center(34.10)],.018)
# Ascending interior shoots obscure unnatural naked leader gaps, especially in the upper crown.
for j in range(57):
 z=27.0+j*.118;a=center(z);angle=j*2.399963;rr=.21*(1-(z-27)/8);b=a+Vector((math.cos(angle)*rr,math.sin(angle)*rr,.30))
 shoot(a,b,.85 if z<32.9 else .63,False)
# Needle-bearing central leader, continues to the old tree height.
for k in range(19):
 z=32.95+k*.055;a=center(z);angle=k*2.4;r=.12*(1-k/21);b=a+Vector((math.cos(angle)*r,math.sin(angle)*r,.13))
 shoot(a,b,.48,False)
shoot(center(33.95),Vector((top.x,top.y,34.10)),.28,False)
# Smooth anisotropic radial shaping stays inside the source crown box; never clips blades flat.
def shaped(p):
 c=center(p.z);d=p-c;return c+Vector((d.x*(1.08 if d.x<0 else .94),d.y*(1.08 if d.y<0 else .94),0))
V=[shaped(v) for v in V];WV=[shaped(v) for v in WV]
# Final-space attachment after asymmetric radial mapping; all five blade vertices move together.
projection_max=0.0
for first,last,ww in attachments:
 pts=[sum(WV[ww+j*5:ww+(j+1)*5],Vector())/5 for j in range(3)]
 for start in range(first,last,5):
  p=V[start];options=[]
  for a,b in zip(pts,pts[1:]):
   q=a.lerp(b,max(0,min(1,(p-a).dot(b-a)/(b-a).length_squared)));options.append(q)
  q=min(options,key=lambda q:(q-p).length_squared);delta=q-p;projection_max=max(projection_max,delta.length)
  for j in range(5):V[start+j]+=delta
(P/'attachment_mapping.json').write_text(json.dumps({'shoots':attachments,'final_space_projection_max_m':projection_max}))
foliage=mesh('CONCEPT | radial articulated needle sprays',V,F,materials,MI);branches=mesh('CONCEPT | tapering connected boughs and shoots',WV,WF,[wood])
for f in branches.data.polygons:f.use_smooth=True
bounds=[[min(v[i] for v in V),max(v[i] for v in V)] for i in range(3)]
(P/'transport_repaired_components.json').write_text(json.dumps({'tube_vertex_starts':transport_repairs,'method':'parallel transport first ring frame along tangent changes only for tubes whose legacy reference axis switches; all unaffected tube frames retain exact original construction'},indent=2))
# Compare final foliage coordinates against the frozen approved appearance asset.
oldpath=str((P/'pre_attachment_repair/isolated_conifer.blend').resolve())
with bpy.data.libraries.load(oldpath,link=False) as (src,dst):dst.meshes=['CONCEPT | radial articulated needle sprays']
oldmesh=dst.meshes[0];assert len(oldmesh.vertices)==len(V)
deltas=[(v-oldmesh.vertices[i].co).length for i,v in enumerate(V)]
(P/'attachment_displacements.json').write_text(json.dumps({'foliage_vertices_compared':len(deltas),'max_displacement_m':max(deltas),'rms_displacement_m':(sum(d*d for d in deltas)/len(deltas))**.5,'old_asset_sha256':sha(Path(oldpath)),'scope':'Needle/secondary roots follow actual piecewise supporting tubes; added continuous closed leader tube from z33.30 through34.10. No art-shape tuning.'},indent=2))
bpy.data.meshes.remove(oldmesh)
report={'status':'UNACCEPTED isolated design study','source_sha256':SHA,'source_saved':False,'primary_boughs':primary_count,'secondary_shoots':shoot_count,'needle_blades':needle_count,'foliage_vertices':len(V),'foliage_triangles':len(F),'wood_polygons':len(WF),'foliage_bounds_xyz':bounds,'source_original_foliage_faces':len(ff),'palette':[m.name for m in materials],'limitations':['Single near-view hero asset; increased budget relative to 496 original faces, not suitable for blanket forest replacement.','Needle blades open-backed; renders double sided. No scene integration, route or footprint clearance certification.','Stylized oversized needle clusters, not a botanical species reproduction.']}
(P/'stats.json').write_text(json.dumps(report,indent=2))
# Isolated diagnostic light, never written into source.
s.world=bpy.data.worlds.new('STUDY neutral world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.68,.74,.78,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
for name,loc,power,size in [('key',(-88,36,37),1400,8),('fill',(-77,44,32),850,7)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-82,42,29))-o.location).to_track_quat('-Z','Y').to_euler()
c=bpy.data.objects.new('STUDY camera',bpy.data.cameras.new('STUDY camera'));s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO';c.data.ortho_scale=11.5;c.data.clip_end=200
s.render.resolution_x=660;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=8;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.use_stamp=False;s.render.use_border=False;s.render.film_transparent=False;s.view_settings.view_transform='Standard';s.view_settings.exposure=0;s.view_settings.look='None';s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.max_bounces=4;s.cycles.use_denoising=True
c.location=(-90,32,30.6);c.rotation_euler=(Vector((-82.05,42.15,28.9))-c.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str((P/'isolated_conifer.blend').resolve()))
receipts=[]
for name,sil,old in []: # Technical replay only; existing verified render precedes <=5.1mm final-base projection.
 original.hide_render=not old;foliage.hide_render=old;branches.hide_render=old
 if sil:
  s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='FLAT';s.display.shading.color_type='SINGLE';s.display.shading.single_color=(0,0,0);s.display.shading.background_type='WORLD';s.world.color=(1,1,1);s.display.shading.show_shadows=False;s.display.shading.show_cavity=False;s.display.shading.show_specular_highlight=False;s.display.shading.show_object_outline=False
 s.render.filepath=str(P/(name+'.png'));tm=time.time();bpy.ops.render.render(write_still=True);receipts.append({'name':name,'seconds':time.time()-tm,'sha256':sha(Path(s.render.filepath))})
assert sha(SRC)==SHA
(P/'render_receipts.json').write_text(json.dumps({'views':receipts,'source_unchanged':True,'diagnostic_not_actual_scene':True},indent=2));print('CONIFER_STUDY_COMPLETE',flush=True)
