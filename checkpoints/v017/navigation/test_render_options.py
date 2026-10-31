"""Standard-Python tests; importing renderer never imports bpy or starts a render."""
import contextlib,io,unittest
import render_manifest_still as render
class RenderOptions(unittest.TestCase):
 def argv(self):return ['--manifest','views.json','--view','hero','--out','image.png']
 def test_preserves_default_four_threads(self):self.assertEqual(render.parse_args(self.argv()).threads,4)
 def test_explicit_benchmarked_counts(self):
  for n in (3,8):self.assertEqual(render.parse_args(self.argv()+['--threads',str(n)]).threads,n)
 def test_rejects_invalid_counts_before_render(self):
  for n in ('0','-1','1025','1.5','many'):
   with self.subTest(n=n),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as e:render.parse_args(self.argv()+['--threads',n])
   self.assertEqual(e.exception.code,2)
 def test_keeps_required_destination(self):
  with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):render.parse_args(['--threads','8'])
if __name__=='__main__':unittest.main()
