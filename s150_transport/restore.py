#!/usr/bin/env python3
"""S150 R2 transport reader. Download files from one advertised GitHub branch."""
import argparse,base64,hashlib,json,os,tempfile,zipfile,re
from pathlib import Path, PurePosixPath
A='01ed2b9b1595effb140ef471489fdaa71e83ff11b45a6718a432b844a48b7c7f'
M='27bc325e2bc610fa9af50b557ae803ad249fd9600abd219a4c7bbfb5f47490c4'
T='3bdc84ff68187e9f12757566093986ca9552b8da9f18de405090122eaccf374d'
C='ca990487d07ec04083fc64fa567e653cad9c90d1'
N=128483763
P=84
H=lambda b:hashlib.sha256(b).hexdigest()
def need(ok,info):
    if not ok: raise ValueError(info)
def bare(p):
    need(p.is_file() and not p.is_symlink(),'missing regular file: '+p.name)
    return p.read_bytes()
def safe(name):
    q=PurePosixPath(name)
    return not q.is_absolute() and '\\' not in name and '..' not in q.parts and not name.endswith('/') and bool(q.parts)
def reconstruct(out):
    base=Path(__file__).resolve().parent
    metadata=bare(base/'MANIFEST.json')
    need(H(metadata)==T,'transport manifest digest mismatch')
    m=json.loads(metadata)
    need(m['format']=='s150-r2-contents-base64-v1' and m['archive_size']==N and m['archive_sha256']==A and m['candidate_sha256']==M and m['historical_source_commit']==C,'unexpected archive identity')
    need(len(m['parts'])==m['part_count']==P,'part count mismatch')
    need(not out.exists() and not out.is_symlink(),'output exists; will not overwrite')
    with tempfile.NamedTemporaryFile(dir=out.parent,prefix='.s150-verified-',delete=False) as w:
        tmp=Path(w.name)
        try:
            ah=hashlib.sha256(); total=0
            for i,row in enumerate(m['parts']):
                name=f'part_{i:03d}.base64'
                need(row['path']==name and row['index']==i and row['offset']==total,'part order mismatch')
                txt=bare(base/name)
                need(len(txt)==row['ascii_size'] and H(txt)==row['ascii_sha256'],'transport text mismatch '+name)
                raw=base64.b64decode(txt,validate=True)
                need(len(raw)==row['raw_size'] and H(raw)==row['raw_sha256'],'decoded content mismatch '+name)
                w.write(raw);ah.update(raw);total+=len(raw)
            w.flush()
            need(total==N and ah.hexdigest()==A,'archive mismatch')
            with zipfile.ZipFile(tmp) as z:
                names=z.namelist()
                need(len(names)==len(set(names)) and all(safe(v) for v in names) and z.testzip() is None,'archive structure or CRC mismatch')
                pm=json.loads(z.read('PAYLOAD_MANIFEST.json'))
                need(pm['parent_commit']==C and len(pm['files'])==976,'sealed inner ancestry or manifest count mismatch')
                need(set(names)=={'PAYLOAD_MANIFEST.json',*pm['files']},'manifest member set mismatch')
                for v,meta in pm['files'].items():
                    with z.open(v) as f: need(z.getinfo(v).file_size==meta['size'] and hashlib.file_digest(f,'sha256').hexdigest()==meta['sha256'],'payload digest mismatch '+v)
                need(pm['files'][m['candidate_member']]['sha256']==M,'native model digest mismatch')
            # Atomically publish without replacing an existing path.
            os.link(tmp,out)
        finally: tmp.unlink(missing_ok=True)
    print(json.dumps(dict(passed=True,archive_size=N,archive_sha256=A,model_sha256=M,parts=P,verified_payloads=976,historical_source_commit=C)))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    reconstruct(p.parse_args().out)
