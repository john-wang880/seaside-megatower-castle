"""Run with standard Python; no bpy dependency."""
import copy, json, pathlib, tempfile, unittest
import navigation as nav
class NavigationTests(unittest.TestCase):
 def test_manifest_has_eight_explicit_views(self):
  m=nav.load_manifest();self.assertEqual(set(m['views']),{'hero','west_approach','east_portal','bend','upper_stairs','terminal','offshore_marker','crown'});self.assertEqual(sum('camera_name' in v for v in m['views'].values()),7)
 def test_same_path_and_existing_and_bad_extension(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);source=p/'source.blend';source.write_bytes(b'original');existing=p/'viewer.blend';existing.write_bytes(b'keep')
   with self.assertRaises(ValueError):nav.check_output(source,source)
   with self.assertRaises(FileExistsError):nav.check_output(source,existing)
   with self.assertRaises(ValueError):nav.check_output(source,p/'bad.txt')
   self.assertEqual(source.read_bytes(),b'original');self.assertEqual(existing.read_bytes(),b'keep');self.assertEqual(nav.check_output(source,p/'new.blend'),p/'new.blend')
 def test_dangling_symlink_collision(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);source=p/'source.blend';source.write_bytes(b'original');link=p/'link.blend'
   try:link.symlink_to(p/'absent.blend')
   except OSError:self.skipTest('Symlinks unavailable')
   with self.assertRaises(FileExistsError):nav.check_output(source,link)
 def test_invalid_manifest(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'views.json';m=nav.load_manifest();m['views']['bend']['target']=m['views']['bend']['location'];p.write_text(json.dumps(m))
   with self.assertRaises(ValueError):nav.load_manifest(p)
 def test_nonfinite_camera_values_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'views.json'
   for field in ('lens','clip_start','clip_end'):
    for value in (float('nan'),float('inf')):
     m=nav.load_manifest();m['views']['bend'][field]=value;p.write_text(json.dumps(m))
     with self.assertRaises(ValueError):nav.load_manifest(p)
if __name__=='__main__':unittest.main()
