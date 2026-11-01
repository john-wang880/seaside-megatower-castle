"""Pure fixture tests, no Blender/model files."""
import hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
sys.dont_write_bytecode=True
import run_qa as q
class Guards(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='hall QA 中文 ');self.r=Path(self.tmp.name);self.qa=self.r/'qa';self.qa.mkdir();self.source=self.r/'source';self.source.write_bytes(b'source');self.candidate=self.r/'candidate';self.candidate.write_bytes(b'accepted');self.accepted=self.r/'accepted';self.accepted.write_bytes(b'accepted');q.SOURCE_SHA=q.sha(self.source);q.ACCEPTED_SHA=q.sha(self.candidate);self.receipt=self.r/'build.json';self.receipt.write_text(json.dumps({'source_sha256':q.SOURCE_SHA,'candidate_sha256':q.ACCEPTED_SHA,'operands':[]}));(self.qa/'accepted_operands.json').write_text('[]');self.manifest();self.out=self.r/'new reports'
 def manifest(self):(self.qa/'FILES.json').write_text(json.dumps({str(p.relative_to(self.qa)):q.sha(p)for p in self.qa.rglob('*')if p.is_file()and p.name!='FILES.json'}))
 def tearDown(self):self.tmp.cleanup()
 def run_gate(self,accepted=None):return q.preflight(self.source,self.candidate,accepted,self.receipt,self.out,self.qa)
 def reject(self):
  with self.assertRaises((RuntimeError,KeyError,ValueError)):self.run_gate()
 def test_valid(self):self.assertEqual(self.run_gate(),q.ACCEPTED_SHA)
 def test_wrong_source(self):self.source.write_bytes(b'wrong');self.reject()
 def test_unknown_candidate(self):self.candidate.write_bytes(b'rebuilt');self.reject()
 def test_rebuilt_with_reference(self):
  self.candidate.write_bytes(b'rebuilt');r=json.loads(self.receipt.read_text());r['candidate_sha256']=q.sha(self.candidate);self.receipt.write_text(json.dumps(r));self.assertEqual(self.run_gate(self.accepted),q.sha(self.candidate))
 def test_wrong_accepted(self):
  self.accepted.write_bytes(b'wrong')
  with self.assertRaises(RuntimeError):self.run_gate(self.accepted)
 def test_receipt_identity(self):
  r=json.loads(self.receipt.read_text());r['candidate_sha256']='bad';self.receipt.write_text(json.dumps(r));self.reject()
 def test_operand_drift(self):
  r=json.loads(self.receipt.read_text());r['operands']=[1];self.receipt.write_text(json.dumps(r));self.reject()
 def test_existing_output(self):self.out.mkdir();self.reject()
 def test_missing_parent(self):self.out=self.r/'missing'/'new';self.reject()
 def test_output_under_bundle(self):self.out=self.qa/'new';self.reject()
 def test_checkpoint_output(self):(self.r/'checkpoints').mkdir();self.out=self.r/'checkpoints'/'new';self.reject()
 def test_hardlink_alias(self):self.candidate.unlink();os.link(self.source,self.candidate);self.reject()
 def test_payload_tamper(self):(self.qa/'accepted_operands.json').write_text('[3]');self.reject()
 def test_extra_cache(self):(self.qa/'extra.pyc').write_bytes(b'bad');self.reject()
 def test_symlink(self):
  p=self.r/'linked';p.symlink_to(self.source)
  with self.assertRaises(RuntimeError):q.clean_path(p)
 def test_traversal(self):
  with self.assertRaises(RuntimeError):q.clean_path(str(self.r/'x'/'..'/'source'))
 def test_optimized(self):
  r=subprocess.run([sys.executable,'-B','-O',str(Path(q.__file__)),'--help'],capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'});self.assertNotEqual(r.returncode,0);self.assertIn(b'Optimized',r.stderr)
if __name__=='__main__':unittest.main()
