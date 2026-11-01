# v026 inspection independent QA

Fresh15-bookmark extension QA is pending; historical14-bookmark acceptance is not reused. The checker must use a new viewer/receipt generated from exactefcdsource and a real highest-livev026manifest.

```sh
python -B run_qa.py --repository-root FRESH_REPOSITORY --tool FRESH_REPOSITORY/scripts/current_inspection --source RESTORED_V026.blend --viewer NEW_VIEWER.blend --receipt NEW_EXPORT.json --output-dir NEW_QA_DIRECTORY --blender BLENDER_5_2_3_EXECUTABLE
```

Quote paths containing spaces/Unicode. Outputdirectory must be new in an existing parent, outside immutablecheckpoint/tool/QA trees. No installation/network/modelsave/render occurs. Require SUMMARY.json pass and validation.json:13originalstatecategories,15bookmarks,20negativeAPIcases, repeatregistration/unregistration and disabled-scriptreopen. Canonical raw/evaluatedgeometry, source cameras, materials/world/lights/render/visibility and all existing modifier weights must remain exact after subtracting only14owned cameras/collection/manualText/provenance marker.

24puretests cover reviewedv026, unknownfuture27, stale25, numericambiguity26/v026, wronghash/size/catalog, aliases/symlinks, freshdestination, Unicode, optimized-mode refusal and exclusivepublication failure/foreign-inode protection. Existing18implementationtests additionally bind exactrear andlateralprovenance and assert runner15/export14+15counts, preventing the previousv025late wrapper-count omission.

Runtime and full QAinventory/modelinputs are hashed before/after. FILES.json binds this bundle. No nativeWindows/desktopclick claim; ordinary explicit manualText/operator API tests are not GUI clicks. Fresh extension run pending; historicalreports deliberately excluded. Packaging adds reports/docs only; executed Python/runtime unchanged. Original executed QA inventory and README are archived under provenance.
