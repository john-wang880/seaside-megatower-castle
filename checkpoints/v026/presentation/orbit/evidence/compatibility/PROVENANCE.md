# Compatibility evidence, not a second renderer

`compatibility.py` is the byte-exact executed read-only audit source; it retains historical working-path spellings and is archived as provenance, not advertised as a standalone CLI. Its required helper is included byte-exact as `deep_snapshot.py`; its original two plan inputs are included as `historical_final_plan.json` and `historical_path_plan.json`. `HISTORICAL_INPUTS.json` pins all46 immutable historical files from Git9d417969…; the actual V016 model is separately restored from that history when replaying the audit. Current source is V026efcd from fixedGitb9015e….

The source-only proposed plan and final production plan differ by added lighting/projection guard fields only, not any96camera pose or quality/composition field. `recipe_comparison.json` records this. Production execution is self-contained under `recipe/`, with exact copied lighting helper named `lighting_snapshot.py`; no runtime import depends on the old work paths. The metadata file records helper and original audit hashes, and the snapshot digest proves current/historical world and lighting equality. Finite ray tests and framing reviews are not full image-visibility certification.

## Historical audit workspace mapping (not production dependencies)

To investigate/replay the exact archived `compatibility.py`, recreate its declared workspace inputs in a separate scratch root, or author a separately identified adapter; do not silently edit/relabel this executed script:

| Executed path | Archived input / restoration |
|---|---|
| `work/orbit_v026/historical/checkpoints/v016/presentation/orbit/final_plan.json` | `historical_final_plan.json` |
| `work/orbit_v026/historical/checkpoints/v016/presentation/orbit/path_plan.json` | `historical_path_plan.json` |
| `work/v023_path_conformance/scripts/deep_snapshot.py` | exact included `deep_snapshot.py` |
| `work/v026/castle_v026.blend` | restore exact efcd source from fixed b9015e58605c5a6d211bd7a977ad5fed542f8769 |

The audit's own output directory `work/orbit_v026` must be fresh for a replay; its additional source-history paths, if reached, are visible in the archived script and pinned by HISTORICAL_INPUTS. This mapping explains provenance, not a promise that invoking the unchanged file anywhere is portable. The actual render runner and lighting helper in `recipe/` are self-contained with explicit source/output arguments.
