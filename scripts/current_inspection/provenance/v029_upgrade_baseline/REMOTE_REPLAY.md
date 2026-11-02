# Current optional editing-index replay

Use **four** freshly exported inspection copies and **`qa/edit_index/run_qa.py`**. The complete commands are in [EDIT_INDEX_REPLAY.md](EDIT_INDEX_REPLAY.md):

1. `default`: no `--editing-index`, no tree option.
2. `off`: `--editing-index`, no tree option.
3. `high`: `--editing-index --tree-mode HIGH`.
4. `low`: `--editing-index --tree-mode LOW`.

All use the byte-exact canonical v028 model SHA256 `f0d135e0c6e554b5ae7c520ef9ccefc61e2a7c4abc3129eef1d3d4118bca8096`, the current real manifest, a fresh output path and the existing reviewed Blender 5.2.3 executable. No render or automatic Text execution occurs. Independent QA also uses the original-tree v018 model `c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd` restored from fixed Git `89cce41edf648eef6487d54ee1ce2a46bbb0ae17`.

The current QA runner requires all four model paths/receipts, source, baseline, tool, Blender and a fresh output directory. It checks the current runtime, panel provenance guard, transactional selection, all 18 bookmarks, optional quality controls and source preservation. Successful saved copies alone are not independent acceptance.

## Historical paths retained, not current acceptance

`qa/run_qa.py`, its helper files and `qa/reports/` remain unmodified historical **pre-index** evidence. They do not validate the current index runtime or its four-copy workflow. To reproduce that earlier tool, use the complete historical repository at fixed Git **`44a6e7b`**, including that version's tool/runtime, rather than mixing the old validator with the new runtime. Existing root export reports likewise retain their original bindings; current reports are explicitly under `reports/edit_index/` and `qa/edit_index/`.

Model v028 and all 18 camera records are unchanged. Native Windows/desktop click workflows are untested. Selection index provenance does not certify manual edits or migrate edited work into a fresh copy.
