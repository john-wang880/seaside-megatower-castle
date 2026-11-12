# Offshore arrival platform review: retain S30

No S31 candidate was built. Source is the verified S30 at 6af1c12842e0fef3a0f4bf0c1cd63c0ade639833, native model SHA256 a6c9715064ae0ea8ee58f369f46ceb3352bfc84fb53687b30bffd35bf38bd9ce. A previous task has already rejected adding repeated small interior props; this is a separate architectural-use investigation.

The broad stair joins an upper platform; the final arrival step is offset to its northwest. We investigated whether a low L-shaped boundary at the platform's north/east edges would clarify arrival while retaining the complete south stair opening and northwestern final step.

The first image is an elevated structural overview, not a standing-person view. It shows the actual stair, platform, tower-foot geometry and lower original base. The second is a normal stair eye-height inspection. The evidence does not establish that a new north/east wall would clarify an existing route; it risks arbitrarily partitioning the original platform and dominating the approach to the tower wall. Neither image demonstrates a new missing safety barrier, dangerous condition, broken entry, or a comprehensively traversable internal route. Lack of an object named guard is not evidence of missing architecture.

Decision: do not build the proposed wall. Preserve source geometry. Do not repeat the proposal merely because the platform looks bare. S30 remains the active verified model. No new model release or old-model retirement is justified by this review.

Reproduce in a writable copy using pinned official Blender 5.2.3 from the S30 documentation:
- blender -b -t 4 --python survey.py -- /path/to/S30/candidate.blend
- blender -b -t 4 --python approach_survey.py -- /path/to/S30/candidate.blend
- blender -b -t 4 --python export_environment.py -- /path/to/S30/candidate.blend

The first two scripts use original lighting, temporary unsaved cameras and 16-sample renders. Geometry export selects evaluated ordinary MESH objects with hide_render false whose triangle AABBs overlap the documented local volume, not dependency-graph instances or a whole-scene navigability test. Model is never saved or changed.
