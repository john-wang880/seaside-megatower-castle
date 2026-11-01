#!/usr/bin/env python3
"""Read-only-input v019 reproduction controller; existing Linux Blender5.2.3 only."""
import argparse,gzip,hashlib,json,os,re,subprocess,sys,time
from pathlib import Path
BASE='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd'
ACCEPTED='e71778349c4c65eafbda3eb0a3d0753cd11e1b368a3456c4de1db2f4c0f8647a'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def require(condition,message):
 if not condition:raise RuntimeError(message)
def verify_mapping(generated,accepted_gzip):
 with gzip.open(accepted_gzip,'rt',encoding='utf-8') as f:expected=json.load(f)
 require(json.loads(Path(generated).read_text())==expected,'Generated mapping semantic drift against accepted public mapping')

def parser():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['baseline','accepted-model','blender','output-dir']:p.add_argument('--'+n,required=True,type=Path)
 p.add_argument('--dry-run',action='store_true',help='Validate paths/hashes and print plan only; no subprocess or writes')
 return p
def preflight(a,root):
 require(not sys.flags.optimize,'Optimized Python unsupported')
 require(sys.platform.startswith('linux'),'Validated platform is Linux; no Windows compatibility claim')
 baseline=a.baseline.expanduser().resolve(strict=True);accepted=a.accepted_model.expanduser().resolve(strict=True);blender=a.blender.expanduser().resolve(strict=True)
 raw=a.output_dir.expanduser().absolute();require(not raw.exists() and not raw.is_symlink(),'Output must be a new nonexistent directory')
 out=raw.resolve();require(out not in root.parents and root not in out.parents and out!=root,'Output must not overlap controller bundle')
 require(baseline!=accepted,'Inputs must be distinct')
 for p,h in [(baseline,BASE),(accepted,ACCEPTED)]:require(p.is_file() and sha(p)==h,'Pinned model hash mismatch: '+str(p));require(out!=p and out not in p.parents and p not in out.parents,'Input/output overlap')
 require(blender.is_file() and os.access(blender,os.X_OK),'Existing executable Blender required; no installation or download')
 paths=[root/'generator/generate_conifer.py',root/'qa/validate_preservation.py',root/'qa/validate_new_geometry.py',root/'qa/audit_tube_folds.py',root/'integration/integrate_conifer.py',root/'integration/deep_snapshot.py',root/'inputs/source_components.json',root/'inputs/v018_route_envelope.json',root/'inputs/component_contact_mapping.json.gz']
 require(all(p.is_file() for p in paths),'Incomplete relative bundle')
 bundle={str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix in ['.py','.json','.md','.gz']}
 return baseline,accepted,blender,out,bundle

