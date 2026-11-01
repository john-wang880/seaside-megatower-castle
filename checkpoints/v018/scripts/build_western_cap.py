"""Deterministic additive western cap slate courses. Never overwrites its v017 input.
Run Blender --disable-autoexec --python build_western_cap.py -- --baseline INPUT --output NEW.blend --report NEW.json
A successful build is not artistic acceptance or remote-backup verification.
"""
import bpy,bmesh,json,hashlib,math,sys,time,resource,collections,argparse
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
args=argparse.ArgumentParser()
args.add_argument('--baseline',required=True);args.add_argument('--output',required=True);args.add_argument('--report',required=True)
a=args.parse_args(sys.argv[sys.argv.index('--')+1:])
src=Path(a.baseline).resolve();output=Path(a.output).resolve();report_path=Path(a.report).resolve()
expected='9ed12e2dd4e21ee91ff65848d3c11601332a690ea80a880fb31bf41f1d7dd943'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert src!=output and src!=report_path and output!=report_path,'Source/output/report paths must be distinct'
assert src.is_file() and sha(src)==expected,'Baseline must be exact accepted v017'
assert not output.exists() and not report_path.exists(),'Refuse existing output/report'
assert output.suffix=='.blend' and report_path.suffix=='.json'
assert output.parent.is_dir() and report_path.parent.is_dir()
sys.path.insert(0,str(Path(__file__).resolve().parent))
import slate_math as sm
from preservation_support import mesh_snapshot,primitive,tree_snapshot,digest
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;o=bpy.data.objects['V002 | western lantern low slate cap'];m=o.data;assert not o.modifiers and len(m.vertices)==160 and len(m.polygons)==100
source_meshes={m.name:mesh_snapshot(m) for m in bpy.data.meshes};source_materials={x.name:digest(tree_snapshot(x.node_tree)) for x in bpy.data.materials};worldhash=digest(tree_snapshot(s.world.node_tree));lights={x.name:digest({'properties':primitive(x),'nodes':tree_snapshot(x.node_tree)}) for x in bpy.data.lights};vs=[o.matrix_world@v.co for v in m.vertices]
params=sm.Parameters(inset=.025,lip=.012,head=.003,bottom=-.012)
params.validate();beams=[]
for first in range(32,160,16):
 a=sum(vs[first:first+8],Vector())/8;b=sum(vs[first+8:first+16],Vector())/8;r=min((vs[first+i]-(a if i<8 else b)).length for i in range(16));beams.append({'a':a,'b':b,'inscribed_radius':r*math.cos(math.pi/8),'circumradius_min':r,'first_vertex':first})
