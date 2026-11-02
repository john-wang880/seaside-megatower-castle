# Fixed lamp pair and one prospective camera pair — CPU plan only

Source acceptedv028 f0d135… remains unchanged. No Blender, geometry creation, model save, lighting mutation or render. This plans the conditionally carved stores, NOT an assertion that its current solid source already contains usable camera space.

## Two exact-style rigid lamp copies
Template: ten actual mesh components `V028 | room 1 …` in current native export, plus exact accepted point-light record from `work/v028_receiving_chamber/lighting_fixed.json` (bound to f0d135). Existing source wall anchor(15,34,30.95). Apply signed-axis90° rotations, not independent vertex redesign:
- South anchor(18.6,34,30.95), Rz−90°, source inward−X becomes+Y.
- North anchor(21.7,38.5,30.95), Rz+90°, source inward−X becomes−Y.

Actual transformed luminous centres:
- south(18.6,34.1899995803833,30.950000762939453);
- north(21.7,38.3100004196167,30.950000762939453).

Preserve POINT type,36.0power,color(1,.5799999833,.25),soft-radius.03500000015 and the full original datablock/node semantics at eventual native copy. No fill/ambient/power tuning. Two rigid assemblies total1160triangles before any unrelated architecture, with20mesh+2light objects. Existing receiving lamps are untouched.

Actual assembly bounds:
- south X18.48999939…18.71000061,Y33.99693203…34.29999924,Z30.77750015…31.21000099;
- north X21.58999939…21.81000061,Y38.20000076…38.50306797,sameZ.

Each transformed mounting plate has a positive-volume seat box0.000004 scene-units³ inside both actual plate and original ashlar source, outside the prospective cavity: southY33.999…33.9995; northY38.5005…38.501. This is actual all-triangle boundary exclusion+solid-angle inclusion, not a wall-AABB inference. Existing arm/bracket intrafixure relations are rigidly retained; exact saved float32 contacts and full component support/coplanar checks remain later gates.

All transformed fixture triangles are disjoint from the1.2-wide axial body proxy Y35.6…36.8,Z29.025…31.1. `reserved_no_shelf_box` expands each complete assembly by.15 for planning; future storage must remain inside clear-room space AND outside these reserved zones. These reserve boxes do not authorize excavation outside the room or into its .30cover.

## Single natural camera pair, fixed before any render
Both standing eyeZ30.65 = floor29+1.65,26mm,sensor36,horizontalfit,960×694,clip.08…1000,level gaze. Exact matrix/data in PLAN.json.

1. **stores_entry** eye(15.2,36.2,30.65),target(23.4,36.2,30.65). Within prospective connector. Near aperture edges intentionally crop: full2.45-high aperture cannot fit from such a short sleeve at natural height/26mm. Owner accepted this honest limitation. Full far-room corners project inside normalizedimageX.2974… .6938,Y.3294… .7010. Both staggered lamps project inside; sidewall/floor/long-axis context retained. No loweredeye/wideangle or angle sweep.
2. **stores_return** eye(22.7,36.2,30.65),target(15,36.2,30.65). From far central lane toward actual deep connecting aperture. Full old-room-side doorway projects X.43434… .56566,Y.39620… .71408,depth7.7. Near northlamp is outside this reverse frame, explicitly not a requirement to show both lights twice.

Near-plane corners lie strictly within each prospective cavity.18 finite rays (3×3destination/aperture samples perview) are split at every planned cavity plane; each open interval lies in the exact union of room+connector air. Actual non-target triangles and planned fixture triangles provide no first-surface blocker on those sampled segments. This proves more than frameprojection but NOT every pixel or visibility in the still-uncut current source. Future saved model must repeat actual firsthit/nearplane/body checks before same-light render; current source hosts were intentionally excluded only where the approved future cavity would remove them.

## Pending gate
Independent CPU review of transforms/seat/route/camera records; parent acceptance of this fixed planning pair. Then exact saved geometry/material/light-state QA and practical doorway/return images after approved construction. No new camera variants, shelf cuts, lights or model have been created here.
