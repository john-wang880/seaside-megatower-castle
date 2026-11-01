"""Read-only portable v026 QA orchestration, no render or model save."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
if sys.flags.optimize:raise RuntimeError('Optimized Python unsupported')
SOURCE_SHA='8a3590082c99a69d50d444f77165fae57fb611cf069cecda03fdf0c6c17cadd2'
ACCEPTED_SHA='efcd894acdc045a30f845f05267662957b656bc7fe0ee4cf48c05fc798b610ee'
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
 if ch!=ACCEPTED_SHA:need(accepted is not None and accepted.is_file()and sha(accepted)==ACCEPTED_SHA,'Rebuild requires exact accepted model for semantic proof first')
 if accepted is not None:need(sha(accepted)==ACCEPTED_SHA,'Wrong accepted reference SHA')
 manifest=json.loads((qa/'FILES.json').read_text());need(all(sha(qa/k)==v for k,v in manifest.items()),'QA payload checksum mismatch');need(set(inventory(qa))==set(manifest)|{'FILES.json'},'Unexpected bundle files/cache')
 return ch

def main():
 p=argparse.ArgumentParser()
 for k in ['source','candidate','output-dir','blender']:p.add_argument('--'+k,required=True)
 p.add_argument('--accepted',help='Required only for a separately saved rebuild; semantic comparison runs first')
 a=p.parse_args();qa=Path(__file__).resolve().parent;source=clean_path(a.source);candidate=clean_path(a.candidate);out=clean_path(a.output_dir);blender=clean_path(a.blender);accepted=clean_path(a.accepted)if a.accepted else None
 need(blender.is_file(),'Blender executable missing');ch=preflight(source,candidate,accepted,out,qa);before=inventory(qa);models={str(x):sha(x)for x in [source,candidate]+([accepted]if accepted else [])};out.mkdir();commands=[]
 def run(script,args,label,bl=False):
  if bl:cmd=[str(blender),'-b','--factory-startup','--disable-autoexec','--python-exit-code','1','--python-expr','import sys; sys.dont_write_bytecode=True','--python',str(qa/script),'--']+list(map(str,args))
  else:cmd=[sys.executable,'-B',str(qa/script)]+list(map(str,args))
  commands.append(cmd)
  with (out/(label+'.log')).open('w')as log:r=subprocess.run(cmd,cwd=out,stdout=log,stderr=subprocess.STDOUT,env={**__import__('os').environ,'PYTHONDONTWRITEBYTECODE':'1'})
  need(r.returncode==0,'Failed gate '+label+'; inspect its log')
 def checked(name):
  d=json.loads((out/name).read_text());need(d.get('pass')is True,'JSON gate not passing: '+name);return d
 if ch!=ACCEPTED_SHA:
  run('validate_repeat.py',['--accepted',accepted,'--rebuilt',candidate,'--report',out/'repeat.json'],'repeat',True);checked('repeat.json')
 common=['--source',source,'--candidate',candidate,'--candidate-sha',ch]
 run('validate.py',common+['--report',out/'preservation.json','--geometry',out/'geometry.json'],'preservation',True);checked('preservation.json')
 run('check_boundary.py',['--geometry',out/'geometry.json','--report',out/'boundary.json'],'boundary');checked('boundary.json')
 run('negative_geometry.py',['--geometry',out/'geometry.json','--output-dir',out/'geometry_negatives'],'geometry_negatives');gn=checked('geometry_negatives/SUMMARY.json');need(len(gn['controls'])==5,'Five geometry negatives required')
 run('adjacent.py',['--model',candidate,'--sha256',ch,'--union','V026 | exact main shaft two-solid union','--report',out/'adjacent.json'],'adjacent',True)
 run('compare_contacts.py',['--before',qa/'original_adjacent.json','--after',out/'adjacent.json','--report',out/'contact_preservation.json'],'contact_preservation');checked('contact_preservation.json')
 run('run_model_negatives.py',['--blender',blender]+common+['--output-dir',out/'model_negatives'],'model_negatives');mn=checked('model_negatives/SUMMARY.json');need(len(mn['controls'])==4,'Four model negatives required')
 run('test_coplanar_predicate.py',['--report',out/'coplanar_controls.json'],'coplanar_controls');cc=checked('coplanar_controls.json');need(len(cc['controls'])==9,'Nine coplanar controls required')
 run('test_compensating_coverage.py',['--output-dir',out/'compensating_control'],'compensating_control');checked('compensating_control/SUMMARY.json')
 need(before==inventory(qa),'Frozen bundle inventory changed');need(all(sha(p)==h for p,h in models.items()),'Model input changed')
 summary={'pass':True,'input_sha256':models,'candidate_sha256':ch,'qa_manifest_sha256':sha(qa/'FILES.json'),'bundle_inventory_unchanged':True,'all_model_inputs_unchanged':True,'semantic_repeat_required_and_passed':ch!=ACCEPTED_SHA,'commands':commands,'nested_native_model_negative_calls':4,'geometry_negative_controls':5,'model_negative_controls':4,'convex_math_controls':7,'coplanar_predicate_controls':9,'reports':{str(f.relative_to(out)):sha(f)for f in out.rglob('*.json')},'scope':'Exact two-solid mainshaft occupied boundary; hidden shared original preserved with declared derivative pointer/user-count change, calibrated OBJECT material retained, native LOW and full pointer rollback. Two inherited top contacts retained. Historical adjacency correction is separate and no global coplanar-free claim is made.'};(out/'SUMMARY.json').write_text(json.dumps(summary,indent=2));print('PUBLIC V026 QA PASS')
if __name__=='__main__':main()
