from pathlib import Path
p=Path(__file__).resolve().with_name('critical.py');exec(compile(p.read_text().split("print('CRITICAL GEOMETRY PASS'")[0],str(p),'exec'))
exec(compile(Path(__file__).with_name('profile_check_fragment.txt').read_text(),'profilecheck','exec'))
exec(compile(Path(__file__).with_name('native_check_fragment.txt').read_text(),'nativecheck','exec'))
(P/'profile.json').write_text(json.dumps({'pass':True,'input_sha256':hashes,'native_modifier_control_differences':native_diff,'continuation_cut_rings_exact_float32':True,'core_actual_vertices_exact_expected_inset_and_end_overlap':True,'original_end_faces_exact':True,'scope':'Original four edge continuations and tilted end faces preserved; core28/35mm insets and10mm overlap exact at savedfloat32 coordinates. Courses intentionally remove volume.'},indent=2));print('PROFILE PASS')
