# Next stores milestone — a coherent functional storage system

Status: **CPU design plan only; no fittings geometry or render approval**. Publish and verify the accepted empty-shell milestone first. The shell is not yet a furnished or stocked stores room.

## Selected system

Two staggered, floor-supported timber racks, each divided into three broad bays, with **four plain lidded supply bins total**, supported on low/middle shelves. No floor crates, loose sacks, tools, labels or decorative scatter. Most upper shelving stays empty so the installation reads as usable storage capacity rather than clutter.

Room clear envelope: X16.4–23.4, Y34–38.5, floor Z29, ceiling Z32.05. Existing connector and protected body lane Y35.6–36.8 remain exact. No excavation, new room, window, exit or lighting change.

## Provisional complete envelopes

All dimensions are scene-coordinate units, not certified real-world measurements. Envelopes include feet, shelves, posts, bracing and stock; these are design targets, not measured clearance certificates.

| Rack | X | Y | Z |
|---|---|---|---|
| South | 19.25–22.85 | 34.08–34.78 | 29–31.10 |
| North | 17.00–21.05 | 37.72–38.42 | 29–31.10 |

This leaves approximately **2.94 clear width** between the racks, Y34.78–37.72, around the protected 1.2-wide central body lane. Preserve the doorway/vestibule and the central end standing area. The 0.55 end-wall gap beyond the south rack is **not** a claim of a walkable aisle behind that rack.

Wall offset is 0.08. All installation remains inside the room envelope; no recess cuts or anchors through the preserved source cover. Floor-supported feet must seat on the actual floor at Z29. Exact seating and stable-looking support need geometric validation; this is not engineering load certification.

## Lamp reservations

Leave full-height, stock-free wall intervals:
- South rack wall: X18.0–19.2.
- North rack wall: X21.1–22.3.

Use actual transformed fixture bounds from `work/v029_interior_program/fixtures_views/PLAN.json` and verify against the saved accepted shell. The reserved X intervals are not substitutes for complete fixture, lighting-ray or body clearance tests. Existing staggered warm lamps, powers, materials, world and exposure remain unchanged. Do not brighten the room to compensate for a rack obscuring a fixture or doorway.

## Construction language

Each rack has four paired upright stations defining three bays. Use broad approximately 0.10–0.12 timber members and thin but visibly supported shelf boards. Proposed shelf surfaces are near Z29.22, 29.90 and 30.58; frame top is Z31.10. Integral back bracing provides a plausible supported appearance; avoid dense decorative slats, ornate brackets or iron embellishment.

Four bins, two per rack, approximately 0.65–0.90 long along X, 0.45–0.55 deep and 0.40–0.50 high. Fit each inside a clear rack bay and beneath the next shelf with a positive gap; bottom faces rest on the actual shelf surface. Do not silently scale stock into beams or generate intersecting stacks. No stock on the floor or in the lamp reserves.

Use subdued desaturated weathered-brown timber. Prefer a suitable existing material **copy** after source inspection; otherwise one local rough timber material. No shared-wall material edits. Bins belong to the same restrained material family with small value variation, not bright colored accents or high-frequency decorative grain.

## Cost and proof before geometry

Target approximately **1.5–3k fixture triangles** for both racks and all four bins; **5k planning ceiling**, not a minimum. Report complete evaluated counts, not only source-asset counts.

Required checks: exact floor seats; closed/internally coherent pieces and supported shelves/bins; room-cover preservation; whole central route and standing/camera/near-plane envelopes; full fixture reserves; actual light and doorway sightlines. AABB separation alone is not proof of unobstructed visual connection. Preserve all shell geometry, material bindings, source rollback and lamp states.

## Same-view visual gate

Use the accepted `stores_entry` and `stores_return` cameras, not prop macro views. At full 960-pixel frame scale the room should read as purposeful stores through broad shelf rhythm and limited supply stock, while retaining its elongated proportions, uncluttered working aisle, readable return doorway and subdued light hierarchy.

If rack placement obscures the connection or lamp cues, stop at the geometric/visual gate rather than use new camera angles, fill lights or denser decorative detail. Functional fittings are a separate milestone from the accepted shell and should be described as such.
