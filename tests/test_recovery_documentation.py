"""The recovery entry point must track the newest checkpoint, not stale history."""
import json
from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parents[1]
class RecoveryDocumentationTests(unittest.TestCase):
 def setUp(self):
  candidates=[p for p in (ROOT/'checkpoints').glob('v*') if re.fullmatch(r'v\d+',p.name) and (p/'MANIFEST.json').is_file()]
  self.latest=max(candidates,key=lambda p:int(p.name[1:]));self.manifest=json.loads((self.latest/'MANIFEST.json').read_text())
  text=(ROOT/'CONTINUATION.md').read_text();self.active=text.split('## 当前唯一有效状态',1)[1].split('\n## ',1)[0]
 def test_active_recovery_manifest_is_newest_and_exists(self):
  links=re.findall(r'checkpoints/v\d+/MANIFEST\.json',self.active)
  self.assertEqual(links,[self.latest.relative_to(ROOT).as_posix()+'/MANIFEST.json'])
  self.assertTrue((ROOT/links[0]).is_file())
 def test_active_recovery_sha_matches_manifest(self):
  self.assertIn(self.manifest['model_sha256'],self.active)
  self.assertIn(format(self.manifest['model_bytes'],','),self.active)
 def test_readme_latest_checkpoint_matches_manifest(self):
  text=(ROOT/'README.md').read_text();line=next(x for x in text.splitlines() if x.startswith('最新检查点：'))
  self.assertIn('checkpoints/'+self.latest.name+'/README.md',line)
if __name__=='__main__':unittest.main()
