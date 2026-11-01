"""External orchestration for fresh Git-only hall QA; no frozen file changes/render."""
import argparse,hashlib,json,os,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
if sys.flags.optimize:raise RuntimeError('Optimization refused')
SOURCE='efcd894acdc045a30f845f05267662957b656bc7fe0ee4cf48c05fc798b610ee'
ACCEPTED='37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255'
QA_MANIFEST='471e2faedee2f31a23ab5b567c33d556e5bd0c82a322b583c76f9da309087090'
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inv(root):return {str(p.relative_to(root)):sha(p)for p in root.rglob('*')if p.is_file()}
def clean(v):
 p=Path(v).absolute();need('..'not in p.parts,'Traversal refused');need(all(not x.is_symlink()for x in [p,*p.parents]),'Symlink refused');return p.resolve()
def manifest(root):
 m=json.loads((root/'FILES.json').read_text());need(all(sha(root/n)==h for n,h in m.items()),'Manifest mismatch '+str(root));need(set(inv(root))==set(m)|{'FILES.json'},'Unexpected bundle contents');return sha(root/'FILES.json')
def main():
 p=argparse.ArgumentParser()
 for k in ['archive','source','candidate','output-dir','blender','commit']:p.add_argument('--'+k,required=True)
 a=p.parse_args();archive=clean(a.archive);source=clean(a.source);candidate=clean(a.candidate);out=clean(a.output_dir);blender=clean(a.blender);need(re.fullmatch('[0-9a-f]{40}',a.commit),'Commit format');need(archive.is_dir()and blender.is_file(),'Inputs absent');need(not out.exists()and out.parent.is_dir()and not out.is_relative_to(archive),'New external output required');need(sha(source)==SOURCE and sha(candidate)==ACCEPTED,'Exact restored source/candidate required')
 qa=archive/'checkpoints/v027/qa';recipe=archive/'checkpoints/v027/reproduce';receipt=archive/'checkpoints/v027/reports/build/build_receipt.json';need(manifest(qa)==QA_MANIFEST,'Reviewed QA manifest differs');recipe_manifest=manifest(recipe);need(sha(recipe/'rebuild.py')=='811ace4ddc5321227b58f8bfcddebdf006ca7b34b331ec09173df0815492e32e','Reviewed wrapper differs');need(sha(recipe/'scripts/build.py')=='6da85e129267f3e5bac597c8635ea1741c1744ed0e147ec3f5816220f23b19a1','Executed builder differs');r=json.loads(receipt.read_text());need(r['candidate_sha256']==ACCEPTED and r['source_sha256']==SOURCE,'Archived build receipt mismatch')
 before=inv(archive);models={str(source):sha(source),str(candidate):sha(candidate)};out.mkdir();commands=[];env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
 def run(args,label):
  cmd=[sys.executable,'-B']+list(map(str,args));commands.append(cmd)
  with (out/(label+'.log')).open('w')as f:proc=subprocess.run(cmd,cwd=out,stdout=f,stderr=subprocess.STDOUT,env=env)
  need(proc.returncode==0,'Failed '+label+'; inspect retained log')
 run([qa/'test_runner.py'],'qa_guards');run([recipe/'test_guards.py','-v'],'recipe_guards')
 run([qa/'run_qa.py','--source',source,'--candidate',candidate,'--build-report',receipt,'--output-dir',out/'accepted_qa','--blender',blender],'accepted_qa')
 accepted=json.loads((out/'accepted_qa/SUMMARY.json').read_text());need(accepted['pass']and accepted['native_calls']==4,'Accepted gates incomplete')
 rebuild=out/'fresh rebuild 中文';rebuild.mkdir();new=rebuild/'rebuilt.blend';raw=rebuild/'rebuilt.json'
 run([recipe/'rebuild.py','--source',source,'--output',new,'--report',raw,'--blender',blender],'rebuild')
 wrapper=json.loads(raw.read_text());need(wrapper['output_sha256']==sha(new)and wrapper['source_unchanged']and wrapper['source_sha256']==SOURCE,'Rebuild receipt failed');builder=rebuild/'builder_report.json';builder.write_text(json.dumps(wrapper['builder_report'],ensure_ascii=False,indent=2)+'\n')
 run([qa/'run_qa.py','--source',source,'--candidate',new,'--build-report',builder,'--accepted',candidate,'--output-dir',out/'rebuilt_qa','--blender',blender],'rebuilt_qa')
 rebuilt=json.loads((out/'rebuilt_qa/SUMMARY.json').read_text());need(rebuilt['pass'],'Rebuilt gates incomplete');need(rebuilt['semantic_repeat_required_and_passed']or sha(new)==ACCEPTED,'Missing semantic proof')
 if sha(new)!=ACCEPTED:
  repeat=json.loads((out/'rebuilt_qa/repeat.json').read_text());need(repeat['pass']and len(repeat['category_checks'])==12 and all(repeat['category_checks'].values()),'Full semantic categories failed')
 for folder in ['accepted_qa','rebuilt_qa']:
  q=out/folder
  for n in ['preservation','neighbor_classification','solid_contacts','touches','clearance','actual_geometry_controls','crown_rays','crown_summary']:need(json.loads((q/(n+'.json')).read_text())['pass']is True,'Report gate '+folder+'/'+n)
  for n in ['source_vertex','source_material']:need(json.loads((q/(n+'.json')).read_text())['pass']is False,'Expected negative missing')
 after=inv(archive);need(before==after,'Frozen archive changed');need(all(sha(p)==h for p,h in models.items()),'Restored input changed');need(not list(qa.rglob('__pycache__'))and not list(recipe.rglob('__pycache__')),'Caches in frozen runtime')
 summary={'pass':True,'owner_verified_remote_commit':a.commit,'archive':str(archive),'archive_file_count':len(before),'archive_inventory_before_sha256':hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),'archive_unchanged':True,'source_and_accepted_unchanged':True,'input_sha256':models,'qa_manifest_sha256':QA_MANIFEST,'recipe_manifest_sha256':recipe_manifest,'rebuilt_sha256':sha(new),'native_calls':accepted['native_calls']+1+rebuilt['native_calls'],'qa_guard_methods':17,'recipe_guard_methods':17,'commands':commands,'accepted_summary_sha256':sha(out/'accepted_qa/SUMMARY.json'),'rebuilt_summary_sha256':sha(out/'rebuilt_qa/SUMMARY.json'),'no_render':True,'scope':'Fresh archived runtime/model accepted-byte full QA, fresh archived recipe rebuild from fixed Git historical source, full semantic equality then complete independent QA. No new accepted model or source mutation. Existing finite crown/route and architectural limits retained.'};(out/'REMOTE_SUMMARY.json').write_text(json.dumps(summary,indent=2));print('REMOTE HALL FULL QA PASS')
if __name__=='__main__':main()
