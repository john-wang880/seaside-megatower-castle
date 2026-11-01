# v023 local path conformance — unaccepted technical candidate

Source99156d… was never saved/modified. Full specification in `plan.json`; exact executed self-contained `scripts/build.py`, sibling`overlay_math.py` and`deep_snapshot.py` need only pinnedsource+plan, not private diagnostic exports.

Scope: sourcepathfaces1140–1259,rows95→105; native invertedMask on63interiorvertices672–734 retains all original raw geometry. ActualMask test confirms exactly1392outside face records remain. One new patchmesh442vertices/800triangles replaces120coarse triangles; no wholepath copy, no newroute/V009connection.

Actual evaluated terrain triangleoverlay preserves each oldXY/material domain in doubleprecision before float32storage. Interiorheightterrain+.021; oldcrossseamZ retained. All14original end-seam vertices are bitexact, inserted seam intersections use originaledge linear interpolation. LateralZ may move at fixedXY. Original three materialdatablocks/graphs and world remain unchanged. Allfaces retain source downwardwinding, flatshading and open-decalnature.

CandidateSHA `c4b1dda3b8f70e4c8cb0171834b2150b6d7610f6296847362fd204b2dfa7ad51`,47,628,324bytes. Localbuild reports8gatespass; zero collapsed/zeroarea/duplicate triangles. Provisional fullaffinegap relative to each generatingterraintriangle0.01701737…0.02565516, within predeclared[.016,.030]. Zchanges range−0.08543975…+0.10524551coordinateunits, so this is **not a blanket upwardlift**. Exactsource14seamcoordinates retained; alloriginalrawmeshes compare exact after onlyownedweights normalization. `source_snapshot.json` preserves deep original semantic baseline.

Independent actualsavedmesh checks are still required: re-overlay everynewtriangle againstactualterrain, XYdomain/materialpartition equality within derivedfloat32precision, seaminterpolants and no cracks/Tjunctiongaps, maxsupportedgap/grade, fullpersistent and evaluatedattribute complement, and negativecontrols. Generatingtriangle affinity alone is not the final terrainproof after rounding. Existing source-style sharedcollinear seam knots are acceptable only if precision/coverage is explicitly verified, not silently waved away. No structuralcapacity/navigationcertification claim.

No render was performed. Actual samecamera visualgate and control/hero review remain pending. Rollback requires disabling the ownedMask AND hiding the newpatch together; otherwise duplicate representation or a missingpatch appears. Originalsourcegeometry, otherpathrows, terrain, trees, architecture, previousMasks and all materials stay recoverable.
