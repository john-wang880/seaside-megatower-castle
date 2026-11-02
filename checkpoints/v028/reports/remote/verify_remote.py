"""Owner-authorized remote archive orchestration only; no private recipe imports.
Run only after explicit native-slot grant. Rebuilds new outputs, never renders/saves inputs.
"""
import argparse,hashlib,json,os,re,subprocess,sys
from pathlib import Path
SOURCE='37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255'
ACCEPTED='f0d135e0c6e554b5ae7c520ef9ccefc61e2a7c4abc3129eef1d3d4118bca8096'
QA_MANIFEST='c1f9a87b267f78e6d24b507383fe18a1f9006d746e3df58bc30b5e53f077ac85'
RECIPE_MANIFEST='076c809079043523d2c45609e7729fc6556b4ec6d7ade506d6402b6f032d7580'
PAYLOAD='0d07d8ceb27f44cd3c612392d56b40921e60c7f8afaa522aa04f74c17df817f2'
BLENDER='/workspace/scratch/8bdb2666bb6b/tools/blender-5.2.3-linux-x64/blender'
def need(x,msg):
 if not x:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def safe(v,kind):
 p=Path(v).expanduser().absolute();need('..' not in p.parts and p.resolve()==p and all(not q.is_symlink() for q in [p,*p.parents]),'Aliased path')
 need(p.is_file() if kind=='file' else p.is_dir() if kind=='dir' else p.parent.is_dir() and not os.path.lexists(p),'Wrong path state: '+str(p));return p
def inventory(root):
 d={}
 for p in sorted(root.rglob('*')):
  need(not p.is_symlink(),'Symlink inside archive')
  if p.is_file():d[p.relative_to(root).as_posix()]=sha(p)
 return d

