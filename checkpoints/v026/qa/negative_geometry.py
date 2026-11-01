import json,sys,subprocess,copy,argparse,hashlib
from pathlib import Path
import sys
if sys.flags.optimize:raise RuntimeError('Assertions required; optimized Python unsupported')
p=argparse.ArgumentParser();p.add_argument('--geometry',required=True);p.add_argument('--output-dir',required=True);p.add_argument('--only-recess',action='store_true');a=p.parse_args();root=Path(a.output_dir);root.mkdir(exist_ok=False);base=json.loads(Path(a.geometry).read_text());script=Path(__file__).with_name('check_boundary.py').resolve();records=[]
cases=['translated_surface','missing_triangle','duplicate_triangle','reversed_orientation','filled_frame_recess']
if a.only_recess:cases=['filled_frame_recess']
for case in cases:
 d=copy.deepcopy(base)
 if case=='filled_frame_recess':
  import surface_partition as sp
  vs=[v for solid in d['original_convex_solids']for f in solid['faces']for v in f];box=sp.box([min(v[k]for v in vs)for k in range(3)],[max(v[k]for v in vs)for k in range(3)]);d['union_triangles']=[[p[0],p[i],p[i+1]]for p in box for i in range(1,len(p)-1)]
 elif case=='raw_box_union_loses_chamfers':
  import surface_partition as sp
  boxes=[]
  for solid in d['original_convex_solids']:
   vs=[v for f in solid['faces']for v in f];boxes.append(sp.box([min(v[k]for v in vs)for k in range(3)],[max(v[k]for v in vs)for k in range(3)]))
  boundary=sp.union_boundary(boxes);d['union_triangles']=[[p[0],p[i],p[i+1]]for f in boundary for p in [f['polygon']]for i in range(1,len(p)-1)]
 elif case=='translated_surface':
  for f in d['union_triangles']:
   for v in f:v[0]+=.03
 elif case=='missing_triangle':d['union_triangles'].pop(max(range(len(d['union_triangles'])),key=lambda i:sum(abs(x)for v in d['union_triangles'][i]for x in v)))
 elif case=='duplicate_triangle':
  # Largest triangle is deliberately duplicated, not a tiny rounding sliver.
  import surface_partition as sp
  f=max(d['union_triangles'],key=sp.area);d['union_triangles'].append(copy.deepcopy(f))
 else:
  import surface_partition as sp
  i=max(range(len(d['union_triangles'])),key=lambda i:sp.area(d['union_triangles'][i]));d['union_triangles'][i].reverse()
 inp=root/(case+'.json');out=root/(case+'_report.json');inp.write_text(json.dumps(d));r=subprocess.run([sys.executable,'-B',str(script),'--geometry',str(inp),'--report',str(out)],capture_output=True,text=True);(root/(case+'.log')).write_text(r.stdout+r.stderr)
 assert out.exists(),('Setup failure',case,r.stderr);report=json.loads(out.read_text());assert r.returncode!=0 and not report['pass']and report['failures'],case
 records.append({'case':case,'rejected':True,'failure_count':len(report['failures']),'report_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
(root/'SUMMARY.json').write_text(json.dumps({'pass':True,'source_geometry_sha256':hashlib.sha256(Path(a.geometry).read_bytes()).hexdigest(),'candidate_sha256':base['candidate_sha256'],'controls':records,'scope':'Mutations of exported actual saved triangles, not saved model edits or additional Blender processes.'},indent=2));print(len(records),'GEOMETRY NEGATIVES PASS')
