"""Pure portable orchestration negatives; no Blender, models, network or installs."""
import unittest,tempfile,pathlib,os,json,subprocess,sys
import run_qa as q
class Guards(unittest.TestCase):
 def setUp(self):self.t=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.t.name);self.f=self.root/'input';self.f.write_text('original')
 def tearDown(self):self.t.cleanup()
 def test_existing_input(self):self.assertEqual(q.clean(self.f),self.f)
 def test_new_output(self):self.assertEqual(q.clean(self.root/'new',False),self.root/'new')
 def test_no_overwrite(self):
  with self.assertRaises(RuntimeError):q.clean(self.f,False)
 def test_missing_input(self):
  with self.assertRaises(RuntimeError):q.clean(self.root/'absent')
 def test_missing_output_parent(self):
  with self.assertRaises(RuntimeError):q.clean(self.root/'absent'/'new',False)
 def test_parent_traversal(self):
  with self.assertRaises(RuntimeError):q.clean(self.root/'elsewhere'/'..'/'new',False)
 def test_symlink_file(self):
  a=self.root/'alias';a.symlink_to(self.f)
  with self.assertRaises(RuntimeError):q.clean(a)
 def test_symlink_ancestor(self):
  d=self.root/'real';d.mkdir();a=self.root/'link';a.symlink_to(d,target_is_directory=True)
  with self.assertRaises(RuntimeError):q.clean(a/'new',False)
 def test_hardlink_role_alias(self):
  a=self.root/'alias';os.link(self.f,a)
  with self.assertRaises(RuntimeError):q.role_guard([a,self.f])
 def test_good_hash(self):self.assertEqual(q.digest_string('a'*64),'a'*64)
 def test_malformed_hash(self):
  for v in ['a'*63,'G'*64,'a'*65,'a'*63+'\n']:
   with self.assertRaises(RuntimeError):q.digest_string(v)
 def manifest(self):
  b=self.root/'bundle';b.mkdir();(b/'a.py').write_text('x=1\n');(b/'FILES.json').write_text(json.dumps({'files':{'a.py':q.sha(b/'a.py')}}));return b
 def test_changed_helper(self):
  old=q.ROOT;q.ROOT=self.manifest()
  try:
   q.bundle_guard();(q.ROOT/'a.py').write_text('x=2\n')
   with self.assertRaises(RuntimeError):q.bundle_guard()
  finally:q.ROOT=old
 def test_extra_cache(self):
  old=q.ROOT;q.ROOT=self.manifest()
  try:
   (q.ROOT/'__pycache__').mkdir();(q.ROOT/'__pycache__/x.pyc').write_bytes(b'bad')
   with self.assertRaises(RuntimeError):q.bundle_guard()
  finally:q.ROOT=old
 def test_optimized_cli(self):
  env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';p=subprocess.run([sys.executable,'-B','-O',str(pathlib.Path(q.__file__)),'--help'],capture_output=True,env=env);self.assertNotEqual(p.returncode,0);self.assertIn(b'Optimized Python refused',p.stderr)
if __name__=='__main__':unittest.main()
