"""One deterministic midground 3-crown study; never saves source or modifies its data.
Run: blender -b work/v022/castle_v022.blend -t 4 --python work/midground_canopy_study/build.py
"""
import bpy,bmesh,json,math,hashlib,random
from pathlib import Path
from mathutils import Vector
ROOT=Path('/workspace/scratch/8bdb2666bb6b/seaside-megatower-castle')
OUT=ROOT/'work/midground_canopy_study'; OUT.mkdir(exist_ok=True)
SOURCE=ROOT/'work/v022/castle_v022.blend'
SHA='99156d901f9d498b86bae4834a642d1d9110dc6e4e3a4273bca64fda17a9dfd2'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
groups=json.loads((ROOT/'work/midground_stand_v022/selected_groups.json').read_text())
fol=bpy.data.objects['V010 | woodland boughs with gate exit clearance']; trunks=bpy.data.objects['V010 | woodland trunks with gate exit clearance']
collection=bpy.data.collections.new('STUDY | Midground overlapping branch-tier crowns'); bpy.context.scene.collection.children.link(collection)
report={'source_sha256':SHA,'generator':'build.py','concept':'Seven staggered overlapping radial branch tiers, broad folded fans, taper to continuous pointed core. Closed convex fan solids intentionally overlap one another and core.','units':'coordinate units','trees':[],'integration':'Append only STUDY collection, reuse original material names by identity/remap; mask exact verified original ranges separately. No original object modified.'}
objects=[]; diagnostic_trunks=[]
# Source index evidence, adjacency checks, and extracted trunk carrier.
adj=[[] for v in trunks.data.vertices]
for e in trunks.data.edges:
 a,b=e.vertices;adj[a].append(b);adj[b].append(a)
