"""Independent bounded v030 mapping/camera and interleaving checks; no bpy."""
import copy,json,unittest,os
from pathlib import Path
import expected_scope as s
class Scope(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tool=Path(os.environ['INSPECTION_QA_TOOL']);cls.catalog=json.loads((cls.tool/'catalog.json').read_text());cls.index=json.loads((cls.tool/'edit_index.json').read_text())
 def test_exact_scope(self):s.validate_scope(self.catalog,self.index,self.tool)
 def test_missing_fitting(self):
  d=copy.deepcopy(self.index);d['groups']['stores_fittings']['objects'].pop()
  with self.assertRaises(RuntimeError):s.validate_scope(self.catalog,d,self.tool)
 def test_wrong_old_mapping(self):
  d=copy.deepcopy(self.index);d['groups']['receiving_shell']['objects'][0]['name']='unreviewed'
  with self.assertRaises(RuntimeError):s.validate_scope(self.catalog,d,self.tool)
 def test_changed_camera(self):
  d=copy.deepcopy(self.catalog);d['views'][next(iter(d['views']))]['label']='changed'
  with self.assertRaises(RuntimeError):s.validate_scope(d,self.index,self.tool)
 def test_exact_interleaving(self):
  seq=list(self.index['groups'])*3+['near_tree_high','stores_fittings'];self.assertEqual(len(seq),20);self.assertEqual(seq.count('near_tree_high'),4);self.assertEqual(seq.count('stores_fittings'),4);self.assertEqual(set(seq),set(s.EXPECTED));self.assertEqual(sum(len(x)for x in s.EXPECTED.values()),51)
if __name__=='__main__':unittest.main()
