"""Four pure-stdlib preflight negatives. No Blender and no canonical input needed."""
import hashlib,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
class Preflight(unittest.TestCase):
 def case(self,mode):
  with tempfile.TemporaryDirectory(prefix='pier Unicode 中文 ') as tmp:
   p=Path(tmp);source=p/'wrong source.blend';source.write_bytes(b'Not the pinned model');output=p/'new output.blend';report=p/'new report.json';before=hashlib.sha256(source.read_bytes()).hexdigest()
   if mode=='existing_output':output.write_bytes(b'preserve me')
   if mode=='source_alias':output=source
   cmd=[sys.executable]+(['-O']if mode=='optimized'else[])+[str(ROOT/'scripts/build.py'),'--','--source',str(source),'--plan',str(ROOT/'plan.json'),'--output',str(output),'--report',str(report)]
   r=subprocess.run(cmd,capture_output=True,text=True,timeout=20)
   self.assertNotEqual(r.returncode,0);self.assertNotIn('ModuleNotFoundError',r.stderr);self.assertNotIn("No module named 'bpy'",r.stderr)
   if mode=='optimized':self.assertIn('RuntimeError: Assertions must remain enabled',r.stderr)
   else:self.assertIn('AssertionError',r.stderr)
   self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),before);self.assertFalse(report.exists())
   if mode=='existing_output':self.assertEqual(output.read_bytes(),b'preserve me')
   elif mode!='source_alias':self.assertFalse(output.exists())
 def test_wrong_source(self):self.case('wrong_source')
 def test_existing_output(self):self.case('existing_output')
 def test_source_alias(self):self.case('source_alias')
 def test_optimized(self):self.case('optimized')
if __name__=='__main__':unittest.main()
