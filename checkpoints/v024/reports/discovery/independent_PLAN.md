# Independent rear-return surface gate

Source v023 c4b1dda3…ad51 was opened with autoexec disabled, inspected without save/render, and its hash remained exact. `inspect.py` and `independent.json` contain actual raw/evaluated component mappings and material links. Independent rectangle intersection calculation reproduces all 40 mapper polygon-clipping patches (within 1e-9 area). This proves duplicate same-facing surfaces, not original artistic intent or structural support.

## Smallest coherent first scope

Choose only the six solids at rear plane Y=65.5: evaluated seeds 56,80,104,128,152,176; raw seeds 16,24,32,40,48,56. These form one overlap-connected group with eight patches, all eight centroid rays camera-exposed in the mapper's finite evidence. Four other groups account for 32 patches and remain deferred, not silently included. A coherent six-piece union removes the connected stepped-return duplicate skins without mixing in four separate framed-gallery assemblies. No claim that this fixes every black region in the overview.

Raw pieces are eight-corner boxes, but their actual visible geometry is NOT their bounding box. Each evaluated piece has 24 vertices/26 faces and a closed edge graph. Existing BEVEL width .065, one segment, ANGLE limit, clamp-overlap enabled produces much smaller effective chamfers. Do not rebuild a bounding-box union or apply BEVEL again to the union. Both would change exterior occupied geometry. All six use material slot 0, shared `Citadel • aged gallery grey`; its procedural coordinates come from Geometry Position, not per-object Generated bounds. Object transform is recorded.

## Reversible construction proposal, conditional on native evaluation test

Preserve original raw mesh and existing BEVEL unchanged. Add uniquely owned weight-1 group covering exactly the 48 raw vertices above, and an inverted Mask AFTER the existing BEVEL. Before accepting this method, prove native evaluated complement deletes exactly the corresponding six 24-vertex solids, with every other evaluated attribute/position unchanged; generated bevel vertices must inherit the intended weights. Existing object currently has no groups. If this fails, stop and design a separately reviewed replacement strategy rather than moving Mask before BEVEL, where global clamp behavior may drift.

Union only the six frozen evaluated solids, retaining their precise chamfer surface and material; no new bevel, fill-to-box, normal recalculation blanket, smoothing change or geometry projection. New object identity/world coordinate mapping must reproduce source. Exact Boolean is a candidate constructor, NOT by itself acceptance proof.

## Required candidate evidence

1. Strict raw/deep source preservation except exact owned weights/Mask/new mesh/object/collection; all earlier v019–v023 modifiers, raw deform weights and hidden originals remain exact. Existing BEVEL settings/order remain exact.
2. Closed, oriented, non-self-intersecting saved union; validate against actual evaluated input, not AABBs. Prove occupied-set equivalence using clipped boundary coverage plus containment of resulting cells/vertices and both-direction Boolean residuals with numerical limits derived from float32 coordinates. Volume equality alone is insufficient. Maintain all actual chamfers and exposed boundary planes, not merely overall min/max bounds.
3. Every newly exposed surface must lie on an original selected solid's exterior boundary; interiors formerly overlapped may be removed. Prove actual union leaves genuine voids/openings unchanged. Exact occupied-set equivalence establishes unchanged intrusion/route volume within this scope; it is not a new full-route certification.
4. Scan all saved union planes against relevant visible adjacent geometry, not only +Y. Distinguish exposed same-facing duplicates from buried interfaces and opposite-facing support contacts; do not broadly whitelist other gallery pieces. All selected positive-area +Y duplicates must be gone. Other four groups explicitly remain out of scope.
5. Paired rollback (Mask disabled/new union hidden) and repeated enabled state, original scene semantics exact. Actual same-camera image confirms black skin removal without loss of chamfer highlights or openings.

Negative controls: enlarge a union face; fill a genuine outside concavity; remove a chamfer; change mask weight or move Mask before BEVEL; change material; mutate unrelated hidden source. Each must fail its intended geometric/preservation invariant, not setup failure. No candidate was built by this read-only audit.
