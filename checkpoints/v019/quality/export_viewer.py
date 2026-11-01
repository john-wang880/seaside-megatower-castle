"""Export a separate optional HIGH/LOW v019 viewer. Never overwrite canonical files.
Blender5.2.3 --background --factory-startup --disable-autoexec --python-exit-code 1
 --python export_viewer.py -- --source accepted.blend --mode HIGH --output new.blend --report new.json
"""
import argparse,hashlib,importlib.util,json,os,sys,tempfile
from pathlib import Path
SOURCE_SHA='e71778349c4c65eafbda3eb0a3d0753cd11e1b368a3456c4de1db2f4c0f8647a'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,message):
 if not ok:raise RuntimeError(message)
def validate_paths(source,output,report):
 source=Path(source).expanduser().resolve(strict=True);rawout=Path(output).expanduser().absolute();rawreport=Path(report).expanduser().absolute()
 for p in [rawout,rawreport]:require(not p.exists() and not p.is_symlink(),'Output/report must not exist or be a symlink')
 output=rawout.resolve();report=rawreport.resolve();require(len({source,output,report})==3,'Input/output aliases forbidden')
 require(output.suffix=='.blend' and report.suffix=='.json','Expected .blend output and .json report')
 require(output.parent.is_dir() and report.parent.is_dir(),'Output parent directories must already exist')
 require(sha(source)==SOURCE_SHA,'Source must be exact accepted v019')
 return source,output,report

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--source',required=True);p.add_argument('--mode',choices=['HIGH','LOW'],required=True);p.add_argument('--output',required=True);p.add_argument('--report',required=True)
 a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:])
 require(not sys.flags.optimize,'Optimized Python unsupported')
 source,output,report=validate_paths(a.source,a.output,a.report)
 import bpy
 require(tuple(bpy.app.version)==(5,2,3),'Requires existing Blender5.2.3')
 controls=Path(__file__).resolve().with_name('quality_controls.py');code=controls.read_text();controlsha=sha(controls)
 spec=importlib.util.spec_from_file_location('castle_quality_controls',controls);q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
 bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False,load_ui=True)
 scene=bpy.context.scene;require(q.MARKER not in scene and q.TEXT_NAME not in bpy.data.texts,'Owned marker/Text collision')
 text=bpy.data.texts.new(q.TEXT_NAME);text.write(code);text.use_module=False
 scene[q.MARKER]=json.dumps({'schema':'castle-v019-quality-v1','source_sha256':SOURCE_SHA,'mode':'HIGH'},sort_keys=True)
 q.find(scene);q.set_mode(scene,a.mode)
 # Export only. Text is manual-run; no automatic handler/class registration occurs here.
 tempfiles=[];published=[]
 try:
  fd,tmp=tempfile.mkstemp(prefix='.castle-quality-',suffix='.blend',dir=str(output.parent));os.close(fd);tmp=Path(tmp);tempfiles.append(tmp)
  bpy.context.preferences.filepaths.save_version=0
  bpy.ops.wm.save_as_mainfile(filepath=str(tmp),copy=True)
  require(sha(source)==SOURCE_SHA and sha(controls)==controlsha,'Input changed during export')
  data={'status':'OPTIONAL_VIEWER_COPY_NOT_NEW_CHECKPOINT','source_sha256':SOURCE_SHA,'source_file_unchanged':True,'output_sha256':sha(tmp),'output_bytes':tmp.stat().st_size,'mode':a.mode,'controls_sha256':controlsha,'marker':json.loads(scene[q.MARKER]),'text':q.TEXT_NAME,'text_use_module':text.use_module,'flags':q.expected_flags(a.mode),'allowed_deltas':['One manual-only Text datablock','One owned scene marker','Six paired visibility flags in LOW; canonical flags in HIGH'],'limits':['Both high meshes remain stored; no file-size saving claim','One tree only; original wood/other forest unchanged','Manual panel never saves or installs an addon','Independent reopened-source/geometry preservation QA required']}
  fd,rtemp=tempfile.mkstemp(prefix='.castle-quality-',suffix='.json',dir=str(report.parent));os.close(fd);rtemp=Path(rtemp);tempfiles.append(rtemp);rtemp.write_text(json.dumps(data,indent=2))
  # Hard-link creation is exclusive and atomic on each destination filesystem; no replace/overwrite.
  for t,d in [(tmp,output),(rtemp,report)]:os.link(t,d);published.append((t,d))
  require(sha(source)==SOURCE_SHA,'Canonical source changed')
  print('VIEWER_EXPORT_PASS',a.mode,data['output_sha256'],flush=True)
 except BaseException:
  for t,d in published:
   if d.exists() and os.path.samefile(t,d):d.unlink()
  raise
 finally:
  for t in tempfiles:t.unlink(missing_ok=True)
if __name__=='__main__':main()
