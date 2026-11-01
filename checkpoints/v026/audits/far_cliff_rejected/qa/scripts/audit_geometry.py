import json,hashlib,argparse,sys
from pathlib import Path
import numpy as np
from geometry_checks import *
import coplanar_predicate as cp
p=argparse.ArgumentParser();p.add_argument('--geometry',required=True);p.add_argument('--report',required=True);p.add_argument('--plan',required=True);a=p.parse_args();assert not Path(a.report).exists();g=json.loads(Path(a.geometry).read_text());plan=json.loads(Path(a.plan).read_text());name=plan['object'];data=g['objects'][name];v=np.array(data['vertices']);ts=np.array(data['triangles']);t=v[ts];cliff=g['objects'][plan['source_cliff']];ct=np.array(cliff['vertices'])[cliff['triangles']];issues=[]
top,edges=topology(v,ts);crossings=self_intersections(v,ts);source_top,_=topology(cliff['vertices'],cliff['triangles']);assert not source_top['bad_oriented_edges'],'Source cliff unexpectedly open';assert source_top['signed_volume']>0
if top['bad_oriented_edges']or len(top['components'])!=1 or top['minimum_triangle_area']<=0 or top['signed_volume']<=0:issues.append('invalid new closed solid')
if crossings['strict_transverse_crossings']or crossings['positive_area_coplanar_overlaps']:issues.append('new self crossing/overlap')
assert len(ts)<=800;assert np.all(v>=np.array(plan['bounds'][0]))and np.all(v<=np.array(plan['bounds'][1]));assert data['materials']==plan['materials']
# Independently propose witnesses from every actual face centroid shifted inward;
# verify actual interior and clearance against both full triangulated meshes.
normals=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);normals/=np.linalg.norm(normals,axis=1)[:,None];witnesses=[]
for i,tri in enumerate(t):
 p=tri.mean(0)-normals[i]*.05
 if p[2]<=0:continue
 own=inside(p,t)
 if own['state']!='inside':continue
 other=inside(p,ct)
 if other['state']=='inside' and min(own['surface_margin'],other['surface_margin'])>.001:
  witnesses.append({'source_triangle_seed':i,'point':list(p),'new_solid':own,'source_cliff':other,'interior_ball_radius_lower_bound':min(own['surface_margin'],other['surface_margin'])})
  if len(witnesses)>=8:break
if not witnesses:issues.append('no positive above-water cliff overlap proved')
# All actual nearby triangle pairs; explicit bounds, strict transverse hits and coplanar clipping.
contacts={};near=[];source_lo=t.min((0,1));source_hi=t.max((0,1))
for oname,obj in g['objects'].items():
 if oname==name:continue
 ot=np.array(obj['vertices'])[obj['triangles']];ol=ot.min(1);oh=ot.max(1);ids=np.where(np.all(oh>=source_lo-1e-7,1)&np.all(ol<=source_hi+1e-7,1))[0];cross=[];cop=[]
 for i,tri in enumerate(t):
  js=ids[np.all(oh[ids]>=tri.min(0)-1e-7,1)&np.all(ol[ids]<=tri.max(0)+1e-7,1)]
  for j in js:
   hits=pair_crossings(tri,ot[j])
   if hits:cross.append({'new_triangle':i,'old_triangle':int(j),'points':hits})
   c=cp.contact(tri.tolist(),ot[j].tolist(),1e-7)
   if c:cop.append({'new_triangle':i,'old_triangle':int(j),**c})
 contacts[oname]={'triangle_box_candidates':len(ids),'strict_transverse_pairs':cross,'positive_area_coplanar_pairs':cop,'local_triangle_z_bounds':[float(ot[ids][:,:,2].min()),float(ot[ids][:,:,2].max())]if len(ids)else None}
 if len(ids)and oname not in [plan['source_cliff'],'Open sea | rippled three-dimensional water surface','Distant ocean to the horizon']:near.append(oname)
 if cop:issues.append('positive area coplanar interface requires classification: '+oname)
 if oname in ['Open sea | rippled three-dimensional water surface','Distant ocean to the horizon']and not cross:issues.append('water surface crossing not established: '+oname)
if near:issues.append('unexpected neighbor triangle bounds: '+str(near))
levels=[0.0]
for k,r in contacts.items():
 if 'water surface'in k and r['local_triangle_z_bounds']:levels+=r['local_triangle_z_bounds']
connectivity=[upper_connected(v,ts,z)for z in sorted(set(levels))]
if any(x['surface_components']!=1 for x in connectivity):issues.append('disconnected above-water surface')
r={'pass':not issues,'issues':issues,'input_sha256':g['input_sha256'],'geometry_export_sha256':hashlib.sha256(Path(a.geometry).read_bytes()).hexdigest(),'topology':top,'self_intersection':crossings,'source_cliff_topology':{k:val for k,val in source_top.items()if k!='components'},'above_water_attachment_witnesses':witnesses,'contacts':contacts,'upper_surface_connectivity':connectivity,'all_render_visible_object_bounds':g['broadphase'],'claim':'Original scene exact plus additive closed solid means original occupied union retained, not welded globally manifold terrain. Interior ball witnesses establish local positive overlap, not structural capacity. Actual water meshes are fluid only. Surface connectivity above finite measured levels, no ocean dynamics or all-angle optical proof.','numerics':{'explicit_contact_plane_epsilon':1e-7,'strict_crossing_barycentric_guard':1e-9,'parity_distinct_crossing_tolerance':1e-9,'inside_near_surface_uncertain':1e-5,'minimum_witness_margin':.001,'float32_max_coordinate_ULP':float(np.spacing(np.float32(abs(v).max())))}};Path(a.report).write_text(json.dumps(r,indent=2));print('GEOMETRY',r['pass'],issues,'witnesses',len(witnesses));assert r['pass'],issues
