"""CPU-only byte-exact replay. No bpy, source save, network or dependencies."""
import argparse,gzip,hashlib,json,os,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
BINDINGS='5e58a4125933f004c015fd51a450790cf6cfc6ef63670addd26e9eab4cadf94f'
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(p):
 require(not any(q.is_symlink()for q in [p,*p.parents]),'symlink path refused')
def verify():
 require(not sys.flags.optimize,'optimized Python refused')
 safe(HERE);require(sha(HERE/'BINDINGS.json')==BINDINGS,'binding identity mismatch')
 b=json.loads((HERE/'BINDINGS.json').read_text())
 for n,h in b['files'].items():
  p=HERE/n;safe(p);require(p.resolve().is_relative_to(HERE),'unsafe dependency');require(sha(p)==h,'dependency changed: '+n)
 return b
def main():
 require(not sys.flags.optimize,'optimized Python refused')
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--source-model',type=Path);a=ap.parse_args();b=verify();out=a.output_dir.absolute();safe(out)
 require(not out.exists(),'output already exists');require(out.parent.is_dir(),'output parent missing');require(not out.resolve().is_relative_to(HERE),'output inside recipe refused')
 if a.source_model:
  safe(a.source_model);require(a.source_model.is_file()and sha(a.source_model)==b['source_sha256'],'wrong source model');require(not a.source_model.resolve().is_relative_to(out.resolve()),'source/output alias')
 code=sha(Path(__file__));out.mkdir() # exclusive; failed attempts retained, never reused silently
 raw=gzip.decompress((HERE/'inputs/native.json.gz').read_bytes());require(len(raw)==b['export_bytes']and hashlib.sha256(raw).hexdigest()==b['export_sha256'],'wrong source export')
 exp=out/'native.json'
 with exp.open('xb')as f:f.write(raw)
 cmd=[sys.executable,'-B',str(HERE/'geometry_builder/build_geometry.py'),'--export',str(exp),'--plan-dir',str(HERE/'frozen_plan'),'--output',str(out/'geometry.json')]
 with (out/'build.log').open('x')as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
 verify();require(sha(Path(__file__))==code,'wrapper changed');require(sha(exp)==b['export_sha256'],'export changed');require(sha(out/'geometry.json')==b['payload_sha256'],'payload not byte exact')
 if a.source_model:require(sha(a.source_model)==b['source_sha256'],'source changed')
 receipt={'pass':True,'scope':'CPU geometry only; no native integration','source_sha256':b['source_sha256'],'source_model_checked':bool(a.source_model),'payload_sha256':b['payload_sha256'],'export_sha256':b['export_sha256'],'bindings_sha256':BINDINGS,'wrapper_sha256':code,'command':cmd}
 with (out/'REPLAY.json').open('x')as f:json.dump(receipt,f,indent=2)
 print(json.dumps(receipt))
if __name__=='__main__':main()
