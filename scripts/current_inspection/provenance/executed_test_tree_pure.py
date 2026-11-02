import unittest,types,json,ast,hashlib,itertools
from pathlib import Path
P=Path(__file__).parent
class Tests(unittest.TestCase):
 def setUp(self):
  self.q=types.ModuleType('q');self.q.json=json;exec((P/'tree_quality_template.py').read_text(),self.q.__dict__)
 def test_all_flags(self):
  for bits in itertools.product([False,True],repeat=6):
   d={'mask_viewport':bits[0],'mask_render':bits[1],'objects':[list(bits[2:4]),list(bits[4:6])]}
   if d in [self.q.expected_flags('HIGH'),self.q.expected_flags('LOW')]:self.assertIn(self.q.classify_flags(d),('HIGH','LOW'))
   else:
    with self.assertRaises(RuntimeError):self.q.classify_flags(d)
 def test_unknown(self):
  with self.assertRaises(RuntimeError):self.q.expected_flags('MEDIUM')
 def test_visible_paths(self):
  def node(name,objects=(),children=()):return types.SimpleNamespace(exclude=False,hide_viewport=False,collection=types.SimpleNamespace(objects=objects,hide_render=False,hide_viewport=False),children=children)
  leaf=node('leaf',('target',));root=node('root',children=[leaf]);self.assertTrue(self.q.visible_collection_paths(root,'target'))
  for obj,attr in [(leaf,'exclude'),(root,'hide_viewport'),(root.collection,'hide_render'),(leaf.collection,'hide_viewport')]:
   setattr(obj,attr,True)
   with self.assertRaises(RuntimeError):self.q.visible_collection_paths(root,'target')
   setattr(obj,attr,False)
  root.children.append(node('other',('target',)))
  with self.assertRaises(RuntimeError):self.q.visible_collection_paths(root,'target')
 def test_toggle_idempotence_and_rollback(self):
  q=self.q;q.CONFIG={'marker':'owned'};scene={'owned':json.dumps({'tree_quality':{'mode':'HIGH'},'keep':'unchanged'})};mod=types.SimpleNamespace(show_viewport=True,show_render=True);objs=[types.SimpleNamespace(hide_viewport=False,hide_render=False)for _ in range(2)];calls=[0];fail=[False]
  def find(scene):
   calls[0]+=1
   if fail[0] and calls[0]%2==0:raise RuntimeError('injected postmutation failure')
   tag=json.loads(scene['owned'])['tree_quality'];return None,mod,objs,tag,tag['mode']
  q.tree_find=find
  self.assertFalse(q.tree_set_mode(scene,'HIGH')['changed']);self.assertTrue(q.tree_set_mode(scene,'LOW')['changed']);self.assertFalse(mod.show_render);self.assertTrue(all(o.hide_render for o in objs));q.tree_set_mode(scene,'HIGH');before=scene.copy();calls[0]=0;fail[0]=True
  with self.assertRaisesRegex(RuntimeError,'injected'):q.tree_set_mode(scene,'LOW')
  self.assertEqual(scene,before);self.assertTrue(mod.show_viewport and mod.show_render);self.assertTrue(all(not o.hide_render and not o.hide_viewport for o in objs))
 def test_catalog_exact(self):
  # Tool staging parent lives in work; use repository root independent of cwd.
  original=P.parents[2]/'scripts/current_inspection/catalog.json'
  self.assertEqual((P/'catalog.json').read_bytes(),original.read_bytes())
 def test_no_auto_save_render_helper(self):
  s=(P/'tree_quality_template.py').read_text();self.assertNotIn('save_as_mainfile',s);self.assertNotIn('bpy.ops.render',s);self.assertNotIn('register()',s)
 def test_unregister_after_scene_guard_failure_and_reexecution(self):
  tree=ast.parse((P/'ui_template.py').read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('register','unregister')]
  cls1=type('OwnedOperator',(),{});cls2=type('OwnedPanel',(),{});registered=types.SimpleNamespace(OwnedOperator=cls1,OwnedPanel=cls2);removed=[]
  fakebpy=types.SimpleNamespace(types=registered,utils=types.SimpleNamespace(unregister_class=lambda c:removed.append(c)))
  registry=types.SimpleNamespace(owner='own',catalog_sha256='cat',ui_text_sha256='text',runtime_identity='runtime',classes=(cls1,cls2));modules={'reg':registry}
  def need(ok,msg):
   if not ok:raise RuntimeError(msg)
  namespace={'CONFIG':{'catalog_sha256':'cat','runtime_identity':'runtime','tree_quality_enabled':False},'OWNER':'own','REGISTRY':'reg','sys':types.SimpleNamespace(modules=modules),'bpy':fakebpy,'need':need,'CASTLE27_INSPECTION_OT_bookmark':cls1,'CASTLE27_PT_bookmarks':cls2,'verify':lambda:{'ui_text_sha256':'text'}}
  code=compile(ast.Module(body=nodes,type_ignores=[]),'isolated-registry','exec');exec(code,namespace)
  self.assertFalse(namespace['register']());exec(code,namespace);self.assertFalse(namespace['register']())
  def broken():raise RuntimeError('ordinary scene edited/hidden')
  namespace['verify']=broken
  with self.assertRaises(RuntimeError):namespace['register']()
  registry.runtime_identity='foreign'
  with self.assertRaises(RuntimeError):namespace['unregister']()
  self.assertEqual(removed,[]);registry.runtime_identity='runtime';self.assertTrue(namespace['unregister']());self.assertEqual(removed,[cls2,cls1]);self.assertFalse(namespace['unregister']())
 def test_stale_off_on_runtime_rejected_without_registry(self):
  tree=ast.parse((P/'ui_template.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='verify')
  def need(ok,msg):
   if not ok:raise RuntimeError(msg)
  for executing,stored in [(False,True),(True,False)]:
   config={'marker':'m','catalog_sha256':'cat','source_sha256':'src','runtime_identity':str(executing),'tree_quality_enabled':executing}
   marker={'owner':'own','catalog_sha256':'cat','source_sha256':'src','runtime_identity':str(stored),'tree_quality_enabled':stored}
   ns={'CONFIG':config,'OWNER':'own','need':need,'json':json,'sys':types.SimpleNamespace(flags=types.SimpleNamespace(optimize=0)),'bpy':types.SimpleNamespace(context=types.SimpleNamespace(scene={'m':json.dumps(marker)}))}
   exec(compile(ast.Module(body=[fn],type_ignores=[]),'verify-stale','exec'),ns)
   with self.assertRaisesRegex(RuntimeError,'Executing runtime'):ns['verify']()
 def test_composed_code(self):
  t=(P/'ui_template.py').read_text();c=json.loads((P/'catalog.json').read_text())
  for enabled in [False,True]:
   config={'tree_quality_enabled':enabled};code=t.replace('CONFIG = None  # Exporter replaces this assignment with literal reviewed config.','CONFIG = '+repr(config)).replace('# TREE_HELPER_LITERAL',(P/'tree_quality_template.py').read_text()if enabled else '');ast.parse(code);self.assertEqual('def tree_find' in code,enabled)
if __name__=='__main__':unittest.main()
