"""Portable input binding and no-overwrite report guards; no model mutation."""
import argparse,hashlib,json,sys
from pathlib import Path
SOURCE_SHA='457348497ba7dade666a909c029f6641a0945012f264fe088b8f06513a937ae9'
ACCEPTED_SHA='99156d901f9d498b86bae4834a642d1d9110dc6e4e3a4273bca64fda17a9dfd2'
PLAN_SHA='97fd236c85f35d05ef4fdb7db67997b7a53a4cc5701d893432ab6be6d69350ec'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inputs():
 if sys.flags.optimize:raise RuntimeError('Assertions required; optimized Python unsupported')
 p=argparse.ArgumentParser()
 for name in ['source','candidate','report']:p.add_argument('--'+name,required=True)
 p.add_argument('--candidate-sha256',default=ACCEPTED_SHA)
 p.add_argument('--case',choices=['mask','hidden_original','enlargement','orientation','backing_gap'])
 a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 paths=[Path(getattr(a,k))for k in ['source','candidate','report']]
 if any(x.is_symlink()for x in paths):raise RuntimeError('Symlink inputs/outputs unsupported')
 source,candidate,report=[x.resolve()for x in paths]
 if len({source,candidate,report})!=3 or report.exists() or not report.parent.is_dir():raise RuntimeError('Distinct existing inputs and new report in existing directory required')
 if len(a.candidate_sha256)!=64 or any(c not in '0123456789abcdef'for c in a.candidate_sha256):raise RuntimeError('Malformed candidate SHA256')
 if sha(source)!=SOURCE_SHA or sha(candidate)!=a.candidate_sha256:raise RuntimeError('Model SHA256 mismatch')
 pp=Path(__file__).resolve().parent/'data/plan.json'
 if sha(pp)!=PLAN_SHA:raise RuntimeError('Plan SHA256 mismatch')
 data={}
 for name,expected in DATA_HASHES.items():
  path=pp.parent/name
  if sha(path)!=expected:raise RuntimeError('Bundled data SHA mismatch: '+name)
  data[name]=json.loads(path.read_text())
 return a,source,candidate,report,data

DATA_HASHES={'camera_preflight.json': '5954165e98e87ee441f901063b1ce4022bcd8306e6c4f45356a27d21db87aa75', 'plan.json': '97fd236c85f35d05ef4fdb7db67997b7a53a4cc5701d893432ab6be6d69350ec', 'build.json': 'b77683ad45635e0fc4ee79243d269c6a433448b720b4d0e46a2ad4a94166df6e'}
