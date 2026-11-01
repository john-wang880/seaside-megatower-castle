"""Generate only the accepted v019 authored tree meshes from exact historical v018.
Run with Blender5.2.3: blender --background --factory-startup --disable-autoexec
 --python-exit-code 1 --python generate_conifer.py -- --baseline /path/v018.blend
 --output-dir /new/directory
No render, integration or source save occurs. .blend byte identity is not promised.
"""
import argparse, hashlib, json, math, random, sys, time
from pathlib import Path
import bpy
from mathutils import Vector

EXPECTED_SOURCE_SHA256 = 'c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd'
EXPECTED_BLENDER = (5, 2, 3)
def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--baseline', type=Path, required=True)
parser.add_argument('--output-dir', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
SRC = args.baseline.expanduser().resolve(strict=True)
P = args.output_dir.expanduser().absolute()
if P.exists() or P.is_symlink():
    raise FileExistsError('Output directory must not exist; no files were replaced: ' + str(P))
P = P.resolve()
if SRC == P or SRC in P.parents:
    raise ValueError('Output aliases or nests below baseline input')
if tuple(bpy.app.version) != EXPECTED_BLENDER:
    raise RuntimeError('Exact semantic recipe requires Blender5.2.3; got ' + bpy.app.version_string)
if not SRC.is_file() or file_sha(SRC) != EXPECTED_SOURCE_SHA256:
    raise ValueError('Baseline must be exact historical v018; input was not modified')
started = time.perf_counter()
bpy.ops.wm.open_mainfile(filepath=str(SRC), use_scripts=False)
s = bpy.context.scene
wo = bpy.data.objects['V010 | woodland trunks with gate exit clearance']
original_axis = [sum((wo.matrix_world @ wo.data.vertices[i].co for i in range(a, a + 5)), Vector()) / 5 for a in (26760,26765)]
materials=[bpy.data.materials[x] for x in ['Fir needles — forest green','Sunlit needle tips','Cypress needles — deep blue green']]
wood=wo.data.materials[0]
assert wood.name == 'Pine bark'
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
s.camera = None
s.world = None
P.mkdir(parents=True, exist_ok=False)

def mesh(name,vs,fs,mats,indices=None):
 m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update()
 for mat in mats:m.materials.append(mat)
 for i,f in enumerate(m.polygons):f.material_index=indices[i] if indices else 0
 o=bpy.data.objects.new(name,m);s.collection.objects.link(o);return o

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
foliage=mesh('CONCEPT | radial articulated needle sprays',V,F,materials,MI);branches=mesh('CONCEPT | tapering connected boughs and shoots',WV,WF,[wood])
for f in branches.data.polygons:f.use_smooth=True
bounds=[[min(v[i] for v in V),max(v[i] for v in V)] for i in range(3)]

# Output metadata is intentionally separate from the immutable numerical recipe.
# Reconstruction of component ranges uses the established deterministic ordering.
W=[v.co.copy() for v in branches.data.vertices]
def ring_centers(offset,count):
    return [sum(W[offset+j*5:offset+(j+1)*5],Vector())/5 for j in range(count)]
wi=ni=fi=0
component_rows=[]
def record_shoot(scale,support):
    global wi,ni,fi
    count=max(22,int(32*scale))+1
    component_rows.append({'role':'needle_shoot','vertex_start':wi,'vertex_count':15,'face_start':fi,'face_count':12,'needle_blade_start':ni,'needle_blade_count':count,'support_polyline':[list(p) for p in support]})
    wi+=15;ni+=count;fi+=12
for tier in range(28):
    t=tier/28
    for k in range(6 if tier<12 else 5):
        primary=ring_centers(wi,6)
        component_rows.append({'role':'primary_bough','vertex_start':wi,'vertex_count':30,'face_start':fi,'face_count':27})
        wi+=30;fi+=27
        for j in range(9 if tier<13 else 7):
            for sign in [-1,1]:record_shoot(.94*(1-t*.22),primary)
            if j%3==1:record_shoot(.85*(1-t*.20),primary)
        record_shoot(.85*(1-t*.25),primary)
leader=ring_centers(wi,3)
component_rows.append({'role':'leader_extension','vertex_start':wi,'vertex_count':15,'face_start':fi,'face_count':12})
wi+=15;fi+=12
axis=[original_axis[0],original_axis[1],leader[-1]]
for j in range(57):record_shoot(.85 if 27+j*.118<32.9 else .63,axis)
for k in range(19):record_shoot(.48,axis)
record_shoot(.28,axis)
assert wi==len(branches.data.vertices) and fi==len(branches.data.polygons)
assert ni==len(foliage.data.vertices)//5==needle_count
assert len(component_rows)==3199

def write_json(name,value):
    (P/name).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n',encoding='utf-8')
write_json('attachment_mapping.json',{'shoots':attachments,'final_space_projection_max_m':projection_max})
write_json('component_contact_mapping.json',{'wood_components':component_rows,'needle_vertex_layout':'Each blade has5vertices, base isfirst; fourtriangles perblade.','source_trunk_vertices':[26760,26770],'leader_supports_above_z':33.30})
write_json('transport_repaired_components.json',{'tube_vertex_starts':transport_repairs,'method':'parallel transport first ring frame along tangent changes only for tubes whose legacy reference axis switches; all unaffected tube frames retain exact original construction'})

# This compact fingerprint is descriptive; independent accepted-model validation
# additionally covers every mesh attribute and complete material graphs.
import struct
mesh_rows=[]
for obj in [foliage,branches]:
    data=obj.data;data.calc_loop_triangles();h=hashlib.sha256()
    for vertex in data.vertices:h.update(struct.pack('<3f',*vertex.co))
    for polygon in data.polygons:
        h.update(struct.pack('<II?',len(polygon.vertices),polygon.material_index,polygon.use_smooth))
        for index in polygon.vertices:h.update(struct.pack('<I',index))
    slots=[mat.name for mat in data.materials]
    h.update(json.dumps(slots,separators=(',',':'),ensure_ascii=False).encode('utf-8'))
    mesh_rows.append({'object':obj.name,'mesh':data.name,'vertices':len(data.vertices),'polygons':len(data.polygons),'triangles':len(data.loop_triangles),'material_slots':slots,'matrix_world':[list(row) for row in obj.matrix_world],'geometry_fingerprint_sha256':h.hexdigest()})
assert sum(row['triangles'] for row in mesh_rows)==420206
assert set(bpy.data.objects.keys())=={foliage.name,branches.name}
write_json('generation_metadata.json',{
    'schema':'v019-conifer-generation-v1','baseline_sha256':EXPECTED_SOURCE_SHA256,
    'recipe_blender_version':list(EXPECTED_BLENDER),'rng_seed':220617,
    'primary_boughs':primary_count,'secondary_shoots':shoot_count,'needle_blades':needle_count,
    'meshes':mesh_rows,'foliage_bounds_xyz':bounds,
    'fingerprint_format':'Ordered vertices packed little-endian float32; each polygon len, material_index uint32 and smooth bool, then ordered uint32 vertices; UTF8 compact JSON material names.',
    'scope':'Standalone generated geometry only. No integration, rendering or new model version. Validate independently against accepted v019; .blend bytes need not match historical standalone asset.',
    'limitations':['Needle blades are open-backed surfaces.','Original source trunk is not part of this output; use authorized integration preserving source context.','No forest-wide use or newly certified route/structural safety.']})
assert file_sha(SRC)==EXPECTED_SOURCE_SHA256
asset=P/'generated_conifer.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(asset))
assert file_sha(SRC)==EXPECTED_SOURCE_SHA256
write_json('runtime_report.json',{
    'baseline_path':str(SRC),'output_directory':str(P),'baseline_sha256_after':file_sha(SRC),
    'generated_asset_sha256':file_sha(asset),'generated_asset_bytes':asset.stat().st_size,
    'generator_sha256':file_sha(Path(__file__).resolve()),'blender_version_string':bpy.app.version_string,
    'blender_build_hash':bpy.app.build_hash.decode('ascii'),'elapsed_seconds':time.perf_counter()-started,
    'source_saved':False,'rendered':False,'generated_objects_only':len(bpy.data.objects)})
print('V019_CONIFER_GENERATION_COMPLETE',str(P),flush=True)
