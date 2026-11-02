import unittest,numpy as np
from coplanar_predicate import candidates,contact as raw_contact
def contact(a,b,eps):return raw_contact(np.asarray(a).tolist(),np.asarray(b).tolist(),eps)
class Controls(unittest.TestCase):
 def setUp(self):self.a=np.array([[0.,0.,0.],[20.,0.,0.],[0.,14.,0.]]);self.eps=1e-7
 def test_known140(self):self.assertAlmostEqual(contact(self.a,self.a,self.eps)['area'],140.)
 def test_same_facing(self):self.assertTrue(contact(self.a,self.a,self.eps)['same_facing'])
 def test_opposite_facing(self):self.assertFalse(contact(self.a,self.a[::-1],self.eps)['same_facing'])
 def test_explicit_broadphase(self):self.assertEqual(candidates(self.a,np.array([self.a]),self.eps),[0])
 def test_parallel_gap(self):self.assertIsNone(contact(self.a,self.a+[0,0,.01],self.eps))
 def test_disjoint_same_plane(self):self.assertIsNone(contact(self.a,self.a+[30,0,0],self.eps))
 def test_edge_only(self):self.assertIsNone(contact(self.a,np.array([[0,0,0],[20,0,0],[0,-14,0.]]),self.eps))
 def test_nonparallel(self):self.assertIsNone(contact(self.a,np.array([[0,0,0],[20,0,0],[0,0,14.]]),self.eps))
 def test_zero_triangle(self):self.assertIsNone(contact(self.a,np.zeros((3,3)),self.eps))
if __name__=='__main__':unittest.main()
