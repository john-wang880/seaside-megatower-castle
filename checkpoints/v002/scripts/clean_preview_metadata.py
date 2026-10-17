"""Remove non-image PNG metadata without decoding or altering any image-data byte.

Usage: python clean_preview_metadata.py INPUT.png OUTPUT.png [REPORT.json]
All critical chunks and colour-management chunks are retained unchanged.
"""
import hashlib
import json
import os
import struct
import sys


def clean(source, output):
    raw=open(source,'rb').read()
    if raw[:8]!=b'\x89PNG\r\n\x1a\n': raise ValueError('Not a PNG file')
    pos=8; kept=[raw[:8]]; removed=[]; before=[]; after=[]
    while pos<len(raw):
        size=struct.unpack('>I',raw[pos:pos+4])[0]
        kind=raw[pos+4:pos+8]; end=pos+12+size
        chunk=raw[pos:end]
        if end>len(raw): raise ValueError('Truncated PNG chunk')
        if kind==b'IDAT': before.append(raw[pos+8:pos+8+size])
        if kind in [b'tEXt',b'zTXt',b'iTXt',b'eXIf']:
            removed.append(kind.decode('ascii'))
        else:
            kept.append(chunk)
            if kind==b'IDAT': after.append(raw[pos+8:pos+8+size])
        pos=end
    if pos!=len(raw): raise ValueError('Unexpected PNG tail')
    image_hash=hashlib.sha256(b''.join(before)).hexdigest()
    if image_hash!=hashlib.sha256(b''.join(after)).hexdigest():
        raise RuntimeError('Compressed image data changed')
    data=b''.join(kept)
    os.makedirs(os.path.dirname(os.path.abspath(output)),exist_ok=True)
    temp=output+'.metadata-clean.tmp'
    with open(temp,'wb') as f:f.write(data)
    os.replace(temp,output)
    return {'source_filename':os.path.basename(source),'output_filename':os.path.basename(output),
            'removed_chunk_types':removed,'image_data_unchanged':True,'idat_sha256':image_hash,
            'output_sha256':hashlib.sha256(data).hexdigest(),'output_bytes':len(data)}


if __name__=='__main__':
    result=clean(sys.argv[1],sys.argv[2])
    if len(sys.argv)>3:
        with open(sys.argv[3],'w') as f:json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))
