import argparse, hashlib, json, os, resource, sys, time
from pathlib import Path
import bpy
from mathutils import Vector
p=argparse.ArgumentParser()
p.add_argument('--output-dir',required=True)
p.add_argument('--persistent',type=int,choices=(0,1),required=True)
p.add_argument('--source-sha',required=True)
p.add_argument('--manifest',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
source=Path(bpy.data.filepath).resolve()
assert sha(source)==a.source_sha
out=Path(a.output_dir).resolve();assert not out.exists();out.mkdir()
s=bpy.context.scene
assert s.render.engine=='CYCLES' and s.cycles.device=='CPU'
assert (s.cycles.samples,s.cycles.adaptive_min_samples,s.cycles.max_bounces)==(80,12,8)
assert abs(s.cycles.adaptive_threshold-.035)<1e-7
assert s.cycles.use_adaptive_sampling and s.cycles.use_denoising
def properties(obj):
    result = {}
    for prop in obj.bl_rna.properties:
        if prop.identifier == 'rna_type':
            continue
        if prop.type in {'BOOLEAN', 'INT', 'FLOAT', 'STRING', 'ENUM'}:
            value = getattr(obj, prop.identifier)
            if getattr(prop, 'is_array', False):
                value = list(value)
            elif isinstance(value, set):
                value = sorted(value)
            result[prop.identifier] = value
    return result


original={'cycles':properties(s.cycles),'render':properties(s.render),'image_settings':properties(s.render.image_settings),'view_settings':properties(s.view_settings)}
manifest=Path(a.manifest);recipes=json.loads(manifest.read_bytes())
cameras={}
for key in ('hero','bend'):
    recipe=recipes['views'][key]
    if 'existing_camera' in recipe:
        c=bpy.data.objects[recipe['existing_camera']];assert c.type=='CAMERA'
    else:
        c=bpy.data.objects.new('Cache benchmark '+key,bpy.data.cameras.new('Cache benchmark '+key));s.collection.objects.link(c)
        c.location=recipe['location'];c.rotation_euler=(Vector(recipe['target'])-c.location).to_track_quat('-Z','Y').to_euler()
        c.data.lens=recipe['lens'];c.data.clip_start=recipe['clip_start'];c.data.clip_end=recipe['clip_end']
    cameras[key]=c
s.render.resolution_x=720;s.render.resolution_y=520;s.render.resolution_percentage=100
s.render.threads_mode='FIXED';s.render.threads=8
s.render.use_persistent_data=bool(a.persistent)
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.render.image_settings.compression=15;s.render.use_stamp=False
frames=[]
for i,key in enumerate(('hero','bend','hero'),1):
    c=cameras[key];s.camera=c
    filename=f'{i:02d}_{key}.png';s.render.filepath=str(out/filename)
    settings={'cycles':properties(s.cycles),'render':properties(s.render),'image_settings':properties(s.render.image_settings),'view_settings':properties(s.view_settings),'camera':{'name':c.name,'matrix_world':[list(row) for row in c.matrix_world],'data':properties(c.data)},'frame':s.frame_current,'world':s.world.name if s.world else None}
    assert settings['cycles']==original['cycles'] and settings['view_settings']==original['view_settings']
    before=resource.getrusage(resource.RUSAGE_SELF);start=time.perf_counter()
    bpy.ops.render.render(write_still=True)
    seconds=time.perf_counter()-start;after=resource.getrusage(resource.RUSAGE_SELF)
    assert sha(source)==a.source_sha
    frames.append({'index':i,'view':key,'filename':filename,'elapsed_render_seconds':seconds,'process_cpu_seconds':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,'peak_rss_linux_kib':after.ru_maxrss,'effective_settings':settings,'png_file_sha256':sha(out/filename)})
    (out/'progress.json').write_text(json.dumps(frames,indent=2)+'\n')
report={'source':str(source),'source_sha256_before':a.source_sha,'source_sha256_after':sha(source),'saved_model':False,'camera_recipe_sha256':sha(manifest),'camera_recipe_note':'V015 navigation camera recipes reused on V016; recipe source_model does not identify rendered model.','persistent_data':bool(a.persistent),'original_settings':original,'affinity_logical_cpus':sorted(os.sched_getaffinity(0)),'blender_version':bpy.app.version_string,'frames':frames,'total_render_seconds':sum(f['elapsed_render_seconds'] for f in frames),'total_render_cpu_seconds':sum(f['process_cpu_seconds'] for f in frames),'peak_rss_linux_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
(out/'metadata.json').write_text(json.dumps(report,indent=2)+'\n')
