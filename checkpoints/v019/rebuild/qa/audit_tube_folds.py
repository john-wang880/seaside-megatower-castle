from pathlib import Path
exec(compile(Path(__file__).resolve().with_name('validate_new_geometry.py').read_text().split('contact_rows=[];')[0],'geometry_prefix','exec'))
folds=[]
for s in comps:
 vs=np.asarray([list(v) for v in s['verts']],float);vs-=vs.mean(0);ts=np.asarray(s['triangles']);tr=vs[ts];lo=tr.min(1);hi=tr.max(1);pairs=[]
 for i in range(len(ts)):
  for j in range(i+1,len(ts)):
   if set(ts[i])&set(ts[j]):continue
   if np.any(hi[i]<lo[j]-1e-10) or np.any(hi[j]<lo[i]-1e-10):continue
   hit=False
   for t,u in [(tr[i],tr[j]),(tr[j],tr[i])]:
    e1=u[1]-u[0];e2=u[2]-u[0]
    for k in range(3):
     d=t[(k+1)%3]-t[k];h=np.cross(d,e2);det=e1@h
     if abs(det)<1e-18:continue
     v=t[k]-u[0];aa=(v@h)/det;cross=np.cross(v,e1);bb=(d@cross)/det;rr=(e2@cross)/det
     if aa>1e-9 and bb>1e-9 and aa+bb<1-1e-9 and 1e-9<rr<1-1e-9:hit=True
   if hit:pairs.append([i,j])
 if pairs:folds.append({'wood_start':s['meta']['vertex_start'],'role':s['meta']['role'],'crossing_triangle_pairs':pairs})
out={'candidate_sha256':before,'components_tested':len(comps),'folded_components':folds,'scope':'Strict interior segment/triangle crossings among nonadjacent triangles without shared vertices. Positive crossings prove surface self-intersection; negative result does not certify all possible coplanar/shared-vertex degeneracy. Numerical barycentric guard1e-9.'};Path(a.report).write_text(json.dumps(out,indent=2));print('FOLDS',len(folds),[(x['wood_start'],len(x['crossing_triangle_pairs'])) for x in folds])
