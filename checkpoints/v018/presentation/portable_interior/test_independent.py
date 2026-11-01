"""Independent portable-runner safeguards; no Blender/model/render operations."""
import unittest,tempfile,sys,os,json,subprocess,hashlib
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import common as c,platform_runtime as rt
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='独立 QA ');self.b=Path(self.tmp.name);self.source=self.b/'model.blend';self.source.write_bytes(b'source');self.out=self.b/'output space'
 def tearDown(self):self.tmp.cleanup()
 def test_source_ancestor(self):
  with self.assertRaises(RuntimeError):c.guard_output(self.source,self.b)
 def test_protected_code(self):
  with self.assertRaises(RuntimeError):c.guard_output(self.source,ROOT/'bad')
 def test_approval_inside_output(self):
  with self.assertRaises(RuntimeError):c.guard_output(self.source,self.out,self.out/'approval.json')
 def test_foreign_output(self):
  self.out.mkdir();(self.out/'foreign').write_text('x')
  with self.assertRaises(RuntimeError):c.guard_output(self.source,self.out)
 @unittest.skipUnless(os.name == 'posix', 'POSIX-only integration control; native Windows locking/junctions not certified')
 def test_owned_symlink(self):
  self.out.mkdir();other=self.b/'other';other.mkdir();(self.out/'frames').symlink_to(other,target_is_directory=True)
  with self.assertRaises(RuntimeError):c.owned_path(self.out,self.out/'frames'/'x')
 def test_unicode_atomic(self):
  self.out.mkdir();p=self.out/'进度.json';c.atomic_json(self.out,p,{'x':'路径'});self.assertEqual(c.read_json(p),{'x':'路径'})
 def test_atomic_replace_failure_preserves(self):
  self.out.mkdir();p=self.out/'receipt.json';p.write_text('original')
  with patch.object(c.os,'replace',side_effect=PermissionError('sharing denied')):
   with self.assertRaises(PermissionError):c.atomic_json(self.out,p,{'x':1})
  self.assertEqual(p.read_text(),'original');self.assertEqual(len(list(self.out.glob('*.tmp'))),1)
 def test_old_frame_not_accepted(self):
  self.out.mkdir();folder=self.out/'frames'/'frame_0001';folder.mkdir(parents=True);(folder/'metadata.json').write_text('{}')
  class V:
   def validate_frame(*args):raise AssertionError('Must not delegate old-generation frame')
  self.assertFalse(c.validate_frame(self.out,folder,1,{}, {'new':True},V())['valid'])
 def test_old_approval_not_accepted(self):
  self.out.mkdir();p=self.b/'approval.json';p.write_text(json.dumps({'approved':True,'identity':{'old':1}}))
  with self.assertRaisesRegex(RuntimeError,'identity'):c.authorize_full(self.out,p,{'new':1},{'pilot_indices':[1]},None)
 def test_optimized_rejected(self):
  result=subprocess.run([sys.executable,'-O',str(ROOT/'run.py'),'--help'],capture_output=True,text=True);self.assertNotEqual(result.returncode,0);self.assertIn('Optimized Python',result.stderr)
 @unittest.skipUnless(os.name == 'posix', 'POSIX-only integration control; native Windows locking/junctions not certified')
 def test_real_cross_process_lock(self):
  lock=self.b/'lease.lock';code='import sys;sys.path.insert(0,sys.argv[1]);from platform_runtime import exclusive_lock;\nwith exclusive_lock(sys.argv[2]): print("owned",flush=True);sys.stdin.read()'
  child=subprocess.Popen([sys.executable,'-c',code,str(ROOT),str(lock)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  try:
   self.assertEqual(child.stdout.readline().strip(),'owned')
   with self.assertRaises(rt.LeaseError):
    with rt.exclusive_lock(lock):pass
   child.stdin.close();child.wait(timeout=10)
   inode=lock.stat().st_ino
   with rt.exclusive_lock(lock):pass
   self.assertEqual(lock.stat().st_ino,inode)
  finally:
   if child.poll() is None:child.kill();child.wait()
   for pipe in (child.stdin,child.stdout,child.stderr):
    if pipe is not None and not pipe.closed:pipe.close()
 def test_windows_adapter_mock(self):
  calls=[]
  class Fake:
   LK_NBLCK=1;LK_UNLCK=2
   @staticmethod
   def locking(fd,mode,n):calls.append((mode,n,os.lseek(fd,0,os.SEEK_CUR)))
  with patch.object(rt.sys,'platform','win32'),patch.dict(sys.modules,msvcrt=Fake):
   with rt.exclusive_lock(self.b/'windows.lock'):pass
  self.assertEqual(calls,[(1,1,0),(2,1,0)])
 def test_windows_lock_failure_no_bypass(self):
  class Fake:
   LK_NBLCK=1;LK_UNLCK=2
   @staticmethod
   def locking(*args):raise PermissionError('locked')
  with patch.object(rt.sys,'platform','win32'),patch.dict(sys.modules,msvcrt=Fake):
   with self.assertRaises(rt.LeaseError):
    with rt.exclusive_lock(self.b/'windows.lock'):self.fail('entered')
 def test_helper_hash_changes_identity(self):
  runtime=self.b/'runtime';runtime.mkdir();frozen=self.b/'frozen';frozen.mkdir();blender=self.b/'Blender exe';blender.write_bytes(b'executable')
  for n in c.RUNTIME_FILES:(runtime/n).write_text('old')
  plan={'frame_count':336,'fps':12,'resolution':[960,694],'frames':[{'index':i} for i in range(1,337)],'pilot_indices':list(range(1,26)),'expected_blender_version':'test'}
  (frozen/'final_plan.json').write_text(json.dumps(plan));(frozen/'final_motion.py').write_text('motion');(frozen/'orbit_common.py').write_text('validator')
  binding={'source_sha256':c.sha(self.source),'archive_manifest_sha256':'manifest'}
  with patch.object(c,'ROOT',runtime),patch.object(c,'FROZEN',frozen),patch.object(c,'verify_frozen',return_value=binding):
   first,_=c.make_identity(self.source,blender);(runtime/'platform_runtime.py').write_text('changed');second,_=c.make_identity(self.source,blender)
  self.assertNotEqual(first,second)
 def test_boundary_catches_identity_swap(self):
  import run,types
  self.out.mkdir();(self.out/'run_identity.json').write_text(json.dumps({'a':1}));args=types.SimpleNamespace(source=self.source,approval_file=None,blender=self.source,stage='pilot')
  with patch.object(run,'make_identity',return_value=({'a':2},{})):
   with self.assertRaisesRegex(RuntimeError,'changed during run'):run.check_boundary(args,self.out,{'a':1},{},None)
 def test_source_mismatch_rejected(self):
  with patch.object(c,'verify_frozen',return_value={'source_sha256':'incorrect'}):
   with self.assertRaisesRegex(RuntimeError,'Source SHA'):c.make_identity(self.source,self.source)
 def test_quarantine_denied_does_not_launch_worker(self):
  import run
  self.out.mkdir();identity={'fixture':True};(self.out/'run_identity.json').write_text(json.dumps(identity));folder=self.out/'frames'/'frame_0001';folder.mkdir(parents=True);(folder/'invalid').write_text('retain')
  plan={'pilot_indices':list(range(1,26))};invalid={'valid':False,'reason':'fixture invalid','index':1}
  with patch.object(run,'make_identity',return_value=(identity,plan)),patch.object(run,'load_validator',return_value=None),patch.object(run,'validate_frame',return_value=invalid),patch.object(run,'execution_lock_path',return_value=self.b/'global.lock'),patch.object(run.os,'rename',side_effect=PermissionError('quarantine denied')),patch.object(run.subprocess,'Popen') as spawn:
   with self.assertRaises(rt.LeaseError):run.main(['--source',str(self.source),'--blender',str(self.source),'--output-dir',str(self.out),'--stage','pilot','--max-new-frames','1'])
   spawn.assert_not_called()
  self.assertEqual((folder/'invalid').read_text(),'retain')
 @unittest.skipUnless(os.name == 'posix', 'POSIX-only integration control; native Windows locking/junctions not certified')
 def test_orphan_worker_holds_global_lock(self):
  import time
  lock=self.b/'shared-global.lock';release=self.b/'release'
  childcode="import sys,time;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from platform_runtime import exclusive_lock;\nwith exclusive_lock(sys.argv[2]):\n print('ready',flush=True)\n end=time.monotonic()+10\n while not Path(sys.argv[3]).exists() and time.monotonic()<end:time.sleep(.02)"
  parentcode="import subprocess,sys,json; p=subprocess.Popen([sys.executable,'-c',sys.argv[1],*sys.argv[2:]],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True);assert p.stdout.readline().strip()=='ready';p.stdout.close();print(p.pid);sys.stdout.flush();__import__('os')._exit(0)"
  result=subprocess.run([sys.executable,'-c',parentcode,childcode,str(ROOT),str(lock),str(release)],capture_output=True,text=True,timeout=5);self.assertEqual(result.returncode,0,result.stderr)
  try:
   with self.assertRaises(rt.LeaseError):
    with rt.exclusive_lock(lock):pass
  finally:release.write_text('finish')
  deadline=time.monotonic()+5
  while True:
   try:
    with rt.exclusive_lock(lock):break
   except rt.LeaseError:
    if time.monotonic()>deadline:raise
    time.sleep(.02)
 def approval_fixture(self):
  self.out.mkdir();identity={'fixture':True};plan={'pilot_indices':list(range(1,26))};frames=[]
  for i in plan['pilot_indices']:
   folder=self.out/'frames'/f'frame_{i:04d}';folder.mkdir(parents=True);(folder/'image.png').write_bytes(b'fixture'+str(i).encode());(folder/'metadata.json').write_text('{}')
   frames.append({'index':i,'valid':True,'png_sha256':c.sha(folder/'image.png'),'metadata_sha256':c.sha(folder/'metadata.json')})
  complete=self.out/'pilot_complete.json';complete.write_text(json.dumps({'identity':identity,'frames':frames}));approval=self.b/'approval.json';approval.write_text(json.dumps({'approved':True,'identity':identity,'approved_indices':plan['pilot_indices'],'pilot_complete_sha256':c.sha(complete)}));return identity,plan,approval
 def test_approval_byte_checks_positive(self):
  identity,plan,approval=self.approval_fixture();c.check_approval_envelope(self.out,approval,identity,plan)
 def test_approved_png_mutation_rejected(self):
  identity,plan,approval=self.approval_fixture();(self.out/'frames/frame_0001/image.png').write_bytes(b'altered')
  with self.assertRaisesRegex(RuntimeError,'pilot bytes changed'):c.check_approval_envelope(self.out,approval,identity,plan)
 def test_approved_metadata_mutation_rejected(self):
  identity,plan,approval=self.approval_fixture();(self.out/'frames/frame_0025/metadata.json').write_text('{"changed":true}')
  with self.assertRaisesRegex(RuntimeError,'pilot bytes changed'):c.check_approval_envelope(self.out,approval,identity,plan)
 def test_approval_wrong_receipt_order(self):
  identity,plan,approval=self.approval_fixture();receipt=self.out/'pilot_complete.json';d=c.read_json(receipt);d['frames'].reverse();receipt.write_text(json.dumps(d));a=c.read_json(approval);a['pilot_complete_sha256']=c.sha(receipt);approval.write_text(json.dumps(a))
  with self.assertRaisesRegex(RuntimeError,'indices mismatch'):c.check_approval_envelope(self.out,approval,identity,plan)
if __name__=='__main__':unittest.main(verbosity=2)
