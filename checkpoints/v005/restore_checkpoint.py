#!/usr/bin/env python3
"""Reconstruct and verify the public seaside castle v005 checkpoint using Python 3."""
from pathlib import Path
import hashlib
import json
import zipfile

CONFIG = json.loads('{"archive": "seaside-castle-v005.zip", "sha256": "138ddeb4e6ac6265db2bbf94f851c7437bbf3fee61281d806951c7e0ff11b3ce", "parts": [{"name": "seaside-castle-v005.zip.part001", "size": 10485760, "sha256": "382cebe663898f8debb177f2faf2226cce7505f36d1abed390478e02df82e700"}, {"name": "seaside-castle-v005.zip.part002", "size": 10485760, "sha256": "5c54a3f61f4b1aa0cdf9a0782e06279ed37c9c93c94ed0db568f8040fed847a4"}, {"name": "seaside-castle-v005.zip.part003", "size": 3535031, "sha256": "180178cb82c8ebe76d17311f2476b1e7852ff91a40876d0e3515ed2108d9ec5a"}]}')
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
    print("Open restored/海边巨塔城堡_v005_双塔石砌校准.blend in Blender 5.2.2 LTS or newer.")

if __name__ == "__main__":
    main()
