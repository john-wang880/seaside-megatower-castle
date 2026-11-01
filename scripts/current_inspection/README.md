# v026 独立检查副本 / Reviewed inspection copy

**Local actual v026 export/reopen validation passed; remote publication is a separate owner step.** This is an opt-in derived viewer, not a new model version or a replacement canonical file. Do not fabricate a live checkpoint manifest. Publication/remote acceptance are separate owner steps.

Reviewed source: `castle_v026.blend`,47,680,699bytes, SHA256 `efcd894acdc045a30f845f05267662957b656bc7fe0ee4cf48c05fc798b610ee`. The highest numeric live checkpoint MANIFEST must match exactly. Futurev027, stalev025, ambiguousv26/v026, wrong source/hash/size, altered catalog, aliases/symlinks and existing destinations fail closed. No fetching, installation or source overwrite.

## Explicit export (existing Blender5.2.3)

```sh
repo='/path/with spaces/seaside-megatower-castle'
blender='/path/to/blender-5.2.3-linux-x64/blender'
mkdir -p "$repo/work/my inspection"
python -B "$repo/checkpoints/v026/restore_checkpoint.py" --repository-root "$repo" --output "$repo/work/my inspection/castle_v026.blend"
"$blender" --background --factory-startup --disable-autoexec --python-exit-code 1 --python-expr 'import sys; sys.dont_write_bytecode=True' --python "$repo/scripts/current_inspection/export_inspection.py" -- --repository-root "$repo" --source "$repo/work/my inspection/castle_v026.blend" --output "$repo/work/my inspection/castle-inspection.blend" --report "$repo/work/my inspection/castle-inspection.json"
```

Both output/report must be new. Exclusive hardlink publication fails on unsupported filesystems; no overwrite fallback. A process crash can leave a complete viewer without its report: use another new pair, do not blindly delete/adopt it. Handled rollback removes only inodes owned by that invocation. Not a malicious concurrent-path replacement or network-filesystem guarantee. Native Windows/desktop clicks have not been tested; Linux5.2.3 is the historical validated environment, with freshv026 actual export/reopen validation passed. Use ordinary Python, never`-O`.

## Manual viewing

Open the derived file, keeping autoexec disabled. In Text Editor select `INSPECT26 | Run manually for bookmarks.py`, inspect and explicitly Run Script. In a3Dviewport pressN, open Castle检查, choose a bookmark. Text.use_moduleFalse; no load handler, addon installation or auto-registration. Repeat registration is idempotent; foreign/partial ownership is refused.

14bookmarks: hero, west approach, east portal, interior bend, upper stairs, terminal platform, offshore marker, main crown, west crown, bridge close, west lower tier, path context, rear overview, **west lateral overview**. The original13records are preserved exactly except ownedINSPECTnamespace. Only the last view is added; exact historicalv025camera recipe plus actualv026source receipt are archived. It is an elevated architectural view, **not a continuous walkthrough or accessibility certification**.

The viewer adds13owned cameras, one collection, manual Text and provenance marker. Existing hero remains the saved default. Camera selection changes only active camera/viewport view; not geometry, materials, lights, world, frame, samples, aspect/resolution, LOD or visibility. Reference aspect is advisory: manually choose it in your copy if needed. Original hidden rollback geometry and weights remain untouched. Use Blender's standard Solid/Material Preview/Rendered controls manually; no new quality switch/performance claim.

Provenance records the exported source only, not certification after user edits. Re-export from canonical bytes if ownership guards refuse; do not silently repair changed objects.

## Review and provenance

18implementation and24independent puretests passed locally. Fresh actual Blender export/reopen passed:13exact source-state categories,14bookmarks,20negativeAPI cases, repeat registration/unregistration and disabled-script reopen. See VALIDATION.json and fresh reports. No historical report was reused.

Historical v025tool/reports: fixed Git `06cf897ea73fa105ba27cb7dd79af6df18587c9a`, `scripts/current_inspection`. Existingcamera recipe/source hashes are historical and deliberately unchanged. Newwest_lateral pose(−480,−30,180)→(−35,55,105),45mm,1200×866 is exactly the approved actual pose; no additional render was made for this tool.
