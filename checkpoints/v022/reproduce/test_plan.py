import json,unittest
from pathlib import Path
class Plan(unittest.TestCase):
 def test_fixed_target_and_course_intervals(self):
  p=json.loads(Path(__file__).with_name('plan.json').read_text());q=p['proposal'];self.assertEqual([v['id']for v in p['target']['vertices']],list(range(56,64)));self.assertEqual(q['course_count'],13);self.assertEqual(q['nominal_cut_z'],[79.2,103.45]);self.assertEqual(q['joint_width'],.018);self.assertEqual(q['bevel'],.010)
  a,b=q['nominal_cut_z'];cuts=[a+(b-a)*i/13 for i in range(14)];intervals=[(lo+(.009 if i else 0),hi-(.009 if i<12 else 0))for i,(lo,hi)in enumerate(zip(cuts,cuts[1:]))]
  self.assertEqual(intervals[0][0],a);self.assertEqual(intervals[-1][1],b)
  for x,y in zip(intervals,intervals[1:]):self.assertAlmostEqual(y[0]-x[1],.018)
  self.assertTrue(all(hi-lo>1.8 for lo,hi in intervals));self.assertEqual(q['backing_inset_xy'],[.028,.035])
if __name__=='__main__':unittest.main()
