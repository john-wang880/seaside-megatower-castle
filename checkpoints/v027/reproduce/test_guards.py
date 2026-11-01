import unittest,tempfile,json,hashlib,os,copy,subprocess,sys
from pathlib import Path
from unittest.mock import patch
import rebuild as r
class Guards(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.p=Path(self.t.name);self.src=self.p/'输入 source.blend';self.src.write_bytes(b'source');self.out=self.p/'new.blend';self.rep=self.p/'new.json';self.plan=json.loads((r.ROOT/'plan.json').read_text())
 def tearDown(self):self.t.cleanup()
 def pre(self):
  with patch.object(r,'validate_scope'),patch.object(r,'SOURCE_BYTES',6),patch.object(r,'SOURCE_SHA',r.sha(self.src)):return r.preflight(self.src,self.out,self.rep)
 def test_real_runtime(self):self.pre();r.validate_scope(self.plan)
 def test_wrong_size(self):
  with self.assertRaises(r.GuardError):r.preflight(self.src,self.out,self.rep)
 def test_wrong_hash(self):
  with patch.object(r,'validate_scope'),patch.object(r,'SOURCE_BYTES',6),self.assertRaises(r.GuardError):r.preflight(self.src,self.out,self.rep)
 def test_overwrite(self):self.out.write_text('x');self.assertRaises(r.GuardError,self.pre)
 def test_source_alias(self):self.out=self.src;self.assertRaises(r.GuardError,self.pre)
 def test_report_alias(self):self.rep=self.out;self.assertRaises(r.GuardError,self.pre)
 def test_symlink(self):self.out.symlink_to(self.src);self.assertRaises(r.GuardError,self.pre)
 def test_dangling_symlink(self):self.out.symlink_to(self.p/'missing');self.assertRaises(r.GuardError,self.pre)
 def test_missing_parent(self):self.out=self.p/'missing'/'out.blend';self.assertRaises(r.GuardError,self.pre)
 def test_parent_alias(self):self.assertRaises(r.GuardError,r.safe,self.p/'x'/'..'/'out.blend')
 def test_runtime_corruption(self):
  with patch.dict(r.PINNED,{'scripts/build.py':'0'*64}),self.assertRaises(r.GuardError):self.pre()
 def test_missing_sibling(self):
  with patch.dict(r.PINNED,{'scripts/missing.json':'0'*64}),self.assertRaises(r.GuardError):self.pre()
 def test_scope_mutations(self):
  for k,v in [('material','wrong'),('stations',[-1.8,.4]),('courses',8),('bounds',[[-3,36.56,31.98],[3.2,39.44,32.82]]),('groove_depth',.06),('crown_top',33)]:
   with self.subTest(k=k):p=copy.deepcopy(self.plan);p[k]=v;self.assertRaises(r.GuardError,r.validate_scope,p)
 def test_utf8_limit(self):p=copy.deepcopy(self.plan);p['object']='岩'*22;self.assertRaises(r.GuardError,r.validate_scope,p)
 def test_optimized(self):
  q=subprocess.run([sys.executable,'-O',str(r.ROOT/'rebuild.py'),'--preflight-only','--source',str(self.src),'--output',str(self.out),'--report',str(self.rep)],capture_output=True,text=True);self.assertNotEqual(q.returncode,0);self.assertIn('Optimized',q.stderr)
 def test_publish_failure_rolls_owned_back(self):
  a=self.p/'a';b=self.p/'b';a.write_text('owned');b.write_text('second');orig=os.link
  def link(x,y):
   if Path(y)==self.rep:raise OSError('second failed')
   return orig(x,y)
  with patch.object(os,'link',side_effect=link),self.assertRaises(OSError):r.publish([(a,self.out),(b,self.rep)])
  self.assertFalse(self.out.exists())
 def test_first_link_foreign_replacement_survives(self):
  a=self.p/'a';b=self.p/'b';a.write_text('owned');b.write_text('second');orig=os.link
  def link(x,y):
   if Path(y)==self.rep:raise OSError('second failed')
   orig(x,y);Path(y).unlink();Path(y).write_text('foreign')
  with patch.object(os,'link',side_effect=link),self.assertRaises(OSError):r.publish([(a,self.out),(b,self.rep)])
  self.assertEqual(self.out.read_text(),'foreign')
if __name__=='__main__':unittest.main()
