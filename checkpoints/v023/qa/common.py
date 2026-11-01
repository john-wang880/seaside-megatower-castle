import argparse,hashlib,json,sys
from pathlib import Path
SOURCE_SHA='99156d901f9d498b86bae4834a642d1d9110dc6e4e3a4273bca64fda17a9dfd2'
ACCEPTED_SHA='c4b1dda3b8f70e4c8cb0171834b2150b6d7610f6296847362fd204b2dfa7ad51'
PLAN_SHA='79385854fbb6247ede375adfba21eb9711a9df7a3ea66ebce7924d4a0ddf51b0'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inputs():
 if sys.flags.optimize:raise RuntimeError('Assertions required; optimized Python unsupported')
 p=argparse.ArgumentParser()
 for k in ['source','candidate','report','geometry']:p.add_argument('--'+k,required=True)
 p.add_argument('--candidate-sha256',default=ACCEPTED_SHA);p.add_argument('--case',choices=['extra_mask','unrelated_source']);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);paths=[Path(getattr(a,k))for k in ['source','candidate','report','geometry']]
 if any(p.is_symlink()for p in paths):raise RuntimeError('Symlink input/output unsupported')
 source,candidate,report,geometry=[p.resolve()for p in paths]
 if len({source,candidate,report,geometry})!=4 or report.exists()or geometry.exists()or not report.parent.is_dir()or not geometry.parent.is_dir():raise RuntimeError('Distinct inputs and new outputs in existing directories required')
 if len(a.candidate_sha256)!=64 or any(c not in '0123456789abcdef'for c in a.candidate_sha256):raise RuntimeError('Malformed candidate SHA')
 if sha(source)!=SOURCE_SHA or sha(candidate)!=a.candidate_sha256:raise RuntimeError('Model SHA mismatch')
 pp=Path(__file__).resolve().parent/'data/plan.json'
 if sha(pp)!=PLAN_SHA:raise RuntimeError('Plan SHA mismatch')
 return a,source,candidate,report,geometry,json.loads(pp.read_text())
