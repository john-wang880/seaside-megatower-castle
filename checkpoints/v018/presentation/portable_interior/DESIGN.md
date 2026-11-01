# Opt-in portable interior-video workflow — design only

Historical design proposal, subsequently approved for bounded implementation on2026-11-01. Implemented sibling lives here; README and test reports describe current validation. This design alone never authorizes Windows execution, installation, model changes or a long rerender. Existing V018 video and its51frozen payload files stay byte-identical.

## Findings and benefit

The frozen runner imports `fcntl`, scans `/proc`, and requires exactly nine affinity CPUs. Its worker imports `resource` and calls `os.sched_getaffinity`. A wrapper that merely changes the lock cannot make that worker portable. `orbit_common.py` needs Pillow and uses assertions. Existing source/plan/settings/camera checks are valuable and must not be weakened for platform convenience.

Benefit: a Windows user can restore the verified source, inspect a dry-run, render the same bounded pilot, explicitly approve it, and resume missing frames without learning cloud paths. This does not make rendering cheap: the accepted 336-frame cloud run used about 8.29 render-hours, excluding approval pause; no Windows speed estimate is established. Existing completed MP4 remains the fastest viewing option. This new workflow is for intentional rerendering, not a prerequisite for opening/viewing the model.

## Proposed files, outside frozen archive

New opt-in directory `tools/portable_interior_video/` (subject to owner naming approval):

1. `run.py`: new coordinator derived narrowly from frozen runner. `--stage pilot|full`, `--dry-run`, explicit source/Blender/output paths, explicit approval path; encoding optional with explicit ffmpeg/ffprobe paths or discovery. No renderer startup on import/help/dry-run.
2. `worker.py`: small separately identified fork of frozen worker. Preserve exact source/frame/camera/quality/provenance checks; replace platform-only metrics, acquire execution lease itself, then open source in memory. Never save source. Launch Blender with `--disable-autoexec --python-exit-code 1 --python worker.py -- --source ...`; do not load the model before the worker acquires its lease.
3. `platform_runtime.py`: native nonblocking exclusive lock context and optional telemetry, with no new third-party dependency. Lazy imports only. Linux RSS retains `peak_rss_linux_kib`; other platforms emit null. CPU duration uses `time.process_time()` with explicit metric description. Affinity is optional/null if unavailable; CPU count is descriptive, not a nine-CPU requirement. Eight render threads remain fixed by exact existing plan.
4. Focused standard-Python tests and a short PowerShell/Linux command guide. No framework, daemon, scheduler, installers or automatic upload.

Read frozen `final_plan.json`, `final_motion.py`, and `orbit_common.py` through explicit resolved paths and pinned SHA identities; do not patch or monkeypatch them. Their original 51-file checksum manifest must pass before and after testing. Include all new executable helper hashes, frozen input hashes, schema identifier, source hash and execution profile in a new run identity. Do not imply byte-identical pixels across OS/builds.

## Restore → inspect → pilot → review → resume

- Existing `python checkpoints/v018/restore_checkpoint.py` performs chunk/full SHA restoration. Keep restore explicit and non-overwriting; the new runner accepts the resulting exact source path. No automatic downloads or software installation.
- Dry-run checks Python version/optimization, Pillow availability, source SHA, immutable inputs, output safety, exact plan shape, compatible executable path and pending/validated frame status. It must not create attempts or render. Dependency/version checks needing Blender execution are a separately explicit preflight, not hidden in dry-run.
- Pilot writes to a NEW output namespace. Render exactly the existing 25 selected poses, then stop. Old cloud approval, old receipts and old frame directories cannot authorize or populate this new run.
- Owner reviews this new pilot and creates an identity-bound approval matching its exact `pilot_complete.json` hash and indices. No automatic approval generation or generic boolean bypass. Full stage refuses absent, stale or cross-run approval.
- Full stage validates/skips only frames produced under this new identity, then renders missing frames. Encode only the verified 336-frame set, 12fps/28s/960×694, H264/yuv420p, no interpolation/audio. Record tool versions, full command, input manifest and video hash; ffprobe/decode checks required before declaring completion.

## Locks and orphan workers

Two different locks, not one misleading coordinator-only lock:

