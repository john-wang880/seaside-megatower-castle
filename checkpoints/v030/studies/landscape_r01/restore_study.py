"""Verify/join a tested-massing study ZIP; no extraction, code execution or model changes."""
import argparse,hashlib,json,os,tempfile,zipfile
from pathlib import Path
D=Path(__file__).resolve().parent
def sha(x):return hashlib.sha256(x).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args();out=Path(a.output).absolute()
 if out.resolve()!=out or any(p.is_symlink()for p in [out,*out.parents])or os.path.lexists(out)or not out.parent.is_dir():raise ValueError('Choose new nonaliased output with existing parent')
 m=json.loads((D/'ARCHIVE.json').read_text());buf=[]
 for r in m['parts']:
  n=r['file']
  if Path(n).name!=n or any(c in n for c in '/\\:'):raise ValueError('Unsafe part')
  b=(D/n).read_bytes()
  if len(b)!=r['bytes']or sha(b)!=r['sha256']:raise ValueError('Part mismatch')
  buf.append(b)
 raw=b''.join(buf)
 if len(raw)!=m['archive_bytes']or sha(raw)!=m['archive_sha256']:raise ValueError('Archive mismatch')
 fd,name=tempfile.mkstemp(dir=out.parent,prefix='.study-');p=Path(name)
 try:
  with os.fdopen(fd,'wb')as f:f.write(raw)
  with zipfile.ZipFile(p)as z:
   bad=z.testzip()
   if bad:raise ValueError('ZIP CRC mismatch')
   inventory=z.read('FILES.json')
   if sha(inventory)!=m['members_manifest_sha256']:raise ValueError('Manifest mismatch')
   spec=json.loads(inventory)
   if set(z.namelist())!=set(spec)|{'FILES.json'}:raise ValueError('Archive member set mismatch')
   for n,r in spec.items():
    if n.startswith('/')or '..'in Path(n).parts:raise ValueError('Unsafe member')
    b=z.read(n)
    if len(b)!=r['bytes']or sha(b)!=r['sha256']:raise ValueError('Member mismatch')
  os.link(p,out)
 finally:p.unlink(missing_ok=True)
 print('Verified tested-massing study ZIP written; nothing extracted or executed.')
if __name__=='__main__':main()
