import argparse,hashlib,json,os,subprocess,time
from pathlib import Path
from PIL import Image,ImageChops
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
    worker=Path(__file__).with_name('render_batch.py').resolve();manifest=worker.with_name('camera_recipes.json')
    (out/'plan.json').write_text(json.dumps({'order':['off','on'],'camera_order':['hero','bend','hero'],'source_sha256':EXPECTED_SHA,'worker_sha256':digest(worker),'orchestrator_sha256':digest(Path(__file__).resolve()),'camera_recipes_sha256':digest(manifest)},indent=2))
    reports=[]
    for enabled in (0,1):
        no_other_blender();case=out/('on' if enabled else 'off')
        cmd=[str(blender),'-b','--disable-autoexec',str(source),'--python',str(worker),'--','--output-dir',str(case),'--persistent',str(enabled),'--source-sha',EXPECTED_SHA,'--manifest',str(manifest)]
        start=time.perf_counter()
        with (out/(case.name+'.log')).open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
        if r.returncode or not (case/'metadata.json').is_file():raise RuntimeError('Failed '+case.name+'; inspect log')
        report=json.loads((case/'metadata.json').read_text());report['fresh_process_wall_seconds']=time.perf_counter()-start
        for f in report['frames']:
            with Image.open(case/f['filename']) as im:
                im.load();assert im.mode=='RGB' and im.size==(720,520)
                f['decoded_pixels_sha256']=hashlib.sha256(im.tobytes()).hexdigest()
        reports.append(report)
        (out/'completed_cases.json').write_text(json.dumps(reports,indent=2)+'\n')
    comparisons=[]
    for off,on in zip(reports[0]['frames'],reports[1]['frames']):
        with Image.open(out/'off'/off['filename']) as x,Image.open(out/'on'/on['filename']) as y:
            diff=ImageChops.difference(x,y);h=diff.histogram()
            settings=[]
            for f in (off,on):
                q=json.loads(json.dumps(f['effective_settings']))
                for k in ('filepath','use_persistent_data'):q['render'].pop(k,None)
                settings.append(q)
            comparisons.append({'frame':off['filename'],'decoded_exact':diff.getbbox() is None,'max_channel_difference_8bit':max(v[1] for v in diff.getextrema()),'mean_absolute_channel_difference_8bit':sum((i%256)*n for i,n in enumerate(h))/(720*520*3),'settings_equal_except_output_and_cache':settings[0]==settings[1]})
    summary={'source_sha256_after':digest(source),'comparisons':comparisons,'all_corresponding_pixels_exact':all(c['decoded_exact'] for c in comparisons),'all_corresponding_settings_equal':all(c['settings_equal_except_output_and_cache'] for c in comparisons),'off_total_render_seconds':reports[0]['total_render_seconds'],'on_total_render_seconds':reports[1]['total_render_seconds'],'observed_batch_speed_ratio':reports[0]['total_render_seconds']/reports[1]['total_render_seconds'],'off_peak_rss_linux_kib':reports[0]['peak_rss_linux_kib'],'on_peak_rss_linux_kib':reports[1]['peak_rss_linux_kib'],'limitation':'Single OFF then ON batch, unchanged scene, camera-only transitions. Not arbitrary mutation cache safety or a general performance guarantee. No profile/source changes saved.'}
    assert summary['source_sha256_after']==EXPECTED_SHA
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
