# Reproduce v030

1. Restore exact v029 source from fixed commit `d753ba032b1d3138a1d0c34e13b0caee40b3d92f` in a separate archive.
2. Follow `reproduce/README.md` to run the explicit source-pinned additive builder with existing Blender 5.2.3, using new outputs.
3. Follow `qa/README.md` and supply the independently restored accepted model via `--accepted` when validating a new serialization.
4. Use the current reviewed manual inspection-copy tool only after its source hash matches. No model auto-exec, source overwrite or automatic render is used.

Local native geometry and saved repeat passed. Portable isolated full replay passed; fresh remote rebuild and complete replay also passed, recorded in reports/remote/VERIFIED.json.
