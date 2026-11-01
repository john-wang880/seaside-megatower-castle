"""Portable input binding and no-overwrite report guards; no model mutation."""
import argparse,hashlib,json,sys
from pathlib import Path
SOURCE_SHA='673dbbadca22d3dd45dc2f2eb5bde4a9e66851c1ca137da5c2570efc67c77614'
ACCEPTED_SHA='457348497ba7dade666a909c029f6641a0945012f264fe088b8f06513a937ae9'
PLAN_SHA='660d847827193a6624d6f9ab91e51d1621cac34bc28bb0cdf19e06c94ba3361a'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inputs():
 if sys.flags.optimize:raise RuntimeError('Assertions required; optimized Python unsupported')
 p=argparse.ArgumentParser()
 for name in ['source','candidate','report']:p.add_argument('--'+name,required=True)
 p.add_argument('--candidate-sha256',default=ACCEPTED_SHA)
 p.add_argument('--case',choices=['bounds','orientation','material','mask','unrelated_source'])
 a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 paths=[Path(getattr(a,k))for k in ['source','candidate','report']]
 if any(x.is_symlink()for x in paths):raise RuntimeError('Symlink inputs/outputs unsupported')
 source,candidate,report=[x.resolve()for x in paths]
 if len({source,candidate,report})!=3 or report.exists() or not report.parent.is_dir():raise RuntimeError('Distinct existing inputs and new report in existing directory required')
 if len(a.candidate_sha256)!=64 or any(c not in '0123456789abcdef'for c in a.candidate_sha256):raise RuntimeError('Malformed candidate SHA256')
 if sha(source)!=SOURCE_SHA or sha(candidate)!=a.candidate_sha256:raise RuntimeError('Model SHA256 mismatch')
 pp=Path(__file__).resolve().parent/'data/plan.json'
 if sha(pp)!=PLAN_SHA:raise RuntimeError('Plan SHA256 mismatch')
 return a,source,candidate,report,json.loads(pp.read_text())
