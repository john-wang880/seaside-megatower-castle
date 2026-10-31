"""Four fresh sequential Blender processes. No launch unless explicitly invoked.
Example: python run_abba.py --blender /path/blender --source /path/castle_v016.blend --output-dir /new/path/results
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import time
from PIL import Image, ImageChops

EXPECTED_SHA = 'd44a4cdecd11dab152fd656c624755369e575a0f342e2eb0bc2460475c6f65eb'

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def no_other_blender():
    active = []
    for entry in Path('/proc').iterdir():
        if entry.name.isdigit():
            try:
                executable = (entry / 'exe').resolve(strict=True).name
                if executable.lower().startswith('blender'):
                    active.append(int(entry.name))
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                pass
    if active:
        raise RuntimeError(f'Other Blender processes present: {active}; do not overlap benchmark')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--blender', type=Path, required=True)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    a = p.parse_args()
    source, output, blender = a.source.resolve(), a.output_dir.resolve(), a.blender.resolve()
    assert source.is_file() and blender.is_file()
    assert digest(source) == EXPECTED_SHA, 'Wrong source model'
    assert not output.exists(), 'Refusing existing output directory (no resume/reuse)'
    assert source != output and source not in output.parents
    assert len(os.sched_getaffinity(0)) == 9, 'Expected nine logical CPUs in affinity'
    no_other_blender()
    output.mkdir(parents=True)
    worker = Path(__file__).with_name('render_one.py').resolve()
    plan = {'order': [3, 8, 8, 3], 'source': str(source), 'source_sha256': EXPECTED_SHA,
            'worker_sha256': digest(worker), 'orchestrator_sha256': digest(Path(__file__).resolve()),
            'policy': 'Four cases only, no auto profile changes. Original scene quality/camera/lighting retained.'}
    (output / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
    cases = []
    for index, threads in enumerate(plan['order'], 1):
        no_other_blender()
        case = output / f'{index:02d}_threads_{threads}'
        command = [str(blender), '-b', '--disable-autoexec', str(source), '--python', str(worker),
                   '--', '--output-dir', str(case), '--threads', str(threads), '--source-sha', EXPECTED_SHA]
        start = time.perf_counter()
        with (output / f'{case.name}.log').open('w') as log:
            completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=False)
        if completed.returncode != 0 or not (case / 'metadata.json').is_file():
            raise RuntimeError(f'Case {case.name} failed; inspect log. No automatic retry.')
        report = json.loads((case / 'metadata.json').read_text())
        report['fresh_process_wall_seconds'] = time.perf_counter() - start
        with Image.open(case / 'image.png') as image:
            image.load()
            assert image.mode == 'RGB' and image.size == (720, 520)
            report['decoded_pixels_sha256'] = hashlib.sha256(image.tobytes()).hexdigest()
            report['decoded_mode'] = image.mode
            report['decoded_dimensions'] = list(image.size)
        report['case'] = case.name
        cases.append(report)
        (output / 'completed_cases.json').write_text(json.dumps(cases, indent=2) + '\n')
    reference = Image.open(output / cases[0]['case'] / 'image.png').convert('RGB')
    comparisons = []
    for case in cases[1:]:
        other = Image.open(output / case['case'] / 'image.png').convert('RGB')
        diff = ImageChops.difference(reference, other)
        hist = diff.histogram()
        comparisons.append({'case': case['case'], 'exact_decoded_pixels': diff.getbbox() is None,
                            'maximum_channel_difference_8bit': max(v[1] for v in diff.getextrema()),
                            'mean_absolute_channel_difference_8bit': sum((i % 256) * n for i, n in enumerate(hist)) / (720 * 520 * 3)})
    def comparable(c):
        settings = json.loads(json.dumps(c['effective_settings']))
        for key in ('threads', 'filepath'):
            settings['render'].pop(key, None)
        return settings
    settings_equal = all(comparable(c) == comparable(cases[0]) for c in cases)
    means = {str(t): statistics.mean(c['elapsed_render_seconds'] for c in cases if c['threads'] == t) for t in (3, 8)}
    summary = {'source_sha256_after': digest(source), 'settings_equal_excluding_threads_and_output': settings_equal,
               'exact_decoded_pixels_all_four': all(c['exact_decoded_pixels'] for c in comparisons),
               'comparisons_against_case_01': comparisons, 'mean_render_seconds_by_threads': means,
               'observed_3_thread_mean_divided_by_8_thread_mean': means['3'] / means['8'],
               'limitation': 'Two runs per setting, one cloud host and one low-resolution scene; not a general speed guarantee. No profile changes made.'}
    assert summary['source_sha256_after'] == EXPECTED_SHA
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
