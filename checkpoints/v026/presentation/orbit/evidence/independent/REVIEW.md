# Independent exterior-orbit runtime review

CPU-only pilot-readiness gate: PASS. Report `report.json` binds the exact recipe inventory; no Blender, actual render, encode or full-sequence authorization occurred in this review.

The twelve independent test methods include thirteen separate metadata-corruption cases, real Linux child-held flock exclusion, source/code/path guards, post-lock revalidation, failed quarantine preservation, interrupted worker recovery, lock-only interrupted setup, explicit-stage refusal, one-frame pilot stopping, and verified-frame skipping. Tests ran with ResourceWarning treated as error. All96 frame recipes and original Cycles quality settings match the immutable v016 plan exactly.

Consequential gaps found and repaired before the final test:
- Forward-vector-only camera checks did not reject roll/sensor/projection/DOF drift; full orthonormal basis and projection fields are now checked.
- Per-output locks alone could not serialize cooperating outputs; the worker now holds a configured per-user execution lease before opening the model.
- No stage flag previously selected all96 implicitly; explicit mutually exclusive pilot49 or full is now required.
- A late NaN could escape max-based error aggregation; exact4×4 finite matrix and finite nonnegative timing checks were added.
- A crash leaving only runner.lock prevented recovery; exactly that state is now admitted before authoritative nonblocking flock and immediate revalidation, without deleting/bypassing locks.

The production cache path must be writable and explicitly consistent through runner, worker and later validation: XDG_CACHE_HOME determines the identity-bound lease path. This does not exclude manual Blender, other users, machines or different cache namespaces. `/proc` enumeration is advisory, not a global process proof.

Worker source/world/light/settings guards were reviewed, but their real render behavior still requires the separately authorized actual frame49. Only after parent visual/cost acceptance may an explicit full run be considered. A successful synthetic receipt is not evidence of actual rendered content, and no96-frame/video quality conclusion is made here.