footprint=[vs[i] for i in range(8)];finialvs=vs[16:32];finialfaces=[[v-16 for v in f.vertices] for f in m.polygons if all(16<=i<32 for i in f.vertices)];finialbvh=BVHTree.FromPolygons(finialvs,finialfaces)
collection='REFINEMENT | v018 western cap slate courses';assert collection not in bpy.data.collections;C=bpy.data.collections.new(collection);s.collection.children.link(C);records=[];allhip=[];alltiles=[];discarded=[]
for facet in range(8):
 f=m.polygons[facet+2];assert list(f.vertices)==[facet,(facet+1)%8,(facet+1)%8+8,facet+8];a,b,c,d=[vs[i] for i in f.vertices];u=(b-a).normalized();up=((c+d-a-b)/2).normalized();normal=u.cross(up).normalized();assert normal.z>0
 polygon=[((p-a).dot(u),(p-a).dot(up)) for p in [a,b,c,d]];width=(b-a).length;length=polygon[2][1];frame={'name':f'facet{facet+1}','origin':tuple(a),'u':tuple(u),'v':tuple(up),'normal':tuple(normal),'polygon':polygon,'width':width,'length':length};domain=sm.inset_polygon(polygon,params.inset);tiles=[]
 for row in range(math.ceil(length/params.exposure)):
  y0=row*params.exposure;offset=(row%2)*params.width/2
  for col in range(-1,math.ceil(width/params.width)+1):
   x0=col*params.width+offset+params.joint/2;x1=x0+params.width-params.joint;poly=domain[:]
   for fn in [lambda q:q[0]-x0,lambda q:x1-q[0],lambda q:q[1]-y0,lambda q:y0+params.length-q[1]]:
    poly=sm.clip(poly,fn)
    if len(poly)<3:break
   if len(poly)<3:continue
   ar=sm.area(poly);span=min(max(q[k] for q in poly)-min(q[k] for q in poly) for k in [0,1])
   if ar<params.min_area or span<params.min_span:discarded.append({'facet':facet+1,'row':row,'col':col,'area':ar,'span':span});continue
   tile={'polygon':poly,'row':row,'col':col,**sm.solid(frame,poly,y0,params)};assert sm.manifold(tile) and tile['volume']>0
   # Shell embed and original octagonal plan; true oriented edge inequalities, not only AABB.
   n=len(poly)
   for k,p0 in enumerate(tile['vertices']):
    p=Vector(p0);height=(p-a).dot(normal)
    if k<n:assert abs(height-params.bottom)<3e-5
    else:assert params.head-3e-5<=height<=params.lip+3e-5
    assert p.z<=186.5+1e-6 and p.z>=177.75-1e-6
    for fa,fb in zip(footprint,footprint[1:]+footprint[:1]):assert (fb.x-fa.x)*(p.y-fa.y)-(fb.y-fa.y)*(p.x-fa.x)>=-1e-6
   # Only polygon side1/3 terminate under existing bronze hips; eave/top-cap are distinct.
   for i,q in enumerate(poly):
    for pa,pb in [(polygon[1],polygon[2]),(polygon[3],polygon[0])]:
     ex,ey=pb[0]-pa[0],pb[1]-pa[1];distance=(ex*(q[1]-pa[1])-ey*(q[0]-pa[0]))/math.hypot(ex,ey)
     if abs(distance-params.inset)>1e-6:continue
     p=Vector(tile['vertices'][i+n]);near=[]
     for beam in beams:
      line=beam['b']-beam['a'];t=(p-beam['a']).dot(line)/line.length_squared
      if 0<=t<=1:near.append(((p-(beam['a']+t*line)).length,beam))
     radial,beam=min(near,key=lambda pair:pair[0]);allhip.append({'facet':facet+1,'point':list(p),'radial':radial,'inscribed_radius':beam['inscribed_radius'],'margin':beam['inscribed_radius']-radial});assert radial<beam['inscribed_radius'],('hip coverage',facet,row,col,radial,beam['inscribed_radius'])
   tiles.append(tile)
 verts=[];faces=[];ranges=[]
 for tile in tiles:
  off=len(verts);verts.extend(tile['vertices']);faces.extend([[off+i for i in f] for f in tile['faces']]);ranges.append({'first':off,'count':len(tile['vertices']),'row':tile['row'],'col':tile['col']})
 name=f'V018 | western slate facet {facet+1:02d}';assert name not in bpy.data.objects and name not in bpy.data.meshes
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(bpy.data.materials['V002 | quiet blue-grey roof slate']);obj=bpy.data.objects.new(name,mesh);C.objects.link(obj);obj['refinement_version']='v018';obj['source_facet']=facet+2
 # No smoothing of cap macrofacets; shallow tile planes remain their proper orientations.
 edges=collections.Counter(tuple(sorted(e)) for f in mesh.polygons for e in f.edge_keys);assert all(v==2 for v in edges.values());bv=BVHTree.FromPolygons([v.co for v in mesh.vertices],[list(f.vertices) for f in mesh.polygons]);overlaps=bv.overlap(finialbvh);assert not overlaps,('possible finial intersection',facet,len(overlaps))
 records.append({'object':name,'mesh':name,'source_face':facet+2,'frame':frame,'tile_count':len(tiles),'vertices':len(verts),'faces':len(faces),'tile_vertex_ranges':ranges,'bounds':[[min(v[k] for v in verts) for k in range(3)],[max(v[k] for v in verts) for k in range(3)]],'closed_edges_two_faces':True,'finial_bvh_overlap_pairs':len(overlaps),'sum_solid_volume_not_union':sum(t['volume'] for t in tiles)});alltiles.extend(tiles)
assert all(mesh_snapshot(bpy.data.meshes[n])==v for n,v in source_meshes.items());assert {x.name:digest(tree_snapshot(x.node_tree)) for x in bpy.data.materials}==source_materials;assert digest(tree_snapshot(s.world.node_tree))==worldhash
bpy.ops.wm.save_as_mainfile(filepath=str(output),copy=True);assert sha(src)==expected
report={'status':'LOCAL BUILD CHECKS PASSED; ARTISTIC AND INDEPENDENT ACCEPTANCE RECORDED SEPARATELY','source_sha256':expected,'candidate_sha256':sha(output),'candidate_bytes':output.stat().st_size,'collection':collection,'parameters':vars(params),'objects':records,'total_tiles':len(alltiles),'total_vertices':sum(len(t['vertices']) for t in alltiles),'total_faces':sum(len(t['faces']) for t in alltiles),'discarded':discarded,'actual_bronze_hip_checks':{'count':len(allhip),'max_radial':max(p['radial'] for p in allhip),'minimum_inscribed_margin':min(p['margin'] for p in allhip)},'checks':{'all_original_meshes_exact':True,'all_original_material_graphs_exact':True,'original_world_exact':True,'all_solids_closed_positive':True,'octagonal_plan_and_height_bounds':True,'shell_normal_embedding':True,'actual_bronze_inscribed_coverage':True,'no_finial_bvh_overlap_pairs':True,'source_file_unchanged':True},'limits':['Independent actual triangle/containment and source preservation review pending.','No visual acceptance or waterproof/engineering claim.','Tiny apex slivers omitted; original slate shell/cap intact underneath.']};report['actual_bronze_hip_points']=allhip
report['source_filename']=src.name;report['output_filename']=output.name
report_path.write_text(json.dumps(report,indent=2))
print('BUILD PASS',len(alltiles),flush=True)
