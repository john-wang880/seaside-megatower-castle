from pathlib import Path
import hashlib,json,sys
p=Path(__file__).resolve().parent
m=json.loads((p/'PARTS.json').read_text())
out=Path(sys.argv[1])
if out.exists(): raise SystemExit('Output must not exist')
blocks=[]
for item in m['parts']:
 b=(p/item['name']).read_bytes()
 if len(b)!=item['bytes'] or hashlib.sha256(b).hexdigest()!=item['sha256']: raise SystemExit('Invalid part: '+item['name'])
 blocks.append(b)
b=b''.join(blocks)
if len(b)!=m['bytes'] or hashlib.sha256(b).hexdigest()!=m['sha256']: raise SystemExit('Archive mismatch')
with out.open('xb') as f: f.write(b)
print('Archive restored and SHA256 verified:',out)
