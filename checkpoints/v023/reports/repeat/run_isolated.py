"""Sequential independent repro/QA, explicit inputs; no model saves/renders."""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path
if sys.flags.optimize:raise RuntimeError('Assertions required')
p=argparse.ArgumentParser()
for k in ['source','accepted','rebuilt','bundle','out','blender']:p.add_argument('--'+k,required=True)
a=p.parse_args();source,accepted,rebuilt,bundle,root,blender=[Path(getattr(a,k)).resolve()for k in ['source','accepted','rebuilt','bundle','out','blender']]
if root.exists():raise RuntimeError('New output directory required')
root.mkdir();qa=root/'copied QA 中文';shutil.copytree(bundle,qa);out=root/'reports';out.mkdir();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();frozen={str(f.relative_to(qa)):sha(f)for f in qa.rglob('*')if f.is_file()};hashes={str(f):sha(f)for f in[source,accepted,rebuilt]};runs=[]
def process(kind,script,name,args):
 report=out/(name+'.json');cmd=([str(blender),'-b','--factory-startup','--disable-autoexec','--python-exit-code','1','--python-expr','import sys; sys.dont_write_bytecode=True','--python',str(qa/script),'--']if kind=='Blender'else[sys.executable,'-B',str(qa/script)])+args+['--report',str(report)]
 with (out/(name+'.log')).open('w')as log:r=subprocess.run(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0,(name,r.returncode);data=json.loads(report.read_text());runs.append({'name':name,'kind':kind,'command':cmd,'report_sha256':sha(report)});print('PASS subprocess',name,flush=True);return data
r=process('Blender','validate_repeat.py','repeat',['--accepted',str(accepted),'--rebuilt',str(rebuilt)]);assert r['pass']and r['inputs_unchanged']and all(r['category_checks'].values())
args=['--source',str(source),'--candidate',str(rebuilt),'--candidate-sha256',hashes[str(rebuilt)]];geom=out/'actual_geometry.json'
r=process('Blender','export_and_preserve.py','preservation',args+['--geometry',str(geom)]);assert r['pass']and r['source_unchanged']and r['candidate_unchanged']and all(r['full_source_checks'].values())and r['actual_geometry_sha256']==sha(geom);gh=sha(geom)
r=process('Python','check_actual_overlay.py','overlay',['--geometry',str(geom)]);assert r['pass']and r['actual_geometry_sha256']==gh and r['input_sha256']=={'source':hashes[str(source)],'candidate':hashes[str(rebuilt)]}and .016<=r['full_face_gap_range'][0]<=r['full_face_gap_range'][1]<=.030 and not r['new_new_positive_area_overlaps']
stategeom=out/'state_geometry.json';r=process('Blender','state.py','state',args+['--geometry',str(stategeom)]);assert r['pass']and r['source_unchanged']and r['candidate_unchanged']and r['active_non_target_evaluated_exact']and r['paired_rollback_twice_exact']and r['actual_geometry_sha256']==sha(stategeom)==gh
r=process('Python','negative_geometry.py','negative_geometry',['--geometry',str(geom)]);assert r['pass']and r['actual_export_sha256']==gh and len(r['cases'])==7 and all(c['rejected']and c['actual_assertion']for c in r['cases'])
for case in ['extra_mask','unrelated_source']:
 r=process('Blender','negative_state.py','negative_'+case,args+['--geometry',str(out/('negative_'+case+'_geometry.json')),'--case',case]);assert r['rejected']and r['case']==case and r['source_sha256']==hashes[str(source)]and r['candidate_sha256']==hashes[str(rebuilt)]and r['actual_assertion']
cmd=[sys.executable,'-B',str(qa/'test_overlay.py')]
with (out/'math_tests.log').open('w')as log:r=subprocess.run(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT)
assert r.returncode==0;runs.append({'name':'math_tests','kind':'Python','command':cmd,'log_sha256':sha(out/'math_tests.log')})
assert all(sha(f)==h for f,h in hashes.items());assert sha(geom)==gh;assert frozen=={str(f.relative_to(qa)):sha(f)for f in qa.rglob('*')if f.is_file()};assert all(sha(bundle/f)==h for f,h in frozen.items())
(root/'SUMMARY.json').write_text(json.dumps({'pass':True,'input_sha256':hashes,'runs':runs,'complete_bundle_inventory_unchanged':True,'original_bundle_unchanged':True,'all_models_unchanged':True,'negative_scopes':{'actual_Blender_in_memory_model_fixtures':2,'actual_evaluated_geometry_export_fixtures':7,'synthetic_math_tests':5},'geometry_export_sha256':gh,'scope':'Pinned accepted semantic rebuild equality, full source/state and affine domain/terrain clearance; no source writes or rendering.'},indent=2));print('ALL ISOLATED GATES PASS',flush=True)
