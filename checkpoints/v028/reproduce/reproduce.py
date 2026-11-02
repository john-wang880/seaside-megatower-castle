"""Explicit opt-in, local-only receiving-chamber reproduction controller."""
import argparse,gzip,hashlib,json,os,re,subprocess,sys
from pathlib import Path
SOURCE='37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255'
EXPORT='83593439fc128700af9302eb1e53185b3f782b00f39e1b7cb972a72823dc362e'
PAYLOAD='0d07d8ceb27f44cd3c612392d56b40921e60c7f8afaa522aa04f74c17df817f2'
ROOT=Path(__file__).resolve().parent

def need(v,msg):
 if not v:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def safe(value,kind):
 p=Path(value).expanduser().absolute()
 need('..'not in p.parts and p.resolve()==p and all(not q.is_symlink()for q in [p,*p.parents]),'Aliased/symlink path refused')
 if kind=='file':need(p.is_file(),'Missing input file')
 else:need(not os.path.lexists(p)and p.parent.is_dir(),'Output directory must be new with existing parent')
 return p

def inventory(root):
 manifest=json.loads((root/'FILES.json').read_text())
 need(isinstance(manifest,dict)and manifest,'Invalid bundle inventory')
 for rel,h in manifest.items():
  p=root/rel
  need(not Path(rel).is_absolute()and'..'not in Path(rel).parts,'Invalid inventory path')
  safe(p,'file');need(sha(p)==h,'Bundle changed: '+rel)
 return {str(root/rel):h for rel,h in manifest.items()}|{str(root/'FILES.json'):sha(root/'FILES.json')}

def check_version(text):
 need(re.search(r'^Blender 5\.2\.3(?:\s|$)',text,re.M)is not None,'Unsupported Blender version: require 5.2.3')

def integration_gate(r,unlit):
 for key in ['full_source_rollback_pass','source_raw_except_owned_weights_pass','evaluated_target_complements_pass','other_source_categories_pass','old_collections_pass']:need(r.get(key)is True,'Integration gate failed: '+key)
 need(r.get('source_sha256')==SOURCE and r.get('payload_sha256')==PAYLOAD,'Integration input binding failed')
 need(r.get('candidate_sha256')==sha(unlit),'Unlit receipt hash mismatch')
 need(r.get('rendered')is False and r.get('source_saved')is False and r.get('lights_added')is False,'Unexpected integration scope')

def lighting_gate(r,final,build_report):
 need(r.get('canonical_source_sha256')==SOURCE and r.get('architecture_receipt_sha256')==sha(build_report),'Light-stage source/receipt binding failed')
 need(r.get('all_preexisting_scene_data_unchanged')is True,'Light stage changed previous scene')
 need(r.get('rendered')is False and len(r.get('lights',[]))==2,'Unexpected light stage scope')
 need(r.get('fixture_triangles')==1160 and r.get('combined_triangles')==1878,'Unexpected geometry budget')
 need(r.get('candidate_sha256')==sha(final),'Final receipt hash mismatch')

def run(source,blender,out,root=ROOT):
 need(not sys.flags.optimize,'Optimized Python unsupported')
 source=safe(source,'file');blender=safe(blender,'file');out=safe(out,'new')
 need(source!=blender,'Input role alias');need(sha(source)==SOURCE,'Wrong baseline SHA256')
 pins=inventory(root);pins[str(source)]=SOURCE;pins[str(blender)]=sha(blender)
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 # Version check is the only native process before output creation; it does not
 # open a scene, install, download, or alter the executable.
 version=subprocess.run([str(blender),'--version'],capture_output=True,text=True,env=env,check=False)
 need(version.returncode==0,'Blender version command failed');check_version(version.stdout)
 need(all(sha(p)==h for p,h in pins.items()),'Inputs changed during preflight')
 out.mkdir();receipt={'status':'running','source_sha256':SOURCE,'input_hashes':pins,'blender_version':version.stdout,'stages':[],'limits':['No render, automatic acceptance, publication or model-version bump.','Reproduced .blend bytes may differ; independent semantic QA against accepted candidate remains required.','Linux Blender 5.2.3 tested by prior component execution; controller native end-to-end test is separate. Windows untested.']}
 def stage(name,argv):
  log=out/(name+'.log')
  with log.open('x')as stream:r=subprocess.run(argv,stdout=stream,stderr=subprocess.STDOUT,cwd=str(out),env=env,check=False)
  receipt['stages'].append({'name':name,'argv':argv,'returncode':r.returncode,'log_sha256':sha(log)})
  need(r.returncode==0,'Stage failed: '+name)
 def native(script,args):return [str(blender),'--background','--factory-startup','-t','8','--disable-autoexec','--python-exit-code','1','--python-expr','import sys;sys.dont_write_bytecode=True','--python',str(root/script),'--',*args]
 try:
  raw=gzip.decompress((root/'native.json.gz').read_bytes());need(hashlib.sha256(raw).hexdigest()==EXPORT,'Export decompression hash mismatch')
  exported=out/'native.json'
  with exported.open('xb')as f:f.write(raw)
  payload=out/'geometry.json';unlit=out/'unlit.blend';build_report=out/'integration.json';final=out/'castle_receiving_chamber.blend';light_report=out/'lighting.json'
  stage('01_geometry',[sys.executable,'-B',str(root/'build_geometry.py'),'--export',str(exported),'--plan-dir',str(root/'frozen_plan'),'--output',str(payload)])
  need(sha(payload)==PAYLOAD,'Generated geometry differs from frozen executed payload');need(json.loads(payload.read_text()).get('pass')is True,'Geometry gates failed')
  stage('02_integration',native('integrate.py',['--source',str(source),'--payload',str(payload),'--output',str(unlit),'--report',str(build_report)]))
  integration_gate(json.loads(build_report.read_text()),unlit)
  stage('03_fixed_lanterns',native('add_room_lanterns.py',['--source',str(unlit),'--build-receipt',str(build_report),'--output',str(final),'--report',str(light_report)]))
  lighting_gate(json.loads(light_report.read_text()),final,build_report)
  receipt.update(status='REPRODUCED_PENDING_INDEPENDENT_SEMANTIC_QA',final_model=str(final),final_sha256=sha(final),unlit_sha256=sha(unlit),geometry_sha256=sha(payload))
 except BaseException as e:
  receipt.update(status='FAILED_NO_ACCEPTANCE',error=type(e).__name__+': '+str(e));raise
 finally:
  stable=all(Path(p).is_file()and sha(p)==h for p,h in pins.items());receipt['all_inputs_unchanged']=stable
  with(out/'REPRODUCTION.json').open('x')as f:json.dump(receipt,f,indent=2)
  need(stable,'Pinned input changed during run')
 return receipt

def main():
 need(not sys.flags.optimize,'Optimized Python unsupported')
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['source','blender','output-dir']:p.add_argument('--'+k,required=True)
 a=p.parse_args();r=run(a.source,a.blender,a.output_dir);print(json.dumps({'status':r['status'],'final_sha256':r['final_sha256']}))
if __name__=='__main__':main()
