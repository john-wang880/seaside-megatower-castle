import unittest,copy
import compare_support as c
class Tests(unittest.TestCase):
 def test_runner_parent_traversal(self):
  import run_qa
  with self.assertRaises(RuntimeError):run_qa.clean_path('/outside/../qa/new')
 def mesh(self):
  p={'weights':[(i,[(0,1.0)]) for i in c.SELECTED],'attributes':[{'name':'strict'}],'topology':{'x':1}}
  return {'hash':c.digest(p),'debug_payload':p,'vertices':204154}
 def test_exact(self):
  m=self.mesh();out,record=c.normalize_owned_weights(m);self.assertEqual(record['count'],298);self.assertEqual(out['debug_payload']['weights'],[]);self.assertEqual(len(m['debug_payload']['weights']),298)
 def test_wrong_weight(self):
  m=self.mesh();m['debug_payload']['weights'][0]=(90395,[(0,.5)])
  with self.assertRaises(RuntimeError):c.normalize_owned_weights(m)
 def test_extra_weight(self):
  m=self.mesh();m['debug_payload']['weights'].append((0,[(0,1.)]))
  with self.assertRaises(RuntimeError):c.normalize_owned_weights(m)
 def test_wrong_group(self):
  with self.assertRaises(RuntimeError):c.normalize_owned_weights(self.mesh(),1)
 def test_missing_weight(self):
  m=self.mesh();m['debug_payload']['weights'].pop()
  with self.assertRaises(RuntimeError):c.normalize_owned_weights(m)
 def test_empty_explicit_only(self):
  m=self.mesh();m['debug_payload']['weights']=[]
  with self.assertRaises(RuntimeError):c.normalize_owned_weights(m)
  self.assertEqual(c.normalize_owned_weights(m,allow_empty=True)[1]['count'],0)
 def test_unknown_attribute_retained(self):
  m=self.mesh();out,_=c.normalize_owned_weights(m);self.assertEqual(out['debug_payload']['attributes'],m['debug_payload']['attributes'])
if __name__=='__main__':unittest.main()
