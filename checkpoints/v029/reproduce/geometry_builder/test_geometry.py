import unittest,tempfile,subprocess,os,sys,json,shutil
from pathlib import Path
import build_geometry as b
import planar
HERE=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 def test_clip_area(self):
  p=[(0.,0.,0.),(4.,0.,0.),(4.,4.,0.),(0.,4.,0.)];box=[[1,1,-1],[3,3,1]]
  self.assertAlmostEqual(sum(b.area(q)for q in b.subtract_box(p,box)),12)
 def test_hole_domain(self):
  p=[(0.,0.,0.),(4.,0.,0.),(4.,4.,0.),(0.,4.,0.)];pieces=b.subtract_box(p,[[1,1,-1],[3,3,1]]);ts=planar.triangulate(pieces,p,2)
  self.assertAlmostEqual(sum(b.area(t)for t in ts),12)
  self.assertTrue(all(not(1<sum(q[0]for q in t)/3<3 and 1<sum(q[1]for q in t)/3<3)for t in ts))
 def test_two_holes(self):
  p=[(0.,0.,0.),(8.,0.,0.),(8.,4.,0.),(0.,4.,0.)];parts=[p]
  for box in ([[1,1,-1],[2,3,1]],[[5,1,-1],[7,3,1]]):parts=[q for r in parts for q in b.subtract_box(r,box)]
  ts=planar.triangulate(parts,p,2);self.assertAlmostEqual(sum(b.area(t)for t in ts),26)
 def test_concave(self):
  p=[(0.,0.,0.),(4.,0.,0.),(4.,1.,0.),(1.,1.,0.),(1.,4.,0.),(0.,4.,0.)];ts=planar.triangulate([p],p,2);self.assertAlmostEqual(sum(b.area(t)for t in ts),7)
 def test_native_quantization(self):self.assertEqual(b.f32(5.4),b.f32(5.400000095367432))
 def test_wrong_source(self):
  with tempfile.TemporaryDirectory(prefix='门厅 tests ')as td:
   p=Path(td)/'bad.json';p.write_text('{}')
   with self.assertRaisesRegex(RuntimeError,'wrong source export'):b.construct(p,HERE.parent/'frozen_plan')
 def test_wrong_plan(self):
  with tempfile.TemporaryDirectory()as td:
   p=Path(td);(p/'MANIFEST.json').write_text('{}')
   with self.assertRaisesRegex(RuntimeError,'wrong frozen plan'):b.construct(p/'unused',p)
 def test_output_exists(self):
  with tempfile.TemporaryDirectory(prefix='门厅 outputs ')as td:
   p=Path(td)/'existing.json';p.write_text('original')
   r=subprocess.run([sys.executable,'-B',str(HERE/'build_geometry.py'),'--export',str(p),'--plan-dir',td,'--output',str(p)],capture_output=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
   self.assertNotEqual(r.returncode,0);self.assertEqual(p.read_text(),'original');self.assertIn(b'output exists',r.stderr)
 def test_optimize(self):
  r=subprocess.run([sys.executable,'-B','-O',str(HERE/'build_geometry.py'),'--help'],capture_output=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'));self.assertNotEqual(r.returncode,0);self.assertIn(b'optimized Python unsupported',r.stderr)
 def test_directed_partition_rounding(self):
  self.assertEqual(b.quantize(28.9),28.900001525878906)
  self.assertNotEqual(b.quantize(28.9),b.f32(28.9))
  self.assertEqual(b.quantize(28.899999618530273),28.899999618530273)
  self.assertEqual(b.quantize(29),29)
 def test_symlink(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);src=p/'src';src.write_text('x');link=p/'alias';link.symlink_to(src)
   with self.assertRaisesRegex(RuntimeError,'symlink'):b.guard_paths(link,p,p/'out')
 def test_dangling_output(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);src=p/'src';src.write_text('x');out=p/'out';out.symlink_to(p/'missing')
   with self.assertRaisesRegex(RuntimeError,'symlink'):b.guard_paths(src,p,out)
 def test_plan_output_refused(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);src=p/'src';src.write_text('x');plan=p/'plan';plan.mkdir()
   with self.assertRaisesRegex(RuntimeError,'frozen plan'):b.guard_paths(src,plan,plan/'new')
 def test_publish_exclusive(self):
  with tempfile.TemporaryDirectory(prefix='储藏室 outputs ')as td:
   p=Path(td)/'existing';p.write_text('foreign')
   with self.assertRaises(FileExistsError):b.publish(p,{'x':1})
   self.assertEqual(p.read_text(),'foreign');self.assertEqual(len(list(p.parent.iterdir())),1)
 def test_publish_unicode(self):
  with tempfile.TemporaryDirectory(prefix='储藏室 outputs ')as td:
   p=Path(td)/'new 中文.json';b.publish(p,{'x':1});self.assertEqual(json.loads(p.read_text()),{'x':1})
 def test_attributes_corrupt(self):
  x=json.loads((HERE.parent/'frozen_plan'/'ATTRIBUTES.json').read_text());x['targets'][b.TARGETS[0][0]]['slots']=[['DATA','wrong']]
  with self.assertRaisesRegex(RuntimeError,'material mapping'):b.validate_attributes(x)
if __name__=='__main__':unittest.main()
