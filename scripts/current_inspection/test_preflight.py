import ast,importlib.util,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import preflight as p
class Guards(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'项目 with spaces';self.root.mkdir();self.repo=self.root/'repo';self.repo.mkdir();self.cp=self.repo/'checkpoints/v028';self.cp.mkdir(parents=True);self.manifest={'format':'blend-zstd-frames-v1','model':'castle_v028.blend','model_sha256':p.SOURCE_SHA,'model_bytes':p.SOURCE_BYTES};self.mp=self.cp/'MANIFEST.json';self.mp.write_text(json.dumps(self.manifest));self.source=self.root/'source.blend';self.source.write_bytes(b'test');self.out=self.root/'检查 copy.blend';self.report=self.root/'检查 report.json';self.catalog=Path(__file__).with_name('catalog.json')
 def tearDown(self):self.tmp.cleanup()
 def test_import_without_bpy(self):
  cmd=[sys.executable,'-c',"import sys;sys.path.insert(0,"+repr(str(Path(__file__).parent))+ ");import export_inspection;assert 'bpy' not in sys.modules"]
  self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
 def test_operator_class_matches_rna_identifier(self):
  tree=ast.parse(Path(__file__).with_name('ui_template.py').read_text())
  cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and '_OT_' in n.name)
  assignment=next(n for n in cls.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='bl_idname' for t in n.targets))
  namespace,operator=ast.literal_eval(assignment.value).split('.')
  self.assertEqual(cls.name,namespace.upper()+'_OT_'+operator)
 def test_known_catalog(self):
  c=p.load_catalog(self.catalog);self.assertEqual(len(c['views']),18);root=self.catalog.parent
  for key in ['rear_landward','west_lateral','east_lateral','ceiling_inspection']:
   v=c['views'][key];pr=v['provenance'];recipe=json.loads((root/pr['recipe']).read_text());receipt=json.loads((root/pr['receipt']).read_text())
   self.assertEqual(p.sha(root/pr['recipe']),pr['recipe_sha256']);self.assertEqual(p.sha(root/pr['receipt']),pr['receipt_sha256']);self.assertEqual(receipt['manifest_sha256'],pr['recipe_sha256'])
   self.assertEqual(receipt['source_sha256_before'],pr['render_source_sha256']);self.assertEqual(receipt['source_sha256_after'],pr['render_source_sha256'])
   self.assertEqual(v['matrix'],recipe['views'][key]['reference_matrix']);self.assertEqual(v['reference_resolution'],recipe['resolution']);data=dict(recipe['views'][key]['camera_data']);data.setdefault('type','PERSP');self.assertEqual(v['data'],data)
  self.assertEqual(c['views']['ceiling_inspection']['provenance']['render_source_sha256'],'37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255')
  for key in ['receiving_doorway','receiving_reverse_connection']:
   v=c['views'][key];pr=v['provenance'];r=json.loads((root/pr['receipt']).read_text())
   self.assertEqual(pr['render_source_sha256'],p.SOURCE_SHA);self.assertEqual(p.sha(root/pr['recipe']),pr['recipe_sha256']);self.assertEqual(p.sha(root/pr['receipt']),pr['receipt_sha256']);self.assertEqual(r['manifest_sha256'],pr['recipe_sha256']);self.assertEqual(v['matrix'],r['settings']['camera']['matrix_world']);data=dict(r['settings']['camera']['data']);data['type']='PERSP';self.assertEqual(v['data'],data)
  checker=(root/'qa/validate_modes.py').read_text();self.assertIn("len(catalog['views'])==18",checker)
  exporter=(root/'export_inspection.py').read_text();self.assertIn("'added_cameras':17,'bookmark_count':18",exporter)

 def test_corrupt_catalog(self):
  f=self.root/'bad.json';f.write_text(self.catalog.read_text()+' ')
  with self.assertRaises(p.GuardError):p.load_catalog(f)
 def test_future_no_fallback(self):
  d=self.repo/'checkpoints/v029';d.mkdir();(d/'MANIFEST.json').write_text('{}')
  with self.assertRaises(p.GuardError):p.latest_manifest(self.repo)
 def test_numeric_not_lexicographic(self):
  d=self.repo/'checkpoints/v9';d.mkdir();(d/'MANIFEST.json').write_text('{}');self.assertEqual(p.latest_manifest(self.repo)[1],self.mp)
 def test_corrupt_latest(self):
  self.mp.write_text('{')
  with self.assertRaises(json.JSONDecodeError):p.latest_manifest(self.repo)
 def test_wrong_binding(self):
  self.manifest['model_bytes']+=1;self.mp.write_text(json.dumps(self.manifest))
  with self.assertRaises(p.GuardError):p.latest_manifest(self.repo)
 def test_wrong_source_bytes(self):
  with self.assertRaisesRegex(p.GuardError,'byte count'):p.preflight(self.repo,self.source,self.out,self.report,self.catalog)
 def test_wrong_source_hash(self):
  with self.source.open('wb') as f:f.truncate(p.SOURCE_BYTES)
  with self.assertRaisesRegex(p.GuardError,'Source SHA'):p.preflight(self.repo,self.source,self.out,self.report,self.catalog)
 def test_success_unicode(self):
  with self.source.open('wb') as f:f.truncate(p.SOURCE_BYTES)
  real=p.sha
  with patch.object(p,'sha',side_effect=lambda x:p.SOURCE_SHA if Path(x)==self.source else real(x)):
   identity,c=p.preflight(self.repo,self.source,self.out,self.report,self.catalog)
  self.assertEqual(identity['output'],str(self.out));self.assertFalse(self.out.exists())
 def test_existing(self):
  self.out.write_text('keep')
  with self.assertRaises(p.GuardError):p.new_destination(self.out,'.blend')
  self.assertEqual(self.out.read_text(),'keep')
 @unittest.skipIf(os.name=='nt','Symlink permissions vary; nativeWindows not tested')
 def test_dangling_symlink(self):
  self.out.symlink_to(self.root/'missing')
  with self.assertRaises(p.GuardError):p.new_destination(self.out,'.blend')
 def test_parent_alias(self):
  with self.assertRaises(p.GuardError):p.unaliased(self.root/'x/../alias')
 def test_publish_success_and_nooverwrite(self):
  a=self.root/'a.tmp';b=self.root/'b.tmp';a.write_bytes(b'model');b.write_bytes(b'report');p.publish_pair(a,self.out,b,self.report)
  self.assertEqual(self.out.read_bytes(),b'model')
  with self.assertRaises(p.GuardError):p.publish_pair(a,self.out,b,self.report)
 def test_publish_second_failure_rolls_back_only_ours(self):
  a=self.root/'a.tmp';b=self.root/'b.tmp';a.write_bytes(b'model');b.write_bytes(b'report');real=os.link;calls=[]
  def link(src,dst):
   calls.append(dst)
   if len(calls)==2:raise OSError('unsupported')
   real(src,dst)
  with patch.object(p.os,'link',side_effect=link):
   with self.assertRaises(OSError):p.publish_pair(a,self.out,b,self.report)
  self.assertFalse(self.out.exists());self.assertFalse(self.report.exists());self.assertTrue(self.source.exists())
 def test_foreign_swap_immediately_after_link_survives(self):
  a=self.root/'a.tmp';b=self.root/'b.tmp';a.write_bytes(b'model');b.write_bytes(b'report');real=os.link;calls=[]
  def link(src,dst):
   calls.append(dst)
   if len(calls)==2:raise OSError('second publish fails')
   real(src,dst);os.unlink(dst);Path(dst).write_bytes(b'foreign replacement')
  with patch.object(p.os,'link',side_effect=link):
   with self.assertRaises(OSError):p.publish_pair(a,self.out,b,self.report)
  self.assertEqual(self.out.read_bytes(),b'foreign replacement')
 def test_o_refused(self):
  code="import sys;sys.path.insert(0,"+repr(str(Path(__file__).parent))+");from preflight import preflight;preflight('x','y','z','a','b')"
  r=subprocess.run([sys.executable,'-O','-c',code],capture_output=True,text=True);self.assertNotEqual(r.returncode,0);self.assertIn('Optimized Python',r.stderr)
if __name__=='__main__':unittest.main()
