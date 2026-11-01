import copy,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import rebuild as r
class Guards(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.d=Path(self.t.name)/'副本 with spaces';self.d.mkdir();self.src=self.d/'source.blend';self.src.write_bytes(b'x');self.out=self.d/'new.blend';self.rep=self.d/'new.json';self.plan=json.loads((r.ROOT/'plan.json').read_text());self.scope=json.loads((r.ROOT/'SCOPE.json').read_text())
 def tearDown(self):self.t.cleanup()
 def test_scope(self):r.validate_scope(self.plan,self.scope)
 def test_scope_mutations(self):
  cases=[]
  p=copy.deepcopy(self.plan);p['mapping'][0]['evaluated']['seed']=57;cases.append(p)
  p=copy.deepcopy(self.plan);p['mapping'][0]['raw']['indices'][0]=15;cases.append(p)
  p=copy.deepcopy(self.plan);p['material']='other';cases.append(p)
  p=copy.deepcopy(self.plan);p['mapping'][0]['evaluated']['materials']=[1];cases.append(p)
  p=copy.deepcopy(self.plan);p['deferred_components']=0;cases.append(p)
  p=copy.deepcopy(self.plan);p['tolerances']['strict_crossing']=.1;cases.append(p)
  for p in cases:
   with self.subTest(p=p):
    with self.assertRaises(r.GuardError):r.validate_scope(p,self.scope)
 def test_wrong_size(self):
  with self.assertRaisesRegex(r.GuardError,'bytes'):r.preflight(self.src,self.out,self.rep)
 def test_wrong_hash(self):
  with self.src.open('wb')as f:f.truncate(r.SOURCE_BYTES)
  with self.assertRaisesRegex(r.GuardError,'hash'):r.preflight(self.src,self.out,self.rep)
 def test_existing_destination(self):
  self.out.write_bytes(b'foreign')
  with self.assertRaises(r.GuardError):r.safe(self.out)
  self.assertEqual(self.out.read_bytes(),b'foreign')
 def test_alias(self):
  with self.assertRaises(r.GuardError):r.safe(self.d/'a/../new.blend')
 @unittest.skipIf(os.name=='nt','Symlink privilege nativeWindows untested')
 def test_dangling_link(self):
  self.out.symlink_to(self.d/'missing')
  with self.assertRaises(r.GuardError):r.safe(self.out)
 def test_success_unicode_mock_source_hash(self):
  with self.src.open('wb')as f:f.truncate(r.SOURCE_BYTES)
  real=r.sha
  with patch.object(r,'sha',side_effect=lambda p:r.SOURCE_SHA if Path(p)==self.src else real(p)):
   self.assertEqual(r.preflight(self.src,self.out,self.rep),(self.src,self.out,self.rep))
 def test_tampered_runtime(self):
  with patch.object(r,'sha',return_value='0'*64):
   with self.assertRaisesRegex(r.GuardError,'Runtime'):r.preflight(self.src,self.out,self.rep)
 def test_publish(self):
  a=self.d/'a';b=self.d/'b';a.write_bytes(b'model');b.write_bytes(b'report');r.publish([(a,self.out),(b,self.rep)]);self.assertEqual(self.out.read_bytes(),b'model')
 def test_foreign_inode_not_deleted(self):
  a=self.d/'a';b=self.d/'b';a.write_bytes(b'model');b.write_bytes(b'report');real=os.link;calls=[]
  def link(s,d):
   calls.append(d)
   if len(calls)==2:raise OSError('fail2')
   real(s,d);os.unlink(d);Path(d).write_bytes(b'foreign')
  with patch.object(r.os,'link',side_effect=link):
   with self.assertRaises(OSError):r.publish([(a,self.out),(b,self.rep)])
  self.assertEqual(self.out.read_bytes(),b'foreign')
 def test_rollback_own_file(self):
  a=self.d/'a';b=self.d/'b';a.write_bytes(b'model');b.write_bytes(b'report');real=os.link;calls=[]
  def link(s,d):
   calls.append(d)
   if len(calls)==2:raise OSError('fail2')
   real(s,d)
  with patch.object(r.os,'link',side_effect=link):
   with self.assertRaises(OSError):r.publish([(a,self.out),(b,self.rep)])
  self.assertFalse(self.out.exists())
 def test_optimized_refused(self):
  cmd=[sys.executable,'-O',str(r.ROOT/'rebuild.py'),'--source','missing','--output','new.blend','--report','new.json','--preflight-only'];p=subprocess.run(cmd,capture_output=True,text=True);self.assertNotEqual(p.returncode,0);self.assertIn('Optimized',p.stderr)
 def test_import_no_bpy(self):self.assertNotIn('bpy',sys.modules)
if __name__=='__main__':unittest.main()
