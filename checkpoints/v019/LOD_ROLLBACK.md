# Reversible foreground-tree detail switch

Use a working copy; do not overwrite the accepted checkpoint. This switch affects only one tree, not a global forest LOD system.

## Original low-detail canopy
1. Hide both `V019 candidate | articulated conifer foliage` and `V019 candidate | connected conifer boughs` in **viewport and render**.
2. On `V010 | woodland boughs with gate exit clearance`, disable **viewport and render** for only the modifier `V019 candidate | original foliage rollback mask`.
3. Leave its owned vertex group and all original wood/hidden recovery objects untouched.

## Restore detailed canopy
1. Re-enable that exact Mask modifier in viewport and render.
2. Unhide the same two new objects in viewport and render (also clear any local eye-icon hide if previously applied).

Do not disable only the mask while leaving the new canopy visible: both foliage representations would overlap. Do not hide only the new objects while leaving the mask enabled: the selected canopy would disappear. Apply the paired switch before preview/rendering. The original trunk and old woody branches remain visible in both modes.

The accepted geometry is not modified by these instructions; no new saved LOD variant was created or benchmarked. Any actual changed working copy needs its own preview and provenance, rather than inheriting the accepted render's identity.
