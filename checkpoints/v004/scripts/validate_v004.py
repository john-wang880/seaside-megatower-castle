"""Read-only baseline-preservation and reopening checks for the v004 expansion checkpoint."""
import argparse
import array
import bpy
import hashlib
import json
import os
import sys

p=argparse.ArgumentParser()
p.add_argument('--baseline',required=True)
p.add_argument('--checkpoint',required=True)
p.add_argument('--report',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])


def mesh_hash(m):
    co=array.array('f',[0.0])*(len(m.vertices)*3)
    loops=array.array('i',[0])*len(m.loops)
    counts=array.array('i',[0])*len(m.polygons)
    m.vertices.foreach_get('co',co); m.loops.foreach_get('vertex_index',loops)
    m.polygons.foreach_get('loop_total',counts)
    return hashlib.sha256(co.tobytes()+loops.tobytes()+counts.tobytes()).hexdigest()


def value(x):
    if x is None or isinstance(x,(bool,int,float,str)): return x
    try: return [float(v) for v in x]
    except (TypeError,ValueError): return str(type(x).__name__)


def tree_hash(tree):
    if not tree:return None
    rows=[]
    for n in tree.nodes:
        d={'name':n.name,'type':n.bl_idname,'inputs':[(s.name,value(s.default_value)) for s in n.inputs if hasattr(s,'default_value')]}
        for k in ['operation','blend_type','noise_dimensions','wave_type','bands_direction','wave_profile','normalize']:
            if hasattr(n,k):d[k]=value(getattr(n,k))
        if hasattr(n,'color_ramp'):
            d['ramp']=[(e.position,list(e.color)) for e in n.color_ramp.elements]
        rows.append(d)
    links=sorted((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in tree.links)
    return hashlib.sha256(json.dumps({'nodes':sorted(rows,key=lambda x:x['name']),'links':links},sort_keys=True).encode()).hexdigest()


def snapshot():
    return {'meshes':{m.name:mesh_hash(m) for m in bpy.data.meshes},
            'materials':{m.name:tree_hash(m.node_tree) for m in bpy.data.materials},
            'objects':{o.name:{'type':o.type,'matrix':[float(x) for row in o.matrix_world for x in row],
                                'hide_render':o.hide_render} for o in bpy.data.objects},
            'cameras':{o.name:{'lens':o.data.lens,'clip_start':o.data.clip_start,'clip_end':o.data.clip_end} for o in bpy.data.objects if o.type=='CAMERA'},
            'lights':{o.name:{'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color)} for o in bpy.data.objects if o.type=='LIGHT'},
            'world':tree_hash(bpy.context.scene.world.node_tree),
            'view':{'transform':bpy.context.scene.view_settings.view_transform,'look':bpy.context.scene.view_settings.look,'exposure':bpy.context.scene.view_settings.exposure,'gamma':bpy.context.scene.view_settings.gamma}}


bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a.baseline),load_ui=True,use_scripts=False)
base=snapshot()
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a.checkpoint),load_ui=True,use_scripts=False)
check=snapshot()
mesh_changes=[name for name,h in base['meshes'].items() if check['meshes'].get(name)!=h]
mat_changes=[name for name,h in base['materials'].items() if check['materials'].get(name)!=h]
object_changes=[]; visibility=[]
for name,v in base['objects'].items():
    other=check['objects'].get(name)
    if not other or other['type']!=v['type'] or other['matrix']!=v['matrix']:object_changes.append(name)
    if other and other['hide_render']!=v['hide_render']:visibility.append(name)
browser_dirs=[]
for screen in bpy.data.screens:
    for area in screen.areas:
        for space in area.spaces:
            if space.type=='FILE_BROWSER' and space.params:
                browser_dirs.append(space.params.directory.decode('utf8','replace'))
report={'version':'v004 expansion','blender_version':bpy.app.version_string,'reopened':True,
        'baseline_filename':os.path.basename(a.baseline),'checkpoint_filename':os.path.basename(a.checkpoint),
        'baseline_sha256':hashlib.sha256(open(a.baseline,'rb').read()).hexdigest(),
        'checkpoint_sha256':hashlib.sha256(open(a.checkpoint,'rb').read()).hexdigest(),
        'baseline_meshes_checked':len(base['meshes']),'baseline_mesh_data_changed':mesh_changes,
        'baseline_materials_checked':len(base['materials']),'baseline_material_node_graphs_changed':mat_changes,
        'baseline_object_transforms_changed':object_changes,'intentional_visibility_changes':visibility,
        'baseline_cameras_unchanged':all(check['cameras'].get(n)==v for n,v in base['cameras'].items()),
        'lights_unchanged':base['lights']==check['lights'],'world_unchanged':base['world']==check['world'],
        'view_transform_and_exposure_unchanged':base['view']==check['view'],
        'object_count':len(bpy.data.objects),'mesh_count':len(bpy.data.meshes),'material_count':len(bpy.data.materials),
        'image_count':len(bpy.data.images),'linked_library_count':len(bpy.data.libraries),'embedded_text_count':len(bpy.data.texts),
        'render_output_relative':bpy.context.scene.render.filepath.startswith('//'),
        'render_filename_stamp_disabled':not bpy.context.scene.render.use_stamp_filename,
        'file_browser_directories_relative':all(v in ('//','') for v in browser_dirs),
        'autoexec_enabled':bpy.context.preferences.filepaths.use_scripts_auto_execute}
assert not mesh_changes and not mat_changes and not object_changes
assert set(visibility)<= {'V003 | main shaft with four genuine recessed lancets','V003 | western monolith with four genuine recessed lancets','V003 | western existing recesses opened at sample windows'}
assert report['baseline_cameras_unchanged'] and report['lights_unchanged'] and report['world_unchanged'] and report['view_transform_and_exposure_unchanged']
assert not report['image_count'] and not report['linked_library_count'] and not report['embedded_text_count']
assert report['render_output_relative'] and report['render_filename_stamp_disabled'] and report['file_browser_directories_relative']
with open(a.report,'w') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
