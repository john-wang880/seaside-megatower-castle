"""Small deterministic guards, no IO or renderer dependencies."""
def validate_indices(indices,count):
 assert indices==list(range(1,count+1)), 'Missing, duplicated, unordered or unexpected indices'
def validate_timestamps(times,count,fps,tolerance=1e-5):
 assert len(times)==count
 assert all(abs(t-i/fps)<tolerance for i,t in enumerate(times)), 'Unexpected presentation timestamps'
def compression_acceptable(mae,channel_bias):
 import math
 return math.isfinite(mae) and mae<5 and all(math.isfinite(x) and abs(x)<3 for x in channel_bias)
def classify_duplicate(decoded_indices,source_hashes,per_frame_mae,source_pair_mae):
 """Same decoded image is legitimate only if distinct sources are close enough.
 Triangle inequality gives source-to-source MAE <= each source-to-decoded MAE sum.
 This is provenance/consistency, not a proof the encoder never repeated a frame.
 """
 assert len(decoded_indices)>=2
 assert len({source_hashes[i] for i in decoded_indices})==len(decoded_indices), 'Original frames not distinct'
 first=decoded_indices[0]
 for other in decoded_indices[1:]:
  assert source_pair_mae[(first,other)] <= per_frame_mae[first]+per_frame_mae[other]+1e-8, 'Duplicate does not match source comparison bounds'
 return {'indices':decoded_indices,'classification':'Lossy-equivalent frames consistent with distinct source PNGs and same-index compression bounds; not evidence of fabrication'}
