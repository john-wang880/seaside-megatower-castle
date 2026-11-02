import json,hashlib,unittest,types
from pathlib import Path
P=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 def test_new_actual_cameras(self):
  c=json.loads((P/'catalog.json').read_text())
  for k in ['stores_entry','stores_return']:
   v=c['views'][k];pr=v['provenance'];r=json.loads((P/pr['receipt']).read_text());plan=json.loads((P/pr['recipe']).read_text())
   self.assertEqual(v['matrix'],r['settings']['camera']['matrix_world']);self.assertEqual(v['data'],r['settings']['camera']['data']);self.assertEqual(v['reference_resolution'],plan['resolution']);self.assertEqual(r['source_sha256_before'],c['source_sha256']);self.assertEqual(r['source_sha256_after'],c['source_sha256'])
   for f in ['recipe','receipt']:self.assertEqual(hashlib.sha256((P/pr[f]).read_bytes()).hexdigest(),pr[f+'_sha256'])
 def test_five_scoped_groups(self):
  x=json.loads((P/'edit_index.json').read_text());g=x['groups'];self.assertEqual(len(g),5)
  self.assertEqual({o['name']for o in g['receiving_shell']['objects']},{'V029 | receiving shell outside stores guard','V029 | local stores shell'})
  for key,prefix in [('room_lantern_meshes','V028 | room '),('stores_lantern_meshes','V029 | stores ')]:
   self.assertEqual(len(g[key]['objects']),20);self.assertTrue(all(o['name'].startswith(prefix)for o in g[key]['objects']));self.assertTrue(all('point light'not in o['name'].lower()for o in g[key]['objects']))
 def test_index_source_pinned(self):
  self.assertEqual(json.loads((P/'catalog.json').read_text())['source_sha256'],json.loads((P/'edit_index.json').read_text())['source_sha256'])
 def test_mixed_hidden_preflight_no_selection_mutation(self):
  ns={'hashlib':hashlib,'json':json,'need':lambda ok,msg:None if ok else (_ for _ in ()).throw(RuntimeError(msg))};exec((P/'edit_index_template.py').read_text().split('class CASTLE29_INSPECTION_OT_edit_index')[0],ns)
  mutations=[];ns['index_find']=lambda *args:(_ for _ in ()).throw(RuntimeError('second target hidden'));ns['_index_select_set']=lambda *args:mutations.append(args)
  with self.assertRaisesRegex(RuntimeError,'hidden'):ns['select_index']('receiving_shell',types.SimpleNamespace())
  self.assertEqual(mutations,[])
if __name__=='__main__':unittest.main()
