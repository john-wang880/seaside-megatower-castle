# V020 independent final-model validation

These sibling scripts and two data files are self-contained. They do not load private work directories, failed prototypes, or the old standalone conifer asset. Blender 5.2.3 supplies bpy/mathutils/NumPy; ordinary Python supplies checksum/report checks. Run with assertions enabled, automatic scripts disabled, and no concurrent Blender worker. No command below saves a model or renders.

## Inputs and identities

- `SOURCE`: restore historical v019 from Git commit `15ed444`; verify SHA256 `e71778349c4c65eafbda3eb0a3d0753cd11e1b368a3456c4de1db2f4c0f8647a`.
- `MODEL`: restored accepted v020, SHA256 `673dbbadca22d3dd45dc2f2eb5bde4a9e66851c1ca137da5c2570efc67c77614`, or a fresh recipe result. A fresh result's save bytes may differ: it additionally requires the semantic repeat comparison below against exact accepted v020.
- `QA`: this directory. `OUT`: a new, empty directory outside source/checkpoint paths. Verify every file listed in `FILES.json` before execution. Use new report filenames, never overwrite original evidence.

Substitute explicit absolute paths in these command templates. `BLENDER` is an existing approved Blender 5.2.3 executable; no installation is performed.

```text
BLENDER -b --factory-startup --disable-autoexec --python-exit-code 1 --python QA/validate_preservation.py -- --source SOURCE --candidate MODEL --specification QA/data/specification.json --report OUT/preservation.json

BLENDER -b --factory-startup --disable-autoexec --python-exit-code 1 --python QA/validate_technical.py -- --candidate MODEL --specification QA/data/specification.json --host-plan QA/data/host_plan.json --report OUT/geometry.json

BLENDER -b --factory-startup --disable-autoexec --python-exit-code 1 --python QA/measure_technical_front.py -- --candidate MODEL --specification QA/data/specification.json --host-plan QA/data/host_plan.json --report OUT/front.json
```

**Required report gate:** a zero exit code alone is insufficient. Require `preservation.json.pass == true`, `geometry.json.focused_geometry_pass == true`, `geometry.json.failures == []`, 23 new pieces, `front.json.remaining_duplicate_front_triangle_patches == []`, and every `front.json.pieces[*].covered_by_actual_cornice_front_m2 == 0`. Verify candidate/source SHA before and after. The geometry script deliberately emits detailed failures for negative-fixture diagnosis; its JSON must be checked.

For an independently regenerated `MODEL`, also run:

```text
BLENDER -b --factory-startup --disable-autoexec --python-exit-code 1 --python QA/validate_repeat.py -- --accepted ACCEPTED_V020 --rebuilt MODEL --report OUT/repeat.json
```

Require `repeat.json.pass == true`. The accepted input is pinned to 673…7614; this comparison covers all persistent and evaluated geometry/material/state semantics, not only object counts or reconstructed file size.

## Negative controls

Use a fresh Blender process and a distinct report for each control:

```text
BLENDER -b --factory-startup --disable-autoexec --python-exit-code 1 --python QA/test_negative_geometry.py -- --candidate MODEL --specification QA/data/specification.json --host-plan QA/data/host_plan.json --validator QA/validate_technical.py --control CONTROL --report OUT/negative_CONTROL.json
```

`CONTROL` is `opening_intrusion`, `floating_piece`, or `unrelated_neighbor`. Require `rejected_at_intended_invariant == true` and `candidate_unchanged == true`.

```text
BLENDER -b --factory-startup --disable-autoexec --python-exit-code 1 --python QA/test_negative_preservation.py -- --source SOURCE --candidate MODEL --specification QA/data/specification.json --validator QA/validate_preservation.py --report OUT/negative_hidden_original.json
```

Require `rejected_at_intended_invariant == true` and `files_unchanged == true`. Mutations are in-memory only. No corrupted model is saved.

## Exact scope and numerical limits

All original raw deformation weights—including existing forest masks—remain part of strict source preservation. Only derived evaluated `.select_edge` BOOLEAN/EDGE and duplicate edge-select arrays on the three named SUBSURF Traveler garments have the previously established non-rendering UI exception. Their values are reported separately; original persisted arrays and all other evaluated fields remain exact.

The 23 components are **21 main parts plus two retained, closed terminal wedges**, not the initial unmerged layout. Each wedge retains original occupied exterior volume and has actual area contact with the existing diagonal host end. Contacts are geometry checks, not structural/load certification.

Only the mapped five upper arch pieces may use the original cornice as a secondary seat; its connection to the primary wall is separately checked. The actual west doorway and central approach domains are explicit. This is not whole-castle navigation/accessibility certification.

Coping support is actual near-coplanar shared-surface contact, not fictitious positive-volume embedding. Maximum allowed plane discrepancy is 6 micrometers, measured **locally on the shared patch**, accounting for float32 interpolation. Residual side overlap is reported against a predeclared local bound `2 × float32 ULP(z) × cap length`; the accepted 7.6097e-8 m² residual is not called mathematical zero.

The historical union/exterior proof compared against intermediate 0dd…c6ca. That failed-prototype file is **not a dependency of final-model checks**. Preserve its report as historical evidence with its original input hash; the public recipe may regenerate intermediates for an optional independent union study. Do not present those historical measurements as freshly rerun without their exact inputs.

Actual approach/oblique/hero visual acceptance is separate evidence. These scripts neither recreate the pictures nor claim GUI interaction. Do not relabel earlier v019 HIGH/LOW viewer exports as v020.
