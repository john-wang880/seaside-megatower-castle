# Evidence chronology

All prior report paths remain present. Existing `qa/reports`, root reports and provenance describe the pre-index v028 camera/optional tree tool, and are NOT relabeled as new index acceptance. Their executed runtime hashes may differ from the new runtime. Existing `qa/run_qa.py` is retained as historical pre-index replay and is not the current index QA entrypoint.

Current index acceptance and independent runnable checks live under `qa/edit_index/`; fresh export receipts are `reports/edit_index/`. The accepted canonical model and all 18 camera catalog records are unchanged. Default no-index and explicit index with tree OFF/HIGH/LOW were tested independently.

The failed first export used Python `is` on native RNA wrappers; corrected equality is documented, with failed source/logs retained in provenance. QA fixture/crash chronology is independently retained in the new QA bundle. No accepted source was overwritten.

## Final panel-provenance guard
The first locally accepted index runtime lacked a draw-time provenance check. Its actions were guarded, but the panel could still show labels in a foreign scene. That unpublished payload is retained under `provenance/pre_panel_guard/`. Current runtime adds only the cheap draw provenance/opt-in check. Fresh four exports are under `reports/edit_index_guarded/`; current full independent reports are under `qa/edit_index/reports/`. Pre-guard reports are historical, not current acceptance.

Frozen pre-index QA is reproducible only with its complete historical tool at fixed Git `44a6e7b`; do not use it to validate current runtime.
