"""CPU analytical section plan only. No mesh, model, or deformation output."""
from pathlib import Path
import json,hashlib,math,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/b0-mpl')
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;src=P.parent/'traces/geometry.json';d=json.loads(src.read_text());o=d['objects']['V002 | western headland with solid rock shore'];r=np.array([[o['vertices'][v]for v in ids]for ids in d['western_rings']['vertex_ids']])
anchors=[(96,0),(112,4),(144,7),(164,10),(174,18),(182,12),(192,4),(200,4),(207,7),(212,5),(224,0)]
def amplitude(i):
 for (a,x),(b,y) in zip(anchors,anchors[1:]):
  if a<=i<=b:
   t=(i-a)/(b-a);t=t*t*(3-2*t);return x+(y-x)*t
 return 0
f=np.array([0,0,.55,1,.9,0]);q=r.copy();directions={}
for i in range(96,225):
 n=r[5,i,:2]-r[1,i,:2];n=n/np.linalg.norm(n);directions[i]=n.tolist();q[:,i,:2]+=f[:,None]*amplitude(i)*n
z=-.4320000112056732
def shore(a,i):
 for j in range(1,5):
  u,v=a[j,i],a[j+1,i]
  if u[2]>=z>=v[2]:return u+(v-u)*(z-u[2])/(v[2]-u[2])
 return None
sections=[]
for i in [96,112,134,144,154,164,174,182,192,207,212,224]:
 u=shore(r,i);v=shore(q,i);sections.append({'column':i,'amplitude':amplitude(i),'source_rings':r[:,i].tolist(),'proposed_section_landmarks':q[:,i].tolist(),'reference_plane_shore_shift':None if u is None else float(np.linalg.norm(v[:2]-u[:2]))})
# Signed XY strip area is a planning footprint estimate, NOT actual water/land union.
old=[];new=[];missing=[]
for i in range(96,225):
 a,b=shore(r,i),shore(q,i)
 if a is None:missing.append(i)
 else:old.append(a[:2]);new.append(b[:2])
def area(p):return .5*sum(np.cross(p[(i+1)%len(p)],p[i])for i in range(len(p)))
strip=None if missing else abs(float(area(np.array(old+new[::-1]))))
runs=[];a=[];b=[]
for i in range(96,225):
 u,v=shore(r,i),shore(q,i)
 if u is None:
  if len(a)>1:runs.append({'start':start,'end':i-1,'signed_strip_magnitude':abs(float(area(np.array(a+b[::-1]))))})
  a=[];b=[]
 else:
  if not a:start=i
  a.append(u[:2]);b.append(v[:2])
if len(a)>1:runs.append({'start':start,'end':224,'signed_strip_magnitude':abs(float(area(np.array(a+b[::-1]))))})
changed=np.array([q[j,i]for j in [2,3,4]for i in range(97,224)])
def crossing(a,b,c,d):
 def cr(u,v):return float(u[0]*v[1]-u[1]*v[0])
 return cr(b-a,c-a)*cr(b-a,d-a)<-1e-14 and cr(d-c,a-c)*cr(d-c,b-c)<-1e-14
crossings=[]
for j in [2,3,4]:
 for i in range(256):
  for k in range(i+2,256):
   if i==0 and k==255:continue
   if crossing(q[j,i,:2],q[j,(i+1)%256,:2],q[j,k,:2],q[j,(k+1)%256,:2]):crossings.append([j,i,k])
report={'ring_xy_proper_crossings_only':crossings,'status' :'NUMERICAL DESIGN ENVELOPE ONLY; no candidate geometry or safety approval','source_sha256':d['source_sha256'],'trace_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'coordinate_units':'uncalibrated scene units','scope':{'columns':[96,224],'cell_arcs':[96,223],'bands':[1,2,3,4],'original_triangles':1024,'fixed':'all plateau/rim/lip, columns96/224, bottom ring, other arcs, main pedestal, marker assembly'},'amplitude_smoothstep_anchors':anchors,'ring_factors':f.tolist(),'direction':'per-column normalized actual lip-to-bottom XY vector; not asserted true surface normal','z_policy':'all sampled Z unchanged; shape change is whole descending cross-section outward projection','old_occupied_volume_policy':'required non-excavating superset, NOT proven by this section field; exact union/boundary proof prerequisite','source_lip_xy_length':float(np.linalg.norm(np.diff(r[1,96:225,:2],axis=0),axis=1).sum()),'source_lip_3d_length':float(np.linalg.norm(np.diff(r[1,96:225],axis=0),axis=1).sum()),'source_lip_z_range':[float(r[1,96:225,2].min()),float(r[1,96:225,2].max())],'proposed_moving_landmark_bounds':[changed.min(axis=0).tolist(),changed.max(axis=0).tolist()],'maximum_outward':18,'sections':sections,'horizon_plane_z':z,'horizon_strip_area_if_continuous':strip,'reference_plane_contiguous_run_areas':runs,'sum_reference_strip_magnitudes_not_union':sum(t['signed_strip_magnitude']for t in runs),'columns_without_above_reference_lip':missing,'water_limits':'Actual rippled-water triangle intersections not evaluated. Missing above-water lips prevent one continuous shoreline strip estimate; do not interpolate across these channels. No actual new land area claimed.','proof_gaps':['nonlocal triangle intersections and winding','old-volume containment','actual water intersections and shoreline component count','new volumes versus architecture/path/marker and retained root seats','upper/end/bottom boundary correspondence','actual whole-view silhouette significance']}
(P/'PLAN.json').write_text(json.dumps(report,indent=2)+'\n')
fig,axs=plt.subplots(2,3,figsize=(15,8));
for ax,i in zip(axs.flat,[134,154,174,192,207,224]):
 n=np.array(directions[i]);origin=r[1,i,:2]
 ax.plot((r[:,i,:2]-origin)@n,r[:,i,2],'o-',color='#666666',label='actual source')
 ax.plot((q[:,i,:2]-origin)@n,q[:,i,2],'o-',color='#b45f21',label='proposed envelope')
 ax.axhline(z,color='#2886aa',ls=':',label='horizon reference only');ax.set_title(f'Column {i}; outward field {amplitude(i):.1f}');ax.set_xlabel('outward scene units from actual lip');ax.set_ylabel('actual Z');ax.grid(alpha=.2);ax.legend(fontsize=7)
fig.suptitle('B0 numerical section hypothesis — fixed lip / bottom; NOT approved geometry or support proof');fig.tight_layout();fig.savefig(P/'SECTIONS.png',dpi=130);plt.close(fig)
fig,ax=plt.subplots(figsize=(13,4));ax.plot(range(96,225),r[1,96:225,2],label='actual fixed lip Z');ax.plot(range(96,225),[amplitude(i)for i in range(96,225)],label='outward amplitude (not Z)');ax.legend();ax.grid(alpha=.2);ax.set_xlabel('actual source column');ax.set_ylabel('scene units');fig.tight_layout();fig.savefig(P/'PROFILE.png',dpi=120);plt.close(fig)
print(json.dumps({k:report[k]for k in ['proposed_moving_landmark_bounds','columns_without_above_reference_lip','horizon_strip_area_if_continuous']}))