- **Output coordinator lease:** runner opens a stable lockfile in the new run directory and retains it through authoritative validation, workers and encoding. Use `fcntl.flock(LOCK_EX|LOCK_NB)` on POSIX, `msvcrt.locking(fd, LK_NBLCK, 1)` on Windows with binary file and seek to byte zero before lock/unlock. Never unlink/recreate lockfiles, never bypass based on age or PID, never delete someone else's lock. Busy, unsupported or unexpected locking failures stop with a clear error.
- **Per-user execution lease:** a stable local lock path shared by this portable tool's runs, independent of output directory. The Blender worker opens and holds it itself from before source loading through render and receipt write. If the coordinator dies while Blender survives, the worker's lease survives and another cooperative worker cannot start rendering. The coordinator also acquires this lease for encoding. No reliance on inherited lock semantics.
- Acquire output lease FIRST; then re-read/revalidate source/code/identity/approval/pilot under the lease before any writes, quarantines or skips. Earlier dry-run/precheck is not authoritative. Recheck relevant hashes immediately before launch and in worker before rendering. Publish success only after child exit and receipt validation.
- Restart during an orphan render may obtain the output lease, but it must fail/stop on the execution lease rather than launch an overlapping render. Do not kill arbitrary Blender processes. Use unique attempt paths; an orphan completion is not automatically promoted/relabelled by a new runner.
- Process enumeration can supplement diagnostics but is not an atomic exclusion guarantee. Native execution locks guarantee exclusion only among cooperating workers using the same local lease path/user context. A manually launched Blender does not participate. Document this explicitly and require user-managed avoidance of unrelated heavy work; do not pretend Windows has `/proc` or silently claim machine-global exclusion. If owner requires strict exclusion of arbitrary external processes, that is a larger design needing separately reviewed Windows process management, not a hidden fallback.
- Scope supported execution to local filesystem/output storage. Network share, synchronized folder and cross-host locks are not established by mocks; do not advertise distributed locking.

## Fail-closed integrity and interrupted flows

- Explicitly reject `sys.flags.optimize != 0` in runner and worker before any work because the retained validator/worker checks use assertions. New safety/error paths use explicit exceptions. Blender is launched with `--python-exit-code 1` so a Python exception cannot look like success.
- Preserve exact expected Cycles, render, view, image, camera gate, source frame and Blender version checks. OS/build differences may cause an understandable mismatch; report differing fields and stop. Never auto-normalize platform fields or relax settings to get a render through.
- Source/output alias checks include canonical paths and existing-file identity where available. Reject outputs inside frozen payload trees or historical final runs; refuse nonempty unrecognized output directories. Case-insensitive Windows aliases/reparse points require tests and conservative rejection when uncertain. Never overwrite source, accepted historical PNGs, MP4s, receipts or approval evidence.
- New run schema prevents old approval/receipt migration even if camera recipes match. Frame validation retains source/plan/worker/camera/settings hashes, actual image dimensions/mode and decoded pixels. New helper/runner identity is bound at run level and to each new receipt.
- Atomic same-filesystem temp-write/replace for manifests; flush/fsync journal. Validate completion from frame receipts, not trusting a truncated final journal line. Missing/corrupt attempts remain recoverable evidence; quarantine invalid final frames only under lock and correct run identity. Never overwrite a valid frame.
- Retry starts by checking locks and current outcome. Parent interruption: wait/stop own child deliberately when possible; unexpected coordinator death is covered by worker lease. A failed child stops the run with retained attempt/log and no completion marker. No endless auto-retry.
- Encoding failure leaves all raw frames intact. Missing ffmpeg/ffprobe is an explicit encoding blocker, not permission to install; `--skip-encode` may complete frames only. Missing Pillow stops validation/render preflight. User-supplied paths support spaces/Unicode via subprocess argument arrays, never shell interpolation.

## Test gates before any release

Linux standard-Python tests plus mocked Windows branch behavior only initially:

- Import/help/dry-run never import bpy/start a process; missing Pillow/tool paths give actionable errors, no auto-install.
- Native POSIX two-process contention and worker-survives-parent test; fake worker, not full Blender render.
- Mock Windows byte-zero seek, nonblocking lock, unlock/close, busy/error cases; no claim this substitutes actual Windows kernel test.
- Post-lock changed identity/approval/source negative tests; output alias/case-path cases; duplicate starts; missing lock capability; no age override.
- Missing `resource`, unavailable affinity/OSError metrics remain optional; unsupported units stay null.
- Wrong source/plan/code/worker/recipe/settings/PNG hashes and old approval all rejected; valid new frames skip; partial/corrupt outputs quarantine only after correct identity/lock; interrupted journal recovery.
- `python -O` rejects before writes/Blender; worker optimized execution likewise rejected; command contains `--python-exit-code 1`.
- Fixtures test fresh pilot gate and full refusal, encode-only resume, missing ffmpeg, failed child/encoding, source preservation, frozen51hashes unchanged.
- Optional owner-approved single Linux actual still can verify the new worker at exact plan quality after code tests. No 25/336-frame rerender implied. Actual Windows Blender, locking and OS-specific expected-settings compatibility remain UNTESTED until a separately authorized Windows validation opportunity.

## Decision requested

Approve this bounded new-package implementation/test scope, or retain documented Linux-only video tooling. Do not start implementation, install dependencies, touch the user's PC or run a new pilot on this design alone.

References: Python official native lock API descriptions: https://docs.python.org/3/library/msvcrt.html and https://docs.python.org/3/library/fcntl.html (consulted2026-11-01). Implementation should use only long-established documented functions, not assume the user's Python matches the documentation's current release.
