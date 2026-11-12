# Stores retrieval review: retain S29, do not publish S30 hardware

This is a negative design decision and bounded read-only geometry investigation, not a new model version. Model remains S29 (candidate SHA256 740efdecdc3a7b081b44c244d8113b678a03aeb7cc377764195354588c00bbd6). Restore it with ../../studies/shore_shelves_20261112/restore.py from the same branch.

The actual original-lighting entrance image shows four pre-existing lidded bins in the two racks; the room is not empty. Proposed front pulls and rear hinges were rejected by independent visual review: shadow and rack rails obscure the bins, rear hinges are hidden, and the solid closed bodies do not become operable storage merely by adding hardware. No added lights, altered camera in the saved model, or decorative model edits were made. The model remains unchanged.

The next check examined actual bin envelopes translated horizontally into the existing aisle. The four rectangular swept envelopes did not penetrate the tested rack, rear-brace or room-shell triangle surfaces. Touching shelf faces are excluded with documented tolerance. This uses raw (not evaluated modifier) mesh surfaces for six named obstacles. This is a boundary-surface test, not a volume-containment, full human ergonomics, grasp, load, lid opening, or all-scene collision certification. It provides no justification for a route repair.

Reproduce using the pinned Blender 5.2.3 LTS from the S29 README:
- blender -b -t 4 --python extract_survey.py -- /path/to/S29/candidate.blend
- python retrieval_audit.py (NumPy required)
- blender -b -t 4 --python view.py -- /path/to/S29/candidate.blend

Continue with a broader architectural-use investigation only when an actual visual/use benefit is established. Do not repeat this hardware proposal or add more coast stones to manufacture progress. No payload retirement is warranted by this review; S29 remains the active complete model.
