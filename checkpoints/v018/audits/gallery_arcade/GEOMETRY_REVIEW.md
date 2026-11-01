# v018 gallery/arcade geometry audit — bounded results

Canonical source SHA `c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd` unchanged. Read-only source inspection; no model/Git changes. Original recipes copied from fixed history commit `91f2c7d2dd38d288b6c52e2469bb4d5b81e322d6`. Current actual-light visual sampling is separately owned under `visual/`; this report does not replace its verdict.

## West cornice “fin”: useful negative, not a detached face
Historical v006 review explicitly identifies the prominent triangle/cut-slot below the west stone-rib sample as inherited from v005. Current geometry confirms it is a substantial closed diagonal bracket, not an open stray triangle or a v006 seam failure.

Visible object: `V012 | retained west rib facade with buried-route clearance`.
- Brace component vertex seed376 (IDs376–383), six closed quad faces; bounds x−126.0818…−120.2242,y83.0000…84.6000,z134.5601…137.5153.
- Upper horizontal bracket seed368, x−125.7760…−120.5300,y82.9000…84.4000,z137.1054…137.6776.
- Tall ribs seed48 and56 provide contacts at opposite brace ends. Brace376↔rib48 and↔rib56 both have minimum tested separating-axis overlap0.025009m. Interior witness points lie within both actual face shells under all three oblique parity rays.
- Brace376↔bracket368 overlap~0.3211m; bracket368↔corner cap360~0.4788m and↔cornice304~0.2837m. All have positive interior witnesses.
- Matching diagonal brace392 connects the opposite side of the same rib56 to bracket384. Its corresponding contact checks also pass. This paired arrangement supports an intentional bracket reading, not an isolated stray spike.

`offline_contacts.json` contains precise coordinates, witnesses and results. Convex-hull SAT uses source world vertices; witnesses are additionally tested against fan-triangulated actual quad faces with three rays. This is bounded intersection evidence, **not a load-capacity claim, historic-authenticity judgment or complete hidden support audit**. Closed components and contact do not alone determine whether the feature looks good. No modification is justified by a floating-piece hypothesis here.

## Main roof-terrace balustrade: internally connected sampled assemblies
`V002 | main roof terrace parapet` has44 separate closed8-vertex/6-face components. Actual geometry yields four internally connected11-piece assemblies,72 rail/post contacts in total. Each side consists of two horizontal rails and nine uprights, matching the original restrained parapet recipe. No isolated post or disconnected rail within these four assemblies was found. External corner-pinnacle/floor anchoring is outside this specific contact test; it is not certified by internal connectivity.

Existing actual crown imagery is the relevant practical-scale visual evidence; no new roof detail or mechanical repetition is proposed. Roof surfaces themselves are excluded from this audit.

## Main lower gallery/corbel belt: sampled topology, not full contact certification
In `V006 | main facade with one short jointed rib sample`,430 connected components intersect the inspection box x10…65,y8…35,z48…80. They comprise396 eight-vertex blocks,29 twenty-vertex solids and five48-vertex solids. All430 have zero boundary/non-two-face edges in the exported source geometry. This establishes closed sampled construction, **not** that every decorative component is attached or every arch is traversable. New medium-view imagery is intended to reveal a genuine local anomaly before spending effort on any deeper all-pairs contact test.

## Windows and short rib samples: no fabricated missing feature
Original v003/v004 scripts already cut actual recesses, add tapered reveals, inset mullions/glazing, sloped sill tiers and contact-checked secondary ribs. Their sparse east-side windows and blank wall fields are deliberate. This audit does not rerun or relabel those22 previously validated openings as newly certified.

The v006 recipe intentionally limits physical stonework to two five-block rib samples, with0.018 joints,0.010 bevels and inset continuous cores. Current west sample lower continuation, backing and first stone remain separate closed solids in the inspected neighborhood. Historical same-camera actual samples and their prior validation—not mass expansion—are the correct comparison. No evidence here supports enlarging joints or tiling all tower ribs.

## Limits and next decision
Distinct geometric finding is **negative**: the conspicuous west fin has demonstrable connected bracket construction. Internal parapet connectivity and lower-gallery closedness are also useful bounded negatives. Final visual review may still establish an artistic or local geometric issue at intended resolution; do not infer such an issue solely from dramatic closeup silhouettes. No whole-castle structural, navigation or render-quality certification is made.

## Final actual-view decision
Both owner-approved current actual-light stills are now complete and personally inspected:
- `visual/actual/west_cornice.png`: wider context reveals the repeated angled bracket family around the tower corner. The historically prominent fin is not an isolated shard; open slots and pointed/notched ends remain stylistic features. Combined with the contact evidence, no warranted corrective edit was established.
- `visual/actual/main_gallery.png`: lower facade gallery, layered cornices, corbels, window-surround context and projecting supports are coherent at1200×866. No conspicuous detached component or discontinuous construction justifies a targeted repair from this view. Fine hidden joints not resolved in the image remain outside this claim.

The renderer used the canonical v018 source, original80 samples/lighting, and no scene save; its exact pose/framing/identity receipts are in `visual/actual/`. Independent visual reviewer concurs with a useful negative. **Retain v018, no new model version, no forced ornamentation or repetitive rib/window expansion.** This closes these sampled questions only, not every arcade or facade in the castle.
