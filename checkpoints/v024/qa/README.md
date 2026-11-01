# Independent v024 six-solid rear-surface QA

Read-only inspection of a restored/rebuilt model. **No render, model save, network access or software installation.** The model source remains the accepted v023 file, SHA `c4b1dda3b8f70e4c8cb0171834b2150b6d7610f6296847362fd204b2dfa7ad51`. It is recoverable from historical Git commit `389770297a21ef2401917e83807e0122711b8df9` using that checkpoint's restore instructions. The reviewed v024 candidate SHA is `89f9f6a8a57103d99100935b96624469ddf1fd52b9703e0d9177a352e735c856`.

All runtime helpers are adjacent to this README. Archived reports contain original execution paths as provenance only; those directories and intermediate models are not dependencies.

## Run

Use a compatible existing Blender executable (actual tests used official Blender 5.2.3). Restore source and candidate first, then:

```sh
python -B run_qa.py \
  --source '/absolute/historical/castle_v023.blend' \
  --candidate '/absolute/restored/castle_v024.blend' \
  --output-dir '/absolute/existing-parent/new QA reports' \
  --blender '/absolute/blender'
```

The output directory must not exist and must be outside the QA/checkpoint trees. Symlinks, parent traversal, wrong source identity, altered/extra bundle files and optimized Python are refused. Inputs are never overwritten. Every Blender command explicitly disables autoexec, sets Python exception exit status, and sets `sys.dont_write_bytecode=True` before loading the script. The runner verifies full bundle inventory and all input hashes again at completion; failed evidence is retained for diagnosis.

For a separately saved rebuild, add `--accepted '/absolute/restored/castle_v024.blend'`. The accepted reference must have the pinned SHA above. A full persistent/evaluated semantic comparison runs **first**, before the rebuilt file's SHA is admitted to the geometry chain. Different save bytes alone are not failure, but any semantic drift is. Do not substitute an arbitrary model with a caller-provided hash to bypass this gate.

Successful completion writes `SUMMARY.json`. Inspect its `pass` and referenced JSON gates, not just process exit. Normal chain: five Blender calls (preservation/export, two actual in-memory negative fixtures, native LOW rollback, adjacent surfaces), three Python calls (boundary, five geometry negatives, six math controls). Rebuild adds one semantic-comparison Blender call.

## Scope and evidence

Only evaluated components 56/80/104/128/152/176 of `V008 | gallery with genuine eastern approach portal` are replaced. Raw vertices16–63 remain stored with exactly48 owned weight-1 assignments; the inverted Mask is **after** the unchanged original global clamped BEVEL. Every other raw/evaluated attribute and all earlier ownership states are preserved. The native LOW test disables the Mask and hides the new union; its144 inherited group values are compared bit-exactly to independent original-Bevel evaluation before removing only those owned weights for render-semantic comparison. Observed values were `0.9999999403953552` and `1.0`.

The new union is closed, consistently oriented and positive-volume. Its saved triangles are compared against an independently constructed union boundary: each actual original convex face is clipped by the other five solids' halfspaces; equal outward coplanar faces receive one owner. Both-direction oriented area coverage and signed volume are checked. This is not a finite-ray occupied-volume assertion or a bounding-box test. Original bevelled planes and concave outline remain represented.

Coordinate tolerance is declared **before residual measurement**: four maximum float32 coordinate ULPs, `3.0517578125e-5` in this source. Per-face area budget is `4*perimeter*distance_budget + 16*distance_budget²`; volume budget is `2*saved_surface_area*distance_budget`. Reports expose full residuals, fractions, maxima and budgets. Actual accepted run: both areas4386.297369691864, coverage residuals2.56e-11/7.70e-11, volume difference−5.46e-12, maximum matched plane displacement1.42e-14. These are numerical results, not exact-rational claims.

Adjacent audit uses evaluated object bounds before culling, then triangle BVH broadphase and actual oriented coplanar polygon clipping across all render-visible surface meshes intersecting the complete union bounds. Actual run inspected14 objects and found no positive-area coplanar contacts with the new union. Same-facing skins and opposite-facing interfaces are distinguished, not broadly waived. Other20 components/four rear groups remain deliberately deferred; this is not complete rear/global structural or navigation certification.

Only the established three Traveler SUBSURF objects' **derived evaluated edge-selection UI metadata** are normalized by the snapshot helper. Their raw selections and all actual geometry/material/other attributes remain strict. No broad visual or numeric geometry tolerance applies to source preservation.

## Controls

- Five **exported actual-geometry** negatives: translated surface, missing triangle, duplicated triangle, reversed orientation, and replacing the six chamfered solids with their raw box union. The last preserves coarse envelope but loses chamfers; it is rejected by388 coverage failures. These do not modify/save Blender models.
- Two **actual Blender in-memory** negatives: extra owned Mask weight; unrelated hidden-original vertex mutation. They must fail the intended preservation invariant, not setup.
- Six pure convex-partition controls: single, overlapping, contained, touching, identical and concave-L unions.
- `python -B test_runner.py`:13 pure orchestration guards using temporary fixtures/mocks. Linux paths with spaces/Unicode and symlink refusal tested; no native Windows or desktop GUI claim.

`reports/native_control_initial.log` and `reports/rollback_initial.log` are **superseded validator setup failures**, not candidate geometry failures. The first used an active single-Mask control despite preserving BEVEL as active; the second incorrectly assumed every Bevel-interpolated weight was exactly1. Final explicit native-state and independently propagated weight comparisons passed without modifying the model or relaxing geometric checks.
