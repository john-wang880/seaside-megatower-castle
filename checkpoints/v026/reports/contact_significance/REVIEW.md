# Historical contact practical-footprint ranking (CPU-only)

Reconstructed all142selected clipped pair polygons from native recorded centroid/halfway-to-vertex samples, reproducing the original grouping and stable two-largest selection order. Reconstructed3Darea agrees with the recorded contact pair area to maximum4.55e−13. Inputs and exact receipt/image hashes are bound in `ranked.json`; no old report changed, no Blender/render/crop/model edits.

## Main evidence to inspect at original image scale

| Existing actual frame | Contact family | Potential projected pair footprint | First-surface pixel controls |
|---|---|---|---|
|v024 rear_after|V024 union / V012 terraceledge, +Z66.300003|bboxX450.44…496.56,Y531.97…563.58; polygon562.08px²|482,547 RGB2/4/4;484,555 RGB0/1/1|
|v025 west-lateral|return01 / V008gallery, −X|bboxX705.08…715.38,Y586.08…613.65;137.56px²|706,604 RGB3/6/6;711,591 RGB1/1/2|
|v025 west-lateral|return02 / V008gallery, −X|bboxX699.09…709.08,Y549.28…572.96;115.15px²|700,565 RGB8/13/13;705,553 RGB0/1/1|
|v025 west-lateral|return03 / V008gallery, −X|bboxX696.78…706.67,Y510.78…535.61;119.49px²|698,527 RGB23/29/29;703,515 RGB0/1/1|
|v025 west-lateral|return04 / V008gallery, −X|bboxX696.73…706.43,Y475.53…498.74;109.63px²|698,491 RGB11/18/19;703,479 RGB0/1/1|

These are the largest selected pair patches with at least one front-facing, in-frame, actual first-surface sample. The partner triangle patches for the fourlateralfamilies are also ranked, but **do not add their areas**: pair footprints may overlap. All ranked reachable contacts satisfy the recorded strict plane-distance<1e−7 flag; that is separate from visual causation.

The v024 top contact is not universally buried:2sampled points are first surface in its actual rear receipt. Its562px²number is the full potential pair projection, **not562visible or black pixels**. Four v025side contacts have projected extents roughly10×24–28pixels, with a few near-black and a few ordinary darkstone samples. This locates practical inspection targets but does not establish every pixel's shader cause, the precise visible area or a new repair scope. They are distinct from the currently nominated tall main-shaft strip.

## Thin/subpixel controls and limitations

The next broad-looking hero patch is98.22px²spread across an80×2.09pixel rectangle atX671.5…751.0,Y547.9…550.0 (return01, −Y). Another underside is16.96px²across100×0.98pixels, so overall bboxlength is not visualprominence. Rear-facing narrowedge contacts are~0.7pixelswide; their recordedRGBvalues23…36 show normal shadedstone rather than uniformlyblack imagecells. Manyremainingcontacts project below1px²and must not become individual versiontargets.

Finite native first-hit samples identify reachable positions only; pixel cells include filtering/denoising and may mix surfaces. No planararea↔visiblepixel conversion is claimed. Actual light and camera are unchanged. Normals, planeoffsets, strict flags, full reconstructed polygons, projected bbox/area, samplepositions and RGB are preserved perpair in `ranked.json`. OriginalheroZ24 is included, so undersides are not dismissed by an erroneous all-cameras-above assumption. Art director may rank significance from existing full frames; this report grants no edit authority.
