"""Calibrate only the two tower-body stone materials; retain source geometry and lighting.

Run from v004 or from this checkpoint. Output must be a new file.
Uses linked geometry plus per-object material overrides, not destructive edits.
"""
import argparse,bpy,hashlib,json,os,sys
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=bpy.data.filepath;output=os.path.abspath(a.output)
if os.path.realpath(source)==os.path.realpath(output):raise RuntimeError('Never overwrite the input checkpoint')
bpy.context.preferences.filepaths.use_scripts_auto_execute=False
COL='REFINEMENT | v005 calibrated tower stone'
if COL in bpy.data.collections:
 for o in list(bpy.data.collections[COL].objects):bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.collections.remove(bpy.data.collections[COL])
for m in list(bpy.data.materials):
 if m.name.startswith('V005 |') and not m.users:bpy.data.materials.remove(m)
col=bpy.data.collections.new(COL);bpy.context.scene.collection.children.link(col)

def node(t,kind,name):
 n=t.nodes.new(kind);n.name=name;n.label=name;return n

def project(t):
 """World-unit XZ/YZ walls, XY tops, chosen by true face normal, not bump normal."""
 geo=t.nodes.get('Geometry') or node(t,'ShaderNodeNewGeometry','Geometry')
 pos=node(t,'ShaderNodeSeparateXYZ','V005 world position');t.links.new(geo.outputs['Position'],pos.inputs[0])
 norm=node(t,'ShaderNodeSeparateXYZ','V005 true face normal');t.links.new(geo.outputs['True Normal'],norm.inputs[0])
 ab=[]
 for c in 'XYZ':
  n=node(t,'ShaderNodeMath','V005 abs normal '+c);n.operation='ABSOLUTE';t.links.new(norm.outputs[c],n.inputs[0]);ab.append(n.outputs[0])
 side=node(t,'ShaderNodeMath','V005 side-axis decision');side.operation='GREATER_THAN';t.links.new(ab[0],side.inputs[0]);t.links.new(ab[1],side.inputs[1])
 ma=node(t,'ShaderNodeMath','V005 max horizontal normal');ma.operation='MAXIMUM';t.links.new(ab[0],ma.inputs[0]);t.links.new(ab[1],ma.inputs[1])
 top=node(t,'ShaderNodeMath','V005 top-axis decision');top.operation='GREATER_THAN';t.links.new(ab[2],top.inputs[0]);t.links.new(ma.outputs[0],top.inputs[1])
 projections=[]
 for axes in ['XZ','YZ','XY']:
  n=node(t,'ShaderNodeCombineXYZ','V005 world '+axes);t.links.new(pos.outputs[axes[0]],n.inputs['X']);t.links.new(pos.outputs[axes[1]],n.inputs['Y']);projections.append(n.outputs[0])
 wall=node(t,'ShaderNodeMixRGB','V005 equal-scale wall projection');wall.blend_type='MIX';t.links.new(side.outputs[0],wall.inputs[0]);t.links.new(projections[0],wall.inputs[1]);t.links.new(projections[1],wall.inputs[2])
 allfaces=node(t,'ShaderNodeMixRGB','V005 wall or top projection');allfaces.blend_type='MIX';t.links.new(top.outputs[0],allfaces.inputs[0]);t.links.new(wall.outputs[0],allfaces.inputs[1]);t.links.new(projections[2],allfaces.inputs[2]);return allfaces.outputs[0]

def roughness(t,brick,bsdf,lo,hi,roughlo,roughhi):
 gray=node(t,'ShaderNodeRGBToBW','V005 block tone for roughness');t.links.new(brick.outputs['Color'],gray.inputs[0])
 remap=node(t,'ShaderNodeMapRange','V005 restrained block roughness');remap.clamp=True
 remap.inputs['From Min'].default_value=lo;remap.inputs['From Max'].default_value=hi;remap.inputs['To Min'].default_value=roughlo;remap.inputs['To Max'].default_value=roughhi;t.links.new(gray.outputs[0],remap.inputs['Value'])
 mix=node(t,'ShaderNodeMixRGB','V005 more matte recessed joints');mix.blend_type='MIX';t.links.new(brick.outputs['Fac'],mix.inputs[0]);t.links.new(remap.outputs[0],mix.inputs[1]);mix.inputs[2].default_value=(.90,.90,.90,1);t.links.new(mix.outputs[0],bsdf.inputs['Roughness'])

def copy_mat(original,name):
 m=bpy.data.materials[original].copy();m.name='V005 | '+name;return m

