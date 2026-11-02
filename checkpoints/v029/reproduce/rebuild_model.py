"""Rebuild the accepted-source stores candidate in a new directory, cloud/local opt-in only."""
import argparse,hashlib,json,os,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parent
SOURCE='f0d135e0c6e554b5ae7c520ef9ccefc61e2a7c4abc3129eef1d3d4118bca8096'
def need(x,m):
 if not x:raise RuntimeError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(p):
 p=pathlib.Path(p).expanduser().absolute();need('..' not in p.parts and all(not q.is_symlink() for q in [p,*p.parents]),'Aliased path');return p

def main():
 need(not sys.flags.optimize,'Optimized Python refused')
 ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--blender',required=True);ap.add_argument('--output-dir',required=True);a=ap.parse_args()
 source=safe(a.source);blender=safe(a.blender);out=safe(a.output_dir)
 need(source.is_file() and sha(source)==SOURCE,'Wrong source model');need(blender.is_file(),'Missing Blender')
 need(out.parent.is_dir() and not out.exists() and not out.resolve().is_relative_to(ROOT),'Output exists/missing parent/inside recipe')
 need(not source.is_relative_to(out),'Source/output alias')
 files=json.loads((ROOT/'NATIVE_BINDINGS.json').read_text())
 for name,h in files.items():need(sha(ROOT/name)==h,'Runtime changed '+name)
 ver=subprocess.run([str(blender),'--version'],capture_output=True,text=True,check=True).stdout
 need(ver.startswith('Blender 5.2.3'),'Blender 5.2.3 required')
 out.mkdir();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',XDG_CACHE_HOME=str(out/'cache'))
 commands=[]
 def run(cmd,name):
  commands.append(cmd)
  with (out/name).open('x') as f:subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 run([sys.executable,'-B',str(ROOT/'reproduce_geometry.py'),'--source-model',str(source),'--output-dir',str(out/'geometry')],'geometry.log')
 prefix=[str(blender),'-b','--factory-startup','--disable-autoexec','--python-exit-code','1','--python']
 run(prefix+[str(ROOT/'integrate.py'),'--','--source',str(source),'--payload',str(out/'geometry/geometry.json'),'--output',str(out/'unlit.blend'),'--report',str(out/'integration.json')],'integrate.log')
 run(prefix+[str(ROOT/'add_room_lanterns.py'),'--','--source',str(out/'unlit.blend'),'--build-receipt',str(out/'integration.json'),'--output',str(out/'candidate.blend'),'--report',str(out/'lighting.json')],'lighting.log')
 need(sha(source)==SOURCE,'Source changed')
 for name,h in files.items():need(sha(ROOT/name)==h,'Runtime changed '+name)
 report={'pass':True,'source_sha256':SOURCE,'rebuilt_sha256':sha(out/'candidate.blend'),'commands':commands,'scope':'Native rebuild only; independent geometry/semantic QA required. Native compressed .blend hashes may differ across equivalent saves.'}
 (out/'REBUILD.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
