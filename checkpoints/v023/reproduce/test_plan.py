"""Pure arithmetic controls; not a substitute for actual Blender geometry QA."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'scripts'))
from overlay_math import area,ccw,clip,plane
class Plan(unittest.TestCase):
 def test_local_mask_incidence(self):
  p=json.loads((ROOT/'plan.json').read_text()); ids=set(range(*p['mask_vertex_range'])); touched=[]
  for row in range(126):
   for cell in range(6):
    a=row*7+cell;b=a+1;c=a+7;d=c+1
    # Both diagonal conventions touch the same face range for these full interior rows.
    for k,tri in enumerate([(a,c,d),(a,d,b)]):
     if ids.intersection(tri):touched.append(row*12+cell*2+k)
  self.assertEqual(touched,list(range(1140,1260)));self.assertEqual(len(ids),63)
  self.assertEqual(p['selected_face_range'],[95*12,105*12]);self.assertEqual(1512-120,1392)
 def test_overlay_partition(self):
  square=ccw([(0.,0.),(2.,0.),(2.,2.),(0.,2.)]); triangles=[ccw([(0.,0.),(2.,0.),(2.,2.)]),ccw([(0.,0.),(2.,2.),(0.,2.)])]
  self.assertAlmostEqual(sum(area(clip(square,t))for t in triangles),area(square))
 def test_plane_and_clearance(self):
  a,b,c=plane([(0,0,1),(2,0,5),(0,2,7)]);self.assertEqual((a,b,c),(2.,3.,1.))
  p=json.loads((ROOT/'plan.json').read_text());self.assertLess(p['full_face_clearance_bounds'][0],p['offset']);self.assertLess(p['offset'],p['full_face_clearance_bounds'][1])
if __name__=='__main__':unittest.main()
