"""Pure Python filesystem guard controls; no Blender required."""
import argparse,hashlib,importlib.util,json,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--exporter',required=True);p.add_argument('--source',required=True);p.add_argument('--report',required=True);a=p.parse_args();source=Path(a.source).resolve();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(source);spec=importlib.util.spec_from_file_location('reviewed_exporter',a.exporter);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);checks={}
with tempfile.TemporaryDirectory(prefix='Castle QA 中文 ') as d:
 d=Path(d);out=d/'浏览 copy.blend';report=d/'receipt.json'
 assert m.validate_paths(source,out,report)==(source,out,report);checks['unicode_spaces_new_paths']=True
 def reject(name,fn):
  try:fn()
  except (RuntimeError,FileNotFoundError):checks[name]=True;return
  raise AssertionError(name)
 reject('source output alias',lambda:m.validate_paths(source,source,report));out.write_bytes(b'keep');reject('existing output',lambda:m.validate_paths(source,out,report));assert out.read_bytes()==b'keep';out.unlink();report.write_text('keep');reject('existing report',lambda:m.validate_paths(source,out,report));assert report.read_text()=='keep';report.unlink();reject('missing output parent',lambda:m.validate_paths(source,d/'absent/out.blend',report));bad=d/'wrong.blend';bad.write_bytes(b'not accepted');reject('wrong source',lambda:m.validate_paths(bad,out,report));out.symlink_to(source);reject('source symlink output',lambda:m.validate_paths(source,out,report));assert out.is_symlink();out.unlink()
assert sha(source)==before;Path(a.report).write_text(json.dumps({'pass':True,'source_sha256':before,'source_unchanged':True,'checks':checks,'scope':'Linux filesystem tests including Unicode/spaces; no Windows GUI claim.'},indent=2));print('PATH GUARDS PASS',len(checks))
