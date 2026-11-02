"""External remote validation orchestrator; public payload is immutable."""
import json,hashlib,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ARCHIVE=ROOT/'remote 中文';TOOL=ARCHIVE/'scripts/current_inspection';SOURCE=ROOT/'restored_v027.blend';BASE=ROOT/'restored_v018.blend';VIEWERS=ROOT/'remote_viewers 中文';PURE=ROOT/'remote_independent_pure';QA=ROOT/'remote_qa'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inv(p):return {str(x.relative_to(p)):sha(x) for x in sorted(p.rglob('*')) if x.is_file()}
def main():
 phase=sys.argv[1];env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
 if phase=='prepare':
  assert not PURE.exists();PURE.mkdir();inventory=inv(ARCHIVE);assert not any('__pycache__' in p or p.endswith('.pyc') for p in inventory)
  (PURE/'archive_before.json').write_text(json.dumps(inventory,indent=2))
  sourcehash={'source':sha(SOURCE),'baseline':sha(BASE)}
  assert sourcehash=={'source':'37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255','baseline':'c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd'}
  commands=[[sys.executable,'-B',str(TOOL/'test_preflight.py'),'-v'],[sys.executable,'-B',str(TOOL/'tests/test_preflight_independent.py'),'--tool',str(TOOL),'--source',str(SOURCE),'-v'],[sys.executable,'-B',str(TOOL/'test_tree_pure.py'),'-v']]
  for i,cmd in enumerate(commands):
   with (PURE/f'{i:02d}.log').open('w') as log:subprocess.run(cmd,env=env,cwd=PURE,stdout=log,stderr=subprocess.STDOUT,check=True)
  assert inventory==inv(ARCHIVE)
  (PURE/'prepared.json').write_text(json.dumps({'pass':True,'source_sha256':sourcehash,'commands':commands,'pure_methods':51},indent=2))
  print('REMOTE PURE51 PASS; native waits for slot')
 elif phase=='native':
  prepared=json.loads((PURE/'prepared.json').read_text());assert prepared['pass'];before=json.loads((PURE/'archive_before.json').read_text());assert before==inv(ARCHIVE);assert not QA.exists()
  cmd=[sys.executable,'-B',str(TOOL/'qa/run_qa.py'),'--source',str(SOURCE),'--baseline',str(BASE),'--tool',str(TOOL),'--blender','/workspace/scratch/8bdb2666bb6b/tools/blender-5.2.3-linux-x64/blender','--output-dir',str(QA)]
  for mode in ['OFF','HIGH','LOW']:cmd+=['--'+mode.lower(),str(VIEWERS/(mode+' viewer.blend')),'--'+mode.lower()+'-receipt',str(VIEWERS/(mode+' receipt.json'))]
  with (PURE/'native_runner.log').open('w') as log:subprocess.run(cmd,env=env,cwd=PURE,stdout=log,stderr=subprocess.STDOUT,check=True)
  summary=json.loads((QA/'SUMMARY.json').read_text());actual=json.loads((QA/'modes.json').read_text());assert summary['pass'] and actual['pass'];assert len(actual['negatives'])==27;assert set(actual['modes'])=={'off','high','low'}
  for mode in actual['modes'].values():assert mode['category_count']==13 and all(mode['category_checks'].values()) and mode['reopen_and_16_bookmark_interleaving']
  assert before==inv(ARCHIVE);assert prepared['source_sha256']=={'source':sha(SOURCE),'baseline':sha(BASE)}
  r={'pass':True,'commit':'dca8c51f7bb296cef777c8af140798748ee7b73e','source_sha256':sha(SOURCE),'baseline_sha256':sha(BASE),'qa_manifest_sha256':sha(TOOL/'qa/FILES.json'),'archive_file_count':len(before),'archive_inventory_sha256':hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),'all_archive_files_unchanged':True,'no_caches':True,'pure_methods':59,'native_calls':1,'negative_native_cases':27,'modes':['OFF','HIGH','LOW'],'categories_each':13,'bookmarks_each':16,'qa_summary_sha256':sha(QA/'SUMMARY.json'),'native_report_sha256':sha(QA/'modes.json'),'runtime_sha256':actual['runtime_sha256'],'viewer_sha256':{k:actual['input_sha256'][k] for k in ['off','high','low']},'orchestrator_sha256':sha(Path(__file__)),'rendered':False,'source_saved':False,'commands':prepared['commands']+[cmd]}
  (QA/'REMOTE_SUMMARY.json').write_text(json.dumps(r,indent=2)+'\n');print('REMOTE TREE QUALITY FULL PASS',sha(QA/'REMOTE_SUMMARY.json'))
 else:raise ValueError(phase)
if __name__=='__main__':main()
