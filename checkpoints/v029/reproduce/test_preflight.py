"""Host-Python safety checks; no Blender import on rejected paths."""
import pathlib,tempfile,subprocess,sys,unittest,json
R=pathlib.Path(__file__).resolve().parent
class Guards(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='v029 guards 中文 ');self.p=pathlib.Path(self.tmp.name);self.source=self.p/'input.blend';self.source.write_bytes(b'wrong source');self.payload=R/'reference_payload.json'
 def tearDown(self):self.tmp.cleanup()
 def cmd(self,source=None,out=None,report=None,opt=False):
  return [sys.executable,'-O' if opt else '-B',str(R/'integrate.py'),'--','--source',str(source or self.source),'--payload',str(self.payload),'--output',str(out or self.p/'candidate.blend'),'--report',str(report or self.p/'report.json')]
 def fails(self,cmd,reason):
  r=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);self.assertNotEqual(r.returncode,0);self.assertIn(reason,r.stdout);self.assertNotIn('ModuleNotFoundError',r.stdout);self.assertFalse((self.p/'candidate.blend').exists());self.assertFalse((self.p/'report.json').exists())
 def test_wrong_source(self):self.fails(self.cmd(),'Wrong source')
 def test_optimized(self):self.fails(self.cmd(opt=True),'Optimized Python refused')
 def test_existing_output(self):
  p=self.p/'occupied.blend';p.write_bytes(b'keep');self.fails(self.cmd(out=p),'Missing input or occupied output');self.assertEqual(p.read_bytes(),b'keep')
 def test_alias(self):
  p=self.p/'alias.blend';p.symlink_to(self.source);self.fails(self.cmd(source=p),'Aliased path')
 def test_missing_parent(self):self.fails(self.cmd(out=self.p/'absent'/'x.blend'),'Missing input or occupied output')
 def test_wrong_payload(self):
  self.payload=self.p/'wrong.json';self.payload.write_text('{}');self.fails(self.cmd(),'Unreviewed geometry payload')
 def test_output_role(self):self.fails(self.cmd(out=self.p/'wrong.txt'),'Role/path mismatch')
if __name__=='__main__':unittest.main()
