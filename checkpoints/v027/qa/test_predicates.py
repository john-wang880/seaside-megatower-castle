import numpy as np,json
from geometry_checks import *
v=np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]],float)
t=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]])
r,e=topology(v,t);assert not r['bad_oriented_edges']and abs(r['signed_volume']-1)<1e-12 and len(r['components'])==1
assert inside([.5,.5,.5],v[t])['state']=='inside';assert inside([2,.5,.5],v[t])['state']=='outside';assert inside([0,.5,.5],v[t])['state']=='uncertain';assert abs(nearest_distance([.5,.5,.5],v[t])-.5)<1e-12
s=self_intersections(v,t);assert not s['strict_transverse_crossings']and not s['positive_area_coplanar_overlaps'];assert upper_connected(v,t,.5)['surface_components']==1
assert topology(v,t[:-1])[0]['bad_oriented_edges'];bad=t.copy();bad[0]=bad[0,::-1];assert topology(v,bad)[0]['bad_oriented_edges'];assert self_intersections(v,np.vstack([t,t[0]]))['positive_area_coplanar_overlaps']
a=np.array([[0,0,0],[2,0,0],[0,2,0.]]);b=np.array([[.3,.3,-1],[.3,.3,1],[.3,1.2,1]]);assert pair_crossings(a,b)
print(json.dumps({'pass':True,'controls':11,'scope':'Unit box topology/interior/exterior/boundary/margin, no false self-crossing, upper connectivity, missing/reversed/duplicate faces and genuine transverse crossing.'}))
