#!/usr/bin/env python3
"""Reconstruct and verify the public seaside castle v006 checkpoint using Python 3."""
from pathlib import Path
import hashlib
import json
import zipfile

CONFIG = json.loads('{"archive": "seaside-castle-v006.zip", "sha256": "e139578ff5d0e129f13f8b876e61485589999430f1ea3156d4f0eb4ed0d52c94", "parts": [{"name": "seaside-castle-v006.zip.part001", "size": 10485760, "sha256": "fc1aab2fe6d434e00add8cea6ec62b03734567b4a169f2b7bb49f31ecb84dd09"}, {"name": "seaside-castle-v006.zip.part002", "size": 10485760, "sha256": "764d2a00c58c112912d3dc0372cec80db8d9a4229e6869b583abc0b6b4f2cffb"}, {"name": "seaside-castle-v006.zip.part003", "size": 4384405, "sha256": "c7328fd2ae965d532d633d123117fb60d1e85a0b15322e8febcde2f5902a9f6a"}]}')
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
    print("Open restored/海边巨塔城堡_v006_局部石肋分块样板.blend in Blender 5.2.2 LTS or newer.")

if __name__ == "__main__":
    main()
