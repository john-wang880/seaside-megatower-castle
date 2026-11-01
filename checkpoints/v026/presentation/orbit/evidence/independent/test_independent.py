"""Independent Linux CPU fixtures. No Blender/render/encode invocation."""
import argparse,sys,os,json,math,copy,tempfile,subprocess,fcntl,hashlib,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('--recipe',required=True);ap.add_argument('--historical-plan',required=True);ap.add_argument('--report',required=True);args,rest=ap.parse_known_args();ROOT=Path(args.recipe).resolve();sys.path.insert(0,str(ROOT));sys.dont_write_bytecode=True
import runtime_guards as g,run_final_orbit as runner,orbit_common as common
PLAN=json.loads((ROOT/'final_plan.json').read_text());BEFORE={str(p.relative_to(ROOT)):g.sha(p)for p in ROOT.rglob('*')if p.is_file()};SOURCE=g.SOURCE_SHA
class Review(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='independent orbit 中文 ');self.root=Path(self.tmp.name);self.env=patch.dict(os.environ,{'XDG_CACHE_HOME':str(self.root/'shared cache'),'PYTHONDONTWRITEBYTECODE':'1'});self.env.start();self.source=self.root/'fixture.blend';self.source.write_bytes(b'not a real model');self.out=self.root/'new output';self.calls=[]
 def tearDown(self):self.env.stop();self.tmp.cleanup()
 def receipt(self,folder,index=49):
  folder.mkdir(parents=True,exist_ok=True);recipe=PLAN['frames'][index-1]['recipe'];d=[recipe['target'][k]-recipe['location'][k]for k in range(3)];length=math.sqrt(sum(x*x for x in d));f=[x/length for x in d];r=[f[1],-f[0],0];n=math.sqrt(sum(x*x for x in r));r=[x/n for x in r];u=[r[1]*f[2]-r[2]*f[1],r[2]*f[0]-r[0]*f[2],r[0]*f[1]-r[1]*f[0]];matrix=[[r[k],u[k],-f[k],recipe['location'][k]]for k in range(3)]+[[0.,0.,0.,1.]]
  camera={'matrix_world':matrix,'use_dof':False,'data':{**{k:v for k,v in PLAN['expected_camera_projection'].items()if k!='use_dof'},**{k:recipe[k]for k in ['lens','clip_start','clip_end']}}};Image.new('RGB',tuple(PLAN['resolution']),(22,33,44)).save(folder/'image.png')
  return {'runtime_identity_before':g.identity(),'runtime_identity_after':g.identity(),'lighting_state_sha256_before':PLAN['expected_lighting_state_sha256'],'lighting_state_sha256_after':PLAN['expected_lighting_state_sha256'],'index':index,'recipe':recipe,'blender_version':PLAN['expected_blender_version'],'manifest_sha256_at_start':g.PLAN_SHA,'worker_sha256':g.sha(ROOT/'render_final_frame.py'),'source_sha256_before':SOURCE,'source_sha256_after':SOURCE,'saved_model':False,'threads':8,'elapsed_render_seconds':1.0,'png_file_sha256':g.sha(folder/'image.png'),'effective_settings':{'cycles':copy.deepcopy(PLAN['expected_cycles']),'view_settings':copy.deepcopy(PLAN['expected_view_settings']),'image_settings':copy.deepcopy(PLAN['expected_image_settings']),'render':dict(PLAN['expected_render_except_filepath'],filepath='fixture only'),'frame':1,'camera':camera}}
 def status(self,folder,r):
  (folder/'metadata.json').write_text(json.dumps(r));return common.validate_frame(folder,49,PLAN,g.PLAN_SHA,g.sha(ROOT/'render_final_frame.py'))
 def fake_worker(self,cmd,**kwargs):
  self.calls.append(cmd);self.assertIn('--python-exit-code',cmd);self.assertIn('--disable-autoexec',cmd);index=int(cmd[cmd.index('--index')+1]);self.assertEqual(index,49);dest=Path(cmd[cmd.index('--output-dir')+1]);r=self.receipt(dest,index);(dest/'metadata.json').write_text(json.dumps(r));return subprocess.CompletedProcess(cmd,0)
 def pilot(self,fn=None):
  argv=['orbit','--source',str(self.source),'--blender',str(Path(sys.executable).resolve()),'--output-dir',str(self.out),'--pilot-frame','49']
  with patch.object(sys,'argv',argv),patch.object(g,'check_source',return_value=self.source),patch.object(runner,'check_source',return_value=self.source),patch.object(runner,'no_other_blender'),patch.object(runner.os,'sched_getaffinity',return_value=set(range(9))),patch.object(runner.subprocess,'run',side_effect=fn or self.fake_worker):runner.main()
 def test_historical_96_poses_quality_unchanged(self):
  old=json.loads(Path(args.historical_plan).read_text());self.assertEqual(PLAN['frames'],old['frames']);self.assertEqual(PLAN['expected_cycles'],old['expected_cycles']);self.assertEqual(PLAN['resolution'],[960,694]);self.assertEqual((PLAN['frame_count'],PLAN['fps']),(96,12))
 def test_metadata_corruption_cases(self):
  folder=self.root/'frame';base=self.receipt(folder);self.assertTrue(self.status(folder,base)['valid'])
  changes={'old_source':lambda d:d.update(source_sha256_after='old'),'old_runner':lambda d:d['runtime_identity_after']['runtime_sha256'].update({'run_final_orbit.py':'old'}),'old_worker':lambda d:d.update(worker_sha256='old'),'pose':lambda d:d['effective_settings']['camera']['matrix_world'][0].__setitem__(3,0),'roll':lambda d:[d['effective_settings']['camera']['matrix_world'][i].__setitem__(j,-d['effective_settings']['camera']['matrix_world'][i][j])for i in range(3)for j in range(2)],'late_nan':lambda d:d['effective_settings']['camera']['matrix_world'][2].__setitem__(1,float('nan')),'sensor':lambda d:d['effective_settings']['camera']['data'].update(sensor_width=12),'dof':lambda d:d['effective_settings']['camera'].update(use_dof=True),'projection':lambda d:d['effective_settings']['camera']['data'].update(type='ORTHO'),'samples':lambda d:d['effective_settings']['cycles'].update(samples=1),'lighting':lambda d:d.update(lighting_state_sha256_after='changed'),'frame':lambda d:d['effective_settings'].update(frame=2),'negative_time':lambda d:d.update(elapsed_render_seconds=-1)}
  for name,mutate in changes.items():
   with self.subTest(name=name):d=copy.deepcopy(base);mutate(d);self.assertFalse(self.status(folder,d)['valid'])
 def test_corrupt_and_wrong_size_png(self):
  folder=self.root/'frame';r=self.receipt(folder);(folder/'image.png').write_bytes(b'corrupt');self.assertFalse(self.status(folder,r)['valid']);Image.new('RGB',(2,2)).save(folder/'image.png');r['png_file_sha256']=g.sha(folder/'image.png');self.assertFalse(self.status(folder,r)['valid'])
 def test_pilot_stops_and_resume_skips(self):
  self.pilot();self.assertEqual(len(self.calls),1);self.assertFalse((self.out/'frames_complete.json').exists());self.assertFalse(list(self.out.glob('*.mp4')));self.assertTrue((self.out/'pilot_frame49.json').exists());self.pilot();self.assertEqual(len(self.calls),1);self.assertEqual([p.name for p in (self.out/'frames').iterdir()],['frame_0049'])
 def test_lock_only_interrupted_setup(self):
  self.out.mkdir();(self.out/'runner.lock').touch();self.pilot();self.assertEqual(len(self.calls),1)
 def test_interrupted_worker_resume(self):
  def fail(cmd,**kwargs):dest=Path(cmd[cmd.index('--output-dir')+1]);dest.mkdir();(dest/'partial').write_text('retain');return subprocess.CompletedProcess(cmd,1)
  with self.assertRaises(RuntimeError):self.pilot(fail)
  self.assertFalse((self.out/'pilot_frame49.json').exists());self.pilot();self.assertEqual(len(self.calls),1);self.assertEqual(len(list((self.out/'attempts').glob('*/partial'))),1)
 def test_quarantine_failure_preserves_invalid_frame(self):
  self.pilot();image=self.out/'frames/frame_0049/image.png';image.write_bytes(b'corrupt')
  with patch.object(runner.os,'rename',side_effect=PermissionError('fixture refusal')):
   with self.assertRaises(PermissionError):self.pilot()
  self.assertEqual(image.read_bytes(),b'corrupt');self.assertEqual(len(self.calls),1)
 def test_unknown_directory_alias_symlink(self):
  self.out.mkdir();(self.out/'foreign').write_text('do not touch')
  with self.assertRaises(RuntimeError):g.check_existing(self.out,g.identity())
  with self.assertRaises(RuntimeError):g.check_output(self.source,self.root)
  link=self.root/'alias';link.symlink_to(self.out)
  with self.assertRaises(RuntimeError):g.check_output(self.source,link)
  self.assertEqual((self.out/'foreign').read_text(),'do not touch')
 def test_source_and_code_drift(self):
  with self.assertRaises(RuntimeError):g.check_source(self.source)
  with patch.object(g,'sha',side_effect=lambda p:'bad'if Path(p).name=='orbit_common.py'else hashlib.sha256(Path(p).read_bytes()).hexdigest()):
   with self.assertRaises(RuntimeError):g.identity()
 def test_post_lock_recheck_failure_no_worker(self):
  with patch.object(runner,'recheck',side_effect=RuntimeError('source changed after lock')):
   with self.assertRaises(RuntimeError):self.pilot()
  self.assertEqual(self.calls,[]);self.assertFalse((self.out/'run_identity.json').exists())
 def test_no_implicit_full_stage_and_optimized_refusal(self):
  for switches in [[],['-O']]:
   r=subprocess.run([sys.executable,'-B',*switches,str(ROOT/'run_final_orbit.py'),'--source',str(self.source),'--blender',str(Path(sys.executable).resolve()),'--output-dir',str(self.out)],capture_output=True,text=True);self.assertNotEqual(r.returncode,0)
  self.assertFalse(self.out.exists())
 def test_cross_output_worker_lease_survives_output_unlock(self):
  lease=g.execution_lease_path();lease.parent.mkdir(parents=True);code="import fcntl,sys;f=open(sys.argv[1],'a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);print('READY',flush=True);sys.stdin.readline()";proc=subprocess.Popen([sys.executable,'-B','-c',code,str(lease)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  try:
   self.assertEqual(proc.stdout.readline().strip(),'READY')
   for output in [self.root/'run A',self.root/'run B']:
    output.mkdir()
    with (output/'runner.lock').open('a')as lock:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    with lease.open('a')as second:
     with self.assertRaises(BlockingIOError):fcntl.flock(second,fcntl.LOCK_EX|fcntl.LOCK_NB)
  finally:
   proc.communicate('\n',timeout=10)
   for stream in [proc.stdin,proc.stdout,proc.stderr]:
    if stream and not stream.closed:stream.close()
if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(Review);result=unittest.TextTestRunner(verbosity=2).run(suite);after={str(p.relative_to(ROOT)):g.sha(p)for p in ROOT.rglob('*')if p.is_file()};assert after==BEFORE,'Recipe changed during independent tests';out=Path(args.report);assert not out.exists();out.write_text(json.dumps({'pass':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'recipe_inventory':BEFORE,'recipe_unchanged':True,'scope':'Independent CPU/synthetic receipt and Linux flock fixtures; mocked frame worker only. No Blender/render/encode or full96-frame authorization.'},indent=2));sys.exit(0 if result.wasSuccessful()else 1)
