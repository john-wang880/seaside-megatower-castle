import os
"""One authorized CPU camera check, no search/native extraction/render."""
import json,sys,hashlib,itertools,math
from pathlib import Path
import numpy as np
P=Path(os.environ['V028_QA_OUTPUT']);DATA=Path(os.environ['V028_QA_DATA']);sys.path.insert(0,str(Path(__file__).resolve().parent));from body_support import analyze
from axis_reference import f32
from exact_axis_boundary import clip_rect,area
from fractions import Fraction as F
n=json.loads((P/'native_geometry.json').read_text());s=json.loads((DATA/'native.json').read_text());p=json.loads((DATA/'geometry_final.json').read_text());fg=json.loads((P/'lit_geometry.json').read_text());targets={(t['object'],t['evaluated_seed']) for t in p['targets']};comps=[c for c in s['components'] if (c['object'],c['seed']) not in targets]+fg['components']
for m in n['meshes']:comps.append({'object':m['name'],'seed':0,'vertices':m['vertices'],'local_faces':m['faces'],'local_triangles':m['triangles']})
E=np.array([f32(x) for x in [13.8,36.8,30.65]]);A=np.array([f32(x) for x in [5.7,37.5,30.65]]);forward=(A-E)/np.linalg.norm(A-E);right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward)
def project(q):
 v=np.array(q)-E;z=v@forward;return [float(480+(v@right)/z*960*26/36),float(347-(v@up)/z*960*26/36)]
radius=math.sqrt(.05**2+(.05*36/26/2)**2+(.05*36/26/2*694/960)**2);boxes={'near_plane_enclosing_AABB':[(E-radius).tolist(),(E+radius).tolist()],'body':[[E[0]-.6,E[1]-.6,29.025],[E[0]+.6,E[1]+.6,31.1]]};body=[]
for name,b in boxes.items():
 rows=[analyze(c,b) for c in comps];assert all(r['disjoint'] for r in rows),(name,[r for r in rows if not r['disjoint']]);body.append({'proxy':name,'box':b,'all_saved_and_preserved_components_disjoint':len(rows)})
tri=[];labels=[]
for c in comps:
 ts=np.asarray(c['vertices'])[np.asarray(c['local_triangles'])];tri.extend(ts);labels.extend([c['object']]*len(ts))
tri=np.asarray(tri);labels=np.array(labels);nonzero=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)>0;tri=tri[nonzero];labels=labels[nonzero]
y0,y1=f32(36.8)+.01,f32(38.2)-.01;z0,z1=29.01,f32(31.45)-.01;doorx=f32(7.);corners=np.array([[doorx,y,z] for y,z in [(y0,z0),(y1,z0),(y1,z1),(y0,z1)]]);center=(corners.mean(0)+E)/2
planes=[(np.array([-1.,0,0]),-doorx),(np.array([1.,0,0]),E[0])]
for a,b in zip(corners,np.roll(corners,-1,axis=0)):
 norm=np.cross(a-E,b-E);norm/=np.linalg.norm(norm);d=norm@E
 if norm@center>d:norm=-norm;d=-d
 planes.append((norm,d))
def clip(poly,n,d):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=d-n@a;db=d-n@b
  if da>=0:out.append(a)
  if (da>=0)!=(db>=0):out.append(a+(b-a)*da/(da-db))
 return out
lo=np.minimum(corners.min(0),E);hi=np.maximum(corners.max(0),E);ix=np.where(np.all(tri.max(1)>=lo,axis=1)&np.all(tri.min(1)<=hi,axis=1))[0];occlusions=[];max_area=0.
for i in ix:
 poly=list(tri[i])
 for norm,d in planes:
  if len(poly)<3:break
  poly=clip(poly,norm,d)
 if len(poly)<3:continue
 q=[]
 for v in poly:
  if E[0]-v[0]<=1e-12:raise RuntimeError('Unexpected geometry at eye apex')
  q.append((E+(v-E)*(E[0]-doorx)/(E[0]-v[0]))[1:])
 ar=abs(sum(float(a[0]*b[1]-b[0]*a[1]) for a,b in zip(q,q[1:]+q[:1])))/2;max_area=max(max_area,ar)
 if ar>1e-10:occlusions.append({'object':str(labels[i]),'triangle':int(i),'projected_aperture_area':ar})
assert not occlusions,occlusions
# 221 finite rays corroborate continuous clipped ray-bundle result.
e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];tv=E-tri[:,0];rays=[]
for y,z in itertools.product(np.linspace(y0,y1,13),np.linspace(z0,z1,17)):
 target=np.array([doorx,y,z]);d=target-E;h=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,h);ok=np.abs(det)>1e-12;inv=np.zeros_like(det);inv[ok]=1/det[ok];u=np.einsum('ij,ij->i',tv,h)*inv;q=np.cross(tv,e1);v=np.einsum('j,ij->i',d,q)*inv;t=np.einsum('ij,ij->i',e2,q)*inv;hit=ok&(u>=-1e-10)&(v>=-1e-10)&(u+v<=1+1e-10)&(t>1e-8)&(t<1-1e-8);assert not np.any(hit),(target,labels[hit].tolist());rays.append({'target':target.tolist(),'pixel':project(target),'unobstructed_to_aperture':True})
# Project actual retained pier boundary boxes; report clipping rather than promise full forms.
piers=[]
for name,b in [('south',[[10.6,34.6,29],[11.4,35.4,32.05]]),('north',[[10.6,38.2,29],[11.4,39,32.05]])]:
 points=[project([f32(x) for x in xyz]) for xyz in itertools.product(*zip(*b))];mins=np.min(points,0);maxs=np.max(points,0);piers.append({'name':name,'projected_corner_bounds':[mins.tolist(),maxs.tolist()],'center_pixel':project(np.mean(b,0)),'intersects_frame':bool(np.all(maxs>[0,0]) and np.all(mins<[960,694])),'fully_inside_frame':bool(np.all(mins>=[0,0]) and np.all(maxs<=[960,694]))})
out={'pass_doorway_visibility_and_camera_clearance':True,'candidate_sha256':fg['candidate_sha256'],'eye_float32':E.tolist(),'aim_float32':A.tolist(),'camera':{'lens':26,'sensor_width':36,'resolution':[960,694],'clip_start':.05},'body_and_nearplane':body,'continuous_clear_aperture':{'x':doorx,'yz_rectangle':[[y0,z0],[y1,z1]],'area':(y1-y0)*(z1-z0),'fraction_of_full_open_aperture':(y1-y0)*(z1-z0)/((f32(38.2)-f32(36.8))*(f32(31.45)-29)),'projected_corners':[project(q) for q in corners],'triangle_candidates':len(ix),'positive_projected_occluders':occlusions,'max_numerical_zero_area_residual':max_area,'area_numerical_threshold':1e-10,'method':'Clip all actual bounded scene triangles against the entire convex eye-to-inset-aperture pyramid; zero positive projected triangle area, not sample-area inference.'},'finite_rays':rays,'pier_projection':piers,'limitations':['South pier center is outside the left image edge; only its clipped contextual portion can be shown. Both complete pier forms are not promised.','Projected pier boxes establish framing, not full visible silhouette or radiometric appearance.','Camera pose arithmetic here models quantized eye/target with double look-at; actual render receipt must reconcile native camera matrix.','Clear region has a deliberate0.01 scene-unit inset from each aperture edge; no statement about edge antialiasing, shadows, or all doorway boundary pixels.','This is the single requested correction, no pose search and no model/light changes.']};(P/'reverse_correction.json').write_text(json.dumps(out,indent=2));print('REVERSE CAMERA PASS',len(rays),piers)
