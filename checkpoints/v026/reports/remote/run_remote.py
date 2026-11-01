"""External orchestration for two frozen Git-restored QA bundles. No model writes."""
import argparse,hashlib,json,os,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
if sys.flags.optimize:raise RuntimeError('Optimized Python unsupported')
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inventory(root):return {str(p.relative_to(root)):sha(p)for p in root.rglob('*')if p.is_file()}
def safe(v):
 p=Path(v).absolute();need('..'not in p.parts and not any(q.is_symlink()for q in [p,*p.parents]),'Aliased paths refused');return p.resolve()
def main():
 p=argparse.ArgumentParser()
 for k in ['archive','qa','historical-qa','source-v024','source-v025','candidate','output-dir','blender','commit']:p.add_argument('--'+k,required=True)
 a=p.parse_args();archive=safe(a.archive);qa=safe(a.qa);historical=safe(a.historical_qa);v24=safe(a.source_v024);v25=safe(a.source_v025);candidate=safe(a.candidate);out=safe(a.output_dir);blender=safe(a.blender)
 need(re.fullmatch('[0-9a-f]{40}',a.commit),'Parent-verified exact Git commit required')
 need(qa.is_relative_to(archive)and historical.is_relative_to(archive)and v25.is_relative_to(archive)and candidate.is_relative_to(archive),'Only fresh archive QA/source/candidate accepted')
 need(not out.exists()and out.parent.is_dir()and not out.is_relative_to(archive),'New external output directory required')
 expected={v24:'89f9f6a8a57103d99100935b96624469ddf1fd52b9703e0d9177a352e735c856',v25:'8a3590082c99a69d50d444f77165fae57fb611cf069cecda03fdf0c6c17cadd2',candidate:'efcd894acdc045a30f845f05267662957b656bc7fe0ee4cf48c05fc798b610ee'}
 need(len(expected)==3 and all(sha(f)==h for f,h in expected.items()),'Exact three model hashes required')
 need(sha(qa/'FILES.json')=='e479b50ae1506a95683191945b3fe532915ee0cadec14b3c479af2a2a155358a','Frozen V026 QA manifest mismatch');need(sha(historical/'FILES.json')=='5af7be21c80661c478e890da32198e4bbe2f2ab8e32331469448d8951e9d04ae','Frozen historical QA manifest mismatch')
 before=inventory(archive);out.mkdir();(out/'archive_inventory_before.json').write_text(json.dumps(before,sort_keys=True,indent=2));commands=[]
 def run(cmd,label):
  commands.append(cmd)
  with (out/(label+'.log')).open('w')as log:r=subprocess.run(cmd,cwd=out,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  need(r.returncode==0,label+' failed; inspect retained log')
 run([sys.executable,'-B',str(historical/'run_recheck.py'),'--source',str(v24),'--candidate',str(v25),'--output-dir',str(out/'historical'),'--blender',str(blender)],'historical')
 hs=json.loads((out/'historical/SUMMARY.json').read_text());need(hs['pass']and hs['model_and_bundle_unchanged'],'Historical gate failed')
 visibility=[]
 for version in ['v024','v025']:
  fresh=json.loads((out/'historical'/(version+'_visibility.json')).read_text());old=json.loads((historical/'evidence'/(version+'_visibility.json')).read_text())
  def normalized(d):
   rows=[]
   for r in d['samples']:
    r=dict(r);r['receipt_sha256']=d['inputs'][r.pop('receipt')];rows.append(r)
   return {'model_sha256':d['model_sha256'],'source_unchanged':d['source_unchanged'],'selection':d['selection'],'samples':rows,'scope':d['scope']}
  need(normalized(fresh)==normalized(old),'Finite visibility semantics changed: '+version);visibility.append({'version':version,'same_semantics_after_receipt_path_normalization':True,'samples':len(fresh['samples'])})
 run([sys.executable,'-B',str(qa/'run_qa.py'),'--source',str(v25),'--candidate',str(candidate),'--output-dir',str(out/'model'),'--blender',str(blender)],'model')
 ms=json.loads((out/'model/SUMMARY.json').read_text());need(ms['pass']and ms['bundle_inventory_unchanged']and ms['all_model_inputs_unchanged'],'V026 model gate failed')
 for name,root in [('historical_guards',historical),('model_guards',qa)]:run([sys.executable,'-B',str(root/'test_runner.py')],name)
 need(before==inventory(archive),'Fresh archive inventory changed');need(all(sha(f)==h for f,h in expected.items()),'Model input changed')
 summary={'pass':True,'parent_verified_remote_commit':a.commit,'exact_model_sha256':{str(f):h for f,h in expected.items()},'archive_files_unchanged':len(before),'v026_qa_manifest':sha(qa/'FILES.json'),'historical_qa_manifest':sha(historical/'FILES.json'),'historical_visibility_exact_after_path_normalization':visibility,'historical_summary_sha256':sha(out/'historical/SUMMARY.json'),'model_summary_sha256':sha(out/'model/SUMMARY.json'),'native_call_count':10,'guard_tests':26,'commands':commands,'scope':'Fresh Git-only frozen-runtime replays, no renders or canonical saves. Historical zero-adjacency conclusions remain superseded; inherited visible-contact candidates are deferred, not silently repaired.'};(out/'REMOTE_SUMMARY.json').write_text(json.dumps(summary,indent=2));print('REMOTE FULL GATES PASS')
if __name__=='__main__':main()
