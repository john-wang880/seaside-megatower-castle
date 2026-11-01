import unittest,tempfile,json,hashlib,subprocess,sys
from pathlib import Path
from unittest.mock import patch
import run_qa as q
class Guards(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='QA 中文 ');self.root=Path(self.temp.name);self.qa=self.root/'bundle';self.qa.mkdir();(self.qa/'a.py').write_text('pass\n');(self.qa/'FILES.json').write_text(json.dumps({'a.py':q.sha(self.qa/'a.py')}));self.source=self.root/'source.blend';self.candidate=self.root/'candidate.blend';self.accepted=self.root/'accepted.blend';self.out=self.root/'new result';self.source.write_text('source');self.candidate.write_text('candidate');self.accepted.write_text('accepted');self.actual=q.sha;self.mock=patch.object(q,'sha',side_effect=lambda p:q.SOURCE_SHA if Path(p)==self.source else q.ACCEPTED_SHA if Path(p)in[self.candidate,self.accepted]else self.actual(p));self.mock.start()
 def tearDown(self):self.mock.stop();self.temp.cleanup()
 def call(self,**kw):
  d=dict(source=self.source,candidate=self.candidate,accepted=None,out=self.out,qa=self.qa);d.update(kw);return q.preflight(**d)
 def test_valid(self):self.assertEqual(self.call(),q.ACCEPTED_SHA);self.assertFalse(self.out.exists())
 def test_existing_output(self):self.out.mkdir();self.assertRaises(RuntimeError,self.call)
 def test_frozen_output(self):self.assertRaises(RuntimeError,self.call,out=self.qa/'new')
 def test_checkpoint_output(self):p=self.root/'checkpoints';p.mkdir();self.assertRaises(RuntimeError,self.call,out=p/'new')
 def test_model_alias(self):self.assertRaises(RuntimeError,self.call,candidate=self.source)
 def test_wrong_source(self):p=self.root/'wrong';p.write_text('wrong');self.assertRaises(RuntimeError,self.call,source=p)
 def test_unknown_candidate(self):p=self.root/'rebuild';p.write_text('rebuild');self.assertRaises(RuntimeError,self.call,candidate=p)
 def test_rebuild_requires_semantic_reference(self):p=self.root/'rebuild';p.write_text('rebuild');self.assertEqual(self.call(candidate=p,accepted=self.accepted),self.actual(p))
 def test_changed_payload(self):(self.qa/'a.py').write_text('changed');self.assertRaises(RuntimeError,self.call)
 def test_extra_cache(self):(self.qa/'extra.pyc').write_text('cache');self.assertRaises(RuntimeError,self.call)
 def test_symlink(self):p=self.root/'alias';p.symlink_to(self.source);self.assertRaises(RuntimeError,q.clean_path,p)
 def test_parent_traversal(self):self.assertRaises(RuntimeError,q.clean_path,self.root/'folder'/'..'/'x')
 def test_optimized_refused(self):r=subprocess.run([sys.executable,'-O',str(Path(q.__file__)),'--help'],capture_output=True);self.assertNotEqual(r.returncode,0);self.assertIn(b'Optimized Python unsupported',r.stderr)
if __name__=='__main__':unittest.main()
