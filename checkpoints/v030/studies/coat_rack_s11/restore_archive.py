from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent
m=json.loads((p/'PARTS.json').read_text())
out=p/m['archive']
if out.exists(): raise SystemExit('Output exists; choose a fresh restoration directory.')
h=hashlib.sha256(); total=0
for a in m['parts']:
 b=(p/a['name']).read_bytes()
 assert len(b)==a['bytes'] and hashlib.sha256(b).hexdigest()==a['sha256'],a['name']
 h.update(b); total+=len(b)
assert total==m['bytes'] and h.hexdigest()==m['sha256']
with out.open('xb') as f:
 for a in m['parts']: f.write((p/a['name']).read_bytes())
print('Verified:',out,m['sha256'])
