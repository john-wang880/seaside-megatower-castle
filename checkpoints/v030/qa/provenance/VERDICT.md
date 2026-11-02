# V030 actual saved fittings — technical PASS, artistic view gate pending

Accepted-for-testing candidate `9f020b7ec6eda309d674653598b169f65ba5dc1d1f194ffa31323f6393feda35`; source v029 remains exact `4f838529d32cbf6a0314cc0a23b3dd1703b73d80c5db146fb4d323697b882df5`.

## Actual geometry, not inherited box assumptions

Six added mesh objects contain78 actual closed, outward, positive convex prisms and2184 native triangles. Each saved coordinate matches the independently reconstructed float32 chamfer/body/lid prescription. Every actual polygon is planar and an outward supporting plane; native triangles cover all780positive parent polygons without outside, missing or multiply-covered area. No exact-zero derived triangles occurred. This proves the individual convex pieces, not that intentionally intersecting post/rail assemblies are globally disjoint or welded.

All16 actual chamfered foot polygons have complete, nonduplicated coverage by the saved upward floor triangles. Their measured areas range0.0142717622075–0.0142719758296, not the old rectangular0.0144. All78components reach the floor through the explicit support graph.36rails have72positive-volume post contacts (minimum0.0005935886963);18shelves each retain two actual rail bearing patches (minimum individual area0.09353604819). Four actual bin-body bottoms are fully covered by their respective shelves (area about0.38441524); each lid covers the entire body-top bearing while retaining its small overhang. No bearing is inferred solely from bounding boxes or metadata.

Exact rational canonical-plane clipping finds zero same-facing positive-area coincident patches between new components.140opposite-facing patches are legitimate bearing/end interfaces. Positive post/rail embeddings are intentional. This is an exact saved-plane result, not a universal near-plane/render-depth statement and not a BVH-based exclusion.

## Existing scene, route and light cues

All53 relevant current saved/source components are checked conservatively. Only actual Z29 floor triangles contact the post envelopes; other source geometry, old/new lamps and walls are clear. The protected continuous central body lane and both original accepted near planes remain clear. All13 fixed actual camera→saved-light/door rays avoid the actual chamfered prisms. There are no braces or upper opaque panels. Finite rays do not certify all emitter pixels, light transport or photographic readability; both fixed same-view actual images remain mandatory, with no fill lights/camera compensation.

One new local material uses only Geometry.Position→Noise→brown ramp→Principled→surface, roughness0.82 and emission strength0. All old material graphs, lights, world and camera states remain unchanged. Appearance is not certified by graph identity.

## Preservation, repeat and controls

Native source→candidate comparison passes all13 emitted categories, including per-layer visibility/selection, collections and scene properties. Only the exact six owned objects/meshes, one material and one collection are added. Removing those IDs in memory restores the full source snapshot. The three established traveler-derived selection-only fields are individually documented; no raw weights or general attributes are waived.

Fresh isolated rebuild `d277fb8155726410081d4a92e7ebd4828dced863832eb7028757585b2049e0c5` was independently reopened and matches accepted candidate semantics across all13categories. Different .blend bytes are not treated as failure or substituted as canonical.

Six actual exported-geometry mutations are rejected by the exact prescribed-profile/topology/ownership gates; their raised-foot/lid labels are **not** claims that downstream contact checks were separately injected. One equal-area hole+duplicate mathematical control directly tests the bearing-coverage predicate. Two focused native original-vertex/material mutations exercise snapshot sensitivity and restore exactly; these are not two complete scene reruns.

No model was saved or rendered by QA. Native sessions67453 and39611 terminated successfully; slot released. No engineering capacity, physical unit calibration, global accessibility or whole-scene manifold claim.
