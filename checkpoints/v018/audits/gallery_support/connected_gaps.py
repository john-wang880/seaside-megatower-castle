from pathlib import Path
import ast
exec(compile(Path('work/gallery_support_graph_v018/graph.py').read_text().split('# Negative controls:')[0],'<contact predicates>','exec'))
tree=ast.parse(Path('work/gallery_support_graph_v018/islands.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['point_tri','segments','distance']],type_ignores=[]),'<distance functions>','exec'))
G=json.load(open(P/'support_graph.json'));r=json.load(open(P/'unresolved_islands.json'));connected={e[k] for e in G['contact_edges'] for k in ('a','b')};ids=sorted(connected);lo=np.array([C[i]['bounds'][0] for i in ids]);hi=np.array([C[i]['bounds'][1] for i in ids]);rows=[]
for index,island in enumerate(r['islands'],1):
 if island['nearest_external_root_connected']:
  best=island['nearest_exported_external_surface_gap_m'];pair=island['nearest_pair'];witness=island['surface_witness']
 else:
  pairs=[]
  for i in island['nodes']:
   dd=np.maximum(0,np.maximum(lo-np.array(C[i]['bounds'][1]),np.array(C[i]['bounds'][0])-hi));dist=np.linalg.norm(dd,axis=1);pairs.extend((float(d),i,j) for d,j in zip(dist,ids))
  pairs.sort();best=float('inf');pair=None;witness=None
  for lower,i,j in pairs:
   if lower>best:break
   d,w=distance(get(i),get(j),best)
   if w is not None:best=d;pair=[i,j];witness=w
 rows.append({'island':index,'nearest_any_exported_surface_gap_m':island['nearest_exported_external_surface_gap_m'],'nearest_any_is_root_connected':island['nearest_external_root_connected'],'nearest_root_connected_surface_gap_m':best,'root_connected_pair':pair,'root_connected_neighbor':{'object':C[pair[1]]['object'],'seed':C[pair[1]]['seed']},'surface_witness':witness})
json.dump(rows,open(P/'connected_gap_comparison.json','w'),indent=2);print([(x['island'],x['nearest_root_connected_surface_gap_m']) for x in rows])
