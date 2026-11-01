"""Independent Linux path/publication tests; no Blender/native Windows claim."""
import unittest,tempfile,json,importlib.util,os,sys,argparse
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
parser=argparse.ArgumentParser(add_help=False);parser.add_argument('--tool',required=True);parser.add_argument('--source',required=True);args,remaining=parser.parse_known_args();sys.argv=[sys.argv[0]]+remaining;TOOL=Path(args.tool).resolve();SOURCE=Path(args.source).resolve();spec=importlib.util.spec_from_file_location('inspection_preflight',TOOL/'preflight.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
class Guards(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='inspection QA 中文 ');self.root=Path(self.temp.name);self.repo=self.root/'repo';(self.repo/'checkpoints/v026').mkdir(parents=True);self.m={'format':'blend-zstd-frames-v1','model_sha256':q.SOURCE_SHA,'model_bytes':q.SOURCE_BYTES,'model':'castle_v026.blend'};(self.repo/'checkpoints/v026/MANIFEST.json').write_text(json.dumps(self.m));self.out=self.root/'new copy.blend';self.report=self.root/'new report.json'
 def tearDown(self):self.temp.cleanup()
 def test_latest_reviewed(self):self.assertEqual(q.latest_manifest(self.repo)[2],self.m)
 def test_unknown_newest(self):
  (self.repo/'checkpoints/v027').mkdir();(self.repo/'checkpoints/v027/MANIFEST.json').write_text('{}')
  with self.assertRaises(q.GuardError):q.latest_manifest(self.repo)
 def test_numeric_ambiguity(self):
  (self.repo/'checkpoints/v26').mkdir();(self.repo/'checkpoints/v26/MANIFEST.json').write_text(json.dumps(self.m))
  with self.assertRaises(q.GuardError):q.latest_manifest(self.repo)
 def test_stale_only(self):
  (self.repo/'checkpoints/v026').rename(self.repo/'checkpoints/v025')
  with self.assertRaises(q.GuardError):q.latest_manifest(self.repo)
 def test_changed_manifest(self):
  self.m['model_sha256']='0'*64;(self.repo/'checkpoints/v026/MANIFEST.json').write_text(json.dumps(self.m))
  with self.assertRaises(q.GuardError):q.latest_manifest(self.repo)
 def test_no_manifest_not_live(self):
  (self.repo/'checkpoints/v999').mkdir();self.assertEqual(q.latest_manifest(self.repo)[2],self.m)
 def test_reviewed_catalog(self):self.assertEqual(len(q.load_catalog(TOOL/'catalog.json')['views']),14)
 def test_corrupt_catalog(self):
  c=self.root/'catalog.json';c.write_text((TOOL/'catalog.json').read_text()+' ')
  with self.assertRaises(q.GuardError):q.load_catalog(c)
 def test_unicode_new_path(self):self.assertEqual(q.new_destination(self.out,'.blend'),self.out)
 def test_existing_nooverwrite(self):
  self.out.write_text('keep')
  with self.assertRaises(q.GuardError):q.new_destination(self.out,'.blend')
  self.assertEqual(self.out.read_text(),'keep')
 def test_dangling_symlink(self):
  self.out.symlink_to(self.root/'absent')
  with self.assertRaises(q.GuardError):q.new_destination(self.out,'.blend')
 def test_symlink_parent(self):
  (self.root/'alias').symlink_to(self.repo,target_is_directory=True)
  with self.assertRaises(q.GuardError):q.unaliased(self.root/'alias/new.blend')
 def test_parent_traversal(self):
  with self.assertRaises(q.GuardError):q.unaliased(str(self.repo)+'/../new.blend')
 def test_optimized_rejected_first(self):
  with patch.object(q.sys,'flags',SimpleNamespace(optimize=1)):
   with self.assertRaises(q.GuardError):q.preflight('','','','','')
 def real_source(self):return SOURCE
 def test_full_real_preflight_no_output(self):
  identity,c=q.preflight(self.repo,self.real_source(),self.out,self.report,TOOL/'catalog.json');self.assertEqual(identity['source_sha256'],q.SOURCE_SHA);self.assertFalse(self.out.exists());self.assertFalse(self.report.exists())
 def test_wrong_source_size(self):
  wrong=self.root/'wrong.blend';wrong.write_bytes(b'wrong')
  with self.assertRaises(q.GuardError):q.preflight(self.repo,wrong,self.out,self.report,TOOL/'catalog.json')
 def test_wrong_source_sha_same_size_guard(self):
  original=q.sha;source=self.real_source()
  with patch.object(q,'sha',side_effect=lambda p:'0'*64 if Path(p)==source else original(p)):
   with self.assertRaises(q.GuardError):q.preflight(self.repo,source,self.out,self.report,TOOL/'catalog.json')
 def test_source_output_alias(self):
  with self.assertRaises(q.GuardError):q.preflight(self.repo,self.real_source(),self.real_source(),self.report,TOOL/'catalog.json')
 def test_immutable_checkpoint_output(self):
  with self.assertRaises(q.GuardError):q.preflight(self.repo,self.real_source(),self.repo/'checkpoints/v026/new.blend',self.report,TOOL/'catalog.json')
 def setup_publish(self):
  a=self.root/'temp.blend';b=self.root/'temp.json';a.write_bytes(b'blend');b.write_bytes(b'receipt');return a,b
 def test_publish_pair(self):
  a,b=self.setup_publish();q.publish_pair(a,self.out,b,self.report);self.assertEqual(self.out.read_bytes(),b'blend');self.assertEqual(self.report.read_bytes(),b'receipt')
 def test_second_collision_rollsback_owned_first(self):
  a,b=self.setup_publish();self.report.write_text('foreign')
  with self.assertRaises(q.GuardError):q.publish_pair(a,self.out,b,self.report)
  self.assertFalse(self.out.exists());self.assertEqual(self.report.read_text(),'foreign')
 def test_second_failure_preserves_replaced_first(self):
  a,b=self.setup_publish();link=os.link
  def intercept(src,dest):
   if Path(dest)==self.report:self.out.unlink();self.out.write_text('foreign replacement');raise OSError('injected second failure')
   return link(src,dest)
  with patch.object(q.os,'link',side_effect=intercept):
   with self.assertRaises(OSError):q.publish_pair(a,self.out,b,self.report)
  self.assertEqual(self.out.read_text(),'foreign replacement');self.assertFalse(self.report.exists())
 def test_swap_after_first_link_before_recording(self):
  a,b=self.setup_publish();link=os.link
  def intercept(src,dest):
   if Path(dest)==self.out:
    link(src,dest);self.out.unlink();self.out.write_text('foreign raced after link');return
   raise OSError('injected second link failure')
  with patch.object(q.os,'link',side_effect=intercept):
   with self.assertRaises((OSError,q.GuardError)):q.publish_pair(a,self.out,b,self.report)
  self.assertTrue(self.out.exists(),'Foreign replacement must not be deleted')
  self.assertEqual(self.out.read_text(),'foreign raced after link');self.assertFalse(self.report.exists())
 def test_platform_no_hardlink_fails_closed_mock(self):
  a,b=self.setup_publish()
  with patch.object(q.os,'link',side_effect=OSError('mock unsupported filesystem')):
   with self.assertRaises(OSError):q.publish_pair(a,self.out,b,self.report)
  self.assertFalse(self.out.exists());self.assertFalse(self.report.exists())
if __name__=='__main__':unittest.main()
