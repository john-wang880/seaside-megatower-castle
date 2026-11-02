import unittest
from exact_axis_boundary import facets_from_cells,validate
from planar_triangulation import triangulate

def cube():
 v=[[0.,0.,0.],[1.,0.,0.],[1.,1.,0.],[0.,1.,0.],[0.,0.,1.],[1.,0.,1.],[1.,1.,1.],[0.,1.,1.]]
 faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
 return v,[t for f in faces for t in triangulate(v,f)]
class Controls(unittest.TestCase):
 def setUp(self):self.v,self.t=cube();self.ref=facets_from_cells([[0,1]]*3,{(0,0,0)})
 def test_valid(self):self.assertTrue(validate(self.v,self.t,self.ref)['pass'])
 def test_missing(self):
  with self.assertRaises(ValueError):validate(self.v,self.t[:-1],self.ref)
 def test_duplicate(self):
  with self.assertRaises(ValueError):validate(self.v,self.t+self.t[:1],self.ref)
 def test_equal_area_missing_duplicate(self):
  with self.assertRaises(ValueError):validate(self.v,self.t[:-1]+self.t[:1],self.ref)
 def test_wrong_orientation(self):
  with self.assertRaises(ValueError):validate(self.v,[list(reversed(self.t[0]))]+self.t[1:],self.ref)
 def test_translated_plane(self):
  v=[p[:] for p in self.v]
  for p in v:p[0]+=.125
  with self.assertRaises(ValueError):validate(v,self.t,self.ref)
 def test_filled_recess(self):
  refs=facets_from_cells([[0,.5,1]]*3,set((i,j,k) for i in range(2) for j in range(2) for k in range(2))-{(1,1,1)})
  with self.assertRaises(ValueError):validate(self.v,self.t,refs)
 def test_zero_triangle(self):
  with self.assertRaises(ValueError):validate(self.v,self.t+[[0,0,1]],self.ref)
 def test_concave_parent(self):
  v=[[0.,0.,0.],[2.,0.,0.],[2.,1.,0.],[1.,1.,0.],[1.,2.,0.],[0.,2.,0.]]
  self.assertEqual(len(triangulate(v,list(range(6)))),4)
 def test_crossed_parent(self):
  with self.assertRaises(ValueError):triangulate(self.v,[0,2,1,3])
if __name__=='__main__':unittest.main()
