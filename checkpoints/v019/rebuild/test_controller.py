"""Standard-library mocked guard tests. No Blender execution/model mutation."""
import unittest,tempfile,contextlib,io,json,subprocess,gzip
from pathlib import Path
from unittest.mock import patch
import rebuild
class Guards(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(prefix='v019 space 中文 ');self.root=Path(self.t.name)/'bundle';self.root.mkdir()
  for p in ['generator/generate_conifer.py','qa/validate_preservation.py','qa/validate_new_geometry.py','qa/audit_tube_folds.py','integration/integrate_conifer.py','integration/deep_snapshot.py','inputs/source_components.json','inputs/v018_route_envelope.json']:
   f=self.root/p;f.parent.mkdir(exist_ok=True,parents=True);f.write_text('{}' if p.endswith('.json') else '# dummy\n')
  (self.root/'inputs/component_contact_mapping.json.gz').write_bytes(gzip.compress(b'{"wood_components": []}',mtime=0))
  self.base=Path(self.t.name)/'baseline 中文.blend';self.base.write_bytes(b'base')
  self.accepted=Path(self.t.name)/'accepted space.blend';self.accepted.write_bytes(b'accepted')
  self.blender=Path(self.t.name)/'blender executable';self.blender.write_bytes(b'not executable real Blender');self.blender.chmod(0o700)
  self.out=Path(self.t.name)/'fresh output 中文';self.a=rebuild.parser().parse_args(['--baseline',str(self.base),'--accepted-model',str(self.accepted),'--blender',str(self.blender),'--output-dir',str(self.out)])
  real=rebuild.sha
  self.hash=patch.object(rebuild,'sha',side_effect=lambda p:rebuild.BASE if Path(p)==self.base else rebuild.ACCEPTED if Path(p)==self.accepted else real(p));self.hash.start()
 def tearDown(self):self.hash.stop();self.t.cleanup()
 def test_dry_run_no_writes_or_process(self):
  self.a.dry_run=True
  with patch('rebuild.subprocess.run') as run,contextlib.redirect_stdout(io.StringIO()):r=rebuild.run(self.a,self.root)
  run.assert_not_called();self.assertFalse(self.out.exists());self.assertEqual(len(r['steps']),6)
 def test_existing_directory_refused(self):
  self.out.mkdir()
  with self.assertRaisesRegex(RuntimeError,'new nonexistent'):rebuild.run(self.a,self.root)
 def test_output_inside_bundle_refused(self):
  self.a.output_dir=self.root/'output'
  with self.assertRaisesRegex(RuntimeError,'overlap controller'):rebuild.run(self.a,self.root)
 def test_mapping_mutation_rejected(self):
  mapping=Path(self.t.name)/'generated.json';mapping.write_text('{"wood_components": [{"wrong": true}]}')
  with self.assertRaisesRegex(RuntimeError,'mapping semantic drift'):rebuild.verify_mapping(mapping,self.root/'inputs/component_contact_mapping.json.gz')
 def test_mapping_serialization_allowed(self):
  mapping=Path(self.t.name)/'generated.json';mapping.write_text('{\n  "wood_components": []\n}')
  rebuild.verify_mapping(mapping,self.root/'inputs/component_contact_mapping.json.gz')
 def test_wrong_hash_refused(self):
  with patch.object(rebuild,'sha',return_value='0'*64),self.assertRaisesRegex(RuntimeError,'hash mismatch'):rebuild.run(self.a,self.root)
 def test_symlink_refused(self):
  self.out.symlink_to(Path(self.t.name)/'does not exist')
  with self.assertRaisesRegex(RuntimeError,'new nonexistent'):rebuild.run(self.a,self.root)
 def test_wrong_version_fail_closed(self):
  with patch('rebuild.subprocess.run',return_value=subprocess.CompletedProcess([],0,'Blender 5.2.4\n','')),self.assertRaisesRegex(RuntimeError,'5.2.3'):rebuild.run(self.a,self.root)
  self.assertEqual(json.loads((self.out/'receipt.json').read_text())['status'],'FAILED')
 def test_subprocess_argv_spaces_and_nonzero(self):
  results=[subprocess.CompletedProcess([],0,'Blender 5.2.3 LTS\n',''),subprocess.CompletedProcess([],9)]
  with patch('rebuild.subprocess.run',side_effect=results) as run,self.assertRaisesRegex(RuntimeError,'subprocess failed'):rebuild.run(self.a,self.root)
  argv=run.call_args_list[1].args[0];self.assertEqual(argv[0],str(self.blender));self.assertIn(str(self.base),argv);self.assertIn('--python-exit-code',argv);self.assertNotIn('shell',run.call_args_list[1].kwargs)
 def test_exit_zero_missing_receipt_rejected(self):
  with patch('rebuild.subprocess.run',side_effect=[subprocess.CompletedProcess([],0,'Blender 5.2.3\n',''),subprocess.CompletedProcess([],0)]),self.assertRaisesRegex(RuntimeError,'missing receipt'):rebuild.run(self.a,self.root)
 def test_full_six_stage_pipeline_exact_flags(self):
  calls=[]
  expected={
   'generate_conifer.py':{'--baseline','--output-dir'},
   'validate_preservation.py':{'--baseline','--checkpoint','--asset','--asset-sha256','--accepted-model','--source-components','--report'},
   'integrate_conifer.py':{'--source','--asset','--asset-sha256','--output','--report','--snapshot-helper'},
   'validate_new_geometry.py':{'--candidate','--mapping','--route-report','--report'},
   'audit_tube_folds.py':{'--candidate','--mapping','--route-report','--report'}}
  def process(argv,**kwargs):
   if argv==[str(self.blender),'--version']:return subprocess.CompletedProcess(argv,0,'Blender 5.2.3 LTS\n','')
   self.assertIsInstance(argv,list);self.assertNotIn('shell',kwargs)
   self.assertEqual(argv[1:10],['--background','--factory-startup','--disable-autoexec','--python-exit-code','1','--threads','8','--python',str(Path(argv[9]))])
   name=Path(argv[argv.index('--python')+1]).name;args=argv[argv.index('--')+1:]
   self.assertEqual(len(args)%2,0,'Stray positional argument')
   flags=args[::2];self.assertEqual(len(flags),len(set(flags)));self.assertEqual(set(flags),expected[name]);opts=dict(zip(flags,args[1::2]));calls.append(name)
   self.assertTrue(all(not v.startswith('--') for v in opts.values()))
   if name=='generate_conifer.py':
    d=Path(opts['--output-dir']);d.mkdir();(d/'generated_conifer.blend').write_bytes(b'generated')
    (d/'component_contact_mapping.json').write_text('{"wood_components": []}')
    (d/'runtime_report.json').write_text(json.dumps({'baseline_sha256_after':rebuild.BASE,'source_saved':False,'rendered':False}))
   elif name=='integrate_conifer.py':
    Path(opts['--output']).write_bytes(b'integrated');Path(opts['--report']).write_text(json.dumps({'source_unchanged':True,'asset_unchanged':True,'checks':{'exact':True}}))
   elif name=='validate_preservation.py':
    self.assertEqual(opts['--accepted-model'],str(self.accepted));self.assertEqual(opts['--source-components'],str(self.root/'inputs/source_components.json'))
    self.assertEqual(opts['--checkpoint'],str(self.accepted if len(calls)==2 else self.out/'reproduced_candidate.blend'))
    Path(opts['--report']).write_text(json.dumps({'pass':True,'generated_asset_semantic_manifest':{'pass':True}}))
   else:
    self.assertEqual(opts['--mapping'],str(self.out/'generated/component_contact_mapping.json'))
    self.assertEqual(opts['--route-report'],str(self.root/'inputs/v018_route_envelope.json'))
    self.assertEqual(opts['--candidate'],str(self.out/'reproduced_candidate.blend'))
    d={'geometry_and_attachment_pass':True,'issues':[]} if name=='validate_new_geometry.py' else {'folded_components':[],'components_tested':3199}
    Path(opts['--report']).write_text(json.dumps(d))
   return subprocess.CompletedProcess(argv,0)
  with patch('rebuild.subprocess.run',side_effect=process):result=rebuild.run(self.a,self.root)
  self.assertEqual(calls,['generate_conifer.py','validate_preservation.py','integrate_conifer.py','validate_preservation.py','validate_new_geometry.py','audit_tube_folds.py'])
  self.assertEqual(len(result['steps_completed']),6);self.assertEqual(result['status'],'REPRODUCTION_VALIDATED_NOT_NEW_ACCEPTANCE');self.assertTrue(result['inputs_unchanged']);self.assertTrue(result['bundle_unchanged'])
if __name__=='__main__':unittest.main()
