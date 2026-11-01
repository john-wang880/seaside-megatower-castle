# Historical v024/v025 adjacency correction replay

This is an additive methodological correction. Original accepted models and old reports remain unchanged; see METHODOLOGY_NOTICE.md. No model cleanup or render is performed.

```sh
python -B run_recheck.py --source /absolute/castle_v024.blend --candidate /absolute/castle_v025.blend --output-dir /absolute/new-historical-qa --blender /absolute/blender
```

`--source` is exact89f9…c856 v024; `--candidate` is exact8a359…add2 v025. No rebuilt substitutes. Four native loads replay two full evaluated-neighbor scans and two finite camera-ray checks. Stored operand geometry/full-source preservation reports are explicit pinned historical evidence for original-boundary linkage; no unavailable private workspace/model dependency. All actual camera receipts and nine-control source geometry are included. Host Python needs NumPy; native runtime is Blender5.2.3.

The explicit triangle AABB/all-vertex plane filter replaces BVH.overlap as coplanar broadphase. Original BVH-related zero-neighbor conclusions are superseded. Contact tests separate same/opposite normals, strict1e−7 plane classification and tolerance-only near planes; report threshold1e−8 pair area and plane budget3.0517578125e−5. Pairwise totals are not unique exposed areas.

Finite visibility samples select two largest triangle-pair patches per rounded plane/normal/orientation class, then centroid and halfway-to-vertex points. Geometric first-surface rays do not simulate pixel filtering or material transparency and are not global burial certification. Completed evidence found2 v024 and53 v025 same-facing in-frame first-surface samples. All contact triangles remain on original occupied boundaries and neighboring geometry is unchanged. Deferred latent contact candidates must not be portrayed as newly introduced union defects or all harmless.

Evidence files include original script bytes as non-executed `.py.txt` provenance. They may contain historical workspace labels; runtime scripts have no workspace-relative imports. Every output stays in a fresh external directory and full package/model inventory remains immutable.
