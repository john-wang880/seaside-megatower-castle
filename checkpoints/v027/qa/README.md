# Independent read-only hall-bay QA

Source v026 SHA`efcd894acdc045a30f845f05267662957b656bc7fe0ee4cf48c05fc798b610ee`; accepted candidate reference SHA`37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255`. Rejected far-cliff study is not an input. This package never renders or saves a model.

```
PYTHONDONTWRITEBYTECODE=1 python -B run_qa.py \
 --source HISTORICAL_V026.blend --candidate CANDIDATE_OR_REBUILD.blend \
 --build-report ITS_BUILD_RECEIPT.json --blender BLENDER_5_2_3 \
 --output-dir NEW_EXTERNAL_DIRECTORY [--accepted EXACT_37C0_REFERENCE.blend]
```

For a newly saved rebuild, `--accepted` is mandatory and full persistent/evaluated semantic equality runs **first**; byte equality is not expected. Both builder receipts must reproduce the frozen authored-operand data, not merely match component counts. Source/candidate files and complete QA bundle inventory are hashed before/after. Outputs must be new and outside frozen checkpoint trees. Symlink/traversal/hardlink source aliases and optimized Python are refused. Native calls disable auto-execution, set `--python-exit-code1`, and explicitly set `sys.dont_write_bytecode=True` before loading QA. Use the sole authorized Blender slot; this runner does not police unrelated processes.

Accepted-byte chain: four native calls (source preservation/export, two in-memory source vertex/material negatives, bounded crown image-ray replay). Rebuilt-byte chain adds one initial native semantic comparison. Pure commands check actual saved topology/positive volume, explicit transverse/coplanar/tangent contacts, full adjacent closed-component separation, protected route/camera envelopes, six actual-geometry controls, eleven predicate controls plus two triangle-box controls. Native negatives must exit1 **and** write the expected changed-category report; setup errors are not passes. Inspect every JSON gate, not just process return codes.

## Scope and claims

- Twelve original snapshot categories remain exact. Only three previously identified Traveler SUBSURF evaluated UI edge-selection fields are separately recorded; raw attributes, material graphs, weights and old modifier chains are not waived.
- One added550-vertex/1104-triangle connected solid contains three curved grooved arches and two bands.29 independently checked interior witnesses cover three crowns, six heels, two band seats and eighteen backed joints; actual authored operands and saved union must both contain the witnesses. Scene-coordinate units are not calibrated physical metres or millimetres.
- Existing lining/ceiling hosts remain separate unchanged meshes. Positive contact is bounded geometric support, not structural-capacity/global manifold certification.
- Initial fourteen legacy triangle-AABB candidates were held, then resolved using explicit triangle-box SAT and closed-component containment; initial hold evidence is retained. No broad whitelist or geometry change was used.
- New additions are separated from archived central static body prisms and continuous camera eye/near-plane boxes; this preserves those bounded envelopes and does not re-certify whole-castle human accessibility or all dynamic motion.
- Crown-seam replay uses fixed pixel centers from the actual accepted +8° inspection image, its exact camera and archived receipt. On a rebuild it runs only after complete semantic equality.27 of36 sample rays hit intact ceiling and nine new arch geometry; intentional haunch airspace is not a missing roof. All three crowns have finite positive ceiling seating. Nearby light-center occlusions support shadows, but do not reproduce all Cycles lighting, texture, antialiasing or denoising effects.
- This is inspectable3D architecture. It does **not** claim the earlier downward walkingframes1–76 now show a successful ceiling cadence. Actual visual acceptance is separate from technical QA.

`evidence/` contains original completed technical reports and the initial broadphase hold. Public adapter edits are path/CLI/orchestration changes; original reports bind their original executed script hashes. The adapted native chain must be rerun on fresh Git-only rebuild inputs before its publication acceptance. Pure tests alone do not establish that replay. No full scene snapshot or private workspace import is needed; source/candidate/receipt are explicit external inputs.
