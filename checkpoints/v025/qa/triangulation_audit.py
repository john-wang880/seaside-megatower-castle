import bpy,json,hashlib,sys,collections,argparse
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parent));from surface_partition import area,cross,sub,dot,norm
if sys.flags.optimize:raise RuntimeError('Optimized Python unsupported')
p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--candidate-sha',required=True);p.add_argument('--report',required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);assert not Path(args.report).exists();src=Path(args.candidate);h=hashlib.sha256(src.read_bytes()).hexdigest();assert h==args.candidate_sha;bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);rows=[];zero=[]
for index in range(1,5):
 o=bpy.data.objects[f'V025 | exact evaluated rear return union {index:02d}'];m=o.data;m.calc_loop_triangles();by=collections.defaultdict(list)
 for t in m.loop_triangles:by[t.polygon_index].append(t)
 maximum=0.
 for f in m.polygons:
  p=[tuple(m.vertices[i].co)for i in f.vertices];assert area(p)>0;total=0.
  for t in by[f.index]:
   q=[tuple(m.vertices[i].co)for i in t.vertices];n=cross(sub(q[1],q[0]),sub(q[2],q[0]));ar=norm(n)/2;total+=ar
   if ar==0:
    v=[[F(c)for c in x]for x in q];exact=cross(sub(v[1],v[0]),sub(v[2],v[0]));assert all(x==0 for x in exact);assert set(t.vertices)<=set(f.vertices);zero.append({'group':index,'triangle':t.index,'vertices':list(t.vertices),'parent_polygon':f.index,'parent_vertices':list(f.vertices),'parent_coordinates':p,'triangle_coordinates':q,'parent_area':area(p),'parent_loop_triangles':[{'index':t.index,'coordinates':[tuple(m.vertices[i].co)for i in t.vertices]}for t in by[f.index]],'exact_rational_cross_zero':True,'parent_edge_segments':[(a,b)for a,b in zip(list(f.vertices),list(f.vertices)[1:]+list(f.vertices)[:1])if a in t.vertices or b in t.vertices]})
   else:assert dot(n,tuple(f.normal))>0
  error=abs(total-area(p));maximum=max(maximum,error);assert error<4*sum(norm(sub(x,y))for x,y in zip(p,p[1:]+p[:1]))*0.000030517578125,('Tessellation residual exceeds declared boundary-rounding budget',index,f.index,error)
 rows.append({'group':index,'positive_polygon_count':len(m.polygons),'loop_triangle_count':len(m.loop_triangles),'maximum_triangulation_area_residual':maximum,'all_nonzero_triangles_follow_polygon_orientation':True})
z=zero[0];parent=z['parent_coordinates'];assert len(parent)==4;main_triangle=[parent[0],parent[1],parent[2]];nonzero=[t for t in z['parent_loop_triangles']if norm(cross(sub(t['coordinates'][1],t['coordinates'][0]),sub(t['coordinates'][2],t['coordinates'][0])))>0];assert len(nonzero)==1 and set(map(tuple,nonzero[0]['coordinates']))==set(map(tuple,main_triangle));z['actual_nonzero_triangle_index']=nonzero[0]['index'];z['nonzero_triangle_exactly_parent_convex_hull']=True
# Exact rational parent21 is a triangle with one extra collinear edge point.
fp=[[F(c)for c in v]for v in parent];n=cross(sub(fp[1],fp[0]),sub(fp[2],fp[0]));assert all(dot(n,sub(v,fp[0]))==0 for v in fp);turns=[dot(n,cross(sub(fp[(i+1)%4],fp[i]),sub(fp[(i+2)%4],fp[(i+1)%4])))for i in range(4)];assert all(t>=0 for t in turns)and sum(t==0 for t in turns)==1;z['parent_exact_planar_convex_with_one_collinear_boundary_vertex']=True;z['nonzero_tessellation_triangle_count']=len(z['parent_vertices'])-2-1;assert z['nonzero_tessellation_triangle_count']==1
assert len(zero)==1 and zero[0]['group']==3 and zero[0]['triangle']==45;assert hashlib.sha256(src.read_bytes()).hexdigest()==h
Path(args.report).write_text(json.dumps({'pass':True,'candidate_sha256':h,'groups':rows,'exact_zero_measure_loop_triangles':zero,'source_unchanged':True,'scope':'One exact-rational collinear tessellation triangle, not a saved degenerate polygon. Omitting its zero measure for oriented surface integration does not remove any area or alter geometry.'},indent=2));print('TRIANGULATION PASS',zero)
