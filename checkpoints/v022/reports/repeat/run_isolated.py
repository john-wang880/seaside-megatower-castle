"""Owner-coordinated sequential orchestration, no hidden input paths."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser()
for k in ['source','accepted','rebuilt','bundle','out','blender']:p.add_argument('--'+k,required=True)
a=p.parse_args();source,accepted,rebuilt,bundle,root,blender=[Path(getattr(a,k)).resolve()for k in ['source','accepted','rebuilt','bundle','out','blender']];assert not root.exists();root.mkdir();copied=root/'copied QA 中文';shutil.copytree(bundle,copied);reports=root/'reports';reports.mkdir();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();frozen={str(f.relative_to(copied)):sha(f)for f in copied.rglob('*')if f.is_file()};hashes={str(f):sha(f)for f in[source,accepted,rebuilt]};runs=[]
def run(script,name,args):
 report=reports/(name+'.json');cmd=[str(blender),'-b','--factory-startup','--disable-autoexec','--python-exit-code','1','--python-expr','import sys; sys.dont_write_bytecode=True','--python',str(copied/script),'--']+args+['--report',str(report)]
 with (reports/(name+'.log')).open('w')as f:r=subprocess.run(cmd,cwd=root,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(name,r.returncode);data=json.loads(report.read_text());runs.append({'name':name,'command':cmd,'report_sha256':sha(report)});print('PASS subprocess',name,flush=True);return data
r=run('validate_repeat.py','repeat',['--accepted',str(accepted),'--rebuilt',str(rebuilt)]);assert r['pass']and r['inputs_unchanged']and all(r['category_checks'].values())
args=['--source',str(source),'--candidate',str(rebuilt),'--candidate-sha256',hashes[str(rebuilt)]]
r=run('critical.py','critical',args);assert r['pass']and r['source_unchanged']and r['candidate_unchanged']and all(r['full_source_checks'].values())
r=run('deeper.py','deeper',args);assert r['pass']and r['source_unchanged']and r['candidate_unchanged']and not r['nonadjacent_self_crossings']and not r['same_facing_new_new_coplanar_patches']and r['paired_rollback_twice_exact']and r['active_non_target_evaluation_exact'];assert r['ray_classifications']=={'backing':55,'other_original_geometry':5}
for case in ['mask','hidden_original','enlargement','orientation','backing_gap']:
 r=run('negative.py','negative_'+case,args+['--case',case]);assert r['rejected']and r['case']==case and r['source_sha256']==hashes[str(source)]and r['candidate_sha256']==hashes[str(rebuilt)]and r['actual_assertion']
assert all(sha(f)==h for f,h in hashes.items());assert frozen=={str(f.relative_to(copied)):sha(f)for f in copied.rglob('*')if f.is_file()};assert all(sha(bundle/f)==h for f,h in frozen.items())
(root/'SUMMARY.json').write_text(json.dumps({'pass':True,'input_sha256':hashes,'runs':runs,'complete_bundle_inventory_unchanged':True,'original_bundle_unchanged':True,'source_accepted_rebuilt_unchanged':True,'private_helpers':False,'scope':'Pinned accepted-model semantic equality followed by all isolated portable QA gates; no rendering or model saves.'},indent=2));print('ALL ISOLATED GATES PASS',flush=True)
