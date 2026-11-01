> Local actual v025 export/reopen validation passed. Remote publication and fresh-remote verification are separate owner steps.

# 最新已审核模型的独立检查副本 / Current reviewed inspection copy

**Opt-in, camera-only derived copy.** The canonical `.blend` is never saved. No new model version, render, installation, network request, autoexec, handler, addon, geometry, material, lighting or LOD toggle. Existing historical navigation/film/quality tools remain immutable.

This catalog is reviewed for **v025 only**, SHA `8a3590082c99a69d50d444f77165fae57fb611cf069cecda03fdf0c6c17cadd2`,47,663,562bytes. The exporter resolves the highest **numeric** existing `checkpoints/vNN/MANIFEST.json` under your explicit repository root. Unknown future latest, stale source, wrong byte count/hash, corrupt manifest/catalog or a changed catalog all fail clearly—never silently fall back to v025. Catalog bytes are hash-pinned in code, not trusted merely because JSON says a source is reviewed.

## Existing Windows tools: PowerShell example

Native Windows execution/UI has **not** been tested. These commands are a quoted workflow for existing Python and Blender5.2.3, not an installation instruction. NTFS hard-link support is required for exclusive publication; unsupported filesystems fail rather than overwriting. Use ordinary Python, not `-O`.

```powershell
$repo = 'C:\My Projects\seaside-megatower-castle'
$blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$tool = Join-Path $repo 'scripts\current_inspection'
$work = Join-Path $repo 'work\my inspection'
New-Item -ItemType Directory -Force -Path $work | Out-Null
$source = Join-Path $work 'castle_v025.blend'
python (Join-Path $repo 'checkpoints\v025\restore_checkpoint.py') --repository-root $repo --output $source
# Pick NEW names; existing files, symlinks and path aliases are rejected.
$output = Join-Path $work 'castle-inspection.blend'
$report = Join-Path $work 'castle-inspection.json'
python (Join-Path $tool 'export_inspection.py') --preflight-only --repository-root $repo --source $source --output $output --report $report
& $blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python (Join-Path $tool 'export_inspection.py') -- --repository-root $repo --source $source --output $output --report $report
```

The published tool lives at `scripts/current_inspection`. The shared restoration CLI is unchanged from the inspected v023 CLI and accepts both shown `--repository-root` and `--output` flags. Do not pass a positional source `.blend` to Blender: the exporter validates bindings before loading it itself with scripts disabled. Existing outputs/reports are never replaced, adopted or deleted. Use a new output/report pair after an interrupted/failed attempt. Publication is atomic per file, not a two-file database transaction: a process crash between links can leave a complete viewer without its report; do not reuse or delete that file blindly. Handled publication failures roll back only files whose inode is still owned by this attempt. The tool does not claim malicious concurrent path-replacement resistance or network-filesystem support.

## Linux example (existing software)

```sh
repo='/path/with spaces/seaside-megatower-castle'
blender='/path/to/blender-5.2.3-linux-x64/blender'
mkdir -p "$repo/work/my inspection"
python "$repo/checkpoints/v025/restore_checkpoint.py" --repository-root "$repo" --output "$repo/work/my inspection/castle_v025.blend"
"$blender" --background --factory-startup --disable-autoexec --python-exit-code 1 --python "$repo/scripts/current_inspection/export_inspection.py" -- --repository-root "$repo" --source "$repo/work/my inspection/castle_v025.blend" --output "$repo/work/my inspection/castle-inspection.blend" --report "$repo/work/my inspection/castle-inspection.json"
```

## Open and use manually

1. Open the **derived output**, not the canonical source. Keep automatic Python execution disabled.
2. In Blender's Text Editor choose `INSPECT25 | Run manually for bookmarks.py`; inspect it, then explicitly **Run Script**.
3. In a3D viewport press **N**, open **Castle检查**, and choose a bilingual bookmark.
4. The thirteen views are hero, west approach, east entrance, interior bend, upper stairs, terminal platform, offshore marker, main crown, west crown, bridge close, western lower tier, existing path context, and elevated rear overview. These are independent inspection views, not a certified continuous walkthrough or general accessibility proof.

Registration is manual-only (`Text.use_module=False`), repeat registration is idempotent; foreign/partial ownership or hidden/excluded camera collections fail rather than being adopted or unhidden. Bookmarks change only the current scene camera and viewport camera-view state; render samples, resolution/aspect, frame, world, lights and geometry remain unchanged. Default saved view is the original hero camera. Reference aspect/resolution is recorded per view and shown in the operator message; for exact historical rendering manually select that aspect in **your copy**. Selecting a camera does not imply pixel-identical framing under a different aspect.

For navigation responsiveness use Blender's standard **Z → Solid / Material Preview / Rendered** modes. Any quality adjustment is optional and manual in the derived copy. No new LOW tree toggle, geometry deletion, automatic sample reduction or performance claim is included. Original hidden forest rollback data stays hidden; no visibility flags are changed.

The scene marker records source/export provenance only. It is **not** a certification of later user edits, present geometry integrity or continued correspondence to canonical bytes. Camera/text/ownership changes can make bookmark guards refuse; re-export from verified canonical bytes instead of silently repairing/adopting changed objects.

## Verification status

This refresh preserves all12 original camera records and adds exactly one explicitly approved rear overview (13 bookmarks,12 added cameras). Its matrix/data are copied from the actual v025 rear render recipe and hash-bound receipt; no new render or other camera is added. Historical camera recipes remain exact. Fresh local tests passed: 18 implementation and 24 independent pure tests, 13 exact source-state categories, all 13 manual bookmarks, 20 negative API cases, repeat registration/unregistration and disabled-script reopen. See VALIDATION.json and fresh reports; historical reports were not reused.

Historical v024 tool and validation: fixed Git `0d332990a252bbb2d51f73e69bdefd34e2931c19`, path `scripts/current_inspection`. Existing `provenance/` recipe files retain historical v018/v021/v022/v023 paths and hashes. No old acceptance report is relabeled.

## Rear overview bookmark
`rear_landward` is an elevated architectural inspection at1200×866 reference aspect, not a human-eye walk or proof of continuous circulation/accessibility. Source pose(−50,500,210) targets(−35,55,105),45mm. Exact copied recipe/actual-source8a359 receipt live in provenance/. Original world/lights/render quality remain unchanged; bookmark selection still changes no aspect or samples automatically.
