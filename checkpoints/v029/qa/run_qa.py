"""Portable read-only v029 QA orchestration. No render, save, install or overwrite."""
import argparse,gzip,hashlib,json,os,re,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE='f0d135e0c6e554b5ae7c520ef9ccefc61e2a7c4abc3129eef1d3d4118bca8096'
ACCEPTED='4f838529d32cbf6a0314cc0a23b3dd1703b73d80c5db146fb4d323697b882df5'
EXPORT='6e9d81a2f541dbce41d98714925a4f5d537603731a177022a7f3b3c0865426c5'
def need(x,msg):
 if not x:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clean(value,exists=True):
 p=Path(value).expanduser().absolute();need('..' not in p.parts,'Parent traversal refused');need(all(not q.is_symlink() for q in [p,*p.parents]) and p.resolve()==p,'Symlink/alias refused')
 need(p.is_file() if exists else p.parent.is_dir() and not os.path.lexists(p),'Missing input or occupied output');return p
def role_guard(paths):need(len({(p.stat().st_dev,p.stat().st_ino) for p in paths})==len(paths),'Input role inode alias')
def digest_string(v):need(bool(re.fullmatch('[0-9a-f]{64}',v)),'Malformed SHA256');return v
def inventory(root):
 result={}
 for p in sorted(root.rglob('*')):
  need(not p.is_symlink(),'Symlink in bundle')
  if p.is_file():result[p.relative_to(root).as_posix()]=sha(p)
 return result
def bundle_guard():
 manifest=json.loads((ROOT/'FILES.json').read_text());actual=inventory(ROOT);need(set(actual)==set(manifest['files'])|{'FILES.json'},'Bundle inventory drift');need(all(actual[k]==h for k,h in manifest['files'].items()),'Bundle content drift');return actual
