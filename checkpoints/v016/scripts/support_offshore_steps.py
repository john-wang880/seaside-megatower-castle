"""Source-preserving static offshore stair support and short upper arrival."""
import bpy,bmesh,sys,argparse,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);src=Path(bpy.data.filepath);out=Path(a.output).resolve();sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha=='578ff47936800fe2a651237b609d95090cd97fefa686a208f8215d57628ac389';assert out!=src.resolve() and not out.exists();assert not any(o.name.startswith('V016 |') for o in bpy.data.objects)
mat=bpy.data.materials['West_Ashlar stone variation'];deps=bpy.context.evaluated_depsgraph_get();rock=bpy.data.objects['Western citadel_West_Sea stack basalt'].evaluated_get(deps);me=rock.to_mesh();me.calc_loop_triangles();rockbvh=BVHTree.FromPolygons([rock.matrix_world@v.co for v in me.vertices],[tuple(t.vertices) for t in me.loop_triangles]);rock.to_mesh_clear()
def rock_range(x,y):
 hi=rockbvh.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200)[0];lo=rockbvh.ray_cast(Vector((x,y,-100)),Vector((0,0,1)),200)[0];assert hi is not None and lo is not None,(x,y);assert hi.z>lo.z;return lo.z,hi.z
made=[]
def mesh(name,vs,fs):
 m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.materials.append(mat);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));
 if bm.calc_volume(signed=True)<0:
  for f in bm.faces:f.normal_flip()
 assert all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(m);bm.free();o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);made.append({'name':name,'vertices':len(m.vertices),'polygons':len(m.polygons),'volume':volume});return o
F=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,lo,hi):
 x,y,z=lo;X,Y,Z=hi;return mesh(name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],F)
# Stepped top is slightly inside the original slabs; no original slab moves.
source=bpy.data.objects['V012 | legacy ashlar with buried-route clearance'];eo=source.evaluated_get(deps);m=eo.to_mesh();steps=[]
for seed in range(5824,5881,8):
 v=[eo.matrix_world@m.vertices[i].co for i in range(seed,seed+8)];lo=[min(q[k] for q in v) for k in range(3)];hi=[max(q[k] for q in v) for k in range(3)];assert abs(lo[0]-113.75)<1e-4 and abs(hi[0]-118.25)<1e-4;steps.append({'seed':seed,'min':lo,'max':hi})
eo.to_mesh_clear();steps.sort(key=lambda q:q['min'][1]);x0,x1=113.85,118.15;y0,y1=184.50,191.80
upper=[(y0,steps[0]['min'][2]+.03)]
for step in steps[1:]:
 y=step['min'][1]+.02;upper.extend([(y,upper[-1][1]),(y,step['min'][2]+.03)])
upper.append((y1,upper[-1][1]));ys=[y0+(y1-y0)*i/292 for i in range(293)];bottoms=[[],[]];row_clearances=[]
for y in ys:
 ends=[]
 for x in (x0,x1):
  lo,hi=rock_range(x,y);ends.append(hi-min(.15,.4*(hi-lo)))
 needs=[];allows=[]
 for i in range(87):
  t=i/86;x=x0+(x1-x0)*t;z=ends[0]*(1-t)+ends[1]*t;lo,hi=rock_range(x,y);needs.append(z-hi+.06);allows.append(z-lo-.005)
 drop=max(0,max(needs));allow=min(allows);assert drop<=allow,(y,drop,allow)
 drop+=min(.015,max(0,allow-drop)/2)
 for j in range(2):bottoms[j].append((y,ends[j]-drop))
 row_clearances.append({'y':y,'additional_cross_width_recess':drop})
profiles=[upper+list(reversed(row)) for row in bottoms];n=len(profiles[0]);vs=[(x,y,z) for x,poly in zip((x0,x1),profiles) for y,z in poly];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]
for i in range(n):
 j=(i+1)%n
 # Triangulate potentially ruled/nonplanar bottom quads deterministically.
 fs.extend([(i,j,j+n),(i,j+n,i+n)])
core=mesh('V016 | offshore terrain-following stair core',vs,fs)
box('V016 | offshore upper landing',(113.75,190.10,6.084),(118.25,191.80,6.444))
box('V016 | offshore final arrival step',(113.75,191.75,6.264),(114.75,192.40,6.624))
box('V016 | offshore final step support',(113.85,191.75,5.70),(114.65,192.40,6.30))
# Bounded dense terrain-embedding check on actual triangulated new underside.
core.data.calc_loop_triangles();cb=BVHTree.FromPolygons([v.co for v in core.data.vertices],[tuple(t.vertices) for t in core.data.loop_triangles]);samples=[]
for iy in range(585):
 y=y0+.001+(y1-y0-.002)*iy/584
 for ix in range(45):
  x=x0+.001+(x1-x0-.002)*ix/44;pt=cb.ray_cast(Vector((x,y,-100)),Vector((0,0,1)),200)[0];assert pt is not None;lo,hi=rock_range(x,y);samples.append({'x':x,'y':y,'core_bottom':pt.z,'rock_bottom':lo,'rock_top':hi,'inside_vertical_rock_interval':lo+.001<pt.z<hi-.005})
bad=[q for q in samples if not q['inside_vertical_rock_interval']];r={'source_sha256':sha,'objects_added':made,'original_step_components':steps,'material_shared':mat.name,'ground_samples':len(samples),'ground_sample_failures':bad,'minimum_below_rock_top':min(q['rock_top']-q['core_bottom'] for q in samples),'minimum_above_rock_bottom':min(q['core_bottom']-q['rock_bottom'] for q in samples),'underside_profiles':bottoms,'upper_profile':upper,'scope':'Static support for8original offshore treads, compact landing and0.18finalrise toexistingupperplinth. Originalallgeometry/materials/lights unchanged. Ground check is denseverticalinterval evidence, not all-surface structural certification or continuous island access.'};Path(a.report).write_text(json.dumps(r,indent=2));assert not bad,('Underside not embedded',bad[:3]);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);assert hashlib.sha256(src.read_bytes()).hexdigest()==sha;r['model_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ['ground_sample_failures','underside_profiles','upper_profile','original_step_components']}))
