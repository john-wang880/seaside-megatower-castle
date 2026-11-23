# S150 R2 alternate backup transport

This branch transports the exact sealed S150 R2 archive as ordered Base64 text. The historical S149 files inherited by this branch are not used to reconstruct it.

Check the top-level status marker. An **INCOMPLETE** marker means not yet accepted. After a complete marker, use the indicated exact verification commit. Fetch this branch alone in a fresh repository or check out the identified verification commit, then run:

```sh
python3 -I s150_transport/restore.py --out S150_BACKUP.zip
```

Expected ZIP: 128,483,763 bytes, SHA-256 `01ed2b9b1595effb140ef471489fdaa71e83ff11b45a6718a432b844a48b7c7f`. Native file: `s150_candidate/candidate.blend` inside it. SHA-256 `27bc325e2bc610fa9af50b557ae803ad249fd9600abd219a4c7bbfb5f47490c4`. Use Blender 5.2.3 LTS to open it. The original standalone archive and source ancestry are unchanged; this branch uses an alternate Git transport.