def main():
 need(not sys.flags.optimize,'Optimized Python refused')
 ap=argparse.ArgumentParser()
 for k in ['blender','source','candidate','candidate-sha','output-dir']:ap.add_argument('--'+k,required=True)
 ap.add_argument('--accepted');ap.add_argument('--preflight-only',action='store_true');a=ap.parse_args()
 before=bundle_guard();source=clean(a.source);candidate=clean(a.candidate);blender=clean(a.blender);out=clean(a.output_dir,False);ch=digest_string(a.candidate_sha);accepted=clean(a.accepted)if a.accepted else None
 need(not out.is_relative_to(ROOT),'Output inside frozen bundle');need(all(not out.is_relative_to(p.parent)for p in [source,candidate]+([accepted]if accepted else [])),'Output inside model input directory');role_guard([source,candidate])
 need(sha(source)==SOURCE and sha(candidate)==ch,'Wrong source/candidate SHA');need(ch==ACCEPTED or accepted is not None,'Rebuilt candidate requires accepted semantic reference')
 if accepted:need(sha(accepted)==ACCEPTED,'Wrong accepted reference')
 with gzip.open(ROOT/'data/native.json.gz','rb')as f:raw=f.read(40*1024*1024+1)
 need(len(raw)<=40*1024*1024 and hashlib.sha256(raw).hexdigest()==EXPORT,'Wrong decoded source export')
 pins={str(p):sha(p)for p in [source,candidate,blender]+([accepted]if accepted else [])}
 env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env.pop('PYTHONOPTIMIZE',None)
 version=subprocess.run([str(blender),'--version'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,text=True);need(version.returncode==0 and version.stdout.startswith('Blender 5.2.3'),'Requires Blender 5.2.3')
 if a.preflight_only:print('PREFLIGHT PASS; no output created');return
 out.mkdir();data=out/'data';data.mkdir()
 for p in (ROOT/'data').iterdir():
  if p.suffix!='.gz':shutil.copyfile(p,data/p.name)
 (data/'native.json').write_bytes(raw);data_before=inventory(data)
 env['V029_QA_DATA']=str(data);env['V029_QA_OUTPUT']=str(out);env['XDG_CACHE_HOME']=str(out/'cache')
 commands=[]
 def unchanged():need(inventory(ROOT)==before and inventory(data)==data_before and all(sha(p)==h for p,h in pins.items()),'Immutable bundle/data/model/executable changed')
 def run(script,args=(),native=False):
  command=([str(blender),'--background','--factory-startup','--disable-autoexec','--threads','4','--python-exit-code','1','--python-expr','import sys; sys.dont_write_bytecode=True','--python',str(ROOT/script),'--']if native else[sys.executable,'-B',str(ROOT/script)])+list(map(str,args));log=out/('%02d_%s.log'%(len(commands)+1,Path(script).stem))
  with log.open('xb')as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,cwd=out,env=env)
  commands.append({'command':command,'native':native,'returncode':r.returncode,'log':log.name});need(r.returncode==0,'Child failed; see '+str(log));unchanged()
 if accepted:run('compare_saved.py',['--accepted',accepted,'--candidate',candidate,'--candidate-sha',ch,'--report',out/'REPEAT.json'],True)
 run('validate_final.py',['--source',source,'--candidate',candidate,'--candidate-sha',ch,'--payload',data/'payload.json','--report',out/'SAVED_PRESERVATION.json','--geometry',out/'saved_geometry.json','--fixtures',out/'saved_fixtures.json'],True)
 run('native_controls.py',['--candidate',candidate,'--candidate-sha',ch,'--payload',data/'payload.json','--report',out/'NATIVE_CONTROLS.json'],True)
 run('check_guard.py',['--export',data/'native.json','--plan',data/'guard_plan.json','--output',out/'GUARD_PROOF.json'])
 run('check_payload.py',['--payload',data/'payload.json','--report',out/'PAYLOAD_PROOF.json'])
 for script in ['test_guard.py','test_payload.py','check_quantized_routes.py','check_fixtures_views.py','check_saved.py','check_saved_neighbors.py','check_saved_visibility.py']:run(script)
 names=['SAVED_PRESERVATION.json','NATIVE_CONTROLS.json','GUARD_PROOF.json','PAYLOAD_PROOF.json','NEGATIVE_CONTROLS.json','PAYLOAD_CONTROLS.json','QUANTIZED_ROUTES.json','FIXTURE_VIEW_PROOF.json','SAVED_GEOMETRY_PROOF.json','SAVED_VISIBILITY.json']+(['REPEAT.json']if accepted else[])
 for n in names:need(json.loads((out/n).read_text())['pass'],'False JSON gate '+n)
 adjacent=json.loads((out/'SAVED_NEIGHBORS.json').read_text());need(adjacent['candidate_sha256']==ch and not any(p['same_facing']for c in adjacent['contacts']for p in c['planes']),'Unexpected local same-facing coplanar patch')
 for n in ['SAVED_PRESERVATION.json','NATIVE_CONTROLS.json','SAVED_GEOMETRY_PROOF.json','SAVED_VISIBILITY.json']:need(json.loads((out/n).read_text())['candidate_sha256']==ch,'Candidate identity drift '+n)
 need(json.loads((out/'PAYLOAD_CONTROLS.json').read_text())['count']==8 and json.loads((out/'NEGATIVE_CONTROLS.json').read_text())['count']==7,'Control count drift');need(len(json.loads((out/'NATIVE_CONTROLS.json').read_text())['controls'])==4,'Native control count drift');unchanged()
 result={'pass':True,'source_sha256':SOURCE,'candidate_sha256':ch,'accepted_reference_sha256':ACCEPTED if accepted else None,'bundle_manifest_sha256':sha(ROOT/'FILES.json'),'input_sha256':pins,'native_calls':sum(c['native']for c in commands),'python_calls':sum(not c['native']for c in commands),'commands':commands,'controls':{'guard':7,'exported_payload_and_math':8,'focused_native_mutations':4},'report_sha256':{n:sha(out/n)for n in names+['SAVED_NEIGHBORS.json']},'bundle_unchanged':True,'decoded_data_unchanged':True,'models_unchanged':True,'limits':'Read-only source and bounded geometry QA. No render/save or structural/global-access claim.'};(out/'SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n');print('PUBLIC V029 QA PASS')
if __name__=='__main__':main()
