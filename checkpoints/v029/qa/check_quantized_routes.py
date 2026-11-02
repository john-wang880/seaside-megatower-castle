"""Replay the executed quantized guard/floor/route proof with explicit runtime paths."""
import os,json
from pathlib import Path
import check_guard_quantized as q
import check_payload as p
D=Path(os.environ['V029_QA_DATA']);O=Path(os.environ['V029_QA_OUTPUT']);n=json.loads((D/'native.json').read_text());plan=json.loads((D/'guard_plan.json').read_text());r=q.run(n,list(map(p.box,plan['guard'])),list(map(p.box,plan['cavities'])));r={k:v for k,v in r.items()if not k.startswith('_')};r['scope']='Same continuous full floor/air/body/29 non-target and finite seat tests, with nearest-float32 cavity/floor extents and directed partition bottom; no native or engineering claim.';(O/'QUANTIZED_ROUTES.json').write_text(json.dumps(r,indent=2)+'\n');print('QUANTIZED ROUTES PASS',r['refined_cell_count'])
