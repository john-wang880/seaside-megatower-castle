"""No Blender needed: ensure refusals occur before bpy import or model writes."""
import hashlib,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
class Guards(unittest.TestCase):
 def run_case(self,kind):
  with tempfile.TemporaryDirectory(prefix='path test 中文 ')as td:
   p=Path(td);source=p/'source file.blend';source.write_bytes(b'wrong source');out=p/'new output.blend';report=p/'new report.json';snapshot=p/'new snapshot.json';h=hashlib.sha256(source.read_bytes()).hexdigest()
   if kind=='existing_output':out.write_bytes(b'keep this')
   if kind=='source_alias':out=source
   if kind=='existing_report':report.write_text('keep report')
   if kind=='existing_snapshot':snapshot.write_text('keep snapshot')
   if kind=='output_report_alias':report=out
   if kind=='symlink':out.symlink_to(source)
   cmd=[sys.executable]+(['-O']if kind=='optimized'else[])+[str(ROOT/'scripts/build.py'),'--','--source',str(source),'--plan',str(ROOT/'plan.json'),'--output',str(out),'--report',str(report),'--source-snapshot',str(snapshot)]
   r=subprocess.run(cmd,capture_output=True,text=True,timeout=20);self.assertNotEqual(r.returncode,0);self.assertNotIn('ModuleNotFoundError',r.stderr)
   self.assertIn('RuntimeError: Assertions must remain enabled'if kind=='optimized'else'AssertionError',r.stderr)
   self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),h)
   if kind=='existing_output':self.assertEqual(out.read_bytes(),b'keep this')
   if kind=='existing_report':self.assertEqual(report.read_text(),'keep report')
   if kind=='existing_snapshot':self.assertEqual(snapshot.read_text(),'keep snapshot')
   if kind not in['existing_output','source_alias','symlink']:self.assertFalse(out.exists())
   if kind!='existing_report':self.assertFalse(report.exists())
   if kind!='existing_snapshot':self.assertFalse(snapshot.exists())
 def test_wrong_source(self):self.run_case('wrong_source')
 def test_existing_output(self):self.run_case('existing_output')
 def test_source_alias(self):self.run_case('source_alias')
 def test_optimized(self):self.run_case('optimized')
 def test_existing_report(self):self.run_case('existing_report')
 def test_existing_snapshot(self):self.run_case('existing_snapshot')
 def test_output_report_alias(self):self.run_case('output_report_alias')
 def test_symlink(self):self.run_case('symlink')
if __name__=='__main__':unittest.main()
