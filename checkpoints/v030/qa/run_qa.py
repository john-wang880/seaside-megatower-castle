"""Portable sequential read-only QA. No installs, renders, model saves, or implicit long jobs."""
import argparse,gzip,hashlib,json,os,re,subprocess,sys
from pathlib import Path
SOURCE='4f838529d32cbf6a0314cc0a23b3dd1703b73d80c5db146fb4d323697b882df5'
ACCEPTED='9f020b7ec6eda309d674653598b169f65ba5dc1d1f194ffa31323f6393feda35'
B=Path(__file__).resolve().parent

def need(v,m):
 if not v:raise RuntimeError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clean(p):
 p=Path(p).expanduser();need('..'not in p.parts,'Parent traversal refused');p=p.absolute()
 for x in [p,*p.parents]:need(not x.is_symlink(),'Symlink refused: '+str(x))
 return p
def inventory(p):return {str(x.relative_to(p)):sha(x)for x in sorted(p.rglob('*'))if x.is_file()}
def verify_bundle():
 m=json.loads((B/'FILES.json').read_text());actual=inventory(B);actual.pop('FILES.json');need(actual==m,'Frozen bundle inventory mismatch');return inventory(B)
def main():
 need(not sys.flags.optimize,'Optimized Python refused')
 p=argparse.ArgumentParser()
 for k in ['blender','source','candidate','candidate-sha','output-dir']:p.add_argument('--'+k,required=True)
 p.add_argument('--accepted');a=p.parse_args();before=verify_bundle()
 source=clean(a.source);candidate=clean(a.candidate);blender=clean(a.blender);out=clean(a.output_dir);accepted=clean(a.accepted)if a.accepted else candidate
 need(re.fullmatch('[0-9a-f]{64}',a.candidate_sha),'Malformed candidate hash')
 need(source.is_file()and candidate.is_file()and accepted.is_file()and blender.is_file(),'Missing input')
 need(sha(source)==SOURCE and sha(candidate)==a.candidate_sha and sha(accepted)==ACCEPTED,'Pinned model identity')
 need(source!=candidate and source!=accepted,'Source alias')
 need(not out.exists()and out.parent.is_dir(),'Output must be new with existing parent')
 for root in [B,source.parent,candidate.parent,accepted.parent]:need(not out.is_relative_to(root),'Output inside immutable input directory')
 modelpins={str(x):sha(x)for x in [source,candidate,accepted]};out.mkdir();inputs=out/'inputs';inputs.mkdir();pins=json.loads((B/'data/INPUTS.json').read_text())
 for n,h in pins.items():
  raw=gzip.decompress((B/'data'/(n+'.gz')).read_bytes());need(hashlib.sha256(raw).hexdigest()==h,'Derived input hash');(inputs/n).write_bytes(raw)
 derived=inventory(inputs)
 # This is an explicit expected-geometry contract, not a claim that frozen builder created rebuilt bytes.
 receipt=json.loads((inputs/'build.json').read_text());receipt['candidate_sha256']=a.candidate_sha;(out/'expected_geometry_contract.json').write_text(json.dumps(receipt,indent=2)+'\n')
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',FITTINGS_QA_INPUTS=str(inputs),FITTINGS_QA_OUTPUT=str(out),XDG_CACHE_HOME=str(out/'cache'))
 commands=[]
 def run(args):
  commands.append([str(x)for x in args]);log=out/('%02d.log'%len(commands))
  with log.open('xb')as f:r=subprocess.run(commands[-1],cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT)
  need(r.returncode==0,'Command failed, see '+str(log))
 def native(script,args):run([blender,'--background','--factory-startup','--disable-autoexec','--threads','4','--python-exit-code','1','--python-expr','import sys; sys.dont_write_bytecode=True','--python',B/script,'--',*args])
 native('compare_repeat.py',['--accepted',accepted,'--candidate',candidate,'--candidate-sha',a.candidate_sha,'--report',out/'REPEAT.json'])
 native('validate_saved.py',['--source',source,'--candidate',candidate,'--candidate-sha',a.candidate_sha,'--build-report',out/'expected_geometry_contract.json','--report',out/'PRESERVATION.json','--geometry',out/'geometry.json'])
 run([sys.executable,'-B',B/'audit_geometry.py','--geometry',out/'geometry.json','--report',out/'BEARING.json'])
 for n in ['check_clearance.py','check_material.py','test_geometry.py']:run([sys.executable,'-B',B/n])
 reports={n:json.loads((out/n).read_text())for n in ['REPEAT.json','PRESERVATION.json','BEARING.json','CLEARANCE.json','MATERIAL.json','GEOMETRY_CONTROLS.json']}
 need(all(d.get('pass')is True for d in reports.values()),'JSON pass gates')
 need(len(reports['PRESERVATION.json']['source_categories'])==13 and all(reports['PRESERVATION.json']['source_categories'].values()),'13 source categories')
 need(reports['GEOMETRY_CONTROLS.json']['count']==7,'Seven geometry/math controls');need(len(reports['REPEAT.json']['focused_native_controls'])==2,'Two native controls')
 need(inventory(inputs)==derived,'Derived inputs changed');need(inventory(B)==before,'Bundle changed');need(all(sha(x)==h for x,h in modelpins.items()),'Model changed')
 (out/'SUMMARY.json').write_text(json.dumps({'pass':True,'model_sha256':modelpins,'bundle_manifest_sha256':sha(B/'FILES.json'),'bundle_unchanged':True,'derived_inputs_unchanged':True,'commands':commands,'native_calls':2,'python_calls':4,'reports':{n:sha(out/n)for n in reports},'limits':'Six geometry mutations fail at profile/topology identity first; one coverage mathematical control, two native snapshot controls. Technical proof is not visual acceptance or engineering capacity.'},indent=2)+'\n');print('PORTABLE FITTINGS QA PASS')
if __name__=='__main__':main()
