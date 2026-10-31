# Byte-exact checkpoint storage

`package_checkpoint.py` reads the seek table already present in Blender's compressed file and stores each original compressed frame plus the original seek-table bytes by SHA-256. It does not decompress or re-encode the model. Reconstruction concatenates the manifest's ordered references and verifies the original model hash.

The packer uses the published [Zstandard seekable format](https://github.com/meta/zstd/blob/dev/contrib/seekable_format/zstd_seekable_compression_format.md). It rejects invalid indexes, reserved format flags and inconsistent sizes. The restore script needs only standard Python; it verifies size and hash per chunk, validates safe names, writes a temporary file, and will not overwrite a different existing model.

Run tests with `python -m unittest discover -s tests -v`. For each new artistic checkpoint, also perform a fresh restoration, Blender reopening, geometry checks and actual preview review. Unit tests alone are not model validation.

Do not prune the current tree until the new manifest/chunks are published, fetched back and restored successfully. Then remove only chunks no longer referenced by the latest checkpoint. Keep prior Git commits; never force-push to shrink history.
