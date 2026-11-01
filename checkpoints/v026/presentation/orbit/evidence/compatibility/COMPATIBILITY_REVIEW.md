# Current v026 compatibility with the immutable v016 orbit

**PASS for preserving the exact existing recipe; no frame has been rendered in this review.** Current sourceefcd894… is unchanged. Actual originalsource d44a4cde… was also loaded read-only and remained unchanged. Historical recipe came from fixedGit9d417969f97c309665fb37067a81785c0aa225a0.

All96 camera location/target/lens/clip recipes match both historicalfinal_plan andpath_plan exactly. `proposed_final_plan.json` differs from the originalfinal_plan **only in source_sha256**. No radius search, composition/angle/lens/quality adjustment:40°partialfrontarc,960×694,12fps,8seconds,80samples/adaptive.035/min12/bounces8,8renderthreads. This is not a360°tour.

## Framing

Actual evaluated selected architecture bounds remainX−155.9766…82.6,Y−8…120.75,Z5.7…212.7;270,799vertices. Offshore architecture2,532vertices and coastal rock18,047vertices also retain originalbounds. Conservative eightcorner bounds fit **all96poses**. Minimum normalized edge margins: mainarchitecture12.1202%,offshore12.8735%,coastalrock2.50536% (only just beyond the historical2.5%requirement; not reason to retune).

Scope is the original selected coastal-rock/architecture set plus current matching architectural additions, not the entire ocean, meadow, clouds, forest or terrainextent. The added V019conifer is excluded from architecturalbounds; its existing pose context receives finite sightline checks. Full source nameinventory/bounds/projections in `compatibility.json`.

## Actual light and settings identity

Two native loads establish exact world properties+nodegraph and all scene light object properties/transforms/data/nodegraphs against actualv016baseline, not merely worldname. Combined state signatures are equal. CurrentCyclesproperties, exposure/viewsettings, effective originalrender settings after the recipe's resolution/thread/output adjustments, image settings, frame1 and Blender5.2.3 all match historicalfinal_plan exactly. No light/material/world was changed to achieve this. `lighting_guard_metadata.json` binds the signaturemethod/helper/script/source/plan hashes for a later production guard.

## Occlusion is not promised

25 finite context rays acrossframes1/25/49/72/96 deliberately show limits: the bridge-pier target is firstsurface in1/25/49/72 but rockoccluded in96; westentrance targets encounter arch/bridgehead/foliage; the near-tree center is obscured by otherforest in25/49; crown target is often blocked by the existing parapet or masonry; offshore target crosses headland early and existingmarker-side geometry later. Targetcenter obstruction does not imply an entire asset disappears, nor a missing-access defect. Volume-only cloudcontainers are skipped for opaquehit classification only and remain present for real rendering. No exhaustive pixel visibility/opticaltransmittance guarantee.

**Recommend exactly original frame49 for one cost/visual pilot**, location(155.3244781494,−575.4694213867,45),target(−35,35,85),40mm. It is representative of the unchanged path, not a handpicked clear entrance view. Only actual current rendering can establish its final visual/readability/cost; this review does not authorize all96renders. Sourcefiles untouched, no scene save, Blender slot released.
