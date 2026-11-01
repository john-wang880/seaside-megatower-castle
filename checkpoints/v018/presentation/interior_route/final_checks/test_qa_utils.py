import unittest
from qa_utils import *
class Guards(unittest.TestCase):
 def test_indices_good(self):validate_indices([1,2,3],3)
 def test_hole(self):
  with self.assertRaises(AssertionError):validate_indices([1,3],3)
 def test_duplicate(self):
  with self.assertRaises(AssertionError):validate_indices([1,2,2],3)
 def test_pts_good(self):validate_timestamps([0,1/12,2/12],3,12)
 def test_pts_wrong(self):
  with self.assertRaises(AssertionError):validate_timestamps([0,1/12,1/12],3,12)
 def test_compression(self):
  self.assertTrue(compression_acceptable(.1,[0,0,0]));self.assertFalse(compression_acceptable(5,[0,0,0]));self.assertFalse(compression_acceptable(1,[3,0,0]));self.assertFalse(compression_acceptable(float('nan'),[0,0,0]))
 def test_legitimate_lossy_duplicate(self):self.assertIn('classification',classify_duplicate([1,2],{1:'a',2:'b'},{1:.1,2:.2},{(1,2):.115}))
 def test_inconsistent_duplicate(self):
  with self.assertRaises(AssertionError):classify_duplicate([1,2],{1:'a',2:'b'},{1:.1,2:.2},{(1,2):1})
 def test_source_duplicate(self):
  with self.assertRaises(AssertionError):classify_duplicate([1,2],{1:'a',2:'a'},{1:.1,2:.2},{(1,2):0})
if __name__=='__main__':unittest.main()
