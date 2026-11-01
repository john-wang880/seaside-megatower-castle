# One seaward plinth bay: bounded material feasibility

**Read-only; no defect, prototype, render or model write.** Accepted v020 sourceSHA `673dbbadca22d3dd45dc2f2eb5bde4a9e66851c1ca137da5c2570efc67c77614` unchanged. All short Blender probes finished and slot released.

## Exact visible region

Actual hero camera `V002 | full coastal skyline camera`, (115,−470,24),43mm,1200×866. Rays through the nominated pixelband identify **`V012 | ashlar with bounded entrance and north stairwell`**, component3052, south-facing **face11568**, slot0. Face worldplaneY−4.5, X2.565…69.435,Z31.565…38.035. It is the pale lower architectural wall, not wet cliff rock or the dark entrance.

A coherent trial bay is approximately **X41.85…46.15,Z32.65…37.845** on that face, bounded by projecting buttresses centeredX41 and47 (components4948/4972). Adjacent clean bay47.85…52.15 provides a control. The target is part of one long face, not a separately assignable bay mesh.

Above: **`V012 | terrace ledges with bounded stair opening`**, component39024, X2.1…69.9,Y−4.9…−1.1,Z37.845…38.175. It projects0.4m beyond the wall. **This is one continuous ledge with no actual joints/outlets. Concentrated drainage streaks would be invented.** Buttresses stop aroundZ37.2, so upper mask boundaries cannot all be concealed behind them.

## Existing material and dependency

Slot0 is **`Citadel • weathered limestone`**,21datablock users. Already uses world Geometry.Position for masonry projection, fine noise(scale10.7), broad noise(scale0.34)/ramp blended22%, mortar bump and grain bump. Existing mottling is real; there is no geometry/shelter-distance or directional grime mechanism. Height is used for brick courses, not a tide/grime gradient. Do not interpret absence of that mechanism as a defect.

Visible ashlar mesh:13,276vertices/14,154faces,one mesh user,no modifiers,no UV layers. No Generated/UV coordinate dependence in the material; duplicating the mesh without moving it does not shift the existing world-scale pattern. Shared material edits would affect unrelated architecture and are inappropriate.

If approved, copy the visible mesh data while retaining the original for rollback; duplicate the material graph and assign its appended slot **only to face11568** on the copied mesh. A world-coordinate, smoothly bounded contribution must be exactlyzero outside the chosen bay; all other material slots/faces and all original graphs stay intact. No geometry/silhouette changes. The broad face makes a hard rectangular mask unacceptable.

## Grounded opportunity, not a repair

V002 originalreview explicitly left “全场景石材的积垢、盐蚀和苔藓也需要位置依据” unresolved (`work/vision_review_v016/sources/V002_STAGE_REVIEW.md`,line55). Here the physical ledge supports only a **quiet, nonuniform sheltered upper-edge aging study**, fading downward, keeping the original grain/mortar legible. No salt/tide line at this elevatedZ32–38m facade, blanket moss, fabricated downpipe, repeated curtain streaks, dark horizontal belt or bright white outline. Since the source already has broad mottling, visible benefit remains uncertain and could legitimately be negative.

Proposed future actual-light comparison camera: **(50,−32,38.5)→(47,−4.5,35.4),55mm,1200×866**. Intended framing includes the entire trialbay, adjacentcleanbay and ledge, not a magnified isolated stain. This is a proposal, not a completed visibility/framing guarantee; source-world lighting/exposure must stay unchanged. Practical pair plus hero must justify any trial, otherwise stop without a muddy parameter loop.

Evidence: `FEASIBILITY.json`, full graph/slot inventory `survey.json`, actual hero ray hits `hero_probe.json`, local component dependencies `bay_probe.json`. No broad material/forest/coast audit is claimed.

## Completed camera preflight and mask limitation

`camera_preflight.json` now contains the actual evaluated camera matrix/data. Whole bay+neighbor+ledge bounds X40.1…53.9,Y−6.35…−4.5,Z31.5…38.9 fit with **9.09% minimum frame margin**.17/18 finite sample rays directly hit face11568; one lower-left ray hits an existing small projecting stone. No render/save was performed; the Blender slot is released. This is practical framing evidence, not everypixel visibility certification.

A no-face-split local shader could use worldZ distance below actual ledgeunderside37.845, softly modulated by the existing world-position broad variation, multiplied by a compact smooth X bell across the bay. It must reach exactlyzero outside the bay and below the upper agedzone, retain the complete original brick/grain/bump chain, and avoid a hard rectangular cutoff or constant-width dark stripe. Only a copied mesh's face11568 gets the copied material; the original21-user material and all other faces remain unchanged.

**Important causal limit:** this seamless ledge shelters both bays similarly. Geometry does not explain a special rain path or why only one bay should age more. Soft masking can prevent a technical seam but cannot manufacture that missing artistic rationale. The proposed one-bay study is at most a modest material variation sample. Inspect the source actual view first; if it already reads well or the isolated variation looks arbitrary, the useful outcome is no prototype—not invented streaks or expanding to an entire dark belt.

## Final artistic decision — no prototype

Owner and independent art director viewed the actual1200×866 unchanged-light baseline. Both reject proceeding with the isolated bay material experiment: existing warm pale masonry variation, buttress/coping cast shadows and projecting stones already provide coherent near-scale character. The continuous ledge offers equal shelter to neighboring bays; a localized grime gradient would be an unexplained stain. This actual close evidence overturned the initial hero-scale nomination. No material candidate was created or rendered, no model saved, and the scope will not be widened to all bays to rescue the idea. This is a closed read-only art feasibility study, not a repaired defect or failed material-render comparison.