for gi,g in enumerate(groups):
 lo,hi=g['foliage_vertex_range']; ids=set(range(lo,hi)); fs=[p for p in fol.data.polygons if any(v in ids for v in p.vertices)]
 assert all(all(v in ids for v in p.vertices) for p in fs)
 assert len(ids)==g['counts'][0] and sum(len(p.vertices)-2 for p in fs)==g['counts'][1]
 assert set(p.index for p in fs)==set(i for c in g['components'] for i in c['face_ids'])
 srcpts=[fol.matrix_world@fol.data.vertices[i].co for i in ids]
 bounds=[[min(p[k] for p in srcpts) for k in range(3)],[max(p[k] for p in srcpts) for k in range(3)]]
 assert max(abs(bounds[j][k]-g['bounds'][j][k]) for j in range(2) for k in range(3))<1e-5
 assert not any(vg.weight>0 for i in ids for vg in fol.data.vertices[i].groups)
 seen={g['trunk_seed']};todo=list(seen)
 while todo:
  for v in adj[todo.pop()]:
   if v not in seen: seen.add(v);todo.append(v)
 tpts=[trunks.matrix_world@trunks.data.vertices[i].co for i in seen]
 tb=[[min(p[k] for p in tpts) for k in range(3)],[max(p[k] for p in tpts) for k in range(3)]]
 assert max(abs(tb[j][k]-g['trunk_bounds'][j][k]) for j in range(2) for k in range(3))<1e-5
 # Diagnostic carrier exact geometry, separate from authored asset.
 tid=sorted(seen);lookup={v:i for i,v in enumerate(tid)}
 tm=bpy.data.meshes.new('DIAGNOSTIC source trunk');tm.from_pydata([trunks.matrix_world@trunks.data.vertices[i].co for i in tid],[],[[lookup[i] for i in p.vertices] for p in trunks.data.polygons if all(i in seen for i in p.vertices)])
 for m in trunks.data.materials:tm.materials.append(m)
 to=bpy.data.objects.new('DIAGNOSTIC trunk '+str(g['trunk_seed']),tm);bpy.context.scene.collection.objects.link(to);diagnostic_trunks.append(to)
 verts=[]; faces=[];mats=[];parts=[];rng=random.Random(g['trunk_seed'])
 def hull(points,mat,role):
  bm=bmesh.new()
  for p in points:bm.verts.new(p)
  bm.verts.ensure_lookup_table();bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
  # Hull interior inputs must not survive as loose vertices.
  for v in list(bm.verts):
   if not v.link_faces:bm.verts.remove(v)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.verts.ensure_lookup_table();bm.verts.index_update()
  assert all(e.is_manifold for e in bm.edges)
  volume=bm.calc_volume(signed=True);assert volume>1e-8
  start=len(verts);fstart=len(faces);verts.extend(tuple(v.co) for v in bm.verts);faces.extend(tuple(start+v.index for v in f.verts) for f in bm.faces);mats.extend([mat]*len(bm.faces))
  parts.append({'role':role,'vertex_range':[start,len(verts)],'triangle_range':[fstart,len(faces)],'material_slot':mat,'closed_oriented':True,'pre_fit_volume':volume});bm.free()
 # Branch arms: high embedded heel -> wide folded shoulder -> downswept edge.
 # Angular phase changes and unequal roots suppress horizontal circular collar lines.
 for tier,t in enumerate([.07,.20,.33,.46,.59,.72,.83]):
  n=6 if tier<5 else 5
  radial=(1-t)**.88
  phase=gi*.71+tier*2.3999632297
  for arm in range(n):
   a=phase+arm*math.tau/n+rng.uniform(-.13,.13)
   length=radial*rng.uniform(.88,1.12)
   width=length*(.48 if gi<2 else .52)*rng.uniform(.88,1.08)
   z=t+rng.uniform(-.018,.018); depth=.115*(1-t)+.035
   # All points retain nonzero thickness. Convex solids prevent folded/self-crossing fans.
   profile=[(.00,0,.95),(.30,-.56,.64),(.30,.56,.64),(.73,-1,.17),(.73,1,.17),(1,-.43,-.04),(1,.43,-.04),(1.06,0,-.14)]
   pts=[]
   for r,w,h in profile:
    for side in [0,1]:
     x=r*length;y=w*width;zz=z+depth*h-(depth*.43 if side else 0)
     pts.append((x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a),zz))
   primary=1 if gi<2 else 2
   mat=0 if (tier*7+arm+gi)%19==0 else (2 if gi<2 and tier==5 and arm==2 else primary)
   hull(pts,mat,f'tier_{tier:02d}_fan_{arm:02d}')
 # Continuous opaque foliage core intersects every embedded heel and old trunk;
 # fits from lowest canopy to original tip, rather than floating separate whorls.
 pts=[]
 for z,r in [(0,.14),(.20,.18),(.45,.14),(.7,.095),(.86,.055)]:
  for i in range(9):pts.append((r*math.cos(i*math.tau/9),r*math.sin(i*math.tau/9),z))
 pts.append((.015,-.01,1.0));hull(pts,1 if gi<2 else 2,'continuous_core_and_pointed_leader')
 # Fit complete authored crown to original bounds, with trunk axis invariant in XY.
 cx,cy=g['trunk_xy'];minz=min(p[2] for p in verts);maxz=max(p[2] for p in verts)
 ext=[(min(p[k] for p in verts),max(p[k] for p in verts)) for k in range(2)]
 fitted=[]
 for p in verts:
  xy=[]
  for k,c in enumerate([cx,cy]):
   xy.append(c+p[k]*((bounds[1][k]-c)/ext[k][1] if p[k]>=0 else (bounds[0][k]-c)/ext[k][0]))
  fitted.append((*xy,bounds[0][2]+(p[2]-minz)/(maxz-minz)*(bounds[1][2]-bounds[0][2])))
 mesh=bpy.data.meshes.new('STUDY crown mesh '+str(g['trunk_seed']));mesh.from_pydata(fitted,[],faces);mesh.update()
 for m in fol.data.materials:mesh.materials.append(m)
 for p,m in zip(mesh.polygons,mats):p.material_index=m;p.use_smooth=False
 obj=bpy.data.objects.new('STUDY | crown trunk '+str(g['trunk_seed']),mesh);collection.objects.link(obj);objects.append(obj)
 obj['source_trunk_seed']=g['trunk_seed'];obj['source_vertex_range']=list(g['foliage_vertex_range']);obj['intentional_overlap']='Closed fan heels overlap continuous core; adjacent fan shoulders and tiers overlap.'
 report['trees'].append({'trunk_seed':g['trunk_seed'],'object':obj.name,'source_range':g['foliage_vertex_range'],'source_counts':g['counts'],'mapping_verified':True,'bounds':bounds,'authored_vertices':len(verts),'authored_triangles':len(faces),'components':parts,'material_triangles':{fol.data.materials[m].name:mats.count(m) for m in sorted(set(mats))},'attachment':'All fan root heels straddle central axis and overlap continuous opaque core, which extends through original trunk centerline. Exact source trunk included only in diagnostic, not asset.','source_trunk_component_vertices':len(seen),'source_trunk_bounds':tb})
report['total_triangles']=sum(t['authored_triangles'] for t in report['trees']);assert report['total_triangles']<=6000
asset=OUT/'midground_canopy_asset.blend';bpy.data.libraries.write(str(asset),{collection},fake_user=True,compress=True)
report['asset_sha256']=hashlib.sha256(asset.read_bytes()).hexdigest();report['asset_bytes']=asset.stat().st_size
(OUT/'manifest.json').write_text(json.dumps(report,indent=2))
# Isolated preflight only: source camera direction, original world/lights/materials.
for o in bpy.context.scene.objects:
 if o.type!='LIGHT' and o not in objects+diagnostic_trunks:o.hide_render=True
camdata=bpy.data.cameras.new('DIAGNOSTIC isolated camera');cam=bpy.data.objects.new('DIAGNOSTIC isolated camera',camdata);bpy.context.scene.collection.objects.link(cam)
center=Vector((-109.5,46,34.5));cam.location=center+Vector((21.7,-54.6,3.5));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=16.5;bpy.context.scene.camera=cam
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=True;sc.render.resolution_x=1000;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(OUT/'isolated_preflight.png');bpy.ops.render.render(write_still=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
print('STUDY_COMPLETE',report['total_triangles'],report['asset_sha256'],flush=True)
