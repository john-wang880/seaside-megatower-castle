import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
pack = load('pack', ROOT/'scripts/package_checkpoint.py')
restore = load('restore', sorted((ROOT/'checkpoints').glob('*/restore_checkpoint.py'))[-1])

def stream():
    # Valid single-segment Zstd frames with one raw block, followed by seek table.
    chunks = []
    for text in (b'castle', b'bridge', b'castle'):
        chunks.append(b'\x28\xb5\x2f\xfd\x20'+bytes([len(text)])+
                      ((len(text)<<3)|1).to_bytes(3,'little')+text)
    entries = b''.join(struct.pack('<II',len(c),6) for c in chunks)
    footer = struct.pack('<IBI',len(chunks),0,0x8F92EAB1)
    return b''.join(chunks)+struct.pack('<II',0x184D2A5E,len(entries)+9)+entries+footer

class CheckpointStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.cp = self.root/'checkpoints'/'v008'
        self.model = self.root/'castle.blend'
        self.model.write_bytes(stream())
        self.stats = pack.package(self.model,self.cp,self.root)
    def tearDown(self):
        self.temp.cleanup()
    def manifest(self):
        return json.loads((self.cp/'MANIFEST.json').read_text())
    def test_byte_exact_roundtrip_and_duplicate_chunk_reuse(self):
        output=restore.restore(self.cp,self.root)
        self.assertEqual(output.read_bytes(),self.model.read_bytes())
        self.assertLess(self.stats['unique_chunks'],self.stats['chunk_references'])
        self.assertEqual(pack.package(self.model,self.cp,self.root)['new_chunk_bytes'],0)
    def test_corrupt_chunk_does_not_replace_existing_output(self):
        out=self.root/'existing.blend';out.write_bytes(b'untouched')
        h=self.manifest()['chunks'][0]['sha256']
        (self.root/'model_chunks'/(h+'.bin')).write_bytes(b'corrupt')
        with self.assertRaises(ValueError):restore.restore(self.cp,self.root,out)
        self.assertEqual(out.read_bytes(),b'untouched')
        self.assertFalse(list(self.root.glob('.restore-*')))
    def test_missing_chunk_fails_without_output(self):
        h=self.manifest()['chunks'][0]['sha256'];(self.root/'model_chunks'/(h+'.bin')).unlink()
        out=self.root/'new.blend'
        with self.assertRaises(FileNotFoundError):restore.restore(self.cp,self.root,out)
        self.assertFalse(out.exists())
    def test_existing_different_model_is_not_overwritten(self):
        out=self.root/'existing.blend';out.write_bytes(b'work in progress')
        with self.assertRaises(FileExistsError):restore.restore(self.cp,self.root,out)
        self.assertEqual(out.read_bytes(),b'work in progress')
    def test_invalid_model_checksum_fails(self):
        m=self.manifest();m['model_sha256']='0'*64;(self.cp/'MANIFEST.json').write_text(json.dumps(m))
        with self.assertRaises(ValueError):restore.restore(self.cp,self.root)
    def test_path_traversal_rejected(self):
        for name in ('../outside.blend','..','x/y.blend','x\\y.blend','x:stream.blend'):
            m=self.manifest();m['model']=name;(self.cp/'MANIFEST.json').write_text(json.dumps(m))
            with self.assertRaises(ValueError):restore.restore(self.cp,self.root)
    def test_invalid_chunk_hash_rejected(self):
        m=self.manifest();m['chunks'][0]['sha256']='../outside';(self.cp/'MANIFEST.json').write_text(json.dumps(m))
        with self.assertRaises(ValueError):restore.restore(self.cp,self.root)
    def test_truncated_or_invalid_footer_rejected(self):
        for data in (b'',stream()[:-1],b'not a zstd model'):
            with self.assertRaises(ValueError):pack.split_seekable(data)
    def test_bad_index_size_rejected(self):
        data=bytearray(stream());table_start=len(data)-17-3*8
        struct.pack_into('<I',data,table_start+8,99999)
        with self.assertRaises(ValueError):pack.split_seekable(bytes(data))
    def test_reserved_descriptor_bits_rejected(self):
        data=bytearray(stream());data[-5]=4
        with self.assertRaises(ValueError):pack.split_seekable(bytes(data))

if __name__=='__main__':unittest.main()