def run(a,root=None):
 root=(root or Path(__file__).resolve().parent).resolve();baseline,accepted,blender,out,bundle=preflight(a,root)
 plan={'baseline_sha256':BASE,'accepted_model_sha256':ACCEPTED,'blender_executable':str(blender),'output_directory':str(out),'bundle_sha256':bundle,'steps':['generate','accepted_asset_semantic_guard','integrate','preservation','geometry_contact','tube_folds'],'no_render':True,'no_publish':True}
 if a.dry_run:print(json.dumps(plan,indent=2));return plan
 out.mkdir(parents=True,exist_ok=False);logs=out/'logs';logs.mkdir();reports=out/'reports';reports.mkdir()
 record={**plan,'status':'RUNNING','started_unix':time.time(),'steps_completed':[],'inputs_before':{str(baseline):sha(baseline),str(accepted):sha(accepted),str(blender):sha(blender)}}
 def write():
  (out/'receipt.json').write_text(json.dumps(record,indent=2))
 def stable():
  require(all(sha(Path(p))==h for p,h in record['inputs_before'].items()),'Input/executable mutated')
  now={str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix in ['.py','.json','.md','.gz']}
  require(now==bundle,'Bundle code/data changed during run')
 def command(label,script,args,report=None,gate=None):
  stable();argv=[str(blender),'--background','--factory-startup','--disable-autoexec','--python-exit-code','1','--threads','8','--python',str(script),'--',*map(str,args)]
  env=os.environ.copy();env.pop('PYTHONOPTIMIZE',None)
  started=time.time()
  with (logs/(label+'.log')).open('xb') as f:result=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT,cwd=str(out),env=env,check=False)
  require(result.returncode==0,label+' subprocess failed; inspect log')
  stable()
  if report:
   require(report.is_file(),label+' missing receipt');data=json.loads(report.read_text());require(gate(data),label+' report failed semantic gate')
  record['steps_completed'].append({'name':label,'argv':argv,'seconds':time.time()-started,'report':str(report) if report else None});write()
 try:
  write()
  version=subprocess.run([str(blender),'--version'],capture_output=True,text=True,check=False)
  require(version.returncode==0 and re.search(r'^Blender 5\.2\.3(?:\s|$)',version.stdout,re.M),'Exact Blender5.2.3 required')
  record['blender_version']=version.stdout;write()
  generated=out/'generated';asset=generated/'generated_conifer.blend';mapping=generated/'component_contact_mapping.json'
  command('generate',root/'generator/generate_conifer.py',['--baseline',baseline,'--output-dir',generated],generated/'runtime_report.json',lambda d:d.get('baseline_sha256_after')==BASE and d.get('source_saved') is False and d.get('rendered') is False)
  require(asset.is_file() and mapping.is_file(),'Generator omitted asset/mapping');verify_mapping(mapping,root/'inputs/component_contact_mapping.json.gz');asset_sha=sha(asset);mapping_sha=sha(mapping)
  record['generated_asset_sha256']=asset_sha;record['generated_mapping_sha256']=mapping_sha
  def preserved(checkpoint,name):
   r=reports/(name+'.json');command(name,root/'qa/validate_preservation.py',['--baseline',baseline,'--checkpoint',checkpoint,'--asset',asset,'--asset-sha256',asset_sha,'--accepted-model',accepted,'--source-components',root/'inputs/source_components.json','--report',r],r,lambda d:d.get('pass') is True and d.get('generated_asset_semantic_manifest',{}).get('pass') is True)
  preserved(accepted,'accepted_asset_semantic_guard')
  candidate=out/'reproduced_candidate.blend';integration=reports/'integration.json'
  command('integrate',root/'integration/integrate_conifer.py',['--source',baseline,'--asset',asset,'--asset-sha256',asset_sha,'--output',candidate,'--report',integration,'--snapshot-helper',root/'integration/deep_snapshot.py'],integration,lambda d:d.get('source_unchanged') is True and d.get('asset_unchanged') is True and all(d.get('checks',{}).values()) and bool(d.get('checks')))
  preserved(candidate,'preservation')
  common=['--candidate',candidate,'--mapping',mapping,'--route-report',root/'inputs/v018_route_envelope.json']
  geom=reports/'geometry.json';command('geometry_contact',root/'qa/validate_new_geometry.py',common+['--report',geom],geom,lambda d:d.get('geometry_and_attachment_pass') is True and d.get('issues')==[])
  folds=reports/'tube_folds.json';command('tube_folds',root/'qa/audit_tube_folds.py',common+['--report',folds],folds,lambda d:d.get('folded_components')==[] and d.get('components_tested')==3199)
  require(sha(asset)==asset_sha and sha(mapping)==mapping_sha,'Generated inputs changed after creation');stable()
  record.update(status='REPRODUCTION_VALIDATED_NOT_NEW_ACCEPTANCE',candidate_sha256=sha(candidate),candidate_bytes=candidate.stat().st_size,inputs_unchanged=True,bundle_unchanged=True,finished_unix=time.time(),limits=['Reproduced .blend file bytes may differ from accepted e717 despite exact semantic checks','No render, publication, new version or new art acceptance','Open-backed needles, legacy open-ended trunk section proxy and bounded route checks remain'])
  write();return record
 except BaseException as e:
  record.update(status='FAILED',error=repr(e),finished_unix=time.time())
  try:stable();record['inputs_unchanged']=True;record['bundle_unchanged']=True
  except BaseException as audit:record['integrity_failure']=repr(audit)
  write();raise
if __name__=='__main__':run(parser().parse_args())
