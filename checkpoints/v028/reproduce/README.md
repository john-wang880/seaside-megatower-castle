# V028 receiving-chamber reproduction — staged local recipe

Explicit invocation reconstructs the reviewed chamber geometry and its two fixed-position room lanterns from **v027 baseline37c0**. It does not render, publish, automatically accept a model, install software, download anything, or modify the baseline. This bundle is staged, not yet published or end-to-end native tested.

## Inputs and command

Use an existing approved **Blender5.2.3** executable and the byte-exact accepted v027 model:
`37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255`.

```sh
PYTHONDONTWRITEBYTECODE=1 python -B reproduce.py \
  --source '/absolute/path/castle_v027.blend' \
  --blender '/absolute/path/blender-5.2.3-linux-x64/blender' \
  --output-dir '/existing/parent/new rebuild 中文'
```

The output directory must not exist. Inputs/output ancestors may not be symlinks or contain unresolved aliases. Spaces and Unicode are passed as subprocess argument arrays, never shell strings. Unsupported version, wrong baseline, changed bundled code/data, existing output and nonzero process exits fail closed. Standard Python only; no external Python dependencies. Native scripts require factory-empty Blender and disable automatic scripts. Linux is the tested component environment; **Windows is untested**, and no desktop-click/UI claim is made.

## Sequence and outputs

1. Check inventory/source/executable, query existing Blender version and verify input stability.
2. Decompress bundled `native.json.gz`, checking lossless32,041,639-byte source-export SHA83593439…c362e.
3. Run unchanged executed `build_geometry.py`/`planar.py` with the exact frozen plan. Generated geometry must match frozen reviewed payload SHA0d07d8ceb27f44cd3c612392d56b40921e60c7f8afaa522aa04f74c17df817f2 exactly.
4. Run unchanged `integrate.py`; retain `unlit.blend` and `integration.json`, verify all preservation gates and receipt hash.
5. Run unchanged corrected `add_room_lanterns.py`; retain `castle_receiving_chamber.blend` and `lighting.json`. Exactly two current turn-lantern copies at approved fixed locations; no old light/world/exposure edits, no matrix-retuning variant.718 architecture triangle-equivalents +1160 fixture triangles =1878 total.
6. Record logs, argv, process return codes and all initial/final input hashes in `REPRODUCTION.json`. Failures retain diagnostics and intermediate output, never an acceptance status.

Reproduced **.blend file bytes may differ** because of native save metadata. Blender executable/code/input bytes must remain stable. Independent full persistent/evaluated semantic comparison against the accepted candidate, actual saved geometry/route/fixture checks and negative controls remain mandatory. This driver does not replace those tests; successful status is explicitly `REPRODUCED_PENDING_INDEPENDENT_SEMANTIC_QA`.

## Frozen source and provenance

`FILES.json` inventories every executable/data/document in this bundle except itself. `PROVENANCE.json` confirms exact byte copies of the executed geometry, integration, corrected lantern and snapshot scripts. Frozen plan directory retains its own exact manifest. No private candidate/standalone asset is required; the gzip source export and explicit v027 baseline are sufficient inputs. Superseded initial lantern transform code is deliberately not used.

`test_driver.py` passes nine pure tests, including a mocked full three-stage pipeline with exact argv checks, failed process and failed JSON-gate propagation, changed inventory, wrong source before process launch, symlink/existing output, unsupported versions and optimized Python. Tests inherit `PYTHONDONTWRITEBYTECODE=1`. This is not a claim that the new controller has already completed a native rebuild; owner will schedule that separately after remaining visual gates.

All dimensions are scene-coordinate units, not engineering-certified metres or structural/accessibility certification. This is a deliberate small receiving-chamber addition, not repair of an allegedly missing historical room.
