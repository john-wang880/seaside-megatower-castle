"""Linux-only, import-safe recipe/path/identity guards; no scene access."""
import hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE_SHA='efcd894acdc045a30f845f05267662957b656bc7fe0ee4cf48c05fc798b610ee'
SOURCE_BYTES=47680699
PLAN_SHA='13db5405453470460cf3bb8868aa71fe23f1272f3fab8cde5911698b04e2e3e3'
RUNTIME=('run_final_orbit.py','render_final_frame.py','orbit_common.py','runtime_guards.py','lighting_snapshot.py')
def need(ok,message):
 if not ok:raise RuntimeError(message)
def environment():
 need(sys.platform.startswith('linux'),'This opt-in runner is Linux-only')
 need(not sys.flags.optimize,'Optimized Python refused; immutable validator uses assertions')
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def clean(path):
 p=Path(path).expanduser().absolute();need('..'not in p.parts and p.resolve()==p,'Path alias refused')
 need(not any(q.is_symlink()for q in [p,*p.parents]),'Symlink path refused');return p
def execution_lease_path():
 cache=clean(os.environ.get('XDG_CACHE_HOME',str(Path.home()/'.cache')))
 return cache/'seaside-castle'/'orbit-execution.lock'
def identity():
 environment();need(sha(ROOT/'final_plan.json')==PLAN_SHA,'Wrong immutable camera/quality plan')
 bindings=json.loads((ROOT/'RUNTIME_BINDINGS.json').read_text());need(set(bindings)==set(RUNTIME),'Wrong runtime binding inventory')
 need(all(sha(ROOT/n)==h for n,h in bindings.items()),'Runtime binding mismatch')
 return {'source_sha256':SOURCE_SHA,'source_bytes':SOURCE_BYTES,'plan_sha256':PLAN_SHA,'runtime_sha256':{n:sha(ROOT/n)for n in RUNTIME},'execution_lease_path':str(execution_lease_path()),'bindings_sha256':sha(ROOT/'RUNTIME_BINDINGS.json'),'kind':'v026-partial-orbit-new-identity'}
def check_source(source):
 p=clean(source);need(p.is_file()and p.stat().st_size==SOURCE_BYTES and sha(p)==SOURCE_SHA,'Wrong source bytes/hash');return p
def check_output(source,out):
 source=clean(source);out=clean(out)
 need(out!=source and not source.is_relative_to(out)and not out.is_relative_to(ROOT)and not ROOT.is_relative_to(out),'Source/recipe output alias refused')
 need('checkpoints'not in out.parts and 'historical'not in out.parts,'Historical/frozen output refused')
 need(not out.exists()or out.is_dir(),'Output is not a directory');need(out.parent.is_dir(),'Existing output parent required')
 if out.exists():need(not any(p.is_symlink()for p in out.rglob('*')),'Output contains symlink')
 return out
def check_existing(out,expected,allow_new_lock=False):
 p=out/'run_identity.json'
 if p.exists():need(p.is_file()and json.loads(p.read_text())==expected,'Output identity mismatch')
 elif out.exists():
  allowed={'runner.lock'}if allow_new_lock else set()
  need({p.name for p in out.iterdir()}<=allowed,'Unknown nonempty output refused')
def recheck(source,expected):
 check_source(source);need(identity()==expected,'Runtime/source identity changed')
