"""Pure direct panel draw contract; does not stand in for native QA."""
import ast,pathlib,types,unittest
class Layout:
 def __init__(self):self.labels=[];self.buttons=[]
 def label(self,**kw):self.labels.append(kw)
 def operator(self,*a,**kw):x=types.SimpleNamespace();self.buttons.append((a,kw,x));return x
class Tests(unittest.TestCase):
 def setUp(self):
  tree=ast.parse((pathlib.Path(__file__).parent/'edit_index_template.py').read_text());cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='CASTLE29_PT_edit_index');fn=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='draw');self.config={'edit_index_enabled':True,'edit_index':{'groups':{str(i):{'label':str(i)} for i in range(4)}}};self.ns={'CONFIG':self.config,'verify':lambda:{'edit_index_enabled':True},'need':lambda ok,msg:None if ok else (_ for _ in ()).throw(RuntimeError(msg)),'CASTLE29_INSPECTION_OT_edit_index':types.SimpleNamespace(bl_idname='test.index')};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<draw>','exec'),self.ns);self.obj=types.SimpleNamespace(layout=Layout());self.ctx=types.SimpleNamespace()
 def test_valid_four(self):
  self.ns['draw'](self.obj,self.ctx);self.assertEqual(len(self.obj.layout.buttons),4);self.assertFalse(any(x.get('icon')=='ERROR' for x in self.obj.layout.labels))
 def test_foreign_unmarked(self):
  self.ns['verify']=lambda:(_ for _ in ()).throw(RuntimeError('unowned'));self.ns['draw'](self.obj,self.ctx);self.assertEqual(self.obj.layout.buttons,[]);self.assertEqual(self.obj.layout.labels,[{'text':'unowned','icon':'ERROR'}]);self.assertEqual(vars(self.ctx),{})
 def test_stale_optin(self):
  self.ns['verify']=lambda:{'edit_index_enabled':False};self.ns['draw'](self.obj,self.ctx);self.assertEqual(self.obj.layout.buttons,[]);self.assertEqual(self.obj.layout.labels[0]['icon'],'ERROR');self.assertEqual(vars(self.ctx),{})
 def test_disabled_config(self):
  self.config['edit_index_enabled']=False;self.ns['draw'](self.obj,self.ctx);self.assertEqual(self.obj.layout.buttons,[]);self.assertEqual(self.obj.layout.labels[0]['icon'],'ERROR')
if __name__=='__main__':unittest.main()
