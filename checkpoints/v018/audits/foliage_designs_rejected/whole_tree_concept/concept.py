"""Isolated, unaccepted whole-tree concept. No .blend save or full-scene render."""
import bpy,bmesh,json,hashlib,math,time
from pathlib import Path
from mathutils import Vector
P=Path('work/forest_whole_tree_concept');P.joinpath('renders').mkdir(exist_ok=True);src=Path('work/v018/castle_v018.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SHA='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd';assert sha(src)==SHA
s=bpy.context.scene;fo=bpy.data.objects['V010 | woodland boughs with gate exit clearance'];wo=bpy.data.objects['V010 | woodland trunks with gate exit clearance'];spec=sorted(json.loads(Path('work/forest_dense_trial/source_components.json').read_text())['components'],key=lambda x:x['ids'][0]);branches=json.loads((P/'branches.json').read_text());original_mats=list(fo.data.materials);woodmat=wo.data.materials[0];lo=Vector((-83.73939,40.63627,23.65438));hi=Vector((-80.68923,43.64584,34.13936));root=Vector(branches[0]['root']);top=Vector(branches[0]['tip']);woodids=set(range(26760,27010));wv=[wo.matrix_world@wo.data.vertices[i].co for i in sorted(woodids)];wf=[[i-26760 for i in f.vertices] for f in wo.data.polygons if all(i in woodids for i in f.vertices)]
# Strip only this unsaved in-memory scene for an isolated concept, never canonical data on disk.
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
geom=[];objs=[]
def add(name,vs,fs,mat,tag):
 m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.materials.append(mat)
 for f in m.polygons:f.use_smooth=True
 o=bpy.data.objects.new(name,m);s.collection.objects.link(o);objs.append(o);geom.append({'name':name,'tag':tag,'vertices':[list(v.co) for v in m.vertices],'faces':[list(f.vertices) for f in m.polygons],'material':mat.name});return o
def center(z):return root.lerp(top,max(0,min(1,(z-root.z)/(top.z-root.z))))
def clamp(p):return Vector((max(lo.x+.002,min(hi.x-.002,p.x)),max(lo.y+.002,min(hi.y-.002,p.y)),max(lo.z+.002,min(hi.z-.002,p.z))))
add('CONCEPT | exact original wood context',wv,wf,woodmat,'unchanged original tree wood subset')
# Dense irregular continuous inner crown, not a stack of disconnected cones.
profiles=[(23.66,.12),(24.3,.58),(25.3,.82),(26.5,.8),(27.5,.64),(28.7,.58),(29.5,.48),(30.5,.36),(31.5,.28),(32.3,.22),(33.4,.15),(34.135,.005)];vs=[];fs=[];N=16
for k,(z,r) in enumerate(profiles):
 c=center(z)
 for j in range(N):
  a=j*math.tau/N;rr=r*(.94+.055*math.sin(a*3+k*.63));vs.append(clamp(Vector((c.x+math.cos(a)*rr,c.y+math.sin(a)*rr,z))))
fs.append(list(range(N-1,-1,-1)));fs.append(list(range((len(profiles)-1)*N,len(profiles)*N)))
for k in range(len(profiles)-1):
 for j in range(N):a=k*N+j;b=k*N+(j+1)%N;fs.append([a,b,b+N,a+N])
fir=bpy.data.materials['Fir needles — forest green'];add('CONCEPT | dense tapered inner crown',vs,fs,fir,'closed opaque core')
for k,branch in enumerate(branches[1:]):
 br=Vector(branch['root']);tip=Vector(branch['tip']);axis=tip-br;axis.z=0;angle=math.atan2(axis.y,axis.x);t=(br.z-25.4)/(32.272-25.4);radius=1.53*(1-t*.69);width=.64+(.055*math.sin(k*2.37));depth=1.15*(1-t*.5);vs=[];fs=[];NR=5;NA=9
 for layer in range(2):
  for ir in range(NR):
   u=ir/(NR-1);r=.12+(radius-.12)*u
   for ia in range(NA):
    v=ia/(NA-1)*2-1;ang=angle+v*width;edge=1-.12*abs(v)**1.5+.035*math.sin(ia*2.1+k);rr=r*edge
    # broad top slopes out/down gently, then lifts its outer tip. Closed lower fringe hangs below.
    topz=br.z+.16-.28*math.sin(u*math.pi)+.17*u*u-.10*abs(v);thick=depth*(.68+.32*u)*(1-.24*abs(v));fringe=(.10+.11*(1-t))*math.sin(ia*2.0+k*.7)**2*u*u
    z=topz if layer==0 else topz-thick-fringe
    vs.append(clamp(Vector((br.x+rr*math.cos(ang),br.y+rr*math.sin(ang),z))))
 M=NR*NA
 for ir in range(NR-1):
  for ia in range(NA-1):
   a=ir*NA+ia;b=a+1;c=b+NA;d=a+NA;fs.extend([[a,b,c,d],[a+M,d+M,c+M,b+M]])
 boundary=list(range(NA))+[r*NA+NA-1 for r in range(1,NR)]+list(range((NR-1)*NA+NA-2,(NR-1)*NA-1,-1))+[r*NA for r in range(NR-2,0,-1)]
 for i,a in enumerate(boundary):b0=boundary[(i+1)%len(boundary)];fs.append([a,a+M,b0+M,b0])
 mat=original_mats[spec[k]['material_indices'][0]];add(f'CONCEPT | radial bough {k+1:02}',vs,fs,mat,{'original_wood_seed':branch['first'],'angle':angle,'outer_radius':radius,'half_width':width,'depth':depth})
assert sha(src)==SHA
report={'status':'UNACCEPTED ISOLATED CONCEPT','source_sha256':SHA,'source_saved':False,'geometry':geom,'total_foliage_faces':sum(len(x['faces']) for x in geom[1:]),'triangle_equivalent':sum(sum(len(f)-2 for f in x['faces']) for x in geom[1:]),'scope':'Whole target crown reorganization; no legacy-clump shape envelopes. Exact original woody context copied only. Source palette reused, new diagnostic world/lights for isolation only.'};(P/'geometry.json').write_text(json.dumps(report))
# Cheap isolated actual geometry views; background and neutral studio lights are diagnostic only.
s.world=bpy.data.worlds.new('CONCEPT | diagnostic neutral world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.8,.8,.8,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
for name,loc,power,size in [('key',(-88,36,38),1100,8),('fill',(-77,44,32),500,6)]:
 d=bpy.data.lights.new('CONCEPT '+name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new('CONCEPT '+name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-82,42,29))-o.location).to_track_quat('-Z','Y').to_euler()
c=bpy.data.objects.new('CONCEPT camera',bpy.data.cameras.new('CONCEPT camera'));s.collection.objects.link(c);s.camera=c;c.data.type='ORTHO';c.data.ortho_scale=11.6;c.data.clip_end=200;s.render.resolution_x=480;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=8;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.use_stamp=False;s.render.use_border=False;s.render.film_transparent=False;s.view_settings.view_transform='Standard';s.view_settings.exposure=0;s.view_settings.look='None'
receipts=[]
for name,loc,sil in [('front_silhouette',(-99,38,29),True),('side_silhouette',(-78,25,29),True),('oblique_neutral',(-90,32,32),False)]:
 c.location=loc;c.rotation_euler=(Vector((-82.05,42.15,28.9))-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(P/'renders'/f'{name}.png');assert not Path(s.render.filepath).exists()
 if sil:
  s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='FLAT';s.display.shading.color_type='SINGLE';s.display.shading.single_color=(0,0,0);s.display.shading.background_type='WORLD';s.world.color=(1,1,1);s.display.shading.show_shadows=False;s.display.shading.show_cavity=False;s.display.shading.show_specular_highlight=False;s.display.shading.show_object_outline=False
 else:s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.max_bounces=4;s.cycles.use_denoising=True
 t0=time.time();bpy.ops.render.render(write_still=True);receipts.append({'view':name,'camera':[list(r) for r in c.matrix_world],'engine':s.render.engine,'seconds':time.time()-t0,'image_sha256':sha(Path(s.render.filepath)),'diagnostic_not_actual_scene_lighting':True})
(P/'render_receipts.json').write_text(json.dumps({'source_sha_after':sha(src),'views':receipts,'saved_model':False},indent=2));assert sha(src)==SHA;print('CONCEPT_RENDER_DONE',flush=True)
