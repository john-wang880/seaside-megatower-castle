#!/usr/bin/env python3
"""Restore byte-exact Blender bytes from content-addressed chunks; standard Python only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def restore(checkpoint, repository_root, output=None):
    checkpoint, repository_root = Path(checkpoint), Path(repository_root)
    m = json.loads((checkpoint / 'MANIFEST.json').read_text(encoding='utf-8'))
    if m.get('format') != 'blend-zstd-frames-v1' or m.get('chunk_directory') != 'model_chunks':
        raise ValueError('Unsupported manifest format or chunk directory')
    name = m['model']
    if not name or name in ('.', '..') or Path(name).name != name or any(c in name for c in '/\\:\0'):
        raise ValueError('Unsafe model filename')
    if not re.fullmatch('[0-9a-f]{64}', m['model_sha256']):
        raise ValueError('Invalid model checksum')
    entries = m['chunks']
    if not entries or sum(e['bytes'] for e in entries) != m['model_bytes']:
        raise ValueError('Invalid model size')
    for e in entries:
        if not re.fullmatch('[0-9a-f]{64}', e['sha256']) or type(e['bytes']) is not int or e['bytes'] <= 0:
            raise ValueError('Invalid chunk entry')
    destination = Path(output) if output else checkpoint / 'restored' / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix='.restore-', delete=False) as target:
            temporary = Path(target.name)
            h = hashlib.sha256()
            for e in entries:
                path = repository_root / 'model_chunks' / (e['sha256'] + '.bin')
                chunk = path.read_bytes()
                if len(chunk) != e['bytes'] or hashlib.sha256(chunk).hexdigest() != e['sha256']:
                    raise ValueError('Missing/corrupt chunk: ' + e['sha256'])
                target.write(chunk)
                h.update(chunk)
        if h.hexdigest() != m['model_sha256']:
            raise ValueError('Reconstructed model checksum mismatch')
        if destination.exists():
            if file_sha(destination) != m['model_sha256']:
                raise FileExistsError('Output contains different data; choose a new --output path')
            temporary.unlink()
        else:
            os.replace(temporary, destination)
        temporary = None
        return destination
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository-root', type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    print('Verified and restored:', restore(Path(__file__).resolve().parent, args.repository_root, args.output))


if __name__ == '__main__':
    main()
