import unittest,tempfile,subprocess,sys,os
from pathlib import Path
HERE=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 def run_cli(self,*args,opt=False):
  return subprocess.run([sys.executable,'-B',*(['-O']if opt else[]),str(HERE/'reproduce_geometry.py'),*map(str,args)],capture_output=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
 def test_existing_output(self):
  with tempfile.TemporaryDirectory()as t:
   r=self.run_cli('--output-dir',t);self.assertNotEqual(r.returncode,0);self.assertIn(b'output already exists',r.stderr)
 def test_wrong_source(self):
  with tempfile.TemporaryDirectory(prefix='replay 中文 ')as t:
   p=Path(t);(p/'wrong.blend').write_text('wrong');r=self.run_cli('--output-dir',p/'out','--source-model',p/'wrong.blend');self.assertNotEqual(r.returncode,0);self.assertIn(b'wrong source model',r.stderr);self.assertFalse((p/'out').exists())
 def test_symlink(self):
  with tempfile.TemporaryDirectory()as t:
   p=Path(t);(p/'out').symlink_to(p/'missing');r=self.run_cli('--output-dir',p/'out');self.assertNotEqual(r.returncode,0);self.assertIn(b'symlink',r.stderr)
 def test_optimized(self):
  r=self.run_cli('--help',opt=True);self.assertNotEqual(r.returncode,0);self.assertIn(b'optimized',r.stderr)
 def test_inside_recipe(self):
  r=self.run_cli('--output-dir',HERE/'FORBIDDEN');self.assertNotEqual(r.returncode,0);self.assertIn(b'inside recipe',r.stderr);self.assertFalse((HERE/'FORBIDDEN').exists())
if __name__=='__main__':unittest.main()
