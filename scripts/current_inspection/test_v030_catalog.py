import json,hashlib,unittest,ast
from pathlib import Path
P=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 def test_twenty_unchanged_camera_records(self):
  old=json.loads((P/'provenance/v029_upgrade_baseline/catalog.json').read_text());new=json.loads((P/'catalog.json').read_text());self.assertEqual(new['views'],old['views']);self.assertEqual(len(new['views']),20)
 def test_five_old_groups_exact(self):
  old=json.loads((P/'provenance/v029_upgrade_baseline/edit_index.json').read_text());new=json.loads((P/'edit_index.json').read_text());self.assertEqual(len(new['groups']),6);self.assertEqual(sum(len(g['objects'])for g in new['groups'].values()),51)
  for k,v in old['groups'].items():self.assertEqual(new['groups'][k],v)
 def test_six_fittings(self):
  g=json.loads((P/'edit_index.json').read_text())['groups']['stores_fittings'];self.assertEqual(len(g['objects']),6);self.assertIn('source architecture unchanged',g['notice']);self.assertTrue(all(o['name'].startswith('V030 | ')for o in g['objects']));self.assertEqual(sum(o['vertices']for o in g['objects']),1248)
 def test_index_source_pin(self):
  c=json.loads((P/'catalog.json').read_text());x=json.loads((P/'edit_index.json').read_text());self.assertEqual(c['source_sha256'],x['source_sha256']);self.assertEqual(c['reviewed_version'],30)
 def test_historical_stores_receipt(self):
  c=json.loads((P/'catalog.json').read_text())
  for k in ['stores_entry','stores_return']:
   v=c['views'][k];pr=v['provenance'];r=json.loads((P/pr['receipt']).read_text());self.assertEqual(r['source_sha256_before'],'4f838529d32cbf6a0314cc0a23b3dd1703b73d80c5db146fb4d323697b882df5');self.assertEqual(v['matrix'],r['settings']['camera']['matrix_world'])
 def test_selection_guards_retained(self):
  s=(P/'edit_index_template.py').read_text();self.assertIn("bpy.context.mode=='OBJECT'",s);self.assertIn('Index geometry/transform changed',s);self.assertIn('HIGH tree unavailable in LOW',s);self.assertIn('Index mapping changed',s)
if __name__=='__main__':unittest.main()
