"""Portable read-only hall QA; no rendering or model saves."""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
if sys.flags.optimize:raise RuntimeError('Optimized execution refused')
SOURCE_SHA='efcd894acdc045a30f845f05267662957b656bc7fe0ee4cf48c05fc798b610ee'
ACCEPTED_SHA='37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255'
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inventory(p):return {str(f.relative_to(p)):sha(f)for f in p.rglob('*')if f.is_file()}
def clean_path(value):
 p=Path(value).absolute();need('..'not in p.parts,'Traversal refused')
 for q in [p,*p.parents]:need(not q.is_symlink(),'Symlink refused')
 return p.resolve()
def preflight(source,candidate,accepted,receipt,out,qa):
 need(source.is_file()and candidate.is_file()and receipt.is_file(),'Inputs missing');need(source!=candidate and not os.path.samefile(source,candidate),'Source/candidate alias');need(not out.exists()and out.parent.is_dir(),'Fresh output directory required');need(not out.is_relative_to(qa)and 'checkpoints'not in out.parts,'Report outside frozen package required');need(sha(source)==SOURCE_SHA,'Source hash mismatch');ch=sha(candidate)
 if ch!=ACCEPTED_SHA:need(accepted is not None and accepted.is_file()and sha(accepted)==ACCEPTED_SHA,'Rebuild requires pinned accepted semantic reference')
 if accepted is not None:need(sha(accepted)==ACCEPTED_SHA,'Wrong accepted reference')
 r=json.loads(receipt.read_text());need(r['candidate_sha256']==ch and r['source_sha256']==SOURCE_SHA,'Build receipt input mismatch');need(r['operands']==json.loads((qa/'accepted_operands.json').read_text()),'Authored operand semantics drift')
 m=json.loads((qa/'FILES.json').read_text());need(all(sha(qa/n)==h for n,h in m.items()),'Payload hash mismatch');need(set(inventory(qa))==set(m)|{'FILES.json'},'Unexpected package file/cache');return ch

def main():
 p=argparse.ArgumentParser()
 for k in ['source','candidate','build-report','output-dir','blender']:p.add_argument('--'+k,required=True)
 p.add_argument('--accepted');a=p.parse_args();qa=Path(__file__).resolve().parent;source=clean_path(a.source);candidate=clean_path(a.candidate);receipt=clean_path(a.build_report);out=clean_path(a.output_dir);blender=clean_path(a.blender);accepted=clean_path(a.accepted)if a.accepted else None;need(blender.is_file(),'Blender missing');ch=preflight(source,candidate,accepted,receipt,out,qa);before=inventory(qa);inputs={str(x):sha(x)for x in [source,candidate,receipt]+([accepted]if accepted else [])};out.mkdir();commands=[]
 def run(script,args,label,native=False,expected=0):
  cmd=([str(blender),'-b','--factory-startup','--disable-autoexec','--python-exit-code','1','--python-expr','import sys; sys.dont_write_bytecode=True','--python',str(qa/script),'--']if native else[sys.executable,'-B',str(qa/script)])+list(map(str,args));commands.append({'command':cmd,'native':native,'expected_exit':expected})
  with (out/(label+'.log')).open('w')as f:r=subprocess.run(cmd,cwd=out,stdout=f,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  need(r.returncode==expected,'Failed '+label+'; inspect log')
 def check(n,positive=True):
  r=json.loads((out/n).read_text());need(r.get('pass')is positive,'JSON gate '+n);return r
 if ch!=ACCEPTED_SHA:run('validate_repeat.py',['--accepted',accepted,'--rebuilt',candidate,'--report',out/'repeat.json'],'repeat',True);check('repeat.json')
 common=['--source',source,'--candidate',candidate,'--candidate-sha',ch,'--build-report',receipt,'--operand-reference',qa/'accepted_operands.json']
 run('validate_preservation.py',common+['--report',out/'preservation.json','--geometry',out/'geometry.json'],'preservation',True);check('preservation.json')
 run('classify_neighbors.py',['--geometry',out/'geometry.json','--report',out/'neighbor_classification.json'],'neighbors');check('neighbor_classification.json')
 run('audit_geometry.py',['--geometry',out/'geometry.json','--plan',qa/'plan.json','--neighbor-report',out/'neighbor_classification.json','--report',out/'solid_contacts.json'],'solid');solid=check('solid_contacts.json');need(len(solid['witnesses'])==29,'29 witnesses required')
 run('check_touches.py',['--geometry',out/'geometry.json','--report',out/'touches.json'],'touches');check('touches.json')
 run('check_clearance.py',['--geometry',out/'geometry.json','--envelopes',qa/'protected_envelopes.json','--report',out/'clearance.json'],'clearance');check('clearance.json')
 run('test_actual_geometry.py',['--geometry',out/'geometry.json','--report',out/'actual_geometry_controls.json'],'geometry_controls');need(len(check('actual_geometry_controls.json')['controls'])==6,'Six controls required')
 run('test_predicates.py',[],'math_controls');math=json.loads((out/'math_controls.log').read_text());need(math['pass']and math['controls']==11,'Math controls')
 negatives=[]
 for kind in ['source_vertex','source_material']:
  run('validate_preservation.py',common+['--negative',kind,'--report',out/(kind+'.json'),'--geometry',out/(kind+'_geometry.json')],kind,True,1);r=check(kind+'.json',False);need(r['inputs_unchanged'],'Negative mutated input');need(not r['checks']['meshes'if kind=='source_vertex'else'materials'],'Wrong negative rejection');negatives.append(kind)
 run('probe_crown.py',['--candidate',candidate,'--candidate-sha',ch,'--receipt',qa/'crown_render_receipt.json','--pixels',qa/'crown_pixels.json','--seating-report',out/'solid_contacts.json','--report',out/'crown_rays.json'],'crown',True);check('crown_rays.json')
 run('summarize_crown.py',['--rays',out/'crown_rays.json','--geometry',out/'geometry.json','--report',out/'crown_summary.json'],'crown_summary');check('crown_summary.json')
 need(before==inventory(qa),'Package inventory changed');need(all(sha(p)==h for p,h in inputs.items()),'Input changed');summary={'pass':True,'input_sha256':inputs,'candidate_sha256':ch,'qa_manifest_sha256':sha(qa/'FILES.json'),'bundle_inventory_unchanged':True,'inputs_unchanged':True,'semantic_repeat_required_and_passed':ch!=ACCEPTED_SHA,'native_calls':sum(x['native']for x in commands),'commands':commands,'model_negative_controls':negatives,'exported_geometry_controls':6,'math_controls':13,'reports':{str(p.relative_to(out)):sha(p)for p in out.glob('*.json')},'scope':'One additive hall union; exact12-category original preservation,29finite support/backing witnesses, explicit neighbor/coplanar/containment proof, original static/camera envelope separation and bounded actual-image crown rays. Not structural/global accessibility certification; no old-walk ceiling cadence claim.'};(out/'SUMMARY.json').write_text(json.dumps(summary,indent=2));print('PUBLIC HALL QA PASS')
if __name__=='__main__':main()
