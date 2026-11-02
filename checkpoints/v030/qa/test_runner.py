import importlib.util,tempfile,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('runner',Path(__file__).with_name('run_qa.py'));r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
class Guards(unittest.TestCase):
 def test_parent_traversal(self):
  with self.assertRaises(RuntimeError):r.clean('/tmp/out/../payload/new')
 def test_symlink(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d);(p/'target').mkdir();(p/'link').symlink_to(p/'target')
   with self.assertRaises(RuntimeError):r.clean(p/'link'/'new')
 def test_missing_plain_output_allowed_for_preflight(self):
  with tempfile.TemporaryDirectory()as d:self.assertEqual(r.clean(Path(d)/'new'),Path(d)/'new')
 def test_need_failclosed(self):
  with self.assertRaises(RuntimeError):r.need(False,'negative')
 def test_hash(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'input';p.write_bytes(b'abc');self.assertEqual(r.sha(p),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
if __name__=='__main__':unittest.main()
