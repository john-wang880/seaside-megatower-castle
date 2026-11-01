from pathlib import Path
p=Path(__file__).resolve().with_name('prove_source_overlay.py');exec(compile(p.read_text().split('faces={')[0],str(p),'exec'))
verts=survey['path']['vertices'];edges=[]
for row in [95,105]:
 for col in range(6):edges.append(('end',row,col,row*7+col,row*7+col+1))
for col in [0,6]:
 for row in range(95,105):edges.append(('lateral',row,col,row*7+col,(row+1)*7+col))
records=[]
for kind,row,col,ia,ib in edges:
 a,b=verts[ia],verts[ib];d=sub(b,a);pieces=[]
 for tid,xy,tb,tz in T:
  if max(a[0],b[0])<tb[0]or min(a[0],b[0])>tb[2]or max(a[1],b[1])<tb[1]or min(a[1],b[1])>tb[3]:continue
  if signed(xy)<0:xy=xy[::-1]
  lo,hi=0.,1.
  for u,v in zip(xy,xy[1:]+xy[:1]):
   e=sub(v,u);c=cross(e,sub(a,u));m=cross(e,d)
   if abs(m)<1e-15:
    if c<0:lo,hi=1,0;break
   elif m>0:lo=max(lo,-c/m)
   else:hi=min(hi,-c/m)
  if hi-lo<=1e-12:continue
  values=[]
  for t in [lo,hi]:q=(a[0]+d[0]*t,a[1]+d[1]*t);values.append(a[2]+(b[2]-a[2])*t-tz(q))
  pieces.append({'triangle':tid,'interval':[lo,hi],'gap_endpoints':values})
 intervals=sorted(p['interval']for p in pieces);assert intervals
 covered=0.;end=0.
 for lo,hi in intervals:
  assert lo<=end+1e-9,(kind,row,col,'coverage gap',lo,end)
  covered+=max(0,hi-max(lo,end));end=max(end,hi)
 assert abs(covered-1)<1e-9,(row,col,covered)
 records.append({'kind':kind,'row':row,'column':col,'vertex_ids':[ia,ib],'coverage':covered,'min_gap':min(v for p in pieces for v in p['gap_endpoints']),'max_gap':max(v for p in pieces for v in p['gap_endpoints']),'pieces':pieces})
sourceproof=json.loads((P/'source_overlay.json').read_text());selected=[f for f in sourceproof['faces']if 1140<=f['face']<1260];total=sum(f['plan_area']for f in selected);buried=sum(f['buried_area']for f in selected);r={'pass':True,'source_sha256':source,'selected_rows':[95,105],'selected_face_ids':[1140,1259],'selected_subset':{'faces':len(selected),'plan_area':total,'buried_area':buried,'buried_fraction':buried/total,'full_face_minimum_gap':min(f['min_full_face_gap']for f in selected),'worst_face':min(selected,key=lambda f:f['min_full_face_gap'])},'end_boundary_minimums':{str(row):min(r['min_gap']for r in records if r['kind']=='end'and r['row']==row)for row in [95,105]},'lateral_boundary_minimum':min(r['min_gap']for r in records if r['kind']=='lateral'),'edges':records,'method':'Independent parameter-interval clipping of full segments against terrain triangle halfplanes; affine gap extrema at interval endpoints, coverage union checked. Float doubleprecision, not rational exact arithmetic. Planimetric area is not camera pixel area.'};assert all(v>0 for v in r['end_boundary_minimums'].values());(P/'boundary_and_subset.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items()if k!='edges'},indent=2))
