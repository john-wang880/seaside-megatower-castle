# v027 independent inspection QA — fresh native run passed

After accepted real v027 manifest and fresh viewer export:
```sh
python -B run_qa.py --repository-root "$repo" --tool "$tool" --source "$source" --viewer "$viewer" --receipt "$receipt" --output-dir "$new_qa_directory" --blender "$blender"
```
Require13 source categories,16 bookmarks,20 API negatives, repeat registration/unregister, disabled-script reopen, exact input/runtime inventories. Only15 owned cameras/collection/manual Text/provenance marker may be subtracted. All source geometry/attributes/modifiers/weights/materials/lights/world/camera settings must remain exact. 24 pure guard tests supplement18 implementation tests, including future28/stale26/ambiguity27 guards and Unicode paths. Linux5.2.3 native validation passed; Windows/desktop clicking untested. No renderer/model saver in QA.
