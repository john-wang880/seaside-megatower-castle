# v022 path arrival image — exact local conformance diagnosis

Source v022 SHA99156d901f9d498b86bae4834a642d1d9110dc6e4e3a4273bca64fda17a9dfd2 remained unchanged throughout this read-only survey. Existing actual stand image: `work/midground_stand_v022/visual/baseline/image.png`. Scene settings METRIC/scale1/METERS are recorded, but measurements below are coordinate units, not globally verified physical metres.

## Not the assumed path endpoint or stair junction

`Narrow winding limestone footpath | conformed to meadow` is a continuous open1512-triangle ribbon with127longitudinal rows×7cross-strip vertices(889vertices). Face schema:row×12+cell×2+triangle,allsourcepolygonsalreadytriangular. First center(−58,−78,12.76968); true last center(−122,90,38.02096). The pronged apparent upperend in the image is an intermediate stretch aroundrows95–104, not a mesh endpoint.

The path continues north under west-tower/bridgehead structures. Centerline upward probes encounter an existing ashlar underside about2.37units above row104 and1.64 above row107; the final endpoint has existing stone above it. These finite probes identify context, not walkable-route certification or original intent. The pre-v002 generator is unavailable; existing grid/name and preserved geometry are evidence, not a claim of designed public access.

V009's separate terrain-following apron is X−91.5…−90,Y36.4…39.6, followed by the approved nine treads to the western portal. Exact nearest original path surface to three apron west-edge vertices is4.665–6.184units away. The pale ribbon does **not** directly meet that apron. Existing west-approach rays hit V009 treads/parapets, while the stand-camera problem maps farther northwest. No new connector, relocated path or new staircase is warranted from the apparent image gap.

## Proven surface mismatch versus deliberate verge

All175sampled original path vertices(rows88–112) lie0.02071…0.02787 above actual western headland. But long pathtriangles interpolate differently from the terrain triangles below. Stand-camera rays at grass interruptions hit actual `V002 | western headland with solid rock shore` **before** the pale path; for examplepixel(820,620),terrainZ28.319 followed bypathZ28.305. Other pixels hit path first. This is not merely a moss-colored path shader.

The path intentionally has three material regions: pale worn limestone/earth, chalky limestone patches, soft mossy verge. Those exact source triangle material partitions stay unchanged. NoUV, modifiers, groups or weights; meshsingleuser; flatshaded, open/downwardwound triangles. Attributes are only standard position/topology/selection/sharpface/material fields. Firsttwo materialgraphs useworldPosition→Noise→Bump; moss is constant Principled color. See `dependencies.json`, including authoritative selected looptriangles.

Doubleprecision intersection of **actual evaluated terrain triangles** with path triangles proves full XY coverage without holes/overlap. Over diagnosticrows95–109,17.4211of89.1784planarea is covered by terrain(19.54%); even innerfourcrosscells show20.79%, distinct from intentionalouterverge. Fullaffine analysis finds worstburial0.08424743, deeper than finite sampling's0.06652. These are planimetric areas, not camera pixel fractions.

## Final bounded patch and clean seams

Onlyrows95→105,sourcefaces1140…1259(120triangles), are proposed: centerlineapproximately(−100.087,41.219,27.919)→(−107.438,61.312,32.392). These contain the visible lower interruptions and upperprongs; later hidden/diagnostic rows106–109 remain out of scope. Original row-to-row centerline slopes here are0.0681…0.3709, not horizontal landing grades.

Final120face XYarea57.56772292; buriedarea12.72784843(22.10935%); worstfullfaceburial0.08424743. Entire six-edge lower seam95 remains≥0.01701785 above terrain; upperseam105≥0.02156259. These minima come from exactsegment clipping to every terrain triangle, not vertex-only checks. Fixed end-seam offset range0.01701785…0.02565516. Lateral edge minimum−0.03636071 means lateralZ must reconform; freezingallboundaryZ would preserve the defect. All lateralXY/jaggedmossoutline remain fixed.

Independent `work/path_arrival_qa/{source_overlay,boundary_and_subset}.json` reproduces area, exactgap extrema and fullsegment seams. Selected interior rows96–104 are63vertices672…734; native invertedMask can remove exactlyfaces1140…1259 without touching shared boundaryrows95/105 or outside1392faces. My initial full-boundaryMask concern was too broad; the refinedinterior-only selection resolves it and is preferred over a pathcopy if actualMaskevaluation passes.

## Authorized technical direction, not a new route

Overlay the120source triangles with actualterrain triangle boundaries; retain exactly their XY/material domains. InteriorZ followsactualterrain+.021; all end-seam originalvertices and inserted collinear interpolants retain oldZ; lateralZ conforms at unchangedXY. Onterrain-aligned triangles, completeaffinegap can be proved, not merely sampled. Predeclared supportedgap gate[.016,.030], including oldpositive endclearance. Keep original downwardwinding/open-decalnature and flat/material attributes. No blanketlift, gravel, newdensity, terrainedit, all-path replacement, or changed destination. Float32 inserted-knots precision must be measured honestly rather than called exact rational collinearity.

The subsequent separately authorized technical candidate is documented under `work/v023_path_conformance`; this source survey itself performs no edits/renders. Same actual standcamera plus control/hero view must judge whether the local repair removes accidental grassholes without losing intentionalverge character. This does not certify the entire scenic path as a continuous navigation route.
