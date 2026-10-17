#!/usr/bin/env python3
"""Reconstruct and verify the public seaside castle v004 checkpoint using Python 3."""
from pathlib import Path
import hashlib
import json
import zipfile

CONFIG = json.loads('{"archive": "seaside-castle-v004.zip", "sha256": "f2fb3dc2c7a7b5f4e4c67a11600bcf8f9a1ce6196384d0913c144c57bb2c941d", "parts": [{"name": "seaside-castle-v004.zip.part001", "size": 10485760, "sha256": "31b150c1baa78751e0d45bf316f86552cee1960c45068f7988cde1f78016fb07"}, {"name": "seaside-castle-v004.zip.part002", "size": 10485760, "sha256": "dc130ee4397d663eaf457ded01448962753a818756e8ba741b5c7f1b84af8829"}, {"name": "seaside-castle-v004.zip.part003", "size": 3472797, "sha256": "e2558028ed3fe50b8fc936aed16fbc1398338b36c17e1cf99b7d0f4d5fecdc0a"}]}')
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
    print("Open restored/海边巨塔城堡_v004_双塔层级窗群.blend in Blender 5.2.2 LTS or newer.")

if __name__ == "__main__":
    main()
