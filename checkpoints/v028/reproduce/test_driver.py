import gzip,hashlib,json,os,subprocess,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
import reproduce as r
class Tests(unittest.TestCase):
 def test_version(self):
  r.check_version('Blender 5.2.3 LTS\n')
  for text in ['Blender 5.2.30','Blender 5.3.0','Blender 4.3.2']:
   with self.assertRaises(RuntimeError):r.check_version(text)
 def test_existing_output(self):
  with tempfile.TemporaryDirectory()as td:
   with self.assertRaises(RuntimeError):r.safe(td,'new')
 def test_symlink(self):
  with tempfile.TemporaryDirectory()as td:
   p=Path(td);(p/'a').write_text('x');(p/'b').symlink_to(p/'a')
   with self.assertRaises(RuntimeError):r.safe(p/'b','file')
 def test_wrong_source_before_process(self):
  with tempfile.TemporaryDirectory()as td:
   p=Path(td);(p/'a').write_text('wrong');(p/'blender').write_text('fake')
   with patch.object(r.subprocess,'run')as m:
    with self.assertRaisesRegex(RuntimeError,'Wrong baseline'):r.run(p/'a',p/'blender',p/'out')
    m.assert_not_called()
 def pipeline(self,fail=None):
  with tempfile.TemporaryDirectory(prefix='重建 driver ')as td:
   p=Path(td);root=p/'bundle';root.mkdir();src=p/'source.blend';src.write_bytes(b'baseline');exe=p/'blender';exe.write_text('fake');out=p/'new outputs';raw=b'export';geom=json.dumps({'pass':True}).encode();ph=hashlib.sha256(geom).hexdigest();source=r.sha(src)
   (root/'native.json.gz').write_bytes(gzip.compress(raw));(root/'frozen_plan').mkdir()
   for n in ['build_geometry.py','integrate.py','add_room_lanterns.py']:(root/n).write_text('unchanged mock script')
   (root/'FILES.json').write_text(json.dumps({str(x.relative_to(root)):r.sha(x)for x in root.rglob('*')if x.is_file()}));calls=[]
   def fake(argv,**kw):
    calls.append(argv);self.assertNotIn('shell',kw);self.assertEqual(kw['env']['PYTHONDONTWRITEBYTECODE'],'1')
    if '--version'in argv:return types.SimpleNamespace(returncode=0,stdout='Blender 5.2.3 LTS\n')
    if 'build_geometry.py'in ' '.join(argv):
     args=argv[argv.index('--export'):];self.assertEqual(args[::2],['--export','--plan-dir','--output']);Path(args[-1]).write_bytes(geom)
    else:
     script=Path(argv[argv.index('--python')+1]).name;args=argv[argv.index('--')+1:];a=dict(zip(args[::2],args[1::2]));output=Path(a['--output']);output.write_bytes(b'unlit'if script=='integrate.py'else b'lit')
     if script=='integrate.py':
      self.assertEqual(args[::2],['--source','--payload','--output','--report']);receipt={k:True for k in ['full_source_rollback_pass','source_raw_except_owned_weights_pass','evaluated_target_complements_pass','other_source_categories_pass','old_collections_pass']};receipt.update(source_sha256=source,payload_sha256=ph,candidate_sha256=r.sha(output),rendered=False,source_saved=False,lights_added=False)
      if fail=='gate':receipt['full_source_rollback_pass']=False
     else:
      self.assertEqual(args[::2],['--source','--build-receipt','--output','--report']);receipt=dict(canonical_source_sha256=source,architecture_receipt_sha256=r.sha(a['--build-receipt']),all_preexisting_scene_data_unchanged=True,rendered=False,lights=[{},{}],fixture_triangles=1160,combined_triangles=1878,candidate_sha256=r.sha(output))
     Path(a['--report']).write_text(json.dumps(receipt))
    return types.SimpleNamespace(returncode=7 if fail=='process'else 0)
   with patch.object(r,'SOURCE',source),patch.object(r,'EXPORT',hashlib.sha256(raw).hexdigest()),patch.object(r,'PAYLOAD',ph),patch.object(r.subprocess,'run',side_effect=fake):
    if fail:
     with self.assertRaises(RuntimeError):r.run(src,exe,out,root)
     receipt=json.loads((out/'REPRODUCTION.json').read_text());self.assertEqual(receipt['status'],'FAILED_NO_ACCEPTANCE');self.assertTrue(receipt['all_inputs_unchanged'])
    else:
     receipt=r.run(src,exe,out,root);self.assertEqual(len(calls),4);self.assertEqual(len(receipt['stages']),3);self.assertTrue(receipt['all_inputs_unchanged']);self.assertEqual(receipt['status'],'REPRODUCED_PENDING_INDEPENDENT_SEMANTIC_QA')
 def test_full_mock_pipeline(self):self.pipeline()
 def test_rc_failure(self):self.pipeline('process')
 def test_json_gate_failure(self):self.pipeline('gate')
 def test_inventory_tamper(self):
  with tempfile.TemporaryDirectory()as td:
   p=Path(td);(p/'a').write_text('x');(p/'FILES.json').write_text(json.dumps({'a':'0'*64}))
   with self.assertRaisesRegex(RuntimeError,'Bundle changed'):r.inventory(p)
 def test_optimize(self):
  z=subprocess.run([sys.executable,'-B','-O',str(Path(r.__file__)),'--help'],capture_output=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'));self.assertNotEqual(z.returncode,0);self.assertIn(b'Optimized Python unsupported',z.stderr)
if __name__=='__main__':unittest.main()
