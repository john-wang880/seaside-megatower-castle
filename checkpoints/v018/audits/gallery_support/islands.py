"""Bounded unresolved-island analysis; reuse audited predicates, no model operations."""
from pathlib import Path
exec(compile(Path('work/gallery_support_graph_v018/graph.py').read_text().split('# Negative controls:')[0],'<contact predicates>','exec'))
G=json.load(open(P/'support_graph.json'));connected={e[k] for e in G['contact_edges'] for k in ('a','b')};targets=set(G['unresolved_target_ids']);LO=np.array([c['bounds'][0] for c in C]);HI=np.array([c['bounds'][1] for c in C]);remaining=set(targets);islands=[];allseen=set();edges=[];uncertain=[]
while remaining:
 seed=min(remaining);seen={seed};q=collections.deque([seed])
 while q:
  i=q.popleft();js=np.where(np.all(LO<=HI[i]+NEAR,axis=1)&np.all(HI>=LO[i]-NEAR,axis=1))[0]
  for j in js:
   j=int(j)
   if j in connected or j in seen:continue
   kind,detail=contact(get(i),get(j))
   if kind.endswith('uncertain'):uncertain.append({'a':i,'b':j,'type':kind})
   elif kind!='separated':seen.add(j);q.append(j);edges.append({'a':i,'b':j,'type':kind,'detail':detail})
 remaining-=seen;allseen|=seen;islands.append(seen);print('ISLAND',len(islands),len(seen),'targets',len(seen&targets),flush=True)
# Exact nearest-point-on-triangle and segment pair distances in float64.
def point_tri(p,t):
 a,b,c=t;ab=b-a;ac=c-a;ap=p-a;d1=ab@ap;d2=ac@ap
 if d1<=0 and d2<=0:return a
 bp=p-b;d3=ab@bp;d4=ac@bp
 if d3>=0 and d4<=d3:return b
 vc=d1*d4-d3*d2
 if vc<=0 and d1>=0 and d3<=0:return a+ab*d1/(d1-d3)
 cp=p-c;d5=ab@cp;d6=ac@cp
 if d6>=0 and d5<=d6:return c
 vb=d5*d2-d1*d6
 if vb<=0 and d2>=0 and d6<=0:return a+ac*d2/(d2-d6)
 va=d3*d6-d5*d4
 if va<=0 and d4-d3>=0 and d5-d6>=0:return b+(c-b)*(d4-d3)/(d4-d3+d5-d6)
 den=va+vb+vc
 if abs(den)<1e-20:return min(t,key=lambda v:np.linalg.norm(p-v))
 return a+ab*vb/den+ac*vc/den
def segments(p,q,a,b):
 u=q-p;v=b-a;w=p-a;A=u@u;B=u@v;D=u@w;E=v@w;F=v@v;den=A*F-B*B
 s=np.clip((B*E-D*F)/den,0,1) if den>1e-20 else 0.;t=(B*s+E)/F if F else 0.
 if t<0:t=0.;s=np.clip(-D/A,0,1) if A else 0.
 elif t>1:t=1.;s=np.clip((B-D)/A,0,1) if A else 0.
 return p+s*u,a+t*v
def distance(a,b,best=float('inf')):
 witness=None
 for ta in a['tri']:
  lo=ta.min(axis=0);hi=ta.max(axis=0);dd=np.maximum(0,np.maximum(b['tri'].min(axis=1)-hi,lo-b['tri'].max(axis=1)));js=np.where(np.linalg.norm(dd,axis=1)<=best)[0]
  for j in js:
   tb=b['tri'][j];pairs=[(p,point_tri(p,tb)) for p in ta]+[(point_tri(p,ta),p) for p in tb]
   pairs += [segments(ta[k],ta[(k+1)%3],tb[l],tb[(l+1)%3]) for k in range(3) for l in range(3)]
   for p,q in pairs:
    d=float(np.linalg.norm(p-q))
    if d<best:best=d;witness=[p.tolist(),q.tolist()]
 return best,witness
results=[]
for group in islands:
 # Nearest external ACTUAL surface, not just nearest root. All exported direct neighbors included.
 pairs=[]
 for i in group:
  dd=np.maximum(0,np.maximum(LO-HI[i],LO[i]-HI));dist=np.linalg.norm(dd,axis=1)
  for j in np.argsort(dist):
   if j not in group:pairs.append((float(dist[j]),i,int(j)))
 pairs.sort();best=float('inf');witness=None;nearest=None;tested=0
 for lower,i,j in pairs:
  if lower>best:break
  d,w=distance(get(i),get(j),best);tested+=1
  if w is not None:best=d;witness=w;nearest=[i,j]
 bounds=[[float(min(LO[i,k] for i in group)) for k in range(3)],[float(max(HI[i,k] for i in group)) for k in range(3)]]
 results.append({'nodes':sorted(group),'target_seeds':[C[i]['seed'] for i in sorted(group&targets)],'node_count':len(group),'target_count':len(group&targets),'bounds':bounds,'nearest_exported_external_surface_gap_m':best,'nearest_pair':nearest,'surface_witness':witness,'surface_pairs_tested':tested,'nearest_external_root_connected':nearest[1] in connected if nearest else None,'scope':'Nearest external surface within evaluated exported neighborhood. Direct target neighbors within2m are exported; indirect extended non-target boundary remains bounded-scope limitation.'})
 print('GAP',len(results),len(group),best,nearest,flush=True)
r={'source_sha256':raw['source_sha256'],'unresolved_targets':129,'island_count':len(results),'islands':results,'island_edges':edges,'uncertain_edges':uncertain,'nodes':{str(i):{'object':C[i]['object'],'seed':C[i]['seed'],'bounds':C[i]['bounds']} for i in allseen},'method':'Actual contact graph within unconnected components, then exact point-triangle and edge-edge surface-distance minimization with conservative AABB lower-bound pruning. No AABB gap substituted for actual surface gap.','limits':'Geometric separation in examined visible neighborhood; no gravity/load claim, no automatic defect or repair verdict.'};(P/'unresolved_islands.json').write_text(json.dumps(r,indent=2));print('DONE',len(results),flush=True)
