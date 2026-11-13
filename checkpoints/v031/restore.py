import pathlib,json,hashlib,tarfile,io
p=pathlib.Path(__file__).resolve().parent;m=json.loads((p/'PARTS.json').read_text());parts=[]
for a in m['parts']:
 b=(p/'archive'/a['name']).read_bytes();assert len(b)==a['bytes']and hashlib.sha256(b).hexdigest()==a['sha256'];parts.append(b)
b=b''.join(parts);assert len(b)==m['bytes']and hashlib.sha256(b).hexdigest()==m['sha256'];out=p/'restored';out.mkdir(exist_ok=False)
with tarfile.open(fileobj=io.BytesIO(b),mode='r:gz')as t:t.extractall(out,filter='data')
for n,h in json.loads((out/'CHECKSUMS.json').read_text()).items():assert hashlib.sha256((out/n).read_bytes()).hexdigest()==h,n
print('RESTORED_AND_VERIFIED',out)
