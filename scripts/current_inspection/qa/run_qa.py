"""Portable independent current-inspection review. Does not export, render or save models."""
import argparse,sys,json,hashlib,subprocess,importlib.util
from pathlib import Path
if sys.flags.optimize:raise RuntimeError('Assertions required')
p=argparse.ArgumentParser()
for name in ['repository-root','tool','source','viewer','receipt','output-dir','blender']:p.add_argument('--'+name,required=True)
a=p.parse_args();root=Path(a.repository_root).resolve();tool=Path(a.tool).resolve();source=Path(a.source).resolve();viewer=Path(a.viewer).resolve();receipt=Path(a.receipt).resolve();out=Path(a.output_dir).resolve();blender=Path(a.blender).resolve();qa=Path(__file__).resolve().parent
if out.exists()or not out.parent.is_dir():raise RuntimeError('New QA output directory in existing parent required')
if out.is_relative_to(root/'checkpoints')or out.is_relative_to(tool)or out.is_relative_to(qa):raise RuntimeError('Reports must remain outside frozen tool/checkpoint/QA trees')
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest();payload=json.loads((qa/'FILES.json').read_text());assert all(sha(qa/f)==h for f,h in payload.items());inventory={str(f.relative_to(qa)):sha(f)for f in qa.rglob('*')if f.is_file()};modelhashes={str(f):sha(f)for f in[source,viewer,receipt]};runtime={n:sha(tool/n)for n in ['preflight.py','export_inspection.py','ui_template.py','catalog.json']};out.mkdir()
sys.dont_write_bytecode=True;spec=importlib.util.spec_from_file_location('reviewed_inspection_preflight',tool/'preflight.py');pf=importlib.util.module_from_spec(spec);spec.loader.exec_module(pf);identity,catalog=pf.preflight(root,source,out/'unused-preflight-copy.blend',out/'unused-preflight-report.json',tool/'catalog.json');rec=json.loads(receipt.read_text());assert rec['manifest_sha256']==identity['manifest_sha256']and rec['catalog_sha256']==identity['catalog_sha256']and rec['source_sha256']==identity['source_sha256']and rec['runtime_sha256']==runtime
cmd=[sys.executable,'-B',str(qa/'test_preflight_independent.py'),'--tool',str(tool),'--source',str(source)]
with (out/'pure_tests.log').open('w')as log:r=subprocess.run(cmd,cwd=out,stdout=log,stderr=subprocess.STDOUT)
assert r.returncode==0,'Independent pure tests failed'
report=out/'validation.json';cmd2=[str(blender),'-b','--factory-startup','--disable-autoexec','--python-exit-code','1','--python-expr','import sys; sys.dont_write_bytecode=True','--python',str(qa/'validate_copy.py'),'--','--source',str(source),'--viewer',str(viewer),'--receipt',str(receipt),'--tool',str(tool),'--report',str(report)]
with (out/'validation.log').open('w')as log:r=subprocess.run(cmd2,cwd=out,stdout=log,stderr=subprocess.STDOUT)
assert r.returncode==0,'Actual Blender API/deep preservation failed'
r=json.loads(report.read_text());assert r['pass']and all(r['full_source_category_checks'].values())and r['manual_bookmarks_tested']==15 and r['all_inputs_unchanged'];assert len(r['negative_cases'])==20
assert all(sha(f)==h for f,h in modelhashes.items());assert all(sha(tool/n)==h for n,h in runtime.items());assert inventory=={str(f.relative_to(qa)):sha(f)for f in qa.rglob('*')if f.is_file()}
summary={'pass':True,'manifest_identity':identity,'input_sha256':modelhashes,'runtime_sha256':runtime,'qa_manifest_sha256':sha(qa/'FILES.json'),'qa_inventory_unchanged':True,'all_model_runtime_inputs_unchanged':True,'pure_tests':24,'actual_source_category_names':list(r['full_source_category_checks']),'actual_source_category_count':len(r['full_source_category_checks']),'api_negative_cases':r['negative_cases'],'commands':[cmd,cmd2],'reports':{'validation.json':sha(report),'pure_tests.log':sha(out/'pure_tests.log')},'scope':'Actual Linux reopen/headless manual UI/operator API; no render/model save, nativeWindows or desktopclick claim. Export provenance is not later edit certification.'};(out/'SUMMARY.json').write_text(json.dumps(summary,indent=2));print('PORTABLE INDEPENDENT QA PASS')
if (out/'unused-preflight-copy.blend').exists()or(out/'unused-preflight-report.json').exists():raise RuntimeError('Preflight unexpectedly wrote output')
