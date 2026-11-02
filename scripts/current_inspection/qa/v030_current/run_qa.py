"""Portable independent QA runner; requires pre-exported default/indexOFF/indexHIGH/indexLOW copies. No renders."""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
from compare_support import SOURCE_SHA,BASE_SHA,require
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inventory(path):return {str(p.relative_to(path)):sha(p) for p in sorted(path.rglob('*')) if p.is_file()}
def clean_path(value):
 p=Path(value);require('..' not in p.parts,'Parent traversal refused');return p.absolute()
def main(argv=None):
 require(not sys.flags.optimize,'Optimized Python unsupported')
 p=argparse.ArgumentParser()
 for key in ('source','baseline','tool','default','off','high','low','default-receipt','off-receipt','high-receipt','low-receipt','blender','output-dir'):p.add_argument('--'+key,required=True)
 a=p.parse_args(argv);paths={k:clean_path(v) for k,v in vars(a).items()}
 for k,path in paths.items():
  require(not any(q.is_symlink() for q in (path,*path.parents)),'Symlink path refused: '+k)
  if k!='output_dir':require(path.exists(),'Missing input: '+k)
 out=paths['output_dir'];require(not out.exists() and out.parent.is_dir(),'New external output directory required')
 require(not out.is_relative_to(ROOT) and not out.is_relative_to(paths['tool']),'Output inside immutable payload refused')
 require(sha(paths['source'])==SOURCE_SHA and sha(paths['baseline'])==BASE_SHA,'Source/baseline SHA mismatch')
 inputs={k:sha(v) for k,v in paths.items() if v.is_file()};before={'qa':inventory(ROOT),'tool':inventory(paths['tool'])};require(not any('__pycache__' in n or n.endswith('.pyc') for x in before.values() for n in x),'Input package contains caches')
 out.mkdir();env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','XDG_CACHE_HOME':str(out/'cache')};env.pop('PYTHONOPTIMIZE',None);env['INSPECTION_QA_TOOL']=str(paths['tool'])
 commands=[[sys.executable,'-B','-m','unittest','discover','-s',str(ROOT),'-p','test_*.py','-v']]
 native=[str(paths['blender']),'-b','--factory-startup','--disable-autoexec','--threads','4','--python-exit-code','1','--python-expr','import sys; sys.dont_write_bytecode=True','--python',str(ROOT/'validate_modes.py'),'--']
 for k in ('source','baseline','tool','default','off','high','low','default_receipt','off_receipt','high_receipt','low_receipt'):native.extend(['--'+k.replace('_','-'),str(paths[k])])
 native.extend(['--report',str(out/'modes.json')]);commands.append(native)
 for phase in ('positive','negative'):
  index_native=native[:native.index('--python')+1]+[str(ROOT/'validate_index.py'),'--']
  for k in ('tool','default','off','high','low'):index_native.extend(['--'+k,str(paths[k])])
  index_native.extend(['--modes-report',str(out/'modes.json'),'--phase',phase,'--report',str(out/('index_'+phase+'.json'))]);commands.append(index_native)
 for i,cmd in enumerate(commands):
  with (out/f'{i:02d}.log').open('w') as log:subprocess.run(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 report=json.loads((out/'modes.json').read_text());require(report['pass'] is True,'Native QA JSON failed');index_reports={phase:json.loads((out/('index_'+phase+'.json')).read_text()) for phase in ('positive','negative')};require(all(r['pass'] is True for r in index_reports.values()),'Index QA JSON failed')
 require(inputs=={k:sha(paths[k]) for k in inputs},'Input bytes changed');require(before=={'qa':inventory(ROOT),'tool':inventory(paths['tool'])},'Payload changed')
 require(len(index_reports['positive']['negatives'])==64,'Expected64 repeated LOW refusals');require({k:len(v['actions'])for k,v in index_reports['positive']['modes'].items()}=={'default':0,'off':20,'high':20,'low':16},'Expected exact bookmark/index action coverage');require(len(report['negatives'])==27,'Expected27 quality controls');require(len(index_reports['negative']['negatives'])==37,'Expected37 selection controls');require(len(index_reports['negative']['native_panel_draw_cases'])==6,'Expected6 direct panel cases');require(all(m['category_count']==13 for m in report['modes'].values()),'Expected13 snapshot categories');
 result={'pass':True,'input_sha256':inputs,'inventory':before,'commands':commands,'native_calls':3,'pure_test_methods':13,'native_report_sha256':sha(out/'modes.json'),'index_report_sha256':{phase:sha(out/('index_'+phase+'.json')) for phase in index_reports},'source_saved':False,'rendered':False,'all_inputs_unchanged':True}
 (out/'SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n');print('CURRENT EDITING INDEX QA PASS')
if __name__=='__main__':main()
