"""Portable read-only v028 QA orchestration. No render, save, install or overwrite."""
import argparse,gzip,hashlib,json,os,re,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE='37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255'
ACCEPTED='f0d135e0c6e554b5ae7c520ef9ccefc61e2a7c4abc3129eef1d3d4118bca8096'
EXPORT='83593439fc128700af9302eb1e53185b3f782b00f39e1b7cb972a72823dc362e'
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
 for k in ['blender','source','candidate','candidate-sha','reference-export','output-dir']:ap.add_argument('--'+k,required=True)
 ap.add_argument('--accepted');ap.add_argument('--preflight-only',action='store_true');a=ap.parse_args()
 before=bundle_guard();src=clean(a.source);candidate=clean(a.candidate);reference=clean(a.reference_export);blender=clean(a.blender);out=clean(a.output_dir,False);ch=digest_string(a.candidate_sha)
 need(not out.is_relative_to(ROOT),'Output inside frozen bundle');need(all(not out.is_relative_to(p.parent) for p in [src,candidate,reference]),'Output inside input directory');role_guard([src,candidate,reference])
 need(sha(src)==SOURCE and sha(candidate)==ch,'Wrong model identity');accepted=clean(a.accepted) if a.accepted else None
 if ch!=ACCEPTED:need(accepted is not None,'Rebuild requires accepted semantic reference')
 if accepted:need(sha(accepted)==ACCEPTED,'Wrong accepted reference')
 raw=reference.read_bytes()
 if reference.suffix=='.gz':
  with gzip.open(reference,'rb') as f:raw=f.read(40*1024*1024+1)
 need(len(raw)<=40*1024*1024 and hashlib.sha256(raw).hexdigest()==EXPORT,'Wrong decoded source export')
 pins={str(p):sha(p) for p in [src,candidate,reference]+([accepted] if accepted else [])}
 if a.preflight_only:print('PREFLIGHT PASS; no output created');return
 out.mkdir();data=out/'data';data.mkdir()
 for p in (ROOT/'data').iterdir():need(p.is_file(),'Unexpected data directory');shutil.copyfile(p,data/p.name)
 (data/'native.json').write_bytes(raw);shutil.copyfile(data/'route_fixture_plan.json',out/'route_fixture_plan.json')
 data_before=inventory(data);route_sha=sha(out/'route_fixture_plan.json')
 env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env.pop('PYTHONOPTIMIZE',None);env['V028_QA_OUTPUT']=str(out);env['V028_QA_DATA']=str(data)
 commands=[]
 def run(script,args=(),native=False):
  command=([str(blender),'-b','--factory-startup','--disable-autoexec','--python-exit-code','1','--python-expr','import sys; sys.dont_write_bytecode=True','--python',str(ROOT/script),'--'] if native else [sys.executable,'-B',str(ROOT/script)])+list(map(str,args));log=out/('%02d_%s.log'%(len(commands)+1,Path(script).stem))
  with log.open('xb') as f:result=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,cwd=out,env=env)
  commands.append({'command':command,'returncode':result.returncode,'native':native,'log':log.name});need(result.returncode==0,'Child failed; preserved log '+str(log))
  need(inventory(ROOT)==before and inventory(data)==data_before and sha(out/'route_fixture_plan.json')==route_sha and all(sha(p)==h for p,h in pins.items()),'Immutable input changed during chain')
 if accepted:run('compare_saved.py',['--accepted',accepted,'--candidate',candidate,'--candidate-sha',ch,'--report',out/'repeat.json'],True)
 run('validate_final.py',['--source',src,'--candidate',candidate,'--candidate-sha',ch,'--payload',data/'geometry_final.json','--report',out/'native_preservation.json','--geometry',out/'native_geometry.json','--fixtures',out/'lit_geometry.json'],True)
 run('native_controls.py',['--candidate',candidate,'--candidate-sha',ch,'--payload',data/'geometry_final.json','--report',out/'native_controls.json'],True)
 run('check_local_payload.py',['--payload',data/'geometry_final.json','--export',data/'native.json','--proof',data/'guard_partition_proof.json','--report',out/'local_final.json'])
 run('check_outside_payload.py',['--payload',data/'geometry_final.json','--export',data/'native.json','--proof',data/'guard_partition_proof.json','--faces',data/'guard_faces_final.json','--report',out/'outside_final.json'])
 run('check_native_tessellation.py',['--geometry',out/'native_geometry.json','--export',data/'native.json','--proof',data/'guard_partition_proof.json','--report',out/'native_tessellation.json'])
 for script in ['check_outside_volumes.py','check_saved_routes.py','check_saved_seats.py','check_local_neighbors.py','check_saved_fixtures.py','check_reverse_correction.py','reverse_pier_footprints.py','test_actual_payload.py','test_exact_boundary.py','test_coplanar_controls.py']:run(script)
 reports=['native_preservation.json','native_controls.json','local_final.json','outside_final.json','native_tessellation.json','outside_volumes.json','saved_routes.json','saved_seats.json','saved_fixtures_final.json','actual_payload_controls.json']+(['repeat.json'] if accepted else [])
 for name in reports:need(json.loads((out/name).read_text())['pass'],'False report gate '+name)
 camera=json.loads((out/'reverse_correction.json').read_text());need(camera['pass_doorway_visibility_and_camera_clearance'] and camera['candidate_sha256']==ch,'Corrected reverse camera gate failed');need(json.loads((out/'reverse_pier_footprints.json').read_text())['candidate_sha256']==ch,'Camera footprint identity drift')
 adjacent=json.loads((out/'local_neighbors_with_interfaces.json').read_text());need(not any(p['same_facing'] for c in adjacent['contacts'] for p in c['planes']),'Unexpected local same-facing contact')
 need(inventory(ROOT)==before and inventory(data)==data_before and sha(out/'route_fixture_plan.json')==route_sha and all(sha(p)==h for p,h in pins.items()),'Final immutable drift')
 result={'pass':True,'source_sha256':SOURCE,'candidate_sha256':ch,'accepted_reference_sha256':ACCEPTED if accepted else None,'bundle_manifest_sha256':sha(ROOT/'FILES.json'),'input_sha256':pins,'native_calls':sum(c['native'] for c in commands),'python_calls':sum(not c['native'] for c in commands),'commands':commands,'controls':{'boundary_math':10,'coplanar_math':9,'exported_actual_geometry_negatives':6,'focused_native_mutations':4},'report_sha256':{n:sha(out/n) for n in reports+['local_neighbors_with_interfaces.json','reverse_correction.json','reverse_pier_footprints.json']},'bundle_unchanged':True,'decoded_copied_data_unchanged':True,'decoded_data_sha256':data_before,'fixed_route_plan_sha256':route_sha,'model_inputs_unchanged':True,'limits':'No render or save. Bounded geometry and source-state proof; no structural capacity/global accessibility/art acceptance claim.'};(out/'SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n');print('PUBLIC V028 QA PASS')
if __name__=='__main__':main()
