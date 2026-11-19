"""Offline candidate pack/restore experiment; does not write remote state."""
import argparse,hashlib,json,pathlib,subprocess,tempfile
CHUNK=716800; MAX_DEPTH=8
H=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
Z=pathlib.Path('/usr/bin/zstd')
def z(*a):
 subprocess.run([str(Z),'-q',*map(str,a)],check=True)
def raw(src,dst):
 with src.open('rb') as f:magic=f.read(4)
 if magic==bytes.fromhex('28b52ffd'):z('-df',src,'-o',dst)
 elif magic==b'BLEN':
  import shutil
  shutil.copyfile(src,dst)
 else: raise ValueError(f'unrecognized Blender container: {src}')
 with dst.open('rb') as f:assert f.read(7)==b'BLENDER'
def canon(src,dst):z('-3','--single-thread','--no-check','-f',src,'-o',dst)
def desc(p):return dict(size=p.stat().st_size,sha256=H(p))
def tool():return {'zstd_version':subprocess.check_output([str(Z),'--version'],text=True).strip(),'binary_sha256':H(Z)}
def pack(base,target,out,depth,parent,checkpoint):
 assert 1<=depth<=MAX_DEPTH and parent and checkpoint
 out.mkdir(); partsdir=out/'parts';partsdir.mkdir()
 with tempfile.TemporaryDirectory(dir=out.parent) as d:
  d=pathlib.Path(d);a=d/'base.raw';b=d/'next.raw';p=d/'forward.zst'
  raw(base,a);raw(target,b)
  z('--patch-from='+str(a),'-f',b,'-o',p)
  assert max(a.stat().st_size,b.stat().st_size)<=2**29,'window policy requires new verified profile'
  restore=d/'restore.raw';z('-df','--long=29','--patch-from='+str(a),p,'-o',restore)
  assert desc(restore)==desc(b)
  can=out/'canonical.blend';canon(b,can)
  check=d/'check.blend';canon(restore,check);assert desc(check)==desc(can)
  old=desc(base);new=desc(can); parts=[]
  with p.open('rb') as f:
   for i,chunk in enumerate(iter(lambda:f.read(CHUNK),b'')):
    n=f'part_{i:05d}.bin';q=partsdir/n;q.write_bytes(chunk);parts.append(dict(name=n,**desc(q)))
  j=dict(schema='blend-raw-zstd-delta-v1',decompress_window_log=29,encoding=['-3','--single-thread','--no-check'],tool=tool(),
   checkpoint_commit=checkpoint,parent_commit=parent,depth=depth,base_container=old,base_raw=desc(a),target_raw=desc(b),patch=desc(p),target_container=new,parts=parts)
  (out/'DELTA_MANIFEST.json').write_text(json.dumps(j,indent=2)+'\n')
def restore(base,folder,out):
 d=json.loads((folder/'DELTA_MANIFEST.json').read_text())
 assert d['schema']=='blend-raw-zstd-delta-v1' and 1<=d['depth']<=MAX_DEPTH
 assert d['decompress_window_log']==29 and d['encoding']==['-3','--single-thread','--no-check'] and d['tool']==tool()
 assert desc(base)==d['base_container']
 with tempfile.TemporaryDirectory(dir=out.parent) as wk:
  wk=pathlib.Path(wk);a=wk/'base.raw';b=wk/'new.raw';p=wk/'all_parts.zst';raw(base,a);assert desc(a)==d['base_raw']
  with p.open('wb') as f:
   for i,x in enumerate(d['parts']):
    assert x['name']==f'part_{i:05d}.bin' and 0<x['size']<=CHUNK
    n=folder/'parts'/x['name'];assert desc(n)=={k:x[k] for k in ('size','sha256')}
    f.write(n.read_bytes())
  assert desc(p)==d['patch']
  z('-df','--long=29','--patch-from='+str(a),p,'-o',b);assert desc(b)==d['target_raw']
  c=wk/'confirmed.blend';canon(b,c);assert desc(c)==d['target_container']
  assert not out.exists();c.replace(out)
a=argparse.ArgumentParser();sp=a.add_subparsers(dest='cmd',required=True)
pk=sp.add_parser('pack');rt=sp.add_parser('restore')
for name in ['base','target','out']:pk.add_argument(name,type=pathlib.Path)
pk.add_argument('--parent',required=True);pk.add_argument('--checkpoint',required=True);pk.add_argument('--depth',type=int,required=True)
for name in ['base','folder','out']:rt.add_argument(name,type=pathlib.Path)
o=a.parse_args()
if o.cmd=='pack':pack(o.base,o.target,o.out,o.depth,o.parent,o.checkpoint)
else:restore(o.base,o.folder,o.out)
