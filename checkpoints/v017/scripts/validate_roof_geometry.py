"""Independent actual tile-face audit, not generator-coordinate replay. Never saves."""
import bpy,bmesh,argparse,sys,json,hashlib,math
from pathlib import Path
from collections import defaultdict,Counter
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--report',required=True);p.add_argument('--baseline-model',required=True);p.add_argument('--baseline-audit',required=True);p.add_argument('--pitches',default='south,east,north,west');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);expected_pitches=set(a.pitches.split(','))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();source=Path(bpy.data.filepath);start_sha=sha(source);canonical=Path(a.baseline_model);canonical_sha=sha(canonical);assert canonical_sha=='d44a4cdecd11dab152fd656c624755369e575a0f342e2eb0bc2460475c6f65eb';before=(len(bpy.data.objects),len(bpy.data.meshes))
base=json.load(open(a.baseline_audit));o=bpy.data.objects[base['object']];assert not o.modifiers and len(o.data.vertices)==166 and len(o.data.polygons)==105
payload={'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(f.vertices) for f in o.data.polygons],'material_indices':[f.material_index for f in o.data.polygons]};signature=hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest();assert signature==base['mesh_content_sha256'];assert [list(r) for r in o.matrix_world]==base['matrix_world']
sv=[o.matrix_world@v.co for v in o.data.vertices]
def planes(vs,fs):
 center=sum(vs,Vector())/len(vs);out=[]
 for f in fs:
  aa=sum((vs[i] for i in f),Vector())/len(f);n=sum(((vs[f[i]]-aa).cross(vs[f[(i+1)%len(f)]]-aa) for i in range(len(f))),Vector()).normalized()
  if n.dot(center-aa)>0:n=-n
  assert max(abs(n.dot(vs[i]-aa)) for i in f)<3e-5,('nonplanar convex reference face',max(abs(n.dot(vs[i]-aa)) for i in f))
  out.append((n,n.dot(aa)))
 assert all(n.dot(v)-d<4e-5 for v in vs for n,d in out),'reference not convex'
 return out
def component_from_ids(c):
 ids=c['vertex_ids'];mapping={v:i for i,v in enumerate(ids)};vs=[sv[i] for i in ids];fs=[[mapping[i] for i in o.data.polygons[j].vertices] for j in c['polygon_ids']];return vs,fs,planes(vs,fs)
shellvs,shellfs,shellplanes=component_from_ids(base['components'][0]);beams=[component_from_ids(c) for c in base['components'][1:6]];finial=component_from_ids(base['components'][6]);caps=[base['components'][i]['bounds'] for i in range(7,11)]
def bbox(vs):return [[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]]
def boxgap(a,b):return math.sqrt(sum(max(a[0][k]-b[1][k],b[0][k]-a[1][k],0)**2 for k in range(3)))
def area(poly):return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1])))*.5
def clip(poly,a,b):
 def d(q):return (b[0]-a[0])*(q[1]-a[1])-(b[1]-a[1])*(q[0]-a[0])
 out=[]
 for x,y in zip(poly,poly[1:]+poly[:1]):
  dx,dy=d(x),d(y)
  if dx>=0:out.append(x)
  if (dx>=0)!=(dy>=0):
   t=dx/(dx-dy);out.append((x[0]+t*(y[0]-x[0]),x[1]+t*(y[1]-x[1])))
 return out
def ccw(poly):
 return poly if sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1]))>0 else poly[::-1]
def intersection_area(p,q):
 for aa,bb in zip(q,q[1:]+q[:1]):
  p=clip(p,aa,bb)
  if len(p)<3:return 0
 return area(p)
