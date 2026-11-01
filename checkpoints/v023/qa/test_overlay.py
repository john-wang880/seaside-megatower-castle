import unittest
from overlay_math import *
class Tests(unittest.TestCase):
 def test_hidden_interior_ridge(self):
  road=[(0,0,.021),(1,0,.021),(0,1,.021)];a=(0,0,0);b=(1,0,0);c=(0,1,0);peak=(1/3,1/3,.1);terrain=[[a,b,peak],[b,c,peak],[c,a,peak]];pieces=triangle_overlay(road,terrain)
  self.assertAlmostEqual(sum(p['area']for p in pieces),.5);self.assertAlmostEqual(min(p['minimum']for p in pieces),-.079);self.assertTrue(all(v[2]>.016 for v in road))
 def test_constant_supported_gap(self):
  terrain=[[(0,0,0),(1,0,.2),(0,1,.1)]];road=[(x,y,z+.021)for x,y,z in terrain[0]];p=triangle_overlay(road,terrain)[0];self.assertAlmostEqual(p['minimum'],.021);self.assertAlmostEqual(p['maximum'],.021)
 def test_float_misleading_maximum(self):
  terrain=[[(0,0,0),(1,0,0),(0,1,0)]];p=triangle_overlay([(0,0,.021),(1,0,.08),(0,1,.021)],terrain)[0];self.assertGreater(p['maximum'],.03)
 def test_clipping_orientation(self):
  a=[(0,0),(1,0),(0,1)];b=[(0,0),(.5,0),(0,.5)];self.assertAlmostEqual(area(clip(a,b)),.125);self.assertAlmostEqual(area(clip(a,b[::-1])),.125)
 def test_overlap_vs_touch(self):
  a=[(0,0),(1,0),(0,1)];b=[(1,0),(1,1),(0,1)];self.assertAlmostEqual(area(clip(a,b)),0);self.assertAlmostEqual(area(clip(a,a)),.5)
if __name__=='__main__':unittest.main()
