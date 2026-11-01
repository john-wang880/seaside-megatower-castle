"""Linux CPU-only fixtures; no Blender invocation or model render."""
import copy,fcntl,hashlib,json,math,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import runtime_guards as g
import run_final_orbit as runner
from orbit_common import validate_frame
class Guards(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(prefix='orbit 中文 ');self.root=Path(self.t.name);self.source=self.root/'fixture.blend';self.source.write_bytes(b'fixture');self.out=self.root/'fresh output'
 def tearDown(self):self.t.cleanup()
 def test_runtime_binding(self):g.identity()
 def test_wrong_source(self):
  with self.assertRaisesRegex(RuntimeError,'source'):g.check_source(self.source)
 def test_unknown_nonempty(self):
  self.out.mkdir();(self.out/'foreign').write_text('retain')
  with self.assertRaises(RuntimeError):g.check_existing(self.out,g.identity())
  self.assertEqual((self.out/'foreign').read_text(),'retain')
 def test_wrong_identity(self):
  self.out.mkdir();(self.out/'run_identity.json').write_text('{}')
  with self.assertRaises(RuntimeError):g.check_existing(self.out,g.identity())
 def test_alias_and_source_containment(self):
  with self.assertRaises(RuntimeError):g.check_output(self.source,self.root)
  with self.assertRaises(RuntimeError):g.clean(self.root/'x/../escape')
  self.out.symlink_to(self.root/'absent')
  with self.assertRaises(RuntimeError):g.check_output(self.source,self.out)
 def test_runtime_mutation(self):
  dst=self.root/'code';shutil.copytree(g.ROOT,dst,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  (dst/'render_final_frame.py').write_text('wrong')
  with patch.object(g,'ROOT',dst):
   with self.assertRaisesRegex(RuntimeError,'binding'):g.identity()
 def test_plan_mutation(self):
  dst=self.root/'code';shutil.copytree(g.ROOT,dst,ignore=shutil.ignore_patterns('__pycache__','*.pyc'));(dst/'final_plan.json').write_text('{}')
  with patch.object(g,'ROOT',dst):
   with self.assertRaisesRegex(RuntimeError,'plan'):g.identity()
 def test_optimized_refusal(self):
  p=subprocess.run([sys.executable,'-B','-O',str(g.ROOT/'run_final_orbit.py'),'--help'],capture_output=True,text=True)
  self.assertNotEqual(p.returncode,0);self.assertIn('Optimized Python refused',p.stderr)
 def test_single_output_lock(self):
  self.out.mkdir();p=self.out/'runner.lock'
  with p.open('a')as a,p.open('a')as b:
   fcntl.flock(a,fcntl.LOCK_EX|fcntl.LOCK_NB)
   with self.assertRaises(BlockingIOError):fcntl.flock(b,fcntl.LOCK_EX|fcntl.LOCK_NB)
 def synthetic_worker(self,cmd,**kwargs):
  self.assertIn('--python-exit-code',cmd);self.assertIn('--disable-autoexec',cmd);self.assertIn('--factory-startup',cmd)
  out=Path(cmd[cmd.index('--output-dir')+1]);index=int(cmd[cmd.index('--index')+1]);self.assertEqual(index,49);out.mkdir();plan=json.loads((g.ROOT/'final_plan.json').read_text());recipe=plan['frames'][index-1]['recipe'];d=[recipe['target'][i]-recipe['location'][i]for i in range(3)]
  def norm(v):
   n=math.sqrt(sum(x*x for x in v));return[x/n for x in v]
  def cross(a,b):return[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
  forward=norm(d);right=norm(cross(forward,[0,0,1]));up=cross(right,forward);matrix=[[right[i],up[i],-forward[i],recipe['location'][i]]for i in range(3)]+[[0,0,0,1]]
  Image.new('RGB',(960,694),(10,20,30)).save(out/'image.png');identity=g.identity()
  report={'lighting_state_sha256_before':plan['expected_lighting_state_sha256'],'lighting_state_sha256_after':plan['expected_lighting_state_sha256'],'runtime_identity_before':identity,'runtime_identity_after':identity,'index':index,'recipe':recipe,'manifest_sha256_at_start':g.PLAN_SHA,'worker_sha256':g.sha(g.ROOT/'render_final_frame.py'),'source_sha256_before':g.SOURCE_SHA,'source_sha256_after':g.SOURCE_SHA,'saved_model':False,'blender_version':plan['expected_blender_version'],'threads':8,'elapsed_render_seconds':0,'png_file_sha256':g.sha(out/'image.png'),'effective_settings':{'cycles':plan['expected_cycles'],'render':dict(plan['expected_render_except_filepath'],filepath='synthetic'),'view_settings':plan['expected_view_settings'],'image_settings':plan['expected_image_settings'],'frame':1,'camera':{'matrix_world':matrix,'use_dof':False,'data':dict({k:v for k,v in plan['expected_camera_projection'].items()if k!='use_dof'},**{k:recipe[k]for k in ('lens','clip_start','clip_end')})}}}
  (out/'metadata.json').write_text(json.dumps(report));return subprocess.CompletedProcess(cmd,0)
 def call_pilot(self,worker):
  args=['runner','--source',str(self.source),'--blender',str(Path(sys.executable).resolve()),'--output-dir',str(self.out),'--pilot-frame','49']
  with patch.object(sys,'argv',args),patch.object(g,'check_source',return_value=self.source),patch.object(runner,'check_source',return_value=self.source),patch.object(runner,'no_other_blender'),patch.object(runner.os,'sched_getaffinity',return_value=set(range(9))),patch.object(runner.subprocess,'run',side_effect=worker)as run:
   runner.main();return run.call_count
 def test_pilot_stop_and_verified_resume(self):
  self.assertEqual(self.call_pilot(self.synthetic_worker),1);self.assertTrue((self.out/'pilot_frame49.json').is_file());self.assertFalse((self.out/'frames_complete.json').exists());self.assertFalse(list(self.out.glob('*.mp4')))
  self.assertEqual(self.call_pilot(lambda *a,**k:(_ for _ in ()).throw(AssertionError('No worker expected'))),0)
 def test_interrupted_lock_only_setup_resumes(self):
  self.out.mkdir();(self.out/'runner.lock').touch()
  self.assertEqual(self.call_pilot(self.synthetic_worker),1)
  self.assertTrue((self.out/'pilot_frame49.json').is_file())
 def test_corrupt_frame_quarantined_and_rerendered(self):
  self.call_pilot(self.synthetic_worker);(self.out/'frames/frame_0049/image.png').write_bytes(b'broken');self.assertEqual(self.call_pilot(self.synthetic_worker),1);self.assertEqual(len(list((self.out/'quarantine').iterdir())),1)
if __name__=='__main__':unittest.main()