expected_counts={'south':1240,'east':1776,'north':1240,'west':1776};results=[];errors=[];allcoords=[];finial_candidates=[]
for pitch in sorted(expected_pitches):
 name='V017 | main crown '+pitch+' slate courses';obj=bpy.data.objects.get(name);assert obj is not None and not obj.hide_render and not obj.modifiers
 assert [m.name for m in obj.data.materials]==['V002 | quiet blue-grey roof slate']
 choices=[(i,n,d) for i,(n,d) in enumerate(shellplanes) if n.z>0 and ((pitch=='south' and n.y<-.1) or (pitch=='north' and n.y>.1) or (pitch=='east' and n.x>.1) or (pitch=='west' and n.x<-.1))];assert len(choices)==1
 face_index,n,d=choices[0];facepoints=[shellvs[i] for i in shellfs[face_index]];u=Vector((0,0,1)).cross(n).normalized();v=n.cross(u).normalized();origin=min(facepoints,key=lambda q:(round(q.z,4),q.dot(u)));domain=ccw([((q-origin).dot(u),(q-origin).dot(v)) for q in facepoints]);edges=list(zip(domain,domain[1:]+domain[:1]))
 me=obj.data;vs=[obj.matrix_world@q.co for q in me.vertices];allcoords+=vs;par=list(range(len(vs)))
 def root(i):
  while par[i]!=i:par[i]=par[par[i]];i=par[i]
  return i
 for edge in me.edges:
  x,y=map(root,edge.vertices)
  if x!=y:par[y]=x
 groups=defaultdict(list)
 for f in me.polygons:groups[root(f.vertices[0])].append(list(f.vertices))
 tiles=[];min_volume=1e9;min_embed=1e9;beam_margins=[];topkeys=set();bound=bbox(vs);capgap=min(boxgap(bound,c) for c in caps)
 for fs in groups.values():
  ids=sorted({i for f in fs for i in f});local={i:j for j,i in enumerate(ids)};vv=[vs[i] for i in ids];ff=[[local[i] for i in f] for f in fs];counts=Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in ff for i in range(len(f)));directions=Counter((f[i],f[(i+1)%len(f)]) for f in ff for i in range(len(f)))
  assert all(z==2 for z in counts.values()) and all(z==directions[b,a] for (a,b),z in directions.items()),'unclosed/inconsistently oriented tile'
  originvol=vv[0];volume=sum((vv[f[0]]-originvol).dot((vv[f[i]]-originvol).cross(vv[f[i+1]]-originvol))/6 for f in ff for i in range(1,len(f)-1));assert volume>1e-7;min_volume=min(min_volume,volume)
  heights=[n.dot(q)-d for q in vv];bottom=min(ff,key=lambda f:sum(heights[i] for i in f)/len(f));top=max(ff,key=lambda f:sum(heights[i] for i in f)/len(f));assert len(bottom)==len(top) and len(vv)==2*len(bottom)
  for i in bottom:
   margin=min(dd-nn.dot(vv[i]) for nn,dd in shellplanes);min_embed=min(min_embed,margin);assert margin>1e-5,'tile bottom not strictly in actual source shell'
   assert abs(heights[i]+.015)<4e-5
  xy=[((vv[i]-origin).dot(u),(vv[i]-origin).dot(v)) for i in top];poly=ccw(xy);h=[heights[i] for i in top];assert min(h)>.0029 and max(h)<.0251
  # Real top points determine expected row-plane intercept; the measured plane
  # must fit every actual top vertex. No analytic vertex list is imported.
  intercept=sum(hh+(.022/.6)*q[1] for hh,q in zip(h,xy))/len(h);row=round((intercept-.025)/(.022*.4/.6));assert max(abs(hh-(intercept-(.022/.6)*q[1])) for hh,q in zip(h,xy))<4e-5
  assert abs(intercept-(.025+row*.022*.4/.6))<5e-5
  key=tuple(sorted(tuple(round(c,4) for c in vv[i]) for i in top));assert key not in topkeys,'duplicate exposed top face';topkeys.add(key)
  for i,q in zip(top,xy):
   for aa,bb in edges:
    el=math.dist(aa,bb);dist=((bb[0]-aa[0])*(q[1]-aa[1])-(bb[1]-aa[1])*(q[0]-aa[0]))/el
    assert dist>.0599,'tile outside 60mm inset domain'
    # Eave has both source edge endpoints at local v=0 and no bronze seam.
    if abs(aa[1])<1e-4 and abs(bb[1])<1e-4:continue
    if abs(dist-.06)<1e-4:
     margins=[min(dd-nn.dot(vv[i]) for nn,dd in pp) for bv,bf,pp in beams];best=max(margins);assert best>1e-5,'clipped tile edge not covered by actual convex bronze rib';beam_margins.append(best)
  if boxgap(bbox(vv),base['components'][6]['bounds'])==0:finial_candidates.append({'pitch':pitch,'tile_seed':min(ids),'bounds':bbox(vv),'vertices_inside_finial':sum(all(nn.dot(q)<dd for nn,dd in finial[2]) for q in vv)})
  tiles.append({'row':row,'poly':poly,'intercept':intercept,'bounds2':[[min(q[k] for q in poly) for k in range(2)],[max(q[k] for q in poly) for k in range(2)]]})
 overlap_pairs=0;min_top_separation=1e9;byrow=defaultdict(list)
 for t in tiles:byrow[t['row']].append(t)
 for row,tt in byrow.items():
  for j,t in enumerate(tt):
   for other in tt[j+1:]+byrow.get(row+1,[]):
    if any(t['bounds2'][1][k]<=other['bounds2'][0][k]+1e-6 or other['bounds2'][1][k]<=t['bounds2'][0][k]+1e-6 for k in range(2)):continue
    ar=intersection_area(t['poly'],other['poly'])
    if ar>1e-7:
     assert other['row']==row+1,'same-row exposed footprint overlap';separation=other['intercept']-t['intercept'];assert separation>.0145,'coplanar/nonordered row tops';min_top_separation=min(min_top_separation,separation);overlap_pairs+=1
 assert len(tiles)==expected_counts[pitch] and overlap_pairs>0 and beam_margins and capgap>0
 results.append({'pitch':pitch,'tiles':len(tiles),'vertices':len(vs),'faces':len(me.polygons),'minimum_positive_component_volume':min_volume,'minimum_bottom_inside_shell_halfspace_margin':min_embed,'measured_adjacent_row_overlap_pairs':overlap_pairs,'minimum_top_plane_separation_on_overlap':min_top_separation,'actual_bronze_cover_points':len(beam_margins),'minimum_bronze_halfspace_cover_margin':min(beam_margins),'corner_cap_aabb_separation_lower_bound':capgap,'bounds':bound})
