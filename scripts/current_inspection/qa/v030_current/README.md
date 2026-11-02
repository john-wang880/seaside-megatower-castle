# v030 optional inspection-copy independent QA

This is a separate acceptance adapter. Historical v029 scripts/reports are not overwritten. Exact v030 source `9f020b7e…feda35`, 47,842,841 bytes; target-only original-tree baseline v018 `c46b581a…ef44cfd`, restored from fixed Git history `89cce41`. Runtime needs only the current canonical source; the historical baseline is an explicit independent QA dependency, not a viewer dependency.

Requires Blender 5.2.3 and Python stdlib; existing numpy is used by snapshot helpers. No install, render or source save. Linux native tested. Windows path mocks are not native Windows testing; recording `Panel.draw` calls are not a desktop GUI interaction claim.

## Export then check, sequential exclusive native slot

Optional `export_four.py --repository-root REPO --tool TOOL --source SOURCE --blender BLENDER --output-dir NEW` creates default, off, high and low copies. REPO must contain the actual reviewed highest numeric v030 MANIFEST. TOOL is the current published tool directory. Output must be external and new. The default copy has index/tree OFF; other copies enable the index, with tree OFF/HIGH/LOW respectively.

```sh
PYTHONDONTWRITEBYTECODE=1 python -B run_qa.py \
 --blender /absolute/blender --tool /absolute/current_inspection \
 --source /absolute/castle_v030.blend --baseline /absolute/castle_v018.blend \
 --default /absolute/viewers/default.blend --default-receipt /absolute/viewers/default.json \
 --off /absolute/viewers/off.blend --off-receipt /absolute/viewers/off.json \
 --high /absolute/viewers/high.blend --high-receipt /absolute/viewers/high.json \
 --low /absolute/viewers/low.blend --low-receipt /absolute/viewers/low.json \
 --output-dir /absolute/new_results
```

Three sequential native phases: four-mode deep/lineage preservation; positive manual registration/reexecution/reopen/bookmark/index/quality flows; selection and panel negatives. Runner checks 13 pure comparison/scope tests, all report gates, and whole QA/tool/model/receipt immutability. No bytecode, optimized execution, symlink paths, parent traversal or output overwrite. Source and baseline have distinct exact pins.

Expected: 13 emitted source categories in all four copies; 20 bookmark records/19 added cameras; six groups/51 target entries; all five previous group records and all 20 camera records exact. Twenty-action interleaving deliberately exercises fittings and near-tree four times each; LOW succeeds on16 and refuses four hidden-tree actions. Total repeated LOW refusals64. Quality controls27, selection controls37, direct panel cases6 (valid six buttons, foreign/unmarked/stale/disabled zero). Index actions do not change camera/view or quality flags; test-owned bookmark UI fields are explicitly restored before aggregate comparison. Partial selection exception rollback restores both selected set and active object.

`runtime_pins.json` and `expected_scope.py` bind reviewed runtime/catalog/index. `predecessor.json` retains the exact old view and group records. `controls/test_preflight_v030.py --tool TOOL --source SOURCE` runs24 additional path/publication controls. No source mesh bulk is bundled; snapshots are derived from the explicitly hashchecked model inputs.

## Provenance

`reports/` contains the completed local native acceptance and receipts, not claims about a future remote run. Frozen executed adapter code is unchanged in this copy. One initial native setup refusal retained a v029 redundant catalog hash and stopped before model load; the literal was corrected to the already reviewed v030 hash, with no runtime/model changes. A separate pure future-version fixture initially collided with v030; corrected to v031. Both setup logs remain in `provenance/`. Prior historical RNA-wrapper and Edit Mode harness lessons are retained through corrected predicates; they are not new v030 runtime failures.

Source identity is provenance, not continued certification after user edits. The index selects visible reviewed targets only; no unhide, canonical rename, editing, deletion, quality switch or structural safety assertion. Existing manual HIGH/LOW is the same six-flag target-only feature.
