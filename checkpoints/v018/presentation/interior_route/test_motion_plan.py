"""Pure-Python final motion/plan invariants; no Blender/render."""
import json,math,unittest
from pathlib import Path
import final_motion as f
class MotionTests(unittest.TestCase):
 def setUp(self):self.plan=json.loads(Path(__file__).with_name('final_plan.json').read_text())
 def test_frames_and_actual_timestamps(self):
  self.assertEqual(len(self.plan['frames']),336)
  for i,r in enumerate(self.plan['frames']):self.assertEqual(r['index'],i+1);self.assertEqual(r['time_seconds'],i/12)
  self.assertEqual(f.MOTION_SECONDS,335/12)
 def test_baked_recipes_match_analytic(self):
  for r in self.plan['frames']:
   p=f.pose(r['time_seconds'])
   for key in ('location','target'):self.assertLess(max(abs(x-y) for x,y in zip(p[key],r['recipe'][key])),1e-12)
 def test_monotone_nonteleport_path(self):
  p=[f.pose(f.MOTION_SECONDS*i/10000) for i in range(10001)]
  self.assertTrue(all(a['distance_xy']<=b['distance_xy'] for a,b in zip(p,p[1:])))
  self.assertLess(max(x['speed_3d_mps'] for x in p),1.5)
  self.assertLess(max(abs(x['yaw_rate_degrees_per_second']) for x in p),45)
  self.assertLess(max(abs(x['yaw_acceleration_degrees_per_second2']) for x in p),37)
 def test_endpoint_stop_and_gaze(self):
  p=f.pose(f.MOTION_SECONDS);self.assertEqual(p['location'],[4.45,59.2,34.275]);self.assertEqual(p['yaw_degrees'],165);self.assertEqual(p['pitch_degrees'],3);self.assertEqual(p['speed_3d_mps'],0)
 def test_speed_and_gaze_join_continuity(self):
  joins=[s['t1'] for s in f.SEGMENTS[:-1]]+[f.TURN_GAZE_TIME_START,f.TURN_GAZE_TIME_END,f.END_GAZE_TIME_START,f.END_GAZE_TIME_END]
  for t in joins:
   a,b=f.pose(t-1e-7),f.pose(t+1e-7)
   for k in ('horizontal_speed_mps','yaw_rate_degrees_per_second','yaw_acceleration_degrees_per_second2','pitch_rate_degrees_per_second','pitch_acceleration_degrees_per_second2'):self.assertLess(abs(a[k]-b[k]),1e-3)
 def test_pilot_windows(self):
  windows=self.plan['pilot_windows'];self.assertEqual(len(windows),3);self.assertTrue(all(len(w)==8 and all(b==a+1 for a,b in zip(w,w[1:])) for w in windows));self.assertEqual(len(set(self.plan['pilot_indices'])),25)
 def test_scene_frozen_original_quality(self):
  self.assertEqual(self.plan['source_scene_frame'],1);self.assertEqual(self.plan['expected_cycles']['samples'],80);self.assertEqual(self.plan['expected_cycles']['max_bounces'],8);self.assertFalse(self.plan['expected_render_except_filepath']['use_persistent_data'])
if __name__=='__main__':unittest.main()
