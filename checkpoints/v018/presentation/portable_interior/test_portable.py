"""Linux tests and Windows adapter mocks; no real render or installation."""
import builtins,importlib.util,json,os,subprocess,sys,tempfile,types,unittest
from pathlib import Path
from unittest import mock
import common,run
import platform_runtime as rt
class PortableTests(unittest.TestCase):
 def test_lazy_imports(self):
  original=builtins.__import__
  def guard(name,*a,**k):
   if name in ('bpy','resource','fcntl','msvcrt'):raise AssertionError(name)
   return original(name,*a,**k)
  for n in ('run.py','worker.py','platform_runtime.py'):
   spec=importlib.util.spec_from_file_location('probe',common.ROOT/n)
   with mock.patch('builtins.__import__',side_effect=guard):spec.loader.exec_module(importlib.util.module_from_spec(spec))
 def test_frozen51(self):self.assertEqual(common.verify_frozen()['archive_payload_count'],51)
 def test_optimized_refused(self):
  p=subprocess.run([sys.executable,'-O',str(common.ROOT/'run.py'),'--help'],capture_output=True,text=True);self.assertNotEqual(p.returncode,0);self.assertIn('Optimized Python',p.stderr)
 def test_source_output_containment(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);src=root/'source';src.write_bytes(b'x')
   for out in (root,src,src/'nested'):
    with self.assertRaises(RuntimeError):common.guard_output(src,out)
 def test_protected_code_history(self):
  for out in (common.FROZEN/'new',common.ROOT/'new',common.REPO/'work/interior_preview_v018/final_v2/new'):
   with self.assertRaises(RuntimeError):common.guard_output(Path('/tmp/source'),out)
 def test_foreign_output_and_approval_inside(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);out=r/'out';out.mkdir();(out/'image.png').write_bytes(b'x')
   with self.assertRaises(RuntimeError):common.guard_output(r/'source',out)
   with self.assertRaises(RuntimeError):common.guard_output(r/'source',r/'fresh',r/'fresh/approval.json')
 def test_unicode_spaces_atomic(self):
  with tempfile.TemporaryDirectory(prefix='space 中文 ') as d:
   r=Path(d);out=r/'输出 directory';out.mkdir();self.assertEqual(common.guard_output(r/'source',out),out)
   common.atomic_json(out,out/'receipt.json',{'中文':'value'});self.assertEqual(common.read_json(out/'receipt.json'),{'中文':'value'})
 def test_symlink_escape(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);out=r/'out';out.mkdir();other=r/'other';other.mkdir()
   try:(out/'link').symlink_to(other,target_is_directory=True)
   except OSError:self.skipTest('no symlinks')
   with self.assertRaises(RuntimeError):common.owned_path(out,out/'link/image.png')
 def test_real_posix_lock_and_reacquire(self):
  if os.name!='posix':self.skipTest('POSIX only')
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'lock';code='from platform_runtime import exclusive_lock;import sys\nwith exclusive_lock(sys.argv[1]): pass'
   with rt.exclusive_lock(path):
    p=subprocess.run([sys.executable,'-c',code,str(path)],cwd=common.ROOT,capture_output=True);self.assertNotEqual(p.returncode,0)
   inode=path.stat().st_ino
   with rt.exclusive_lock(path):pass
   self.assertEqual(inode,path.stat().st_ino)
 def test_windows_lock_seek_release(self):
  calls=[];fake=types.SimpleNamespace(LK_NBLCK=1,LK_UNLCK=2,locking=lambda fd,m,n:calls.append((m,n,os.lseek(fd,0,os.SEEK_CUR))))
  with tempfile.TemporaryDirectory() as d,mock.patch.object(rt.sys,'platform','win32'),mock.patch.dict(sys.modules,msvcrt=fake):
   with rt.exclusive_lock(Path(d)/'lock'):pass
  self.assertEqual(calls,[(1,1,0),(2,1,0)])
 def test_windows_busy_no_bypass(self):
  fake=types.SimpleNamespace(LK_NBLCK=1,LK_UNLCK=2,locking=mock.Mock(side_effect=OSError('busy')))
  with tempfile.TemporaryDirectory() as d,mock.patch.object(rt.sys,'platform','win32'),mock.patch.dict(sys.modules,msvcrt=fake):
   path=Path(d)/'lock'
   with self.assertRaises(rt.LeaseError):
    with rt.exclusive_lock(path):self.fail('entered')
   self.assertTrue(path.exists());self.assertEqual(fake.locking.call_count,1)
 def test_optional_windows_metrics(self):
  with mock.patch.object(rt.sys,'platform','win32'),mock.patch.object(rt.os,'sched_getaffinity',side_effect=OSError('no'),create=True):self.assertEqual(rt.optional_metrics(),{'affinity_logical_cpus':None,'peak_rss_linux_kib':None})
 def test_missing_resource(self):
  with mock.patch.object(rt.sys,'platform','linux'),mock.patch.dict(sys.modules,resource=None):self.assertIsNone(rt.optional_metrics()['peak_rss_linux_kib'])
 def test_command_empty_start_unicode(self):
  with tempfile.TemporaryDirectory(prefix='space 中文 ') as d:
   r=Path(d);common.atomic_json(r,r/'run_identity.json',{'id':1});a=types.SimpleNamespace(blender=r/'Blender App.exe',source=r/'城堡.blend',current_index=1,stage='pilot',approval_file=None)
   cmd=run.worker_command(a,r/'attempts/frame',r);self.assertIn('--factory-startup',cmd);self.assertIn('--disable-autoexec',cmd);self.assertEqual(cmd[cmd.index('--python-exit-code')+1],'1');self.assertNotIn(str(a.source),cmd[:cmd.index('--')]);self.assertEqual(cmd[0],str(a.blender))
 def test_old_approval_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);out=r/'out';out.mkdir();ap=r/'approval.json';ap.write_text(json.dumps({'approved':True,'identity':{'old':1}}))
   with self.assertRaisesRegex(RuntimeError,'identity'):common.check_approval_envelope(out,ap,{'new':1},{'pilot_indices':[1]})
 def test_incomplete_pilot_no_authorization(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);out=r/'out';out.mkdir();ap=r/'approval.json';ap.write_text(json.dumps({'approved':True,'identity':{'new':1},'approved_indices':[1]}))
   with self.assertRaises(OSError):common.check_approval_envelope(out,ap,{'new':1},{'pilot_indices':[1]})
 def test_postlock_identity_changed(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);out=r/'out';out.mkdir();a=types.SimpleNamespace(source=r/'source',blender=r/'blender',approval_file=None,stage='pilot')
   with mock.patch.object(run,'make_identity',return_value=({'changed':1},{})):
    with self.assertRaisesRegex(RuntimeError,'changed'):run.check_boundary(a,out,{'old':1},{},None)
 def test_missing_encoder_no_install(self):
  with mock.patch.object(run.shutil,'which',return_value=None):
   with self.assertRaisesRegex(RuntimeError,'no auto-install'):run.tool_path(None,'ffmpeg')
 def test_old_frame_receipt_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);f=r/'frame';f.mkdir();(f/'metadata.json').write_text('{}');v=mock.Mock();self.assertFalse(common.validate_frame(r,f,1,{}, {'new':1},v)['valid']);v.validate_frame.assert_not_called()
 def test_video_pts_and_noaudio(self):
  probe={'streams':[{'codec_type':'video','codec_name':'h264','pix_fmt':'yuv420p','width':960,'height':694,'nb_read_frames':'336','avg_frame_rate':'12/1'}],'format':{'duration':'28'}}
  frames={'frames':[{'best_effort_timestamp_time':str(i/12)} for i in range(336)]}
  self.assertEqual(len(run.validate_video_probe(probe,frames)),336)
  import copy
  for kind in ('wrong_pts','missing_frame','audio','wrong_type','wrong_fps'):
   p=copy.deepcopy(probe);f=copy.deepcopy(frames)
   if kind=='wrong_pts':f['frames'][42]['best_effort_timestamp_time']='3.6'
   elif kind=='missing_frame':f['frames'].pop()
   elif kind=='audio':p['streams'].append({'codec_type':'audio'})
   elif kind=='wrong_type':p['streams'][0]['codec_type']='audio'
   else:p['streams'][0]['avg_frame_rate']='24/1'
   with self.subTest(kind=kind),self.assertRaises(RuntimeError):run.validate_video_probe(p,f)
if __name__=='__main__':unittest.main()
