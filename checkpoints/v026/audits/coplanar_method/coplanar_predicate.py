"""Conservative explicit triangle bounds/plane filter, then oriented polygon clipping.
Unlike BVH.overlap, this does not use a transverse triangle-intersection test.
"""
import numpy as np
from surface_partition import *
def candidates(triangle,other_triangles,epsilon):
 arr=np.asarray(other_triangles,dtype=float)
 if len(arr)==0:return []
 n,d=plane(triangle);lo=np.min(triangle,axis=0);hi=np.max(triangle,axis=0);tlo=arr.min(axis=1);thi=arr.max(axis=1);mask=np.all(thi>=lo-epsilon,axis=1)&np.all(tlo<=hi+epsilon,axis=1);ix=np.where(mask)[0];ix=ix[np.max(np.abs(arr[ix]@np.array(n)-d),axis=1)<=epsilon];return [int(j)for j in ix]
def contact(a,b,epsilon):
 if exact_zero_triangle(a)or exact_zero_triangle(b):return None
 n,d=plane(a);m,e=plane(b);al=dot(n,m);dist=max(abs(dot(n,v)-d)for v in b)
 if abs(al)<.99999 or dist>epsilon:return None
 projected=[sub(v,mul(n,dot(n,v)-d))for v in b]
 if al<0:projected.reverse()
 ar=overlap_area(a,projected,n)
 if ar<=1e-8:return None
 return {'normal':n,'plane_offset':d,'same_facing':al>0,'area':ar,'max_plane_distance':dist,'strict_coplanar_at_1e_7':dist<1e-7}
