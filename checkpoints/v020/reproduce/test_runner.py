"""Pure mocked recipe guards. No Blender runs or model mutation."""
import unittest,tempfile,json,subprocess,sys
from pathlib import Path
from unittest.mock import patch
import rebuild
class Recipe(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(prefix='threshold space 中文 ');base=Path(self.t.name);self.root=base/'bundle';self.root.mkdir();(self.root/'scripts').mkdir();(self.root/'plans').mkdir()
  for n in ['build.py','union_springers.py','clip_coping_embed.py']:(self.root/'scripts'/n).write_text('#mock')
  (self.root/'plans/host_plan_forward.json').write_text('{}');self.source=base/'source 中文.blend';self.source.write_bytes(b'source');self.blender=base/'blender executable';self.blender.write_bytes(b'mock');self.blender.chmod(0o700);self.out=base/'new result 中文';self.calls=[];self.failure=None
 def tearDown(self):self.t.cleanup()
 def process(self,argv,**kwargs):
  if argv==[str(self.blender),'--version']:return subprocess.CompletedProcess(argv,0,'Blender 5.2.3 LTS\n','')
  expected={'build.py':{'--source','--plan','--output','--report'},'union_springers.py':{'--input','--input-sha256','--build-report','--output','--report'},'clip_coping_embed.py':{'--input','--input-sha256','--union-report','--output','--report'}}
  self.assertNotIn('shell',kwargs);self.assertEqual(argv[0],str(self.blender));self.assertIn('--disable-autoexec',argv);self.assertEqual(argv[argv.index('--python-exit-code')+1],'1');name=Path(argv[argv.index('--python')+1]).name;args=argv[argv.index('--')+1:];self.assertEqual(len(args)%2,0);flags=args[::2];self.assertEqual(len(flags),len(set(flags)));opts=dict(zip(flags,args[1::2]));self.assertEqual(set(opts),expected[name]);self.calls.append(name)
  if '--input' in opts:self.assertEqual(rebuild.sha(opts['--input']),opts['--input-sha256'])
  if self.failure=='rc':return subprocess.CompletedProcess(argv,9)
  if self.failure=='missing':return subprocess.CompletedProcess(argv,0)
  model=Path(opts['--output']);model.write_bytes(name.encode());r={'candidate_sha256':rebuild.sha(model)}
  if name=='build.py':r.update(source_unchanged=True,source_sha256=rebuild.SOURCE,total_components=23,checks={n:True for n in rebuild.FORWARD_CHECKS})
  elif name=='union_springers.py':r.update(input_unchanged=True,component_count=21,all_other_meshes_exact=True,all_material_graphs_exact=True)
  else:r.update(input_unchanged=True,component_count=23,other_meshes_and_material_graphs_exact=True)
  if self.failure=='empty_checks':r['checks']={}
  if self.failure=='false_check':r['checks']['all_source_meshes_exact']=False
  if self.failure=='bad_model_hash':r['candidate_sha256']='0'*64
  if self.failure=='source_mutation':self.source.write_bytes(b'mutated')
  if self.failure=='code_mutation':(self.root/'scripts/build.py').write_text('# changed')
  Path(opts['--report']).write_text('{bad json' if self.failure=='malformed_json' else json.dumps(r));return subprocess.CompletedProcess(argv,0)
 def invoke(self,pin=None):
  argv=['rebuild.py','--source',str(self.source),'--blender',str(self.blender),'--output-dir',str(self.out)]
  with patch.object(rebuild,'__file__',str(self.root/'rebuild.py')),patch.object(rebuild,'SOURCE',pin or rebuild.sha(self.source)),patch.object(sys,'argv',argv),patch('rebuild.subprocess.run',side_effect=self.process):rebuild.main()
 def test_three_stage_exact_flags_and_runtime_hash_chain(self):
  self.invoke();self.assertEqual(self.calls,['build.py','union_springers.py','clip_coping_embed.py']);r=json.loads((self.out/'receipt.json').read_text());self.assertEqual(r['status'],'RECIPE_COMPLETED_INDEPENDENT_SEMANTIC_QA_REQUIRED');self.assertTrue(r['source_unchanged'])
 def test_wrong_pin(self):
  with self.assertRaisesRegex(RuntimeError,'exact v019'):self.invoke('0'*64)
  self.assertFalse(self.out.exists());self.assertFalse(self.calls)
 def test_existing_output(self):
  self.out.mkdir()
  with self.assertRaisesRegex(RuntimeError,'must be new'):self.invoke()
 def test_dangling_output_symlink(self):
  self.out.symlink_to(self.out.with_name('absent'))
  with self.assertRaisesRegex(RuntimeError,'must be new'):self.invoke()
 def test_source_alias(self):
  self.out=self.source
  with self.assertRaises(RuntimeError):self.invoke()
 def test_bundle_overlap(self):
  self.out=self.root/'new'
  with self.assertRaisesRegex(RuntimeError,'overlap'):self.invoke()
 def failure_case(self,kind):
  self.failure=kind
  with self.assertRaises((RuntimeError,json.JSONDecodeError)):self.invoke()
  self.assertEqual(len(self.calls),1);self.assertEqual(json.loads((self.out/'receipt.json').read_text())['status'],'FAILED')
 def test_nonzero_stops(self):self.failure_case('rc')
 def test_missing_receipt_stops(self):self.failure_case('missing')
 def test_empty_checks_rejected(self):self.failure_case('empty_checks')
 def test_false_check_rejected(self):self.failure_case('false_check')
 def test_wrong_output_hash_rejected(self):self.failure_case('bad_model_hash')
 def test_malformed_json_rejected(self):self.failure_case('malformed_json')
 def test_source_mutation_rejected(self):self.failure_case('source_mutation')
 def test_code_mutation_rejected(self):self.failure_case('code_mutation')
if __name__=='__main__':unittest.main()
