# v020 main bridge ring — read-only feasibility

Source `work/v020/castle_v020.blend`, SHA256 `673dbbadca22d3dd45dc2f2eb5bde4a9e66851c1ca137da5c2570efc67c77614`, unchanged. No model save, material edit, prototype or render. Existing polished A inspected; its two conspicuous openings are part of a three-span authored bridge, with western span largely obscured by terrain/forest. This is not a structural defect audit.

## One nominated span

Central exposed opening: X −38.5…−23.5, spring Z16.2, apex (−31,24). Actual intrados is a 30-segment pointed profile, extruded Y34.8…41.2. Body: `V007 | western stonework with actual bridgehead passage`, component seed15890,66vertices/35faces, topZ26.4. Adjacent source pier bodies seeds15956 and15964 reach Z6…26.4; opposite next span seed15972 lies X−19.5…−6.5. Existing deck, route, piers and profile remain immutable. This survey identifies dependencies, not renewed contact/route certification.

Camera-facing ring already comprises **30 separate six-face/8-vertex stone components** in `V012 | retained west rib facade with buried-route clearance`: seeds10008+16k, k=0…29. Interleaved components at seed+8 form opposite-side ring. Front face Y34.25, backY34.85, depth~0.60; existing body beginsY34.8. Whole front-ring bounds X−38.8223…−23.1777,Z16.1748…24.1669. Two existing vertical trim legs seeds10488/10496, Y34.28…34.88,Z6…16.2. Nothing should add another larger arch or keystone.

Mesh has one user, no modifiers, no UV layers. Ring slot0 is `West_Sunlit ivory carved stone`,3material users; original source graph must remain unchanged. Body slot0 is `West_Cool weathered limestone`,16users. Both use world Geometry.Position→Noise→ColorRamp for color and Noise→Bump; no actual joint/brick shader. Ring is not a monolithic simple strip, but **all29 adjacent front quads overlap coplanarly**, measured exact evaluated XZ convex clipping:0.0012498…0.0382825m². Thus disconnected source pieces do not supply recessed physical joints. Full face/vertex IDs and material graphs: `survey.json`; measured pair polygons: `front_junctions.json`.

## Practical source camera

Location(−43,−26,25),target(−31,37,18),55mm,1200×866; original source lighting/exposure. Includes whole span, piers/deck and adjacent context. Bounding region X[−42,−20.5],Y[33.9,42],Z[6,30] has6.49%minimum frame margin. All30 front-stone center rays hit their intended visible faces; finite samples, not every-pixel clearance. Exact matrix/data in `camera_preflight.json`. Historical camera `03 | Stone bridge and western curtain wall` exists at(28,−138,64),58mm; it is a wider scene-context pose, so this single bounded closer pose is proposed. Blender slot released for owner's one actual baseline render.

## Decision gate, not implementation authorization

First inspect actual source image. Existing silhouette/stone faceting may already read as crafted, in which case stop. Only if practical-scale divisions are demonstrably absent and an artist supports enrichment: consider restrained joint/edge relief within the **existing** front-ring envelope on this one span, preserving actual intrados and outer silhouette. Do not overlay a second ring or assume additive blocks can solve coplanar overlaps. Any implementation would need reversible isolation of only these30 source stones, exact preservation of unrelated merged-mesh content, real host seats, and a deliberate way to retain the occupied shell/profile while articulating shallow surface joints. Existing overlapping quads make this more than blindly adding23 portal stones; no recipe or geometry is proposed as accepted yet. No mechanical propagation to other spans, no global material changes, no contact/load-capacity claims.

## Closed actual-view decision
Owner, parent and independent art director found existing divisions adequate in `visual/baseline/image.png` (exact actual-light receipt alongside). No ring prototype or model change; do not repeat or expand this treatment. Separate subsequent pier-slot survey is not a ring styling continuation.
