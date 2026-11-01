"""Read-only portable historical-v024-v025 QA orchestration, no render or model save."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
if sys.flags.optimize:raise RuntimeError('Optimized Python unsupported')
SOURCE_SHA='89f9f6a8a57103d99100935b96624469ddf1fd52b9703e0d9177a352e735c856'
ACCEPTED_SHA='8a3590082c99a69d50d444f77165fae57fb611cf069cecda03fdf0c6c17cadd2'
def need(ok,message):
 if not ok:raise RuntimeError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inventory(p):return {str(f.relative_to(p)):sha(f)for f in p.rglob('*')if f.is_file()}
def clean_path(value):
 p=Path(value).absolute();need('..'not in p.parts,'Parent traversal unsupported')
 for q in [p,*p.parents]:need(not q.is_symlink(),'Symlink paths unsupported')
 return p.resolve()
def preflight(source,candidate,accepted,out,qa):
 need(not out.exists()and out.parent.is_dir(),'New output directory in existing parent required')
 need(not out.is_relative_to(qa)and 'checkpoints'not in out.parts,'Reports must stay outside frozen bundle/checkpoint trees')
 need(source.is_file()and candidate.is_file(),'Source and candidate files required')
 need(source!=candidate,'Source/candidate alias')
 need(sha(source)==SOURCE_SHA,'Wrong historical source SHA')
 ch=sha(candidate)
 need(ch==ACCEPTED_SHA and accepted is None,'Exact two historical models required; no rebuild substitution')
 manifest=json.loads((qa/'FILES.json').read_text());need(all(sha(qa/k)==v for k,v in manifest.items()),'QA payload checksum mismatch');need(set(inventory(qa))==set(manifest)|{'FILES.json'},'Unexpected bundle files/cache')
 return ch

def main():
 p=argparse.ArgumentParser()
 for k in ['source','candidate','output-dir','blender']:p.add_argument('--'+k,required=True)

 a=p.parse_args();qa=Path(__file__).resolve().parent;source=clean_path(a.source);candidate=clean_path(a.candidate);out=clean_path(a.output_dir);blender=clean_path(a.blender);accepted=None
 need(blender.is_file(),'Blender executable missing');ch=preflight(source,candidate,accepted,out,qa);before=inventory(qa);models={str(x):sha(x)for x in [source,candidate]+([accepted]if accepted else [])};out.mkdir();commands=[]
 def run(script,args,label,bl=False):
  if bl:cmd=[str(blender),'-b','--factory-startup','--disable-autoexec','--python-exit-code','1','--python-expr','import sys; sys.dont_write_bytecode=True','--python',str(qa/script),'--']+list(map(str,args))
  else:cmd=[sys.executable,'-B',str(qa/script)]+list(map(str,args))
  commands.append(cmd)
  with (out/(label+'.log')).open('w')as log:r=subprocess.run(cmd,cwd=out,stdout=log,stderr=subprocess.STDOUT,env={**__import__('os').environ,'PYTHONDONTWRITEBYTECODE':'1'})
  need(r.returncode==0,'Failed gate '+label+'; inspect its log')
 def checked(name):
  d=json.loads((out/name).read_text());need(d.get('pass')is True,'JSON gate not passing: '+name);return d
 run('test_coplanar_predicate.py',['--report',out/'controls.json'],'controls');need(len(checked('controls.json')['controls'])==9,'Nine corrected-predicate controls required')
 for version,model,h,unions in [('v024',source,SOURCE_SHA,['V024 | exact evaluated rear stepped union']),('v025',candidate,ACCEPTED_SHA,[f'V025 | exact evaluated rear return union {i:02d}'for i in range(1,5)])]:
  args=['--model',model,'--sha256',h,'--report',out/(version+'.json')]
  for name in unions:args+=['--union',name]
  run('adjacent_saved.py',args,version+'_adjacent',True);d=json.loads((out/(version+'.json')).read_text());need(d['source_unchanged']and d['model_sha256']==h,'Historical source drift')
  # Exact deterministic contact output is compared to the archived completed recheck.
  expected=json.loads((qa/'evidence'/(version+'.json')).read_text());need(d==expected,'Historical corrected contact report differs; investigate before claiming replay')
  run('link_original_boundary.py',['--contacts',out/(version+'.json'),'--geometry',qa/(version+'_geometry.json'),'--preservation',qa/(version+'_preservation.json'),'--report',out/(version+'_original_boundary.json')],version+'_boundary_link');checked(version+'_original_boundary.json')
  args=['--model',model,'--contacts',out/(version+'.json'),'--report',out/(version+'_visibility.json')]
  for view in ['hero','rear']+(['lateral']if version=='v025'else[]):args+=['--receipt',qa/f'{version}_{view}_receipt.json']
  run('contact_visibility.py',args,version+'_visibility',True);need(json.loads((out/(version+'_visibility.json')).read_text())['source_unchanged'],'Visibility source changed')
 need(before==inventory(qa),'Frozen historical bundle changed');need(all(sha(p)==h for p,h in models.items()),'Historical model changed')
 (out/'SUMMARY.json').write_text(json.dumps({'pass':True,'models':models,'bundle_manifest_sha256':sha(qa/'FILES.json'),'commands':commands,'model_and_bundle_unchanged':True,'historical_zero_contact_claim_superseded':True,'scope':'Replays corrected neighbor contacts and finite camera rays. Archived full-scene preservation and original-operand geometry are explicit evidence dependencies, not silently reexecuted source builds. No repair or visual/global absence certification.'},indent=2));print('HISTORICAL RECHECK PASS')
if __name__=='__main__':main()
