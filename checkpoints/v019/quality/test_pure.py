import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace as N
import quality_controls as q
import export_viewer as e
class Pure(unittest.TestCase):
 def test_modes(self):
  for m in ['HIGH','LOW']:self.assertEqual(q.classify_flags(q.expected_flags(m)),m)
 def test_mixed(self):
  d=q.expected_flags('HIGH');d['objects'][0][1]=True
  with self.assertRaisesRegex(RuntimeError,'Mixed'):q.classify_flags(d)
 def test_unknown(self):
  with self.assertRaisesRegex(RuntimeError,'Unknown'):q.expected_flags('MEDIUM')
 def test_collection_paths(self):
  def node(names=(),children=()):return N(collection=N(objects=set(names),hide_viewport=False,hide_render=False),children=list(children),exclude=False,hide_viewport=False)
  leaf=node(['tree']);parent=node(children=[leaf]);root=node(children=[parent])
  self.assertTrue(q.visible_collection_paths(root,'tree'))
  for obj,attr in [(root,'exclude'),(parent,'hide_viewport'),(parent.collection,'hide_viewport'),(parent.collection,'hide_render')]:
   setattr(obj,attr,True)
   with self.assertRaises(RuntimeError):q.visible_collection_paths(root,'tree')
   setattr(obj,attr,False)
  root.children.append(node(['tree']))
  with self.assertRaisesRegex(RuntimeError,'multiple'):q.visible_collection_paths(root,'tree')
  with self.assertRaises(RuntimeError):q.visible_collection_paths(root,'absent')
 def test_paths(self):
  with tempfile.TemporaryDirectory(prefix='castle 中文 ') as d:
   p=Path(d);s=p/'source.blend';s.write_bytes(b'x')
   with patch.object(e,'sha',return_value=e.SOURCE_SHA):
    self.assertEqual(e.validate_paths(s,p/'new.blend',p/'new.json')[0],s)
    with self.assertRaises(RuntimeError):e.validate_paths(s,s,p/'new.json')
    link=p/'dangling.blend';link.symlink_to(p/'absent')
    with self.assertRaises(RuntimeError):e.validate_paths(s,link,p/'new.json')
    (p/'existing.json').write_text('{}')
    with self.assertRaises(RuntimeError):e.validate_paths(s,p/'new.blend',p/'existing.json')
   with self.assertRaisesRegex(RuntimeError,'exact accepted'):e.validate_paths(s,p/'new.blend',p/'new.json')
if __name__=='__main__':unittest.main()
