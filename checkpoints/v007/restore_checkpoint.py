#!/usr/bin/env python3
"""Verify and restore the current Blender checkpoint using only standard Python."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parent

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()

def main():
 m=json.loads((ROOT/'MANIFEST.json').read_text())
 for item in m['parts']:
  p=ROOT/item['name']
  if p.stat().st_size!=item['size'] or sha(p)!=item['sha256']:raise RuntimeError('Invalid part: '+p.name)
 archive=ROOT/m['archive']
 with archive.open('wb') as out:
  for item in m['parts']:
   with (ROOT/item['name']).open('rb') as f:
    for block in iter(lambda:f.read(1024*1024),b''):out.write(block)
 if sha(archive)!=m['archive_sha256']:raise RuntimeError('Invalid archive')
 dest=ROOT/'restored';dest.mkdir(exist_ok=True)
 with zipfile.ZipFile(archive) as z:
  if z.namelist()!=[m['model']] or z.testzip():raise RuntimeError('Unexpected archive payload')
  if (dest/m['model']).resolve().parent!=dest.resolve():raise RuntimeError('Unsafe model path')
  z.extractall(dest)
 if sha(dest/m['model'])!=m['model_sha256']:raise RuntimeError('Invalid restored model')
 print('Verified all parts, archive, and model:',dest/m['model'])
if __name__=='__main__':main()
