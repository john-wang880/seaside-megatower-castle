#!/usr/bin/env python3
"""Reconstruct and verify the public seaside castle v003 checkpoint using Python 3."""
from pathlib import Path
import hashlib
import json
import zipfile

CONFIG = json.loads('{"archive": "seaside-castle-v003.zip", "sha256": "76696ef3d7e8042241b7806288d997ee8795ee533053ac29778f79c6f0e7bb9f", "parts": [{"name": "seaside-castle-v003.zip.part001", "size": 10485760, "sha256": "d80ca9144a94f584a092d5e80e8b2199e788d418cee3131418d81a8b37899884"}, {"name": "seaside-castle-v003.zip.part002", "size": 10485760, "sha256": "8685ae91fcf76afaf328113b052a8b1fc908e208d74e15ab4a88dd1a854514d3"}, {"name": "seaside-castle-v003.zip.part003", "size": 2136102, "sha256": "190e0125c1ca7eb005033df51ebcd0427843cbebfffee6ba278c808eec1fabf4"}]}')
ROOT = Path(__file__).resolve().parent

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main():
    archive = ROOT / CONFIG["archive"]
    for part in CONFIG["parts"]:
        source = ROOT / part["name"]
        if source.stat().st_size != part["size"] or digest(source) != part["sha256"]:
            raise RuntimeError("Archive part checksum mismatch: " + part["name"])
    with archive.open("wb") as output:
        for part in CONFIG["parts"]:
            with (ROOT / part["name"]).open("rb") as source:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    output.write(block)
    if digest(archive) != CONFIG["sha256"]:
        raise RuntimeError("Reconstructed ZIP checksum mismatch")
    destination = ROOT / "restored"
    destination.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise RuntimeError("ZIP integrity test failed")
        for item in bundle.infolist():
            resolved = (destination / item.filename).resolve()
            if destination.resolve() not in resolved.parents:
                raise RuntimeError("Unsafe archive path")
        bundle.extractall(destination)
    for line in (destination / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        expected, name = line.split("  ", 1)
        if digest(destination / name) != expected:
            raise RuntimeError("Extracted file checksum mismatch: " + name)
    print("Verified: archive parts, complete ZIP, and all extracted payload files.")
    print("Open restored/海边巨塔城堡_v003_双塔样板窗洞.blend in Blender 5.2.2 LTS or newer.")

if __name__ == "__main__":
    main()