bounds=bbox(allcoords);assert bounds[0][0]>=21 and bounds[1][0]<=49 and bounds[0][1]>=32.6 and bounds[1][1]<=60.4 and bounds[0][2]>=192.55 and bounds[1][2]<210.55
actual_pitches={o.name.removeprefix('V017 | main crown ').removesuffix(' slate courses') for o in bpy.data.objects if o.name.startswith('V017 | main crown ') and o.name.endswith(' slate courses')};assert actual_pitches==expected_pitches
expected_finial={(pitch,seed) for pitch in ('east','west') if pitch in expected_pitches for seed in (14154,14162)}
assert {(c['pitch'],c['tile_seed']) for c in finial_candidates}==expected_finial
assert all(c['vertices_inside_finial']==1 and c['bounds'][1][2]<=210.5103 for c in finial_candidates)
finial_acceptance={'accepted':True,'classification':'Only the disclosed four terminal-tile vertex seating contacts in the unchanged central finial base are accepted; not a blanket finial collision exemption.','candidate_tile_count':len(finial_candidates),'inside_vertex_count':sum(c['vertices_inside_finial'] for c in finial_candidates),'contact_z_bounds':[210.5,210.5103],'conservative_radial_bound_from_original_finial_convex_prism':base['components'][6]['radius_range'][1]+1e-5,'radial_bound_kind':'upper bound from inside-source-finial classification, not measured per-contact radial distance','scope':'Local bronze cover/seating contact only; original finial base lies below original ridge. No load or watertightness claim.'}
r={'pass':True,'candidate_sha256':start_sha,'source_roof_geometry_signature':signature,'source_roof_signature_matches_baseline':True,'pitches':results,'tile_count':sum(x['tiles'] for x in results),'new_bounds':bounds,'finial_base_aabb_candidates_separately_reported':finial_candidates,'bounded_finial_contact_acceptance':finial_acceptance,'canonical_unchanged':sha(canonical)==canonical_sha,'candidate_unchanged':sha(source)==start_sha,'no_temporary_datablocks_left':before==(len(bpy.data.objects),len(bpy.data.meshes)),'scope':'Actual persisted new tile faces with no modifiers. Closed consistently oriented positive components, actual source convex-shell embedding, projected overlap/top-plane separation, clipped edges inside actual bronze-rib convex halfspaces and corner-cap AABB separation. Finial base candidates are separately disclosed, not silently treated as cap clearance. Deep source preservation is a separate audit. No waterproofing/historical/load claim.'}
assert r['canonical_unchanged'] and r['candidate_unchanged'] and r['no_temporary_datablocks_left'];Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
