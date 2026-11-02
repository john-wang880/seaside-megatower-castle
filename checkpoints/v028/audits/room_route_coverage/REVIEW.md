# v028 intended room-route coverage review

**Conclusion: no new floor-support defect or missing intended-lane body test found. No new native job, render, geometry change, or repeat of the full QA is warranted.** This is a review of frozen continuous geometry evidence, not a new claim of full-floor accessibility.

## Complete intended network already checked

Every box below is swept continuously, not sampled along its centerline. Body width is 1.2, vertical interval **29.025–31.1** (scene coordinate units).

| Lane | Full XY swept footprint |
|---|---|
| Entry shift | X 3.85–5.05, Y 36.9–38.6 |
| Entry east / doorway | X 3.85–8.2, Y 36.9–38.1 |
| Central | X 7–14.4, Y 36.9–38.1 |
| West aisle | X 8.6–9.8, Y 32.7–40.3 |
| East aisle | X 13.2–14.4, Y 32.7–40.3 |
| South cross-aisle | X 8.6–14.4, Y 32.7–33.9 |
| North cross-aisle | X 8.6–14.4, Y 39.1–40.3 |

Entry shift overlaps entry east; entry east overlaps central. Central crosses both longitudinal aisles; each longitudinal aisle intersects both cross-aisles. Thus the intended south and north side-bay lanes connect continuously through the chamber and existing doorway. This does not cover every point between lane footprints, wall margins, or the retained pier footprints.

`checkpoints/v028/reports/remote/model_qa/saved_routes.json` records actual triangle-versus-box SAT and closed-solid containment for **30 architectural/source components** against all seven boxes plus four camera proxies. `saved_fixtures_final.json` independently checks all **20 new fixture components** against all eleven boxes. These are broader than the entry/camera tests alone. The source proof/export excludes no render-enabled viewport-hidden object or instance in the bounded neighborhood.

## Floor continuity is supplied by separate existing boundary proof

The body boxes intentionally omit the 0.025 foot-contact slice; their disjointness alone would not prove a floor. The required floor evidence is instead:

1. The preserved `V012 | entrance hall limestone floor` is an actual eight-corner, six-face closed box, not an inferred AABB. Its top is exactly Z=29 and east endpoint X=5.400000095367432; its Y extent 36.599998474121094–39.400001525878906 covers both old-entry footprints up to that endpoint. Its raw/evaluated geometry is unchanged.
2. The local shell floor and threshold are part of the **entire oriented boundary**, not isolated support samples. `native_tessellation.json` verifies the saved shell against independently quantized occupied cells: zero uncovered, outside, or multiply-covered area on all 34 oriented planes, including Z=29. The reference is the actual three-source union plus the approved sleeve, minus the common room/door cavity with retained piers/band. The 948 quantized cells (1038 nominal planning cells) are boundary-aligned uniform cells, not a finite sampling approximation.
3. The common room/door bottom is Z=29. The quantized doorway begins at the same X=5.400000095367432 as the unchanged old floor endpoint. There is no nominal-5.4 versus float32 endpoint crack. The sleeve fills the old X=5.5…5.550000190734863 interval before the common cut; no independent overlapping floor panel was added.
4. `outside_final.json` preserves 112 remote polygons and all eight clipped source domains/caps; `guard_partition_proof.json` records **no changed guard-interface cells**. `local_neighbors_with_interfaces.json` explicitly finds opposite-facing contact with the old floor at that shared X plane. Its pairwise contact-area sum is not treated as unique support area.
5. `saved_seats.json` retains the positive threshold-to-foundation witness and other seats. Those finite witnesses establish connection; they are **not** substituted for the full floor boundary proof above.

As a read-only diagnostic of the existing export, the saved local shell has 28 upward loop triangles at Z=29, area 64.96000169754188. This area is not used alone to infer coverage: the existing separate uncovered/multiple/outside-area proof is essential. It corresponds to the room floor excluding retained pier bases plus the doorway floor, at saved float32 coordinates.

## Exact accepted-model linkage

The public remote reports concern rebuilt bytes `1efa55bc…224d8`. `repeat.json` proves all twelve persistent/evaluated semantic categories equal accepted canonical `f0d135…a8096`, with only the previously explicit derived traveler selection-UI normalization. `native_preservation.json` proves the saved four replacement meshes equal the frozen payload and all unrelated source geometry/fixtures remain exact. The remote summary binds every report and accepted-reference hash. Thus the geometry evidence applies to current v028; it is not borrowed from a different room version.

## Limits / no forced extension

- Continuous **specified square-body lanes** and continuous geometric floor/threshold, not every floor location, arbitrary turning radius, human gait, collision-engine skin policy, gravity/load capacity, or global castle access.
- The foot-contact slice is intentionally not an obstacle-clearance claim; the floor plane and support are separately proven. No claim that a human body extends to Z=29 without intersecting its support surface.
- Genuine pier and band solids remain; headroom is bounded by the tested 31.1 body top (door head margin about .35, band margin .7), not a new universal minimum-height certification.
- No genuine limited floor-support gap was found. A new seven-footprint floor clipper would mostly restate the already complete saved boundary/cell proof. Only a newly requested foot-shape/zero-clearance policy or additional off-network bay destinations would justify a different bounded test; neither is required here.
