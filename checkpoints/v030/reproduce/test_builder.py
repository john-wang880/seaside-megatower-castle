import importlib.util,json,os,subprocess,sys,tempfile,unittest
from unittest import mock
from pathlib import Path
P=Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('builder',P/'build_fittings.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
class Tests(unittest.TestCase):
 def test_budget(self):
  g=b.geometry(json.loads((P/'PLAN.json').read_text()));self.assertEqual((len(g),sum(len(x['components'])for x in g),sum(sum(len(f)-2 for f in x['faces'])for x in g)),(6,78,2184))
 def test_deterministic(self):
  p=json.loads((P/'PLAN.json').read_text());self.assertEqual(b.geometry(p),b.geometry(p))
 def test_closed_seats(self):
  v,f=b.prism([1,2,29],[2,3,31]);self.assertGreater(b.certify(v,f),0);self.assertEqual(set(p[2]for p in v),{29,31});self.assertEqual(len(f),10)
 def test_bad_plan(self):
  p=json.loads((P/'PLAN.json').read_text());p['candidate_sha256']='wrong'
  with self.assertRaises(RuntimeError):b.geometry(p)
 def test_existing_output(self):
  with self.assertRaises(RuntimeError):b.safe(P/'PLAN.json')
 def test_symlink(self):
  with tempfile.TemporaryDirectory()as t:
   p=Path(t)/'alias';p.symlink_to(P/'PLAN.json')
   with self.assertRaises(RuntimeError):b.safe(p,True)
 def test_optimized_guard(self):
  r=subprocess.run([sys.executable,'-O',str(P/'build_fittings.py')],env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True);self.assertNotEqual(r.returncode,0);self.assertIn('Optimized Python refused',r.stderr)
 def test_wrong_source(self):
  with tempfile.TemporaryDirectory()as t:
   p=Path(t);(p/'source.blend').write_bytes(b'not source')
   with mock.patch.object(sys,'argv',['builder','--source',str(p/'source.blend'),'--output',str(p/'new.blend'),'--report',str(p/'new.json')]):
    with self.assertRaisesRegex(RuntimeError,'Wrong source hash'):b.main()
 def test_occupied_report(self):
  with tempfile.TemporaryDirectory()as t:
   p=Path(t);(p/'report.json').write_text('{}')
   with self.assertRaises(RuntimeError):b.safe(p/'report.json')
 def test_alias_dotdot(self):
  with self.assertRaises(RuntimeError):b.safe(P/'..'/'PLAN.json',True)
 def mismatch(self,which):
  with tempfile.TemporaryDirectory()as t:
   p=Path(t);source=p/'source.blend';source.write_bytes(b'test')
   def digest(path):
    if Path(path)==source:return b.SOURCE
    if Path(path).name==which:return 'mismatch'
    return b.PLAN_SHA if Path(path).name=='PLAN.json'else b.HELPER_SHA
   with mock.patch.object(b,'sha',digest),mock.patch.object(sys,'argv',['builder','--source',str(source),'--output',str(p/'new.blend'),'--report',str(p/'new.json')]):
    with self.assertRaisesRegex(RuntimeError,'Frozen helper/plan changed'):b.main()
 def test_plan_hash_mismatch(self):self.mismatch('PLAN.json')
 def test_helper_hash_mismatch(self):self.mismatch('snapshot_support.py')
 def test_open_component(self):
  v,f=b.prism([0,0,0],[1,1,1])
  with self.assertRaises(RuntimeError):b.certify(v,f[:-1])
 def test_reversed_component(self):
  v,f=b.prism([0,0,0],[1,1,1])
  with self.assertRaises(RuntimeError):b.certify(v,[list(reversed(p))for p in f])
 def test_positive_lid_seat(self):
  for m in b.geometry(json.loads((P/'PLAN.json').read_text())):
   if len(m['components'])==2:
    a,z=m['components'];self.assertEqual(a['top_z'],z['bottom_seat_z']);self.assertAlmostEqual(a['bounds'][0][0]-z['bounds'][0][0],.006);self.assertAlmostEqual(z['bounds'][1][0]-a['bounds'][1][0],.006)
if __name__=='__main__':unittest.main()
