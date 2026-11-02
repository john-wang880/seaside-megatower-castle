import importlib.util,tempfile,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'scripts/update_root_checksums.py';s=importlib.util.spec_from_file_location('inventory',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class RootInventoryTests(unittest.TestCase):
 def test_unicode_spaces_preserved(self):
  with tempfile.TemporaryDirectory()as d:
   r=Path(d);(r/'新版').mkdir();(r/'新版/report.json').write_bytes(b'data');(r/'a b.txt').write_bytes(b'x');text=m.manifest_for_paths(r,['新版/report.json','a b.txt']);self.assertEqual(len(text.splitlines()),2);self.assertIn('  新版/report.json\n',text);self.assertIn('  a b.txt\n',text)
 def test_root_self_and_deleted_omitted(self):
  with tempfile.TemporaryDirectory()as d:
   r=Path(d);(r/'SHA256SUMS.txt').write_text('old');self.assertEqual(m.manifest_for_paths(r,['SHA256SUMS.txt','deleted']), '')
 def test_duplicates_once(self):
  with tempfile.TemporaryDirectory()as d:
   r=Path(d);(r/'a').write_bytes(b'x');self.assertEqual(len(m.manifest_for_paths(r,['a','a']).splitlines()),1)
 def test_escape_and_ambiguous_paths_refused(self):
  with tempfile.TemporaryDirectory()as d:
   for n in ['../outside','/absolute','line\nbreak','bad\\name']:
    with self.assertRaises(ValueError):m.manifest_for_paths(Path(d),[n])
if __name__=='__main__':unittest.main()
