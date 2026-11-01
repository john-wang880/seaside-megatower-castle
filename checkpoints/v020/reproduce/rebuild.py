#!/usr/bin/env python3
"""Three-stage threshold recipe from pinned v019. No render or publication."""
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
FORWARD_CHECKS={'all_source_meshes_exact','all_material_graphs_exact','world_exact','closed_oriented_positive_additions','actual_host_embedded_witnesses'}
SOURCE='e71778349c4c65eafbda3eb0a3d0753cd11e1b368a3456c4de1db2f4c0f8647a'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['source','blender','output-dir']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();require(not sys.flags.optimize,'Assertions required');root=Path(__file__).resolve().parent;source=a.source.resolve(strict=True);blender=a.blender.resolve(strict=True);raw=a.output_dir.absolute()
 require(not raw.exists() and not raw.is_symlink(),'Output directory must be new');out=raw.resolve();require(root not in out.parents and out not in root.parents and root!=out,'Output must not overlap recipe bundle');require(source!=out and out not in source.parents and source not in out.parents,'No source/output alias');require(sha(source)==SOURCE,'Expected exact v019 source');require(blender.is_file() and os.access(blender,os.X_OK),'Existing Blender executable required; no install/fetch')
 files={str(x.relative_to(root)):sha(x)for x in sorted(root.rglob('*'))if x.is_file() and '__pycache__' not in x.parts and x.suffix in ['.py','.json','.md']};blendersha=sha(blender);out.mkdir(parents=True,exist_ok=False);record={'status':'RUNNING','source_sha256':SOURCE,'blender_sha256':blendersha,'bundle_files':files,'steps':[],'scope':'Technical recipe only; not acceptance/newversion/render/publication'}
 def stable():
  require(sha(source)==SOURCE and sha(blender)==blendersha,'Input changed');now={str(x.relative_to(root)):sha(x)for x in sorted(root.rglob('*'))if x.is_file() and '__pycache__' not in x.parts and x.suffix in ['.py','.json','.md']};require(now==files,'Recipe changed')
 def write():(out/'receipt.json').write_text(json.dumps(record,indent=2))
 def step(name,script,args,model,report,gate):
  stable();argv=[str(blender),'--background','--factory-startup','--disable-autoexec','--python-exit-code','1','--threads','8','--python',str(root/'scripts'/script),'--',*map(str,args)];start=time.time();env=os.environ.copy();env.pop('PYTHONOPTIMIZE',None)
  with (out/(name+'.log')).open('xb')as f:r=subprocess.run(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT,env=env,check=False)
  require(r.returncode==0,name+' failed');require(model.is_file() and report.is_file(),name+' missing output');d=json.loads(report.read_text());require(d['candidate_sha256']==sha(model) and gate(d),name+' report failure');stable();record['steps'].append({'name':name,'argv':argv,'seconds':time.time()-start,'model_sha256':sha(model),'report_sha256':sha(report)});write();return sha(model)
 try:
  write();v=subprocess.run([str(blender),'--version'],capture_output=True,text=True,check=False);require(v.returncode==0 and (v.stdout.splitlines()[0].split()[:2] if v.stdout.splitlines() else [])==['Blender','5.2.3'],'Requires existing Blender5.2.3');record['blender_version']=v.stdout
  forward=out/'forward.blend';fr=out/'forward.json';h=step('forward','build.py',['--source',source,'--plan',root/'plans/host_plan_forward.json','--output',forward,'--report',fr],forward,fr,lambda d:d.get('source_unchanged') is True and d.get('total_components')==23 and set(d.get('checks',{}))==FORWARD_CHECKS and all(v is True for v in d['checks'].values()) and d.get('source_sha256')==SOURCE)
  joined=out/'joined.blend';jr=out/'joined.json';h=step('union','union_springers.py',['--input',forward,'--input-sha256',h,'--build-report',fr,'--output',joined,'--report',jr],joined,jr,lambda d:d.get('input_unchanged') is True and d.get('component_count')==21 and d.get('all_other_meshes_exact') is True and d.get('all_material_graphs_exact') is True)
  final=out/'reproduced_threshold.blend';cr=out/'coping.json';h=step('coping','clip_coping_embed.py',['--input',joined,'--input-sha256',h,'--union-report',jr,'--output',final,'--report',cr],final,cr,lambda d:d.get('input_unchanged') is True and d.get('component_count')==23 and d.get('other_meshes_and_material_graphs_exact') is True)
  stable();record.update(status='RECIPE_COMPLETED_INDEPENDENT_SEMANTIC_QA_REQUIRED',candidate_sha256=h,source_unchanged=True,finished_unix=time.time());write()
 except BaseException as e:
  record.update(status='FAILED',error=repr(e))
  try:stable();record['source_unchanged']=True;record['recipe_unchanged']=True
  except BaseException as integrity:record['integrity_failure']=repr(integrity)
  write();raise
if __name__=='__main__':main()
