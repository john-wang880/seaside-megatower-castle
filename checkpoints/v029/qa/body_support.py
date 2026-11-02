"""Exact extracted executed analyze/gap helpers; planning entrypoint omitted."""
import numpy as np
import continuous_box_cover as q
def analyze(c,box):
 lo,hi=np.asarray(box,float);v=np.asarray(c['vertices'],float);t=v[np.asarray(c['local_triangles'],int)]
 idx=np.flatnonzero(np.all(t.max(1)>=lo-1e-9,axis=1)&np.all(t.min(1)<=hi+1e-9,axis=1))
 hits=[int(i) for i in idx if not q.triangle_box_separated(t[i],lo,hi)]
 closed=q.oriented_closed(c['local_faces']);w=q.solid_winding(v,c['local_triangles'],(lo+hi)/2) if closed and not hits else None
 return {'object':c['object'],'seed':c['seed'],'broadphase_triangles':len(idx),'actual_boundary_triangles':hits,'closed_oriented':closed,'winding_when_boundary_disjoint':w,'disjoint':not hits and (not closed or abs(w)<1e-8),'classification':('boundary intersects/touches; not automatically positive-volume overlap' if hits else ('closed solid disjoint' if closed and abs(w)<1e-8 else ('box inside solid' if closed else 'open surface disjoint; no solid-volume claim')))}

def gap(a,b):return float(np.linalg.norm(np.maximum(0,np.maximum(np.asarray(a[0])-b[1],np.asarray(b[0])-a[1]))))
