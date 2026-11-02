# v029 source-only model rebuild

Restore exact v028 source f0d135 from fixed Git commit f3f56c21c97c9a76c79050c709790611681ae2b8. This recipe creates a NEW candidate and never saves source; Blender5.2.3 and Python3 required, no installation or automatic execution.

```sh
python -B rebuild_model.py --blender /absolute/blender --source /absolute/castle_v028.blend --output-dir /absolute/new-output
```

Geometry payload is byte-exact ea64d1…; compressed native saves may have different bytes. Independently validate rebuilt output with ../qa/run_qa.py and exact accepted4f838529… via --accepted. Clean isolated Linux replay passes; no Windows execution claim. No overwrite/symlink/optimized Python, fixed original lights plus two36-power room copies. Runtime files and source input hashes are pinned.

962 architecture triangles preserve268 remote face cycles and11 affected domains;1160 fixture triangles,2122 combined. Directed guard-only bottom28.900001525878906 avoids a native rounding collapse; cavity/floor unchanged. This is not engineering or global access certification.
