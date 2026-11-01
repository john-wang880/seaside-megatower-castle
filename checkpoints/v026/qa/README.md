# V026 independent read-only QA

Inputs: historical v025 SHA `8a3590082c99a69d50d444f77165fae57fb611cf069cecda03fdf0c6c17cadd2`; accepted v026 SHA `efcd894acdc045a30f845f05267662957b656bc7fe0ee4cf48c05fc798b610ee`. Use Blender5.2.3, Python with NumPy, and new external report directory. No source save or render occurs.

```sh
python -B run_qa.py --source /absolute/castle_v025.blend --candidate /absolute/castle_v026.blend --output-dir /absolute/new-qa --blender /absolute/blender
```

For a separate regenerated save, add `--accepted /absolute/accepted_v026.blend`; exact full persistent/evaluated semantic comparison runs first. A different save hash alone is not acceptance. Inputs and complete bundled file inventory are checked before/after. Symlink, traversal, existing output, optimized Python and wrong historical/source references fail closed. Every native subprocess explicitly disables bytecode and autoexec.

The source visible mainshaft gains an identical owned single-user mesh copy and16 owned weights/Mask; its hidden V004 original, original shared mesh and calibrated OBJECT material remain exact. The expected data-pointer change and original mesh users2→1 are explicit. Native LOW restores source rendering while the derivative graph remains; full undo restores original pointer/users2 and removes owned additions.

Independent saved-surface clipping proves the two actual-box occupied union rather than an AABB substitute; it separates missing and double-covered areas. Actual maximum plane displacement was0, duplicate area residual2.27e−13 and volume residual2.91e−11. Declared coordinate budget is4 float32 ULP (6.103515625e−5), not mathematical exactness. Two pre-existing top contacts (140 and18.84998894 pairwise area) must remain; no global coplanar-free claim.

Checks: six native calls (preservation/LOW/full undo, adjacency, four injected model negatives), plus one semantic native call for a rebuild; five exported-geometry negatives; six convex partition controls plus equal-area missing/duplicate cancellation control; nine exact broadphase/contact controls including known140-area original geometry. Four native negative fixtures must fail at the intended assertion, not setup. The three established Traveler SUBSURF evaluated UI edge-selection fields are separately normalized; raw fields and all geometric arrays remain strict.

The initial optimized adjacency report failed only NumPy-bool JSON serialization. Its exact log/code are retained as superseded setup provenance. Three-point conversion to native lists fixed output encoding; the final optimized-array path passed all nine controls and actual native replay. No candidate/tolerance change.

Historical v024/v025 adjacency-method correction is a separate self-contained package and must accompany release notes. Some inherited coplanar contacts reach first surface in finite camera samples; zero-neighbor historical claims are withdrawn, not silently reused. Actual v026 lateral/front/rear visual approval is outside this technical runner.
