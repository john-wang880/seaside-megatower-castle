import os
"""Independent prospective rigid fixture seats, continuous body and finite camera rays."""
import json,hashlib,copy
from pathlib import Path
import numpy as np
import check_guard as q
import check_payload as p
D=Path(os.environ['V029_QA_OUTPUT']);R=p.ROOT
paths={'native':Path(os.environ['V029_QA_DATA'])/'native.json','plan':Path(os.environ['V029_QA_DATA'])/'fixture_plan.json','guard':Path(os.environ['V029_QA_DATA'])/'guard_plan.json'}
n,plan,g=[json.loads(paths[k].read_text())for k in ['native','plan','guard']];C=list(map(p.box,g['cavities']));source=[c for c in n['components']if c['object'].startswith('V028 | room 1 ')];q.require(len(source)==10,'Ten source fixture meshes');ashlar=next(c for c in n['components']if c['object']==q.NAMES[1]);copies=[];seats=[]
for record,rot,anchor in zip(plan['lamps'],[np.array([[0,1,0],[-1,0,0],[0,0,1]]),np.array([[0,-1,0],[1,0,0],[0,0,1]])],[[18.6,34,30.95],[21.7,38.5,30.95]]):
 M=np.asarray(record['rigid_matrix']);expected=np.eye(4);expected[:3,:3]=rot;expected[:3,3]=np.asarray(anchor)-rot@np.array([15,34,30.95]);q.require(np.array_equal(M,expected),'Exact signed-axis rigid transform');q.require(np.linalg.det(rot)==1 and np.array_equal(rot.T@rot,np.eye(3)),'Proper rotation')
 group=[]
 for c in source:
  d=copy.deepcopy(c);d['vertices']=(np.asarray(c['vertices'])@rot.T+M[:3,3]).tolist();d['object']=record['id']+' copy of '+c['object'];group.append(d)
 copies+=group;plate=next(c for c in group if c['object'].endswith('mounting plate'));b=record['positive_plate_source_seat_box'];s1=q.box_inside(plate,*b);s2=q.box_inside(ashlar,*b);q.require(s1['pass'] and s2['pass'],'Whole positive seat box');q.require(not any(all(b[0][k]<c[1][k]and c[0][k]<b[1][k]for k in range(3))for c in C),'Seat enters cavity');seats.append({'id':record['id'],'box':b,'plate':s1,'original_host':s2})
 q.require(record['light']['energy']==36 and record['light']['color']==[1.,0.5799999833106995,.25],'Planned light identity')
body=[[14.6,35.6,29.025],[23.3,36.8,31.1]];q.require(all(q.analyze(c,body)['disjoint']for c in copies),'Fixture body intrusion')
others=[c for c in n['components']if c['object']not in q.NAMES]+copies
triangles=np.concatenate([np.asarray(c['vertices'])[c['local_triangles']]for c in others]);tlo=triangles.min(1);thi=triangles.max(1)
def segment(a,b):
 a=np.asarray(a);b=np.asarray(b);d=b-a;ts=[0.,1.]
 for box in C:
  for k in range(3):
   if d[k]!=0:
    ts +=[(z-a[k])/d[k]for z in [box[0][k],box[1][k]]if 0<(z-a[k])/d[k]<1]
 ts=sorted(set(ts))
 for l,h in zip(ts,ts[1:]):q.require(any(q.inside(a+d*((l+h)/2),box)for box in C),'Ray interval outside prospective air')
 tr=triangles[np.all(thi>=np.minimum(a,b),axis=1)&np.all(tlo<=np.maximum(a,b),axis=1)];e1=tr[:,1]-tr[:,0];e2=tr[:,2]-tr[:,0];cross=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,cross);valid=np.abs(det)>1e-12
 if valid.any():
  tr=tr[valid];e1=e1[valid];e2=e2[valid];cross=cross[valid];det=det[valid];s=a-tr[:,0];u=np.einsum('ij,ij->i',s,cross)/det;cr=np.cross(s,e1);v=cr@d/det;t=np.einsum('ij,ij->i',e2,cr)/det;q.require(not np.any((u>=0)&(v>=0)&(u+v<=1)&(t>1e-9)&(t<1-1e-9)),'Finite actual non-target ray blocker')
 return len(tr)
views=[]
for view in plan['views']:
 M=np.asarray(view['reference_matrix']);eye=np.asarray(view['eye']);q.require(np.array_equal(M[:3,3],eye),'Camera origin');q.require(np.allclose(M[:3,:3].T@M[:3,:3],np.eye(3),atol=1e-14,rtol=0),'Camera basis');forward=-M[:3,2];q.require(np.allclose(forward,(np.asarray(view['target'])-eye)/np.linalg.norm(np.asarray(view['target'])-eye),atol=1e-14,rtol=0),'Camera aim')
 near=view['camera_data']['clip_start'];hw=near*36/52;hh=hw*694/960;corners=np.array([(M@np.array([x,y,-near,1]))[:3]for x in [-hw,hw]for y in [-hh,hh]]);container=C[1]if view['key']=='stores_entry'else C[0];q.require(all(q.inside(x,container)for x in corners),'Whole near plane not inside convex cavity');box=[corners.min(0),corners.max(0)];q.require(all(q.analyze(c,box)['disjoint']for c in others),'Near plane fixture/source collision')
 target=C[0]if view['key']=='stores_entry'else C[1];x=target[1][0]if view['key']=='stores_entry'else target[0][0];ends=[[x,y,z]for y in np.linspace(target[0][1]+.01,target[1][1]-.01,5)for z in np.linspace(target[0][2]+.01,target[1][2]-.01,5)];checks=[segment(eye,b)for b in ends];project=[]
 for y in target[0][1],target[1][1]:
  for z in target[0][2],target[1][2]:
   local=M[:3,:3].T@(np.array([x,y,z])-eye);depth=-local[2];uv=[.5+local[0]*26/36/depth,.5-local[1]*26/36*(960/694)/depth];q.require(depth>near and all(0<u<1 for u in uv),'Destination/aperture outside frame');project.append(uv)
 views.append({'key':view['key'],'near_plane_clear':True,'finite_interior_grid_rays_clear':len(checks),'projected_target_corners':project})
r={'pass':True,'input_sha256':{k:hashlib.sha256(v.read_bytes()).hexdigest()for k,v in paths.items()},'fixture_meshes':len(copies),'triangles':sum(len(c['local_triangles'])for c in copies),'seats':seats,'continuous_body_clear':body,'views':views,'scope':'Independent CPU prospective rigid-copy and quantized-cavity checks. Fifty finite interior rays, not whole projected-area or rendered visibility certification. Native evaluated transform decomposition, actual final seats/materials/power must still pass.'};(D/'FIXTURE_VIEW_PROOF.json').write_text(json.dumps(r,indent=2)+'\n');print('FIXTURE/VIEWS CPU PASS')
