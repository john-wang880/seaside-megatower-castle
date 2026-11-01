"""Optional castle review-camera installer. Never saves the canonical source.

From repository root:
python checkpoints/v018/navigation/navigation.py --list
blender -b --disable-autoexec --python-exit-code 1 checkpoints/v018/restored/castle_v018.blend
  --python checkpoints/v018/navigation/navigation.py -- --view bend
  --output checkpoints/v018/restored/my_castle_viewer.blend
Only an explicitly named, previously nonexistent separate viewer file is saved.
"""
import argparse, hashlib, json, math, os, shutil, sys, tempfile
from pathlib import Path
OWNER = 'castle-navigation-v1'
TAG = 'castle_navigation_owner'
MANIFEST = Path(__file__).with_name('views.json')

def load_manifest(path=MANIFEST):
    m = json.loads(Path(path).read_text(encoding='utf-8'))
    if m.get('schema') != OWNER or not isinstance(m.get('views'), dict):
        raise ValueError('Unsupported navigation manifest')
    names = []
    for key, v in m['views'].items():
        if 'existing_camera' in v:
            if 'target' in v and (len(v['target'])!=3 or not all(isinstance(x,(int,float)) and math.isfinite(x) for x in v['target'])):
                raise ValueError('Invalid original-camera orbit target')
            continue
        names.append(v['camera_name'])
        for field in ('location', 'target'):
            if len(v[field]) != 3 or not all(isinstance(x,(int,float)) and math.isfinite(x) for x in v[field]):
                raise ValueError('Invalid camera vector: '+key)
        if not all(isinstance(v[p],(int,float)) and math.isfinite(v[p]) for p in ('lens','clip_start','clip_end')) or v['location'] == v['target'] or not 0 < v['clip_start'] < v['clip_end'] or not v['lens'] > 0:
            raise ValueError('Invalid camera parameters: '+key)
    if len(set(names)) != len(names):
        raise ValueError('Duplicate review camera names')
    return m

def check_output(source, output):
    source = Path(source).resolve()
    requested = Path(output).expanduser().absolute()
    output = requested.resolve()
    if output == source:
        raise ValueError('Refusing canonical/source overwrite')
    if output.suffix.lower() != '.blend' or not output.parent.is_dir():
        raise ValueError('Output must be .blend in an existing directory')
    if os.path.lexists(str(requested)) or os.path.lexists(str(output)):
        raise FileExistsError('Output already exists: '+str(output))
    return output

