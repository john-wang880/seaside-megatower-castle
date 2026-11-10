from pathlib import Path
import hashlib,json,tarfile
p=Path(__file__).resolve().parent;m=json.loads((p/'PARTS.json').read_text());out=p/'restored'
assert not out.exists(), 'Choose a fresh restoration directory'
buf=[]
for a in m['parts']:
 b=(p/a['name']).read_bytes();assert len(b)==a['bytes'] and hashlib.sha256(b).hexdigest()==a['sha256'];buf.append(b)
b=b''.join(buf);assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256']
import io
with tarfile.open(fileobj=io.BytesIO(b),mode='r:gz') as t:t.extractall(out,filter='data')
for line in (out/'SHA256SUMS.txt').read_text().splitlines():
 h,name=line.split('  ',1);assert hashlib.sha256((out/name).read_bytes()).hexdigest()==h,name
print('All parts, archive and extracted files verified:',out)
