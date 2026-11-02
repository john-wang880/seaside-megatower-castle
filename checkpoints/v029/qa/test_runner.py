"""Pure path/identity/inventory guards; no Blender or model mutation."""
import tempfile,unittest,os,subprocess,sys
from pathlib import Path
import run_qa as r
class Guards(unittest.TestCase):
 def test_optimized_refused(self):
  env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
  result=subprocess.run([sys.executable,'-B','-O',str(Path(r.__file__)),'--help'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,env=env)
  self.assertNotEqual(result.returncode,0);self.assertIn('Optimized Python refused',result.stdout)
 def test_hash(self):
  for v in ['','A'*64,'0'*63,'../x']:
   with self.assertRaises(RuntimeError):r.digest_string(v)
  self.assertEqual(r.digest_string('a'*64),'a'*64)
 def test_missing_and_existing(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'x';p.write_text('x')
   with self.assertRaises(RuntimeError):r.clean(p,False)
   with self.assertRaises(RuntimeError):r.clean(Path(d)/'absent')
 def test_parent_traversal(self):
  with tempfile.TemporaryDirectory()as d:
   with self.assertRaises(RuntimeError):r.clean(Path(d)/'outside/../payload/new',False)
 def test_symlink(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'x';p.write_text('x');s=Path(d)/'link';s.symlink_to(p)
   with self.assertRaises(RuntimeError):r.clean(s)
 def test_hardlink_alias(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'x';p.write_text('x');s=Path(d)/'link';os.link(p,s)
   with self.assertRaises(RuntimeError):r.role_guard([p,s])
 def test_inventory_symlink(self):
  with tempfile.TemporaryDirectory()as d:
   (Path(d)/'link').symlink_to('/tmp')
   with self.assertRaises(RuntimeError):r.inventory(Path(d))
 def test_inventory_detects_change(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'x';p.write_text('x');before=r.inventory(Path(d));p.write_text('y');self.assertNotEqual(before,r.inventory(Path(d)))
if __name__=='__main__':unittest.main()