def install(m, view):
    """Install owned cameras idempotently; select a view in memory only.

    Existing names are never adopted or deleted. All collisions are preflighted
    before mutation. Existing geometry/materials/lights/cameras remain untouched.
    """
    import bpy
    from mathutils import Vector, Matrix
    if view not in m['views']:
        raise ValueError('Unknown view: '+view)
    if bpy.context.view_layer.layer_collection.hide_viewport:
        raise ValueError('Current view layer is hidden')
    expected = {v['camera_name']: (k,v) for k,v in m['views'].items() if 'camera_name' in v}
    col = bpy.data.collections.get(m['collection'])
    if col and (col.get(TAG) != OWNER or col.children or col.hide_render or col.hide_viewport or col.hide_select):
        raise ValueError('Collection name/configuration collision')
    if col and (set(o.name for o in col.objects)-set(expected)):
        raise ValueError('Unexpected objects in owned collection')
    if col and col.name not in bpy.context.scene.collection.children:
        raise ValueError('Owned collection not directly linked to current scene')
    if col:
        layer = next((lc for lc in bpy.context.view_layer.layer_collection.children if lc.collection == col), None)
        if layer is None or layer.exclude or layer.hide_viewport:
            raise ValueError('Owned camera collection is excluded/hidden in current view layer')
    for v in m['views'].values():
        if 'existing_camera' in v:
            o = bpy.data.objects.get(v['existing_camera'])
            if not o or o.type != 'CAMERA' or bpy.context.view_layer.objects.get(o.name) != o or o.hide_get() or o.hide_select:
                raise ValueError('Required original camera missing')
    for name,(key,v) in expected.items():
        o = bpy.data.objects.get(name); d = bpy.data.cameras.get(name+' data')
        if (o is None) != (d is None):
            raise ValueError('Partial camera/data name collision: '+name)
        if not o:
            continue
        q = (Vector(v['target'])-Vector(v['location'])).to_track_quat('-Z','Y')
        world = Matrix.Translation(Vector(v['location'])) @ q.to_matrix().to_4x4()
        okay = (col is not None and o.type=='CAMERA' and o.data==d and o.get(TAG)==OWNER and d.get(TAG)==OWNER
                and o.get('view_id')==key and tuple(o.users_collection)==(col,) and d.users==1
                and not o.parent and not o.constraints and not o.modifiers and not o.animation_data and not d.animation_data
                and not o.hide_render and not o.hide_viewport and not o.hide_get() and not o.hide_select
                and bpy.context.view_layer.objects.get(name) == o
                and o.rotation_mode == 'XYZ'
                and o.delta_location.length<1e-8 and o.delta_rotation_euler.to_matrix()==Matrix.Identity(3)
                and (o.delta_scale-Vector((1,1,1))).length<1e-8
                and max(abs(o.matrix_world[i][j]-world[i][j]) for i in range(4) for j in range(4))<1e-5
                and d.type=='PERSP' and d.sensor_fit=='AUTO' and abs(d.sensor_width-36)<1e-6 and abs(d.sensor_height-24)<1e-6
                and abs(d.shift_x)<1e-8 and abs(d.shift_y)<1e-8 and not d.dof.use_dof
                and (o.location-Vector(v['location'])).length<1e-5
                and max(abs(o.rotation_euler.to_matrix()[i][j]-q.to_matrix()[i][j]) for i in range(3) for j in range(3))<1e-5
                and (o.scale-Vector((1,1,1))).length<1e-6
                and all(abs(getattr(d,p)-v[p])<1e-4 for p in ('lens','clip_start','clip_end')))
        if not okay:
            raise ValueError('Existing review camera changed/collision: '+name)
    if col is None:
        col=bpy.data.collections.new(m['collection']);col[TAG]=OWNER;bpy.context.scene.collection.children.link(col)
    for name,(key,v) in expected.items():
        if bpy.data.objects.get(name):
            continue
        d=bpy.data.cameras.new(name+' data');d[TAG]=OWNER
        for p in ('lens','clip_start','clip_end'):setattr(d,p,v[p])
        o=bpy.data.objects.new(name,d);o[TAG]=OWNER;o['view_id']=key;col.objects.link(o)
        o.location=v['location'];o.rotation_euler=(Vector(v['target'])-o.location).to_track_quat('-Z','Y').to_euler()
    v=m['views'][view];cam=bpy.data.objects.get(v.get('existing_camera',v.get('camera_name')))
    bpy.context.scene.camera=cam
    for obj in bpy.context.view_layer.objects:obj.select_set(False)
    cam.select_set(True);bpy.context.view_layer.objects.active=cam
    bpy.context.view_layer.update()
    # Give each saved 3D viewport a useful orbit pivot when leaving camera view.
    target=Vector(v['target']) if 'target' in v else cam.location+cam.rotation_euler.to_quaternion()@Vector((0,0,-500))
    distance=(cam.location-target).length
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type!='VIEW_3D':continue
            sp=area.spaces.active;sp.camera=cam;sp.use_local_camera=False
            sp.clip_start=.05;sp.clip_end=3000;sp.lens=cam.data.lens
            region=sp.region_3d
            region.view_location=target;region.view_distance=distance;region.view_rotation=cam.rotation_euler.to_quaternion()
            region.view_perspective='CAMERA';region.view_camera_offset=(0,0);region.view_camera_zoom=0
    return {'view':view,'active_camera':cam.name,'added_or_reused_cameras':sorted(expected),'collection':col.name}

def export_viewer(output, view, manifest=MANIFEST):
    import bpy
    m=load_manifest(manifest)
    if view not in m['views']:raise ValueError('Unknown view: '+view)
    source=Path(bpy.data.filepath).resolve()
    if not source.is_file():raise ValueError('Open the canonical source file first')
    source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    if source_hash!=m['source_sha256']:raise ValueError('Source hash does not match the audited canonical model')
    output=check_output(source,output)  # Refuse before camera or viewport changes.
    report=install(m,view)
    # Save a temporary COPY, then exclusive-create requested output. Neither
    # Blender nor Python is ever asked to overwrite source or existing output.
    fd,tmp=tempfile.mkstemp(prefix='.castle-viewer-',suffix='.blend',dir=str(output.parent));os.close(fd);os.unlink(tmp)
    created=False
    try:
        result=bpy.ops.wm.save_as_mainfile(filepath=tmp,copy=True,compress=True,check_existing=False)
        if 'FINISHED' not in result:raise RuntimeError('Blender save failed')
        with open(tmp,'rb') as src,open(output,'xb') as dst:
            created=True;shutil.copyfileobj(src,dst)
        if hashlib.sha256(source.read_bytes()).hexdigest()!=source_hash:raise AssertionError('Source changed unexpectedly')
        report.update({'source_sha256':source_hash,'source_unchanged':True,'viewer_output':str(output),'viewer_sha256':hashlib.sha256(output.read_bytes()).hexdigest()})
        return report
    except BaseException:
        if created and output.exists():output.unlink()  # Only our newly created incomplete output.
        raise
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def main(argv=None):
    if argv is None:argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--list',action='store_true');p.add_argument('--view');p.add_argument('--output');p.add_argument('--manifest',type=Path,default=MANIFEST);a=p.parse_args(argv)
    m=load_manifest(a.manifest)
    if a.list:
        print(json.dumps({k:v['label'] for k,v in m['views'].items()},ensure_ascii=False,indent=2));return
    if not a.view or not a.output:p.error('--view and --output are required (or use --list)')
    if a.view not in m['views']:p.error('Unknown view: '+a.view)
    print(json.dumps(export_viewer(a.output,a.view,a.manifest),indent=2))
if __name__=='__main__':main()
