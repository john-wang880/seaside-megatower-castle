"""Read-only portable v025 QA orchestration, no render or model save."""
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
  with (out/(label+'.log')).open('w')as log:r=subprocess.run(cmd,cwd=out,stdout=log,stderr=subprocess.STDOUT)
  need(r.returncode==0,'Failed gate '+label+'; inspect its log')
 def checked(name):
  d=json.loads((out/name).read_text());need(d.get('pass')is True,'JSON gate not passing: '+name);return d
 if ch!=ACCEPTED_SHA:
  run('validate_repeat.py',['--accepted',accepted,'--rebuilt',candidate,'--report',out/'repeat.json'],'repeat',True);checked('repeat.json')
 common=['--source',source,'--candidate',candidate,'--candidate-sha',ch,'--scope',qa/'SCOPE.json']
 scope=json.loads((qa/'SCOPE.json').read_text());need(scope['source_sha256']==SOURCE_SHA,'Scope source mismatch')
 run('export_preservation.py',common+['--report',out/'preservation.json','--geometry',out/'geometry.json'],'preservation',True);checked('preservation.json')
 run('triangulation_audit.py',['--candidate',candidate,'--candidate-sha',ch,'--report',out/'triangulation.json'],'triangulation',True);tri=checked('triangulation.json');need(len(tri['exact_zero_measure_loop_triangles'])==1,'Expected one proven exact-zero derived triangle')
 run('check_groups.py',['--geometry',out/'geometry.json','--baseline-cross',qa/'cross_group_analysis.json','--output-dir',out/'boundaries'],'boundaries');boundary=checked('boundaries/SUMMARY.json');need(boundary['group_boundary_passes']==4,'Four boundary gates required')
 geometry_controls=0
 for i in range(1,5):
  extra=[]if i==1 else ['--only-recess']
  run('negative_geometry.py',['--geometry',out/f'boundaries/group_{i:02d}.json','--output-dir',out/f'geometry_negatives_{i:02d}']+extra,f'geometry_negatives_{i:02d}');neg=checked(f'geometry_negatives_{i:02d}/SUMMARY.json');geometry_controls+=len(neg['controls'])
 need(geometry_controls==9,'Nine geometry negative controls required')
 for case in ['extra_mask_weight','old_v024_weight','old_v024_union','unrelated_hidden_source']:
  run('negative_model.py',['--case',case,'--result',out/('negative_'+case+'.json')]+common+['--report',out/('UNEXPECTED_'+case+'.json'),'--geometry',out/('UNEXPECTED_'+case+'_geometry.json')],'negative_'+case,True);checked('negative_'+case+'.json')
 run('rollback.py',common+['--report',out/'rollback.json'],'rollback',True);checked('rollback.json')
 adjacent_counts=[]
 for group in scope['groups']:
  i=group['ordinal'];run('adjacent.py',['--candidate',candidate,'--candidate-sha',ch,'--union',group['replacement_object'],'--report',out/f'adjacent_{i:02d}.json'],f'adjacent_{i:02d}',True);adj=json.loads((out/f'adjacent_{i:02d}.json').read_text());need(adj['source_unchanged']and not adj['contacts'],'New positive-area adjacent coplanar contacts require review');adjacent_counts.append(len(adj['scanned_objects']))
 run('surface_partition.py',[],'six_partition_controls')
 run('test_compensating_coverage.py',['--output-dir',out/'compensating_control'],'compensating_control');checked('compensating_control/SUMMARY.json')
 need(before==inventory(qa),'Frozen bundle inventory changed');need(all(sha(p)==h for p,h in models.items()),'Model input changed');need(not list(out.glob('UNEXPECTED*')),'Negative fixture unexpectedly wrote success output')
 summary={'pass':True,'input_sha256':models,'candidate_sha256':ch,'qa_manifest_sha256':sha(qa/'FILES.json'),'bundle_inventory_unchanged':True,'all_model_inputs_unchanged':True,'semantic_repeat_required_and_passed':ch!=ACCEPTED_SHA,'commands':commands,'geometry_negative_controls':9,'model_negative_controls':4,'math_controls':7,'adjacent_objects_checked_by_group':adjacent_counts,'reports':{str(f.relative_to(out)):sha(f)for f in out.rglob('*.json')},'scope':'Four five-solid evaluated chamfered frame unions; independent oriented set-coverage boundary clipping and saved float32 budgets. Genuine recesses and three existing cross-frame intersections retained; originalV024union exact. No render/model save/global structure or whole-castle navigation certification.'};(out/'SUMMARY.json').write_text(json.dumps(summary,indent=2));print('PUBLIC V025 QA PASS')
if __name__=='__main__':main()
