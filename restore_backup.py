#!/usr/bin/env python3
"""Reconstruct and verify the public seaside castle baseline using Python 3."""
from pathlib import Path
import hashlib
import json
import zipfile

CONFIG = json.loads('{"archive": "海边巨塔城堡_公开恢复包.zip", "sha256": "64a394e5fd9e610002602be56f867acf872a8bb23ad590c1fa87496b6d71ca91", "parts": [{"name": "海边巨塔城堡_公开恢复包.zip.part001", "sha256": "93bd7095035e3290fce3f8f4b1ab92c327379beaa740e46e81b1cdbc0b83674e", "size": 10485760}, {"name": "海边巨塔城堡_公开恢复包.zip.part002", "sha256": "e45cfce60340f089a289119a273e2f131431f938159b8cd0eec426a5e2446a28", "size": 8702777}]}')
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
    print("Open restored/海边巨塔城堡_Dots轻量版.blend in Blender 5.2.2 LTS or newer.")

if __name__ == "__main__":
    main()
