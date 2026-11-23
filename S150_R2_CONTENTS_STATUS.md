# S150 R2 alternate backup

Status: **COMPLETE**. This alternate branch carries the exact sealed S150 R2 native archive as 84 ordered Base64 transport parts. A fresh Git repository fetched this branch alone at verification commit `42a38907bd9a4c322abb6a3cebc96008c178a32f`, reconstructed the archive without the parent payload, and reopened the native project in Blender 5.2.3 LTS with no missing or unpacked assets.

- Archive size: 128,483,763 bytes.
- Archive SHA-256: `01ed2b9b1595effb140ef471489fdaa71e83ff11b45a6718a432b844a48b7c7f`.
- Native model SHA-256: `27bc325e2bc610fa9af50b557ae803ad249fd9600abd219a4c7bbfb5f47490c4`.

See [restore instructions](s150_transport/README.md). This is the alternate Git transport; the sealed archive itself is unchanged.
