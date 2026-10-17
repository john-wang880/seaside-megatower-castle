#!/usr/bin/env python3
"""Reconstruct and verify the public seaside castle v002 checkpoint using Python 3."""
from pathlib import Path
import hashlib
import json
import zipfile

CONFIG = json.loads('{"archive": "seaside-castle-v002.zip", "sha256": "6d2ccae9a36039a64ad74abf61ce01da5e50a547f7c19631b012a1f7b7385a85", "parts": [{"name": "seaside-castle-v002.zip.part001", "size": 10485760, "sha256": "acf43e3e55ab4aa89e20c6cf1333d8b7474a04398892b27a48a143470803bf51"}, {"name": "seaside-castle-v002.zip.part002", "size": 10485760, "sha256": "fb65e479204743535af6bb8a147c6c0bc126cad51a3df7d55b51aa9834b93427"}, {"name": "seaside-castle-v002.zip.part003", "size": 1869760, "sha256": "dc8ce0b4b527cd10a33087b10e06ed0880b6078bfdf96f4d1cadcc10c24e18e5"}]}')
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
    print("Open restored/海边巨塔城堡_v002_塔冠与岩岸.blend in Blender 5.2.2 LTS or newer.")

if __name__ == "__main__":
    main()