main=copy_mat('Citadel • deep slate ashlar','main large ashlar calibrated world units');t=main.node_tree
brick=t.nodes['Brick Texture'];t.links.new(project(t),brick.inputs['Vector'])
for k,v in [('Scale',1.0),('Brick Width',1.30),('Row Height',.52),('Mortar Size',.012),('Mortar Smooth',.004)]:brick.inputs[k].default_value=v
brick.offset=.5;brick.offset_frequency=2;brick.squash=1.;brick.squash_frequency=2
# Preserve existing low-frequency patina as the base, with a separately normalized block multiplier.
t.nodes['Mix (Legacy).001'].inputs[0].default_value=.95
brick.inputs['Mortar'].default_value=(.101325,.1475292,.1532034,1)
# Retain the original low-frequency colour field; only modulate it with normalized block colour.
normalize=node(t,'ShaderNodeVectorMath','V005 normalized restrained block colour');normalize.operation='DIVIDE'
normalize.inputs[1].default_value=(.120625,.17563,.182385);t.links.new(brick.outputs['Color'],normalize.inputs[0])
mod=node(t,'ShaderNodeMixRGB','V005 preserve old patina with subtle ashlar');mod.blend_type='MULTIPLY';mod.inputs[0].default_value=.25
t.links.new(t.nodes['Mix (Legacy).001'].outputs[0],mod.inputs[1]);t.links.new(normalize.outputs[0],mod.inputs[2]);t.links.new(mod.outputs[0],t.nodes['Principled BSDF'].inputs['Base Color'])
b=t.nodes['Bump'];b.invert=True;b.inputs['Strength'].default_value=.20;b.inputs['Distance'].default_value=.014
micro=t.nodes['Bump.001'];micro.inputs['Strength'].default_value=.10;micro.inputs['Distance'].default_value=.008
roughness(t,brick,t.nodes['Principled BSDF'],.13,.20,.79,.85)

west=copy_mat('West_Ancient monolith','west subdued coarse stone courses');t=west.node_tree
brick=node(t,'ShaderNodeTexBrick','V005 quiet west ashlar');t.links.new(project(t),brick.inputs['Vector'])
for k,v in [('Scale',1.0),('Brick Width',1.65),('Row Height',.65),('Mortar Size',.010),('Mortar Smooth',.004)]:brick.inputs[k].default_value=v
brick.inputs['Color1'].default_value=(.96,.96,.96,1);brick.inputs['Color2'].default_value=(1.04,1.04,1.04,1);brick.inputs['Mortar'].default_value=(.92,.92,.92,1)
brick.offset=.5;brick.offset_frequency=2;brick.squash=1.;brick.squash_frequency=2
# Preserve the existing west-tower hue and macro-field, with only +/-2.4% block modulation.
mod=node(t,'ShaderNodeMixRGB','V005 subtle block variation over original patina');mod.blend_type='MULTIPLY';mod.inputs[0].default_value=.6;t.links.new(t.nodes['Color Ramp'].outputs['Color'],mod.inputs[1]);t.links.new(brick.outputs['Color'],mod.inputs[2]);t.links.new(mod.outputs[0],t.nodes['Principled BSDF'].inputs['Base Color'])
b=node(t,'ShaderNodeBump','V005 west recessed mortar');b.invert=True;b.inputs['Strength'].default_value=.16;b.inputs['Distance'].default_value=.014;t.links.new(brick.outputs['Fac'],b.inputs['Height'])
micro=t.nodes['Bump'];micro.inputs['Strength'].default_value=.08;micro.inputs['Distance'].default_value=.025;t.links.new(b.outputs['Normal'],micro.inputs['Normal'])
roughness(t,brick,t.nodes['Principled BSDF'],.96,1.04,.815,.865)

mapping=[('V004 | main shaft selective front and east-facing windows','V005 | main tower calibrated stone surface','Citadel • deep slate ashlar',main),('V004 | west shaft selective front and east-facing windows','V005 | west tower calibrated stone surface','West_Ancient monolith',west)]
replacements=[]
for srcname,newname,oldmat,newmat in mapping:
 src=bpy.data.objects[srcname];obj=src.copy();obj.name=newname;col.objects.link(obj);obj.hide_render=False;obj.hide_viewport=False
 found=0
 for slot in obj.material_slots:
  if slot.material and slot.material.name==oldmat:slot.link='OBJECT';slot.material=newmat;found+=1
 if not found:raise RuntimeError('Expected body material not found on '+srcname)
 src.hide_render=True;src.hide_viewport=True
 assert obj.data==src.data
 replacements.append({'source_object':srcname,'replacement_object':newname,'linked_mesh_unchanged':obj.data==src.data,'material_slot_overrides':found,'material':newmat.name})
s=bpy.context.scene;s['v005_scope']='Two tower body material overrides only. Geometry, windows, lighting and exposure are unchanged. Fine mortar is shader relief, not new geometry.';s.render.filepath='//previews/v005_tower_stone.png';s.render.use_stamp=False
for k in ['use_stamp_filename','use_stamp_date','use_stamp_time']:
 if hasattr(s.render,k):setattr(s.render,k,False)
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
report={'version':'v005 tower material calibration B retained macro patina','source_filename':os.path.basename(source),'source_sha256':hashlib.sha256(open(source,'rb').read()).hexdigest(),'output_filename':os.path.basename(output),'replacements':replacements,'new_materials':[main.name,west.name],'original_materials_unchanged':True,'new_meshes':0,'new_geometry_faces':0,'unit_settings':{'system':s.unit_settings.system,'scale_length':s.unit_settings.scale_length},'stone_dimensions_scene_units':{'main':[1.30,.52],'west':[1.65,.65]},'projection':'True-normal selected world XZ/YZ, XY tops, equal world-unit scale','mortar_is_shader_bump_not_displacement':True,'lighting_world_exposure_unchanged':True,'status':'Awaiting same-view render review; not project completion.'}
os.makedirs(os.path.dirname(output),exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=output,compress=True);report['output_sha256']=hashlib.sha256(open(output,'rb').read()).hexdigest()
with open(a.report,'w',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
