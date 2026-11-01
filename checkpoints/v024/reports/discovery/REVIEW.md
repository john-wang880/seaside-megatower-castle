# v023 rear / landward discovery — read-only geometry map

Source `work/v023/castle_v023.blend`, SHA `c4b1dda3b8f70e4c8cb0171834b2150b6d7610f6296847362fd204b2dfa7ad51`, verified unchanged. No model save, render, architecture addition or Git write. Coordinate units only, not globally calibrated real-world metres.

## Useful current finding

There is a genuine **authored front/rear hierarchy**, not evidence that every blank rear face is unfinished. Main shaft's north face (`V005 | main tower calibrated stone surface`, evaluated face3) is a broad planar ashlar surface atY62.5, spanning approximatelyX17.5–47.5,Z39.6–180. North probes atX20/35,Z75/110/160 hit that same face. The east return is atY59.5. The west shaft has a similarly plain rear atY114; its lower massive base extends toY115.5. Existing V004 windows deliberately target front/east elevations; existing V002 crowns have four-sided apertures. No missing rear-window defect can be inferred from this asymmetric design.

The rear is not universally landward: **the main castle's north side is a sea-facing headland edge**, while the western tower sits on a much larger elevated landmass. AtmainX−5…75,Y75, existing headland top samples are aroundZ25.7–28.3; atY90 they rangeZ0.9–19.9; byY110 all these samples hit original water aroundZ−0.3. Main foundation's actual north face isY72, with existing stone/terrace masses in front of the headland. Western terrain extends north toY181.24 and rises toZ49.16; finite horizontal samples atX−135,Y≈161 meet the steep outer terrain side before the west tower. This is precisely the kind of far-side massing worth viewing once, **not a proven terrain or access defect**.

Original V002 explicitly left inland terrain untouched and far-side landform/rock direction as later review; it prioritized camera-specific craft instead of full-scene density. Existing rear simplicity may be intentional backdrop. This survey does not authorize adding access routes, rear rooms, windows, battlements or cosmetic rock clutter.

## Existing circulation, with occlusion limits

- Original winding path ends atcenter(−122,90,38.02096), under/against western tower context. From the proposed north view, west masonry blocks that endpoint by~26.94 coordinate units along the tested sightline. It is not a new exposed disconnected approach finding.
- Main entrance route is the existing V012 L-shaped internal corridor and north stair: floorX3.5–5.4,Y39.4–45.5,Z29;20treads proceedY45.5–58 toZ32.625, with paired guardsX3.4–3.5/5.4–5.5. Previously accepted destination is the limited covered terminal nearY58–60.5, **not a general northern exit to terrain/sea**.
- The north terminal target(4.45,60.5,32.625) is occluded in this overview by existing ashlar about6.51 units before the target. Do not use the overview to claim interior path visibility or whole-castle accessibility.
- The central bridge rear is visible geometrically: target(−40,41.2,20) hits the accepted V021 pier union at3.8e−6 distance. This is just an opaque-surface sightline, not a new support certification.

## One useful current overview proposal

**Camera(−50,500,210) → target(−35,55,105),45mm,1200×866**, sensor36/horizontal,zero shifts,clip0.1–3000. Frame1,original world/lights/exposure,80samples/8threads if owner elects to render. Exact `reference_matrix` and `camera_data` in **views.json**, same schema as the existing actual-light worker.

This looks approximately southward from north, opposite the previous southern hero. It shows rear wall coverage, both tower crowns, bridge rear and their different land/sea settings. All selected actual main-architecture vertices fall within normalizedX0.19257–0.86257,Y0.15344–0.91931 (minimum8.07%margin), positive depth. This is not a claim that all peripheral coast or the distant offshore marker is in frame. The target is an informative rear composition, not a new cinematic lighting treatment.

Finite actual scene rays hit main rear wall, west rear wall, bridge pier and main rear terrain. The initial northwest pose crossed the western cloud container and was discarded as a less useful discovery view. Two framing-only preflight rejections are retained; no exploratory render batch was made. Final rays skip **volume-only shader container boundaries** when classifying opaque surfaces; no cloud or atmospheric object was hidden or changed. Rendered haze/transmittance remains unknown until an actual image. `survey.json` names all nine volume-only containers, records exact first opaque hits, and retains honest interior occlusions.

## Scope / stopping boundary

The survey maps selected low rear components and finite face/top-surface samples; it does **not** validate all component contacts, closedness, erosion physics, walkability or backside completeness. Existing circulation and blank-wall observations alone do not justify a model change. The one actual north overview is the appropriate next discovery gate if the owner wants it; assess that picture before nominating any exposed unfinished region. If the backdrop is coherent, close negative rather than fill it by assumption.

Files: `survey.py`, `survey.json`, `survey_final.log`, `views.json`, preliminary non-render preflight logs. Original vision reference `work/vision_review_v016/sources/V002_STAGE_REVIEW.md`; existing route history `work/interior_survey/recommendation.json` is historical intent, while the mapped V012 objects are current v023 geometry.
