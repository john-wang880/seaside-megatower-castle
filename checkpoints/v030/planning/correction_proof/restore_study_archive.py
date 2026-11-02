"""Verify and join project study archive parts; never extracts or executes."""
from pathlib import Path
import hashlib,json,argparse
r=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.exists() or a.output.is_symlink():raise FileExistsError(a.output)
d=json.loads((r/'ARCHIVE.json').read_text());chunks=[]
for e in d['parts']:
 b=(r/e['file']).read_bytes()
 if len(b)!=e['bytes'] or hashlib.sha256(b).hexdigest()!=e['sha256']:raise ValueError(e['file'])
 chunks.append(b)
b=b''.join(chunks)
if len(b)!=d['bytes'] or hashlib.sha256(b).hexdigest()!=d['sha256']:raise ValueError('Archive mismatch')
with a.output.open('xb') as f:f.write(b)
print('Verified archive:',a.output)
