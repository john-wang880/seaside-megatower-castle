"""Actual-light navigation still renderer. Optional thread override; default4 preserved.
Import/--help and argument tests use standard Python; rendering needs Blender.
"""
import argparse,sys,json,time,hashlib
from pathlib import Path

def peak_rss_linux_kib():
    """Optional Linux ru_maxrss telemetry; None means unavailable, not zero.

    Other platforms may lack resource or report different units. Never label
    those values as Linux KiB, and never fail a render over optional telemetry.
    """
    if sys.platform != 'linux':
        return None
    try:
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except Exception:
        # Confined to optional telemetry; render/source errors remain fatal.
        return None

def parse_args(argv=None):
    if argv is None:argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',required=True);p.add_argument('--view',required=True);p.add_argument('--out',required=True)
    p.add_argument('--threads',type=int,default=4,help='Explicit render thread count1–1024; default4 is unchanged')
    a=p.parse_args(argv)
    if not 1<=a.threads<=1024:p.error('--threads must be between1 and1024')
    return a

def main(argv=None):
    a=parse_args(argv)
    import bpy
    from mathutils import Vector
    manifest_bytes=Path(a.manifest).read_bytes();manifest_start_sha=hashlib.sha256(manifest_bytes).hexdigest();m=json.loads(manifest_bytes);v=m['views'][a.view];source=Path(bpy.data.filepath);sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha==m['source_sha256']
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=24;s.cycles.use_denoising=True;s.cycles.max_bounces=6;s.cycles.volume_bounces=1;s.render.resolution_x=720;s.render.resolution_y=520;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=a.threads
    if 'existing_camera' in v:c=bpy.data.objects[v['existing_camera']];assert c.type=='CAMERA'
    else:
     c=bpy.data.objects.new('Temporary still '+a.view,bpy.data.cameras.new('Temporary still '+a.view));s.collection.objects.link(c);c.location=v['location'];c.rotation_euler=(Vector(v['target'])-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=v['lens'];c.data.clip_start=v.get('clip_start',.05);c.data.clip_end=v.get('clip_end',3000)
    s.camera=c;s.render.filepath=str(Path(a.out).resolve());s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.use_stamp=False
    start=time.time();bpy.ops.render.render(write_still=True);assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
    r={'view':a.view,'source':source.name,'source_sha256':sha,'view_manifest_sha256':manifest_start_sha,'manifest_hash_timing':'render-start bytes snapshot','preset':v,'actual_camera':{'location':list(c.location),'rotation_euler':list(c.rotation_euler),'lens':c.data.lens,'clip_start':c.data.clip_start,'clip_end':c.data.clip_end},'resolution':[720,520],'samples':24,'render_threads':a.threads,'seconds':time.time()-start,'peak_rss_linux_kib':peak_rss_linux_kib(),'runtime':bpy.app.version_string,'lighting':'Actual existing world/lights/exposure unchanged. No diagnostic fill or hidden geometry.','scope':'Independent camera still, not simulated walking or a dynamic navigation proof.','source_saved':False}
    Path(a.out).with_suffix('.json').write_text(json.dumps(r,indent=2))

if __name__=='__main__':main()
