"""Pure contract tests, not native Blender acceptance."""
import unittest,types,json,hashlib,pathlib,ast,sys
ROOT=pathlib.Path(__file__).resolve().parent
class Obj:
 def __init__(self,name,selected=False):self.name=name;self.selected=selected
 def select_get(self,view_layer=None):return self.selected
 def select_set(self,v,view_layer=None):self.selected=v
class Objects(list):pass
class Tests(unittest.TestCase):
 def setUp(self):
  self.ns={'hashlib':hashlib,'json':json,'need':lambda ok,msg:None if ok else (_ for _ in ()).throw(RuntimeError(msg))}
  exec((ROOT/'edit_index_template.py').read_text().split('class CASTLE29_INSPECTION_OT_edit_index')[0],self.ns)
  self.a=Obj('a',True);self.b=Obj('b');self.c=Obj('c');self.objects=Objects([self.a,self.b,self.c]);self.objects.active=self.a
  self.ctx=types.SimpleNamespace(view_layer=types.SimpleNamespace(objects=self.objects));self.ns['index_find']=lambda key,context:[self.b,self.c]
 def test_success(self):
  r=self.ns['select_index']('x',self.ctx);self.assertEqual(r['selected'],['b','c']);self.assertFalse(self.a.selected);self.assertIs(self.objects.active,self.b)
 def test_repeat(self):
  for _ in range(3):self.ns['select_index']('x',self.ctx)
  self.assertEqual(len(self.objects),3);self.assertEqual([x.selected for x in self.objects],[False,True,True])
 def test_preflight_failure(self):
  self.ns['index_find']=lambda *a:(_ for _ in ()).throw(RuntimeError('hidden'))
  with self.assertRaises(RuntimeError):self.ns['select_index']('x',self.ctx)
  self.assertEqual([x.selected for x in self.objects],[True,False,False]);self.assertIs(self.objects.active,self.a)
 def test_partial_set_failure(self):
  def fail(o,value,layer):
   if o is self.c:raise RuntimeError('injected')
   o.select_set(value)
  self.ns['_index_select_set']=fail
  with self.assertRaises(RuntimeError):self.ns['select_index']('x',self.ctx)
  self.assertEqual([x.selected for x in self.objects],[True,False,False]);self.assertIs(self.objects.active,self.a)
 def test_postflight_failure(self):
  calls=[]
  def find(*a):
   calls.append(1)
   if len(calls)>1:raise RuntimeError('postflight')
   return [self.b,self.c]
  self.ns['index_find']=find
  with self.assertRaises(RuntimeError):self.ns['select_index']('x',self.ctx)
  self.assertEqual([x.selected for x in self.objects],[True,False,False]);self.assertIs(self.objects.active,self.a)
 def node(self,objects=(),children=(),hidden=False):
  return types.SimpleNamespace(collection=types.SimpleNamespace(objects=objects,hide_viewport=hidden,hide_render=False,hide_select=False),children=children,exclude=False,hide_viewport=False)
 def test_paths(self):self.assertTrue(self.ns['index_paths'](self.node(children=[self.node(['a'])]),'a'))
 def test_hidden_path(self):
  with self.assertRaises(RuntimeError):self.ns['index_paths'](self.node(children=[self.node(['a'])],hidden=True),'a')
 def test_multiple_path(self):
  with self.assertRaises(RuntimeError):self.ns['index_paths'](self.node(children=[self.node(['a']),self.node(['a'])]),'a')
 def test_mapping(self):
  x=json.loads((ROOT/'edit_index.json').read_text());self.assertEqual([len(g['objects']) for g in x['groups'].values()],[2,20,1,2,20]);self.assertFalse(any('outside chamber guard' in o['name'] for g in x['groups'].values() for o in g['objects']))
 def test_no_automatic_actions(self):
  m=ast.parse((ROOT/'edit_index_template.py').read_text());self.assertTrue(all(isinstance(x,(ast.Expr,ast.FunctionDef,ast.ClassDef)) for x in m.body))
if __name__=='__main__':unittest.main()
