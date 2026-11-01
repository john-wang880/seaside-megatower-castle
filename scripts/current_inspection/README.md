# 最新已审核模型的独立检查副本 / Current reviewed inspection copy

**Opt-in, camera-only derived copy.** The canonical `.blend` is never saved. No new model version, render, installation, network request, autoexec, handler, addon, geometry, material, lighting or LOD toggle. Existing historical navigation/film/quality tools remain immutable.

This catalog is reviewed for **v024 only**, SHA `89f9f6a8a57103d99100935b96624469ddf1fd52b9703e0d9177a352e735c856`,47,631,759bytes. The exporter resolves the highest **numeric** existing `checkpoints/vNN/MANIFEST.json` under your explicit repository root. Unknown future latest, stale source, wrong byte count/hash, corrupt manifest/catalog or a changed catalog all fail clearly—never silently fall back to v024. Catalog bytes are hash-pinned in code, not trusted merely because JSON says a source is reviewed.

## Existing Windows tools: PowerShell example

Native Windows execution/UI has **not** been tested. These commands are a quoted workflow for existing Python and Blender5.2.3, not an installation instruction. NTFS hard-link support is required for exclusive publication; unsupported filesystems fail rather than overwriting. Use ordinary Python, not `-O`.

```powershell
$repo = 'C:\My Projects\seaside-megatower-castle'
$blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$tool = Join-Path $repo 'scripts\current_inspection'
$work = Join-Path $repo 'work\my inspection'
New-Item -ItemType Directory -Force -Path $work | Out-Null
$source = Join-Path $work 'castle_v024.blend'
python (Join-Path $repo 'checkpoints\v024\restore_checkpoint.py') --repository-root $repo --output $source
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
python "$repo/checkpoints/v024/restore_checkpoint.py" --repository-root "$repo" --output "$repo/work/my inspection/castle_v024.blend"
"$blender" --background --factory-startup --disable-autoexec --python-exit-code 1 --python "$repo/scripts/current_inspection/export_inspection.py" -- --repository-root "$repo" --source "$repo/work/my inspection/castle_v024.blend" --output "$repo/work/my inspection/castle-inspection.blend" --report "$repo/work/my inspection/castle-inspection.json"
```

## Open and use manually

1. Open the **derived output**, not the canonical source. Keep automatic Python execution disabled.
2. In Blender's Text Editor choose `INSPECT24 | Run manually for bookmarks.py`; inspect it, then explicitly **Run Script**.
3. In a3D viewport press **N**, open **Castle检查**, and choose a bilingual bookmark.
4. The twelve views are hero, west approach, east entrance, interior bend, upper stairs, terminal platform, offshore marker, main crown, west crown, bridge close, western lower tier, existing path context. These are independent inspection views, not a certified continuous walkthrough or general accessibility proof.

Registration is manual-only (`Text.use_module=False`), repeat registration is idempotent; foreign/partial ownership or hidden/excluded camera collections fail rather than being adopted or unhidden. Bookmarks change only the current scene camera and viewport camera-view state; render samples, resolution/aspect, frame, world, lights and geometry remain unchanged. Default saved view is the original hero camera. Reference aspect/resolution is recorded per view and shown in the operator message; for exact historical rendering manually select that aspect in **your copy**. Selecting a camera does not imply pixel-identical framing under a different aspect.

For navigation responsiveness use Blender's standard **Z → Solid / Material Preview / Rendered** modes. Any quality adjustment is optional and manual in the derived copy. No new LOW tree toggle, geometry deletion, automatic sample reduction or performance claim is included. Original hidden forest rollback data stays hidden; no visibility flags are changed.

The scene marker records source/export provenance only. It is **not** a certification of later user edits, present geometry integrity or continued correspondence to canonical bytes. Camera/text/ownership changes can make bookmark guards refuse; re-export from verified canonical bytes instead of silently repairing/adopting changed objects.

## Verification status (v024 refresh)

The refreshed v024 runtime passed18 implementation tests,24 independent pure tests and actual Linux Blender5.2.3 export/reopen checks. All13 source categories, including original masks/deform weights and evaluated geometry, remain exact after removing only owned viewer additions. All12 bookmarks,20 API refusal cases, repeated registration/unregistration and disabled-script reopen passed. Fresh viewer SHA `fa76c374f9916dd821565f49ec2bd10d84bfbef4484019cff220a4263fb4f9ce`; source89f9 and all runtime inputs stayed unchanged. See VALIDATION.json and the fresh reports; no v023 receipt is relabeled. Background/headless API tests are not native Windows execution or desktop clicking; no performance or later-user-edit certification.

Historical v023 tool and validation remain recoverable at fixed Git commit `4a7cd90ceb9d545de67951cae536e2c4604a547a` under `scripts/current_inspection`. The unchanged `provenance/` files describe the historical camera recipes, not new v024 renders. Historical v018/v021/v022/v023 recipe paths and hashes remain exact. This refresh retains the same12 views, matrices, labels, intent and quality behavior; it does not add the rear discovery camera.
