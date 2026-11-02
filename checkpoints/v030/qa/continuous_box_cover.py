"""CPU connected-box inclusion certificates, not a nonconvex AABB substitution.
A strictly boundary-disjoint connected box with winding +/-1 witness is inside
that actual closed oriented triangle solid. Coverage uses overlapping box slabs.
"""
import numpy as np,math,collections

def oriented_closed(faces):
 e=collections.Counter((f[i],f[(i+1)%len(f)]) for f in faces for i in range(len(f)))
 return bool(e) and all(n==1 and e[(b,a)]==1 for (a,b),n in e.items())

def solid_winding(vertices,triangles,p):
 t=np.asarray(vertices,float)[triangles]-np.asarray(p,float);a,b,c=t[:,0],t[:,1],t[:,2]
 la=np.linalg.norm(a,axis=1);lb=np.linalg.norm(b,axis=1);lc=np.linalg.norm(c,axis=1)
 den=la*lb*lc+np.einsum('ij,ij->i',a,b)*lc+np.einsum('ij,ij->i',b,c)*la+np.einsum('ij,ij->i',c,a)*lb
 return float(np.sum(2*np.arctan2(np.einsum('ij,ij->i',a,np.cross(b,c)),den))/(4*math.pi))

def triangle_box_separated(triangle,lo,hi,eps=1e-9):
 """Full SAT; no triangle-BVH exclusion. Near contacts retained as uncertain."""
 lo=np.asarray(lo,float);hi=np.asarray(hi,float);c=(lo+hi)/2;h=(hi-lo)/2;t=np.asarray(triangle,float)-c
 edges=[t[1]-t[0],t[2]-t[1],t[0]-t[2]];axes=[*np.eye(3),np.cross(edges[0],edges[1])]
 axes += [np.cross(e,a) for e in edges for a in np.eye(3)]
 for axis in axes:
  length=np.linalg.norm(axis)
  if length==0:continue
  axis=axis/length;pr=t@axis;r=float(np.abs(axis)@h)
  if pr.min()>r+eps or pr.max()<-r-eps:return True
 return False

def box_inside(component,lo,hi):
 vv=np.asarray(component['vertices'],float);tt=np.asarray(component['local_triangles'],int)
 if not oriented_closed(component['local_faces']):return {'pass':False,'reason':'source not closed oriented'}
 overlap=np.all(vv[tt].max(axis=1)>=np.asarray(lo)-1e-9,axis=1)&np.all(vv[tt].min(axis=1)<=np.asarray(hi)+1e-9,axis=1)
 hits=[int(i) for i in np.flatnonzero(overlap) if not triangle_box_separated(vv[tt[i]],lo,hi)]
 if hits:return {'pass':False,'reason':'actual boundary intersects or numerically touches box','triangles':hits}
 winding=solid_winding(vv,tt,(np.asarray(lo)+np.asarray(hi))/2)
 return {'pass':abs(abs(winding)-1)<1e-8,'closed_oriented':True,'boundary_candidates':int(overlap.sum()),'actual_boundary_intersections':0,'winding':winding,'bounds':[list(lo),list(hi)],'source':{'object':component['object'],'seed':component['seed']},'numerical_sat_distance_allowance':1e-9}

def covered_room(foundation,base,lo,hi,split=30.72,overlap=.1):
 """Lower and upper slabs overlap by .2; their union is exactly the requested box."""
 lo=np.asarray(lo,float);hi=np.asarray(hi,float)
 assert lo[2]<split-overlap<split+overlap<hi[2]
 lower_hi=hi.copy();lower_hi[2]=split+overlap
 upper_lo=lo.copy();upper_lo[2]=split-overlap
 lower=box_inside(foundation,lo,lower_hi);upper=box_inside(base,upper_lo,hi)
 return {'pass':lower['pass'] and upper['pass'],'cover':'two connected overlapping slabs whose union equals requested full box','lower':lower,'upper':upper}