def main():
 need(not sys.flags.optimize,'Optimized Python refused')
 p=argparse.ArgumentParser(description=__doc__)
 for k in ('archive','source','accepted','output-dir','commit'):p.add_argument('--'+k,required=True)
 p.add_argument('--blender',default=BLENDER);p.add_argument('--preflight-only',action='store_true');a=p.parse_args();need(bool(re.fullmatch('[0-9a-f]{40}',a.commit)),'Malformed supplied Git commit')
 archive=safe(a.archive,'dir');src=safe(a.source,'file');accepted=safe(a.accepted,'file');out=safe(a.output_dir,'new');blender=safe(a.blender,'file')
 need(src.is_relative_to(archive) and accepted.is_relative_to(archive),'Models must be restored in the provided fresh archive');need(not out.is_relative_to(archive),'Output must be external to immutable archive');need((src.stat().st_dev,src.stat().st_ino)!=(accepted.stat().st_dev,accepted.stat().st_ino),'Model role alias')
 need(sha(src)==SOURCE and sha(accepted)==ACCEPTED,'Wrong restored model identity')
 qa=archive/'checkpoints/v028/qa';recipe=archive/'checkpoints/v028/reproduce';need(sha(qa/'FILES.json')==QA_MANIFEST and sha(recipe/'FILES.json')==RECIPE_MANIFEST,'Wrong public bundle manifests')
 before=inventory(archive);pins={str(src):SOURCE,str(accepted):ACCEPTED,str(blender):sha(blender),str(Path(__file__).resolve()):sha(__file__)}
 if a.preflight_only:print('REMOTE PREFLIGHT PASS; no process launched/output created');return
 out.mkdir();cache=out/'cache';cache.mkdir();env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env.pop('PYTHONOPTIMIZE',None);env['XDG_CACHE_HOME']=str(cache)
 (out/'ARCHIVE_BEFORE.json').write_text(json.dumps(before,indent=2)+'\n');commands=[];report={'pass':False,'supplied_verified_remote_commit':a.commit,'archive':str(archive),'archive_files':len(before),'source_sha256':SOURCE,'accepted_sha256':ACCEPTED,'qa_manifest_sha256':QA_MANIFEST,'reproduction_manifest_sha256':RECIPE_MANIFEST,'input_sha256':pins,'commands':commands}
 def stable():return inventory(archive)==before and all(sha(f)==h for f,h in pins.items())
 def run(name,argv):
  with (out/(name+'.log')).open('xb') as stream:r=subprocess.run(argv,cwd=out,env=env,stdout=stream,stderr=subprocess.STDOUT)
  commands.append({'name':name,'argv':list(map(str,argv)),'returncode':r.returncode,'log_sha256':sha(out/(name+'.log'))});need(r.returncode==0,name+' failed; see retained log');need(stable(),'Immutable input changed after '+name)
 try:
  rebuilt_dir=out/'rebuilt';run('reproduction',[sys.executable,'-B',str(recipe/'reproduce.py'),'--source',str(src),'--blender',str(blender),'--output-dir',str(rebuilt_dir)])
  receipt=json.loads((rebuilt_dir/'REPRODUCTION.json').read_text());rebuilt=rebuilt_dir/'castle_receiving_chamber.blend'
  need(receipt['status']=='REPRODUCED_PENDING_INDEPENDENT_SEMANTIC_QA' and receipt['all_inputs_unchanged'] is True,'Reproduction receipt failed');need(len(receipt['stages'])==3 and all(x['returncode']==0 for x in receipt['stages']),'Wrong reproduction stage outcomes');need(receipt['final_sha256']==sha(rebuilt) and receipt['geometry_sha256']==PAYLOAD,'Rebuilt/payload identity mismatch')
  qaout=out/'qa';run('independent_qa',[sys.executable,'-B',str(qa/'run_qa.py'),'--blender',str(blender),'--source',str(src),'--candidate',str(rebuilt),'--candidate-sha',sha(rebuilt),'--accepted',str(accepted),'--reference-export',str(recipe/'native.json.gz'),'--output-dir',str(qaout)])
  summary=json.loads((qaout/'SUMMARY.json').read_text());need(summary['pass'] is True and summary['source_sha256']==SOURCE and summary['candidate_sha256']==sha(rebuilt) and summary['accepted_reference_sha256']==ACCEPTED,'Independent identity/gate failed');need(summary['native_calls']==3 and summary['python_calls']==13,'Unexpected public QA command counts');need(all(summary[k] is True for k in ['bundle_unchanged','decoded_copied_data_unchanged','model_inputs_unchanged']),'QA immutable gate failed');need(all(sha(qaout/n)==h for n,h in summary['report_sha256'].items()),'Referenced QA report hash mismatch')
  repeat=json.loads((qaout/'repeat.json').read_text());need(repeat['pass'] is True and all(v is True for v in repeat['checks'].values()),'Saved semantic repeat failed')
  report.update(pass_=True,rebuilt_sha256=sha(rebuilt),reproduction_receipt_sha256=sha(rebuilt_dir/'REPRODUCTION.json'),qa_summary_sha256=sha(qaout/'SUMMARY.json'),qa_report_count=len(summary['report_sha256']),reproduction_stages=3,reproduction_model_native_calls=2,qa_native_calls=3,qa_python_calls=13,blender_version_queries=1,whole_archive_unchanged=True,limits=['Supplied Git commit provenance is owner-verified; this helper does not fetch or authenticate Git remotely.','Rebuilt save bytes may differ; full persistent/evaluated semantic equality and actual QA gates are required.','No additional rendering, source/model acceptance renaming, publication or old-payload cleanup.'])
  report['pass']=report.pop('pass_');need(stable(),'Final archive/input drift')
 except BaseException as e:
  report['error']=type(e).__name__+': '+str(e);report['whole_archive_unchanged']=stable();raise
 finally:
  (out/'REMOTE_SUMMARY.json').write_text(json.dumps(report,indent=2)+'\n')
 print('REMOTE V028 REBUILD + FULL QA PASS',report['rebuilt_sha256'])
if __name__=='__main__':main()
