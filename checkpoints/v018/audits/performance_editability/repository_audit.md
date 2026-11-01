# v018 repository storage/editability audit (read-only)

Commit inspected: `24bb79cf849bdc91505eb8ce1531c1ac07f550e6`. No Blender, model changes, Git writes, deletion or history rewrite. Detailed exact groups and hashes: `repository_audit.json`.

## Useful finding, modest priority
There are **19 byte-identical duplicate path groups**, with **6,832,643 bytes (~6.52MiB)** of ordinary checkout duplication, about7.8% of the tracked tree's87,600,396 logical bytes. Equality is established by Git blob OID **and actual checked-out SHA256**, not similar names or visual resemblance.

However, identical paths already share one Git blob. Removing an extra path would **not remove another copy of that blob from Git storage**, nor remove its historical references. Unique current-tree blob payload is80,767,753 uncompressed bytes; that is not measured packfile size or clone transfer. No download-speed or Blender-runtime gain is claimed.

The strongest low-risk candidate *if ordinary checkout/package size matters* is canonicalizing repeated presentation still paths while retaining documentation links:

| Byte-identical pair under `checkpoints/v018/` | Checkout bytes potentially avoided |
|---|---:|
| `navigation/renders/hero.png` ↔ `previews/hero_after_v018.png` |1,219,674|
| `navigation/renders/west_crown.png` ↔ `previews/west_cap_after_v018.png` |991,456|
| `navigation/rear_before_v017.png` ↔ `previews/west_cap_opposite_before_v017.png` |1,002,784|

These three total3,213,914 bytes (~3.07MiB). This would be **metadata/path consolidation**, not a scene optimization or reason for a new model version. Both checkpoint and navigation README currently link their respective image paths; the navigation rendering workflow expects its own output convention. Before consolidation choose a canonical destination, update every public link and relevant render-manifest/output convention, and rebuild checksum inventories atomically. Do not introduce platform-sensitive symlinks merely for this small saving. If maintaining self-contained gallery folders is more useful, keeping these exact duplicates is defensible.

## Copies that carry distinct stage/provenance roles
- Final route preview frames0001/0076/0336 are identical to retained V2 pilot PNGs: combined redundant2,048,259 bytes. These document both the approved pilot gate and completed sequence. The pilot README and approval/identity records retain their historical stage meaning. Consolidation could replace image copies with explicit canonical references **only after** checking frozen-run/checksum paths; deleting the pilot evidence or rewriting its chronology would be wrong.
- V1 arrival historical frame0303/0336 duplicates rejected-pilot image copies:1,387,865 bytes. They retain useful rejected-route evidence. The interior `archive_checksums.json` explicitly names `historical_v1_arrival/...` paths. Do not delete rejected evidence or repurpose it as current video.
- Remaining identical receipts/reports sum only182,605 redundant bytes. Examples include local/remote route support, hinge contacts and geometry reports. Their identical contents do not erase the separate verification-stage semantics established by surrounding receipts. Tiny storage benefit does not justify disturbing provenance merely to reduce file count.

All eight duplicated PNGs total6,650,038 bytes; the rest are small text records. Similar-looking images not sharing exact bytes are deliberately **not** called redundant.

## Strong negative finding: current model archival organization is already sound
The sole tracked checkpoint isv018. `MANIFEST.json` has109 chunk entries referencing94 unique chunk hashes; exactly94 files are present in tracked `model_chunks/`, totaling31,662,428 bytes. Every stored chunk is referenced, all hash filenames verify, and **no orphan model chunk exists**. Repeated manifest references are valid content reuse, not duplicate physical files. Do not prune those entries or redesign the archive on this evidence. Prior model versions remain in Git history, not additional current tracked model snapshots.

## Avoid mistaking local scratch for published duplication
Filesystem `du` over `checkpoints/` includes ignored local restore/archive directories: v00651,117,170B; v00762,475,997B; v00863,657,675B; v0095,857B. None is tracked at this commit. Their combined177,256,699B explains much of the mismatch between working-folder disk use and current-tree size. This audit did not validate disposal prerequisites for those recovery/build inputs, so **no local deletion is proposed**. Removing them would not change the published repository tree or Git history.

## Decision
No urgent repository-storage repair is warranted. A bounded3.07MiB presentation-path consolidation is possible if checkout size is a real goal, but yields no new Git-blob saving and needs link/checksum care. Otherwise retain current paths and provenance. This audit establishes neither Blender editability nor scene performance; the separate scene audit owns those questions.
