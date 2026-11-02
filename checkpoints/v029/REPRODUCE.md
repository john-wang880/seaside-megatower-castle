# Reproduce v029

1. Restore byte-exact v028 source from fixed commit `f3f56c21c97c9a76c79050c709790611681ae2b8` in a separate clone/archive; use its checkpoint restore script. Do not rewrite the current checkout to obtain historical inputs.
2. Run `reproduce/rebuild_model.py` with existing Blender5.2.3, exact sourcef0d135…, and a NEW output directory.
3. Run `qa/run_qa.py` on rebuilt output, supplying the restored accepted4f838529… via `--accepted`. This validates complete semantics before geometry/source preservation checks. See each README for exact CLI.
4. Optional inspection copy is separate and manual-only. It never changes the canonical model; the latest reviewed catalog must match. Unknown future versions fail closed.

Original-light visual recipes in `reports/visual/` pin the accepted model hash and exact camera/quality settings. Rendering is optional and explicit; no script automatically renders on opening a .blend. Historical videos retain their original model provenance.

Local clean native rebuild and portableQA passed. Fresh remote source-only rebuild and complete QA replay passed from additive commit1a53001a84c3edc375ffe4089619ee1e480fa28e; see reports/remote/VERIFIED.json.
