from pathlib import Path
import hashlib,json,tarfile,io
p=Path(__file__).resolve().parent;m=json.loads((p/'PARTS.json').read_text());b=b''
for a in m['parts']:
 q=(p/a['name']).read_bytes();assert len(q)==a['bytes'] and hashlib.sha256(q).hexdigest()==a['sha256'];b+=q
assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256']
o=p/'restored';o.mkdir(exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(b),mode='r:gz') as t:t.extractall(o,filter='data')
for n,h in json.loads((o/'CHECKSUMS.json').read_text()).items():assert hashlib.sha256((o/n).read_bytes()).hexdigest()==h,n
print('Verified',o)
