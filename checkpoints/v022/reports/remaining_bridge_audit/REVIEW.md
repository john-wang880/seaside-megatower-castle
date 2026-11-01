# v021 remaining bridge-pier family — closed read-only negative

Source `work/v021/castle_v021.blend`, SHA256 `457348497ba7dade666a909c029f6641a0945012f264fe088b8f06513a937ae9`, unchanged. The accepted central cleanup is complete. No model edit, render, new camera, prototype or version is warranted by this pass.

## Exact bounded inventory

The original three spans have six authored end-shaft components in `V007 | western stonework with actual bridgehead passage`: seeds15874,15882,15956,15964,16038,16046. Central15882/15956 are correctly absent from evaluated target mesh under existing v021 masks; their raw originals remain. Four untouched shaft components' actual world coordinates remain in evaluated geometry.

- West endpoint shaft15874: X−56.3…−54.5,Y34.8…41.2,Z6.271…26.825 (locally warped, do not pretend its bounding box is an exact box). Its single foot5136 in `V012 | legacy ashlar with buried-route clearance`: X−56.725…−54.075,Y34.3…41.7,Z5.950…8.555. This is an endpoint under the western abutment, **not another assembled internal pier nearX−58**. No second same-family shaft or foot overlaps it. Six of eight endpoint front samples per existing view hit terrain/forest first; two upperZ25 samples see the stone. No duplicate-strip issue is identified in that exposed top.
- Remaining interior shafts15964 and16038: X−23.5…−21.7 and−21.3…−19.5,Y34.8…41.2,Z6…26.4. They are separated by0.4m, not coplanarly overlapping. The already-examined right dark line hits a sideface; it is not reclassified as an artifact here.
- East endpoint16046: X−6.5…−4.7,Y34.8…41.2,Z6…26.4; foot5176 X−6.925…−4.275. Single same-family endpoint, no paired duplicate to treat.

The six raw foot components are5136,5144,5152,5160,5168,5176. Central5144/5152 remain correctly masked/replaced by v021. This audit did not change their groups, weights or modifiers.

## Remaining foot overlap is not a practical visible target

Foot5160: X−23.925…−21.275. Foot5168: X−21.725…−19.075. BothY34.3…41.7,Z5.7…8.1, material `West_Ashlar stone variation`. Their front overlap is X−21.725…−21.275, width0.45000076m, area1.08000209m². This is a real repeated-source coplanar condition, but not automatically a reason to modify buried geometry.

A3×3 grid on the overlap front was cast from each **existing** source hero and accepted bridge closeview. All18/18 rays encounter visible coastal rock or headland before the patch. Hero sample region is approximatelyX634.85…635.83,Y644.01…649.40 pixels at1200×866; closeviewX872.82…883.42,Y720.87…774.35. Closeview rock/terrain is3.77…13.93m before the target; hero rock is63.93…67.20m before it. No evidence of a visible black duplicate strip is supplied by these practical views. Existing close image already shows this base behind rock.

## Stopping boundary

Stop with a documented negative: do not union all repeated components merely because the central correction succeeded, and do not move a camera behind the rocks to manufacture a new aesthetic need. This is a finite-sample visibility result and a six-shaft/six-foot family inventory, **not** proof of invisibility from every angle or global castle coplanar certification. No structural/load claim, no blind gap fill, no terrain change. Exact component IDs/materials/raw-to-evaluated presence and ray records are in `audit.json`; compact decision in `SUMMARY.json`. Script `audit.py` is read-only but intentionally retains its local camera-preflight dependency as provenance; it is not presented as a standalone published rebuild tool.
