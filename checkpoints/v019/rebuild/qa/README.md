# Standalone regeneration QA adapter (new, opt-in)

This directory does not modify the frozen historical validators or accepted model. Run with Blender 5.2.3, `-b --disable-autoexec --python-exit-code 1 --python SCRIPT -- ARGS`; do not use optimized Python (`-O`). All paths are explicit; the fold audit loads its sibling geometry validator, not a historical work directory.

`validate_preservation.py` requires:
- `--baseline`: restored historical v018, exact SHA c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd.
- `--accepted-model`: public restored v019, exact SHA e71778349c4c65eafbda3eb0a3d0753cd11e1b368a3456c4de1db2f4c0f8647a.
- `--checkpoint`: accepted or freshly integrated model being checked.
- `--asset`: newly regenerated standalone asset; `--asset-sha256`: its explicit measured byte identity.
- `--source-components`: public v019 reproduction/source_components.json.
- `--report`: a new output JSON path.

The runtime asset hash alone is NOT acceptance. Full expected mesh snapshots are independently derived from the pinned accepted model, including all attributes, coordinate/topology arrays, corner normals, material indices, smoothing, UVs, weights, shape keys, and custom mesh properties. Generated counterpart transforms must be identity, with no modifiers/parents/constraints/animation/groups. Referenced material properties and node graphs must exactly match accepted materials. Expected/actual semantic hashes are recorded before original scene preservation checks proceed.

`validate_new_geometry.py` and `audit_tube_folds.py` require `--candidate --mapping --route-report --report`. Decode the public component mapping gzip with CRC validation. These tests retain the explicitly bounded original open-trunk section-envelope interpretation and the strict nonadjacent triangle-crossing scope; they do not imply structural certification or closed needle leaves.

`test_negative.py` adds `--validator` and `--control`: asset_vertex, asset_material, asset_transform, wrong_mask_vertex, hidden_original. It mutates only in-memory data and requires rejection at the intended invariant, preserving all input files. Use separate fresh Blender processes and report paths.

Generation must depend only on restored v018 plus the portable generator recipe. Accepted v019 is a comparison oracle, not a source for extracting replacement geometry during generation. Historical private standalone641 is neither required nor treated as the new asset identity.
