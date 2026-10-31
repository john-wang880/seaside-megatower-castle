import argparse,hashlib,json,os,subprocess,time
from pathlib import Path
from PIL import Image
EXPECTED_SHA='d44a4cdecd11dab152fd656c624755369e575a0f342e2eb0bc2460475c6f65eb'
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
    p=argparse.ArgumentParser();p.add_argument('--blender',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args()
    source=a.source.resolve();out=a.output_dir.resolve();blender=a.blender.resolve()
    assert digest(source)==EXPECTED_SHA and blender.is_file()
    assert not out.exists(),'Refuse reused output directory'
    assert len(os.sched_getaffinity(0))==9
    no_other_blender();out.mkdir(parents=True)
    worker=Path(__file__).with_name('render_keyframe.py').resolve();manifest=worker.with_name('keyframes.json')
    views=list(json.loads(manifest.read_text())['views']);assert len(views)==5
    (out/'plan.json').write_text(json.dumps({'order':views,'source_sha256':EXPECTED_SHA,'worker_sha256':digest(worker),'orchestrator_sha256':digest(Path(__file__).resolve()),'manifest_sha256':digest(manifest)},indent=2))
    reports=[]
    for view in views:
        no_other_blender();case=out/view
        cmd=[str(blender),'-b','--disable-autoexec',str(source),'--python',str(worker),'--','--output-dir',str(case),'--view',view,'--source-sha',EXPECTED_SHA,'--manifest',str(manifest)]
        start=time.perf_counter()
        with (out/(view+'.log')).open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
        if r.returncode or not (case/'metadata.json').is_file():raise RuntimeError('Failed '+view+'; inspect log')
        report=json.loads((case/'metadata.json').read_text());report['fresh_process_wall_seconds']=time.perf_counter()-start
        with Image.open(case/'image.png') as im:
            im.load();assert im.mode=='RGB' and im.size==(640,462)
            report['decoded_pixels_sha256']=hashlib.sha256(im.tobytes()).hexdigest()
            report['dimensions']=list(im.size)
        reports.append(report)
        (out/'completed_views.json').write_text(json.dumps(reports,indent=2)+'\n')
        print(view,round(report['elapsed_render_seconds'],2),'s',flush=True)
    assert digest(source)==EXPECTED_SHA
    summary={'source_sha256_after':digest(source),'views':views,'all_five_complete':len(reports)==5,'all_16_preview_samples':all(d['effective_settings']['cycles']['samples']==16 for d in reports),'total_render_seconds':sum(d['elapsed_render_seconds'] for d in reports),'scope':'Current V016 low-resolution 16-sample actual-lighting path feasibility previews, not a simulated walkthrough. No model writes, cache changes, diagnostic light, image edits or saved profile changes.'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
