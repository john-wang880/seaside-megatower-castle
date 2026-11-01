# Optional v019 conifer generator

This adapter regenerates the **two authored foreground-tree meshes**, not the castle or a new model version. It needs only Blender **5.2.3** and the byte-exact historical v018 baseline. It does not read a previous tree asset, the accepted v019 model, reference pictures, or the original working directory.

The original executed generator remains archived unchanged. This adapter copies its numerical geometry/RNG recipe and mesh constructor unchanged; `recipe_equivalence.json` records their AST comparison. Historical displacement diagnostics and studio presentation setup were removed, not silently substituted.

## Run

First restore historical v018 from repository commit `89cce41edf648eef6487d54ee1ce2a46bbb0ae17` using that commit's checkpoint restore tool. Required baseline SHA256:

```text
c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd
```

Run from any directory; all inputs and output destinations are explicit:

```bash
/path/to/blender --background --factory-startup --disable-autoexec \
  --python-exit-code 1 --python /path/to/generate_conifer.py -- \
  --baseline /path/to/restored_v018.blend \
  --output-dir /path/to/new-tree-output
```

The output directory must **not exist**. Wrong source bytes, unsupported Blender versions, existing destinations and input aliases are rejected. The baseline is opened with scripts disabled, never saved, and hashed again after generation. No renderer runs. The adapter writes only under the new output directory; Blender itself may attempt its usual user-cache/thumbnail writes.

## Outputs

- `generated_conifer.blend`: only the two `CONCEPT` mesh objects, with original material slots/graphs and identity transforms. No studio lights, camera, duplicate original tree or integration changes.
- `generation_metadata.json`: deterministic counts, coordinate bounds, compact geometry fingerprints, source identity and recipe parameters. Its fingerprint is descriptive, not a replacement for full independent mesh/material validation.
- `component_contact_mapping.json`, `attachment_mapping.json`, `transport_repaired_components.json`: deterministic attachment and repaired-frame metadata.
- `runtime_report.json`: paths, elapsed time, exact Blender build, generator hash and generated file's byte hash. These execution-dependent values are deliberately separate from deterministic metadata.

A generated `.blend` is **not expected to have the historical standalone asset's byte hash**. Two tested fresh builds had distinct file hashes but identical deterministic metadata. The accepted v019 model is used only by a separate validation step, never as generator input. Full semantic comparison must cover mesh coordinates/topology/attributes, material slot order and shader graphs, and object state—not merely triangle counts or these compact fingerprints.

The historical integrator that pins the old `641651…` asset hash should reject this newly generated file. Do not replace its pin or bypass that check casually; use a separately validated integration adapter with explicit generated-file identity and accepted-mesh semantic checks.

## Limits

This is one near-view tree, not a forest-wide recipe. It produces 465,855 vertices / 420,206 triangles. Needle blades are open-backed surfaces; capped woody components intersect rather than forming one combined manifold. Original trunk/context belongs to the baseline and is not included in the two-mesh output. Generation alone does not repeat scene preservation, route, visual acceptance, physical attachment or remote-backup validation.

## Verified adapter result

The isolated generated asset was independently compared against accepted v019SHA `e71778349c4c65eafbda3eb0a3d0753cd11e1b368a3456c4de1db2f4c0f8647a`. Complete mesh semantic snapshots, object transforms, material slots and all four material graphs matched exactly; `independent_semantic_manifest.json` retains the expected/actual digests. Generated attachment mappings also match the accepted archived JSON values exactly. Two fresh-process builds gave byte-identical deterministic metadata; wrong-source, existing-output and input-alias tests rejected without changing baseline or prior output. This establishes generator reproduction, not a new model version or a replacement for downstream integration checks.
