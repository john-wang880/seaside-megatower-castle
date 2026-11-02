import pathlib,tempfile,subprocess,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parent
class Guards(unittest.TestCase):
 def setUp(self):self.t=tempfile.TemporaryDirectory(prefix='v029 replay 空间 ');self.p=pathlib.Path(self.t.name);self.src=self.p/'source.blend';self.src.write_bytes(b'wrong')
 def tearDown(self):self.t.cleanup()
 def run_guard(self,source=None,opt=False):
  out=self.p/'output';cmd=[sys.executable,'-O' if opt else '-B',str(ROOT/'rebuild_model.py'),'--source',str(source or self.src),'--blender','/not/a/blender','--output-dir',str(out)];r=subprocess.run(cmd,capture_output=True,text=True);self.assertNotEqual(r.returncode,0);self.assertFalse(out.exists());return r.stderr
 def test_wrong_source(self):self.assertIn('Wrong source model',self.run_guard())
 def test_symlink(self):
  a=self.p/'alias';a.symlink_to(self.src);self.assertIn('Aliased path',self.run_guard(a))
 def test_optimized(self):self.assertIn('Optimized Python refused',self.run_guard(opt=True))
if __name__=='__main__':unittest.main()
