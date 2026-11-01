# Independent QA plan — exactly three midground crowns

Planning only; no Blender, model save, rendering, Git or source edits. Source v022 SHA25699156d901f9d498b86bae4834a642d1d9110dc6e4e3a4273bca64fda17a9dfd2. Exact selected carrier/crown inventory is in midground_stand_v022. Specialist owns its short Blender slot and one concept; final asset schema is pending.

## Owned scope and preservation

Tree trunks90130/54140/3350 and source foliage ranges[159318,159634),[122118,122433),[15211,15589), total1009vertices/1558source triangles. These are spatially corroborated carrier groups, not recovered original generator IDs. No additional trees, trunk/position edits or near-hero-tree changes.

Original source foliage already owns the v019298-vertex Mask/group. The integration must add a uniquely owned second Mask/group, with precise1009weights and no changed pre-existing group indices, weights, modifier properties/order, raw mesh attributes, material slots or hidden original forest. Validate the *composed* evaluated complement against the current v022 evaluator, not raw source alone. Explicitly map raw indices through the first Mask before mapping the new keep set; a simple raw-index assumption would be wrong. Preserve every unselected POINT/EDGE/FACE/CORNER attribute, topology, material, normal and any isolated vertices. No blanket deformation-weight or attribute exclusions.

All original woods, hidden source meshes, architecture, prior v019–v022 geometry, materials/nodegraphs/world/lights/cameras and transforms remain exact. New identity-world meshes reuse original existing palette only; preserve the two dark/one lighter crown distinction. Any procedural material dependence on object bounds/random/UV must be inspected before assuming a new object renders equivalently.

Paired rollback disables only the new three-tree Mask and hides exactly the new crown objects. Earlier v019 Mask stays active. Repeated rollback/HIGH must reproduce source/active evaluated states; mixed states are invalid. Source and candidate .blend bytes are never written by QA.

## Budget, actual geometry and contact graph

Count actual evaluated loop triangles across all replacement crown/core components: <=6000 total (ceiling, not target). Compare actual mesh arrays, not generator promises. No needle assets, new tree density or material-based camouflage.

Decompose actual connected components; require intended solids closed, oriented, positive and nondegenerate. Strict nonadjacent triangle crossings are tested separately from topology; report coplanar/shared-vertex limits rather than implying global embedding proof. Match supplied component roles/ranges to actual components, not vice versa. Inspect intended core/tier intersections versus exposed same-facing doubled faces and unexpected inter-tree/architecture overlaps.

Build an explicit crown-part→core/woody-carrier contact graph. Roots are exact associated source wood components, not nearest arbitrary trunk vertex. Use actual evaluated visible wood; hidden originals are not support. If source wood is open-ended (as prior hero trunk was), do not cap it silently and claim a closed actual solid. Actual side intersection and explicitly labeled section-envelope evidence may support a bounded root attachment statement. Test each part's true connection or documented composite contact, not just hierarchy or bounding overlap. Preserve actual source trunk ownership and root data.

## Crown profile / fullness evidence

Keep source tree positions, heights and footprints. Compare candidate projected/sliced profiles against actual source per tree, not one collective box; report changed silhouette fractions and height bands. Original AABB volumes are envelope measures, not occupied volume. Do not sum overlapping part volumes.

For occupied fullness, first verify source/candidate solid eligibility. Measure union occupancy on the *same* per-tree spatial lattice, then a second offset or finer lattice. Use per-component containment and OR union (not parity cancellation across overlaps). Quantify sampling sensitivity and label volume estimates, especially at thin tiers/outer gaps. Invalid/open source components are an explicit uncertainty, not silently ignored. Report retention, added mass in old voids and per-height-band changes separately. Do not set a post-hoc aesthetic threshold to match the candidate. Actual full-context and A-scale views remain the acceptance criterion; polygon increase or an aggregate ratio cannot prove better massing.

## Actual local path corridor — not AABB safety

Relevant surface: `Narrow winding limestone footpath | conformed to meadow`. Existing nearest-root distances10.44/4.93/3.58 are only point samples. In particular tree3350 spansX−109.35…−104.20,Y41.10…46.34,Z29.44…37.43, close to actual pathX−106.08…−101.15. A new solid can fill an old safe void while remaining inside the old crown box.

After the candidate is available, inspect actual evaluated full path triangles. Select by full triangle bounds intersecting the candidate-relevant XY region, not just vertices inside a rectangle. Extrude each relevant actual path triangle vertically into a closed triangular prism from floor+0.025 to floor+2.1 coordinate units (same bounded local camera/headroom convention, not a legal/human-accessibility standard). This covers the actual path footprint continuously; no imaginary width or global navigation claim. If local route design gives a narrower explicit traversable ribbon, document it before testing, not after a collision.

Check new closed crown/core solids against these actual prisms using triangle intersection plus containment or exact closed-volume intersection. Test source selected foliage against the identical envelope as a baseline; report any pre-existing occupancy and every new intrusion separately. Also check ground/path sheets for actual surface intersection; open terrain is not a fictitious enclosing volume. Evaluated object bounds precede broadphase culling. Bound the result to the inspected path triangle IDs, vertical interval and three candidate crowns; preserve path readability in the actual context image.

## Neighbor and visual scope

Actual world geometry checks cover adjacent unselected crowns, source wood, path and nearest architecture where new crowns could intersect. Original envelope containment alone is insufficient to waive added collisions or silhouette occlusion. Identify intended source-wood/within-crown intersections precisely; no whole-object exclusions. Existing terrain/path visibility and canopy rhythm need identical-camera review; a near hero tree's420k-triangle design is explicitly excluded.

## Negative controls / execution

After candidate and slot release: extra selected weight, wrong existing v019 weight/modifier, hidden-original mutation, detached crown/core piece, invalid face orientation, and deliberate new path-prism intrusion should each fail their relevant invariant. AABB-overlap but disjoint geometry and contained-solid/no-boundary-crossing fixtures protect the collision predicate. Full rollback and repeated-state checks follow.

Critical geometry/preservation/budget/contact/path gate can precede expensive fullness refinement if visual rejection is likely. One concept only; no undeclared parameter sweep or expansion. Stop on visual rejection or unresolved source/attachment/path uncertainty. Any public adapter uses explicit source/candidate/report CLI, bundled exact metadata hashes, no private work paths and a fresh isolated run with bytecode disabled before publication. Units remain coordinate units despite METRIC UI settings; no global metre calibration, engineering capacity or whole-forest navigation certification.
