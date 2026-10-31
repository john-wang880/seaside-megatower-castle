#!/usr/bin/env python3
"""Byte-exact content-addressed backup of a seekable-Zstd compressed .blend.

Only standard Python is needed. No decompression/recompression occurs.
Seek-table specification: https://github.com/meta/zstd/blob/dev/contrib/seekable_format/zstd_seekable_compression_format.md
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def digest(data):
    return hashlib.sha256(data).hexdigest()


def split_seekable(data):
    """Return exact stored frames and original seek table, validated structurally."""
    if len(data) < 17:
        raise ValueError('Input is too short for a seekable Zstd stream')
    count, descriptor, magic = struct.unpack('<IBI', data[-9:])
    if magic != 0x8F92EAB1 or descriptor & 0x7C:
        raise ValueError('Unsupported or invalid seekable Zstd footer')
    width = 12 if descriptor & 0x80 else 8
    table_size = count * width + 9
    table_start = len(data) - table_size - 8
    if count == 0 or table_start < 0:
        raise ValueError('Invalid frame count or seek-table size')
    if struct.unpack('<II', data[table_start:table_start+8]) != (0x184D2A5E, table_size):
        raise ValueError('Seek-table header does not match footer')
    offset = 0
    chunks = []
    for i in range(count):
        size, _ = struct.unpack_from('<II', data, table_start + 8 + i * width)
        if size < 4 or offset + size > table_start:
            raise ValueError('Frame size extends outside the data region')
        frame = data[offset:offset+size]
        marker = int.from_bytes(frame[:4], 'little')
        if marker != 0xFD2FB528 and not 0x184D2A50 <= marker <= 0x184D2A5F:
            raise ValueError('Invalid frame marker at indexed offset')
        chunks.append(frame)
        offset += size
    if offset != table_start:
        raise ValueError('Frame sizes do not cover the complete data region')
    chunks.append(data[table_start:])
    return chunks


def package(model, checkpoint, repository_root, baseline=None):
    model, checkpoint, repository_root = Path(model), Path(checkpoint), Path(repository_root)
    data = model.read_bytes()
    chunks = split_seekable(data)
    directory = repository_root / 'model_chunks'
    directory.mkdir(parents=True, exist_ok=True)
    checkpoint.mkdir(parents=True, exist_ok=True)
    entries = []
    new_bytes = 0
    for chunk in chunks:
        sha = digest(chunk)
        path = directory / (sha + '.bin')
        if path.exists():
            if path.read_bytes() != chunk:
                raise ValueError('Existing content-addressed chunk is corrupt: ' + sha)
        else:
            path.write_bytes(chunk)
            new_bytes += len(chunk)
        entries.append({'sha256': sha, 'bytes': len(chunk)})
    manifest = {'format': 'blend-zstd-frames-v1', 'model': model.name,
                'model_sha256': digest(data), 'model_bytes': len(data),
                'chunk_directory': 'model_chunks', 'chunks': entries}
    if baseline is not None:
        manifest['baseline'] = baseline
    (checkpoint / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return {'model_bytes': len(data), 'chunk_references': len(entries),
            'unique_chunks': len({x['sha256'] for x in entries}), 'new_chunk_bytes': new_bytes,
            'model_sha256': manifest['model_sha256']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model', required=True)
    p.add_argument('--checkpoint', required=True)
    p.add_argument('--repository-root', default='.')
    p.add_argument('--baseline-manifest')
    args = p.parse_args()
    baseline = None
    if args.baseline_manifest:
        old = json.loads(Path(args.baseline_manifest).read_text(encoding='utf-8'))
        baseline = {'model': old['model'], 'model_sha256': old['model_sha256']}
    print(json.dumps(package(args.model, args.checkpoint, args.repository_root, baseline), indent=2))


if __name__ == '__main__':
    main()
