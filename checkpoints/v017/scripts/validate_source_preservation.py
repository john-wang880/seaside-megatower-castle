"""Read-only deep semantic source preservation audit; only V017 roof-course additions allowed.
Hashes persisted mesh attributes/topology/shading data, plus evaluated visible
mesh data. It does not equate Blender file bytes (which intentionally differ).
"""
import argparse,array,bpy,hashlib,json,os,sys,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--baseline',required=True);p.add_argument('--checkpoint',required=True);p.add_argument('--report',required=True);p.add_argument('--expected-additions',type=int,default=4);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
allowed=set()
originals={'Dense western woodland | irregular three-dimensional needle boughs','Woodland tree trunks','V010 | woodland boughs with gate exit clearance','V010 | woodland trunks with gate exit clearance'}
start=time.time();source_sha=hashlib.sha256(Path(a.baseline).read_bytes()).hexdigest();candidate_sha=hashlib.sha256(Path(a.checkpoint).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def val(x):
 if x is None or isinstance(x,(bool,int,float,str)):return x
 if isinstance(x,bytes):return x.hex()
 if isinstance(x,set):return sorted(x)
 if isinstance(x,bpy.types.ID):return {'id_type':x.bl_rna.identifier,'name':x.name}
 if hasattr(x,'items'):return {str(k):val(v) for k,v in x.items()}
 try:return [val(q) for q in x]
 except TypeError:return str(type(x).__name__)
def primitive(o,depth=0):
 d={}
 for prop in o.bl_rna.properties:
  n=prop.identifier
  if n in {'rna_type','users','session_uid','is_updated','is_updated_data','is_evaluated','is_runtime_data','original','tag','is_embedded_data','is_missing','is_library_indirect','is_editable','is_editmode'}:continue
  if prop.type in {'BOOLEAN','INT','FLOAT','STRING','ENUM'}:
   try:d[n]=val(getattr(o,n))
   except (AttributeError,TypeError):pass
  elif prop.type=='POINTER':
   target=getattr(o,n,None)
   if target is None or isinstance(target,bpy.types.ID):d[n]=val(target)
   elif depth<2:d[n]=primitive(target,depth+1)
  elif prop.type=='COLLECTION' and depth<1 and n not in {'rna_properties'}:
   collection=getattr(o,n,[])
   d[n]=[primitive(q,depth+1) if hasattr(q,'bl_rna') else val(q) for q in collection]
 if hasattr(o,'items'):
  try:d['custom_properties']={str(k):val(v) for k,v in o.items()}
  except TypeError:d['custom_properties']=None # RNA struct cannot carry ID properties
 return d

def field_hash(coll,name,kind,width=1):
 if not len(coll):return {'count':0,'hash':None}
 code={'FLOAT':'f','INT':'i','BOOLEAN':'b'}[kind];buf=array.array(code,[0])*(len(coll)*max(1,width));coll.foreach_get(name,buf)
 return {'count':len(coll),'type':kind,'width':width,'hash':hashlib.sha256(buf.tobytes()).hexdigest()}
def mesh_snapshot(m):
 attrs=[]
 for attr in m.attributes:
  fields={}
  if len(attr.data):
   for prop in attr.data[0].bl_rna.properties:
    if prop.identifier=='rna_type':continue
    if prop.type in {'FLOAT','INT','BOOLEAN'}:fields[prop.identifier]=field_hash(attr.data,prop.identifier,prop.type,prop.array_length)
    elif prop.type=='STRING':fields[prop.identifier]=digest([val(getattr(q,prop.identifier)) for q in attr.data])
    else:raise AssertionError(('Unsupported attribute field',attr.name,prop.identifier,prop.type))
  attrs.append({'name':attr.name,'type':attr.data_type,'domain':attr.domain,'count':len(attr.data),'fields':fields})
 topology={}
 for label,coll,props in [('vertices',m.vertices,[('co','FLOAT',3),('select','BOOLEAN',1),('hide','BOOLEAN',1)]),('edges',m.edges,[('vertices','INT',2),('select','BOOLEAN',1),('hide','BOOLEAN',1),('use_seam','BOOLEAN',1),('use_edge_sharp','BOOLEAN',1)]),('loops',m.loops,[('vertex_index','INT',1),('edge_index','INT',1)]),('polygons',m.polygons,[('loop_start','INT',1),('loop_total','INT',1),('material_index','INT',1),('use_smooth','BOOLEAN',1),('select','BOOLEAN',1),('hide','BOOLEAN',1)])]:
  topology[label]={n:field_hash(coll,n,k,w) for n,k,w in props if not len(coll) or hasattr(coll[0],n)}
 weights=[(i,[(q.group,q.weight) for q in v.groups]) for i,v in enumerate(m.vertices) if len(v.groups)]
 shapes=None
 if m.shape_keys:shapes=[{'name':k.name,'value':k.value,'relative_key':k.relative_key.name,'coordinates':field_hash(k.data,'co','FLOAT',3)} for k in m.shape_keys.key_blocks]
 return {'hash':digest({'attributes':attrs,'topology':topology,'corner_normals':field_hash(m.corner_normals,'vector','FLOAT',3),'materials':[q.name if q else None for q in m.materials],'weights':weights,'shapes':shapes,'uv_layers':[primitive(q) for q in m.uv_layers],'uv_active_index':m.uv_layers.active_index,'custom_properties':{k:val(v) for k,v in m.items()}}),'attribute_schema':[(q['name'],q['type'],q['domain'],q['count']) for q in attrs],'vertices':len(m.vertices),'polygons':len(m.polygons)}

def tree_snapshot(t,seen=None):
 if t is None:return None
 seen=set() if seen is None else seen
 if t.name in seen:return {'recursive_reference':t.name}
 seen=seen|{t.name};nodes=[]
 for n in t.nodes:
  d={'properties':primitive(n),'inputs':[{'name':s.name,'identifier':s.identifier,'type':s.bl_idname,'value':val(s.default_value) if hasattr(s,'default_value') else None} for s in n.inputs]}
  if hasattr(n,'node_tree') and n.node_tree:d['group']=tree_snapshot(n.node_tree,seen)
  if hasattr(n,'color_ramp'):d['ramp']={'properties':primitive(n.color_ramp),'elements':[primitive(e) for e in n.color_ramp.elements]}
  if hasattr(n,'mapping') and hasattr(n.mapping,'curves'):d['curves']={'properties':primitive(n.mapping),'curves':[[primitive(p) for p in c.points] for c in n.mapping.curves]}
  nodes.append(d)
 return {'nodes':nodes,'links':sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in t.links)}
def snap():
 deps=bpy.context.evaluated_depsgraph_get();evaluated={};objects={}
 for o in bpy.data.objects:
  objects[o.name]={'properties':primitive(o),'type':o.type,'data':o.data.name if o.data else None,'matrix':[list(row) for row in o.matrix_world],'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'hidden':o.hide_get(),'parent':o.parent.name if o.parent else None,'parent_inverse':[list(row) for row in o.matrix_parent_inverse],'slots':[(s.link,s.material.name if s.material else None) for s in o.material_slots],'modifiers':[primitive(m) for m in o.modifiers],'constraints':[primitive(c) for c in o.constraints],'vertex_groups':[primitive(g) for g in o.vertex_groups],'custom_properties':{k:val(v) for k,v in o.items()}}
  if o.type=='MESH' and not o.hide_render:
   eo=o.evaluated_get(deps);me=eo.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
   evaluated[o.name]={'matrix':[list(row) for row in eo.matrix_world],'mesh':mesh_snapshot(me)};eo.to_mesh_clear()
 scene=bpy.context.scene
 return {'meshes':{m.name:mesh_snapshot(m) for m in bpy.data.meshes},'objects':objects,'materials':{m.name:digest({'properties':primitive(m),'nodes':tree_snapshot(m.node_tree)}) for m in bpy.data.materials},'lights':{l.name:digest({'properties':primitive(l),'nodes':tree_snapshot(l.node_tree)}) for l in bpy.data.lights},'cameras':{c.name:digest({'properties':primitive(c),'dof':primitive(c.dof)}) for c in bpy.data.cameras},'worlds':{w.name:digest({'properties':primitive(w),'nodes':tree_snapshot(w.node_tree)}) for w in bpy.data.worlds},'visible_evaluated':evaluated,'scene':{'world':scene.world.name if scene.world else None,'camera':scene.camera.name if scene.camera else None,'render':primitive(scene.render),'cycles':primitive(scene.cycles),'view':primitive(scene.view_settings),'frame':scene.frame_current,'unit':primitive(scene.unit_settings)},'libraries':[l.filepath for l in bpy.data.libraries],'texts':[(t.name,hashlib.sha256(t.as_string().encode()).hexdigest()) for t in bpy.data.texts]}
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a.baseline),load_ui=True,use_scripts=False);base=snap()
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a.checkpoint),load_ui=True,use_scripts=False);check=snap()
removed_objects=set(base['objects'])-set(check['objects']);removed_meshes=set(base['meshes'])-set(check['meshes'])
diffs={}
for category in ('objects','meshes','materials','lights','cameras','worlds','visible_evaluated'):
 diffs[category]=[n for n in set(base[category])&set(check[category]) if base[category][n]!=check[category][n]]
 diffs[category+'_added']=sorted(set(check[category])-set(base[category]))
 if category not in ('objects','meshes'):diffs[category+'_removed']=sorted(set(base[category])-set(check[category]))
for category in ('scene','libraries','texts'):diffs[category]=[] if base[category]==check[category] else ['changed']
source_unchanged=source_sha==hashlib.sha256(Path(a.baseline).read_bytes()).hexdigest();candidate_unchanged=candidate_sha==hashlib.sha256(Path(a.checkpoint).read_bytes()).hexdigest()
r={'source_sha256':source_sha,'candidate_sha256':candidate_sha,'source_file_unchanged':source_unchanged,'candidate_file_unchanged':candidate_unchanged,'allowed_removed_objects':sorted(allowed),'removed_objects':sorted(removed_objects),'removed_meshes':sorted(removed_meshes),'removed_objects_were_hidden':all(base['objects'][n]['hide_render'] for n in removed_objects),'original_full_forest_and_latest_visible_preserved':originals<=set(check['objects']) and all(base['objects'][n]==check['objects'][n] and base['meshes'][base['objects'][n]['data']]==check['meshes'][check['objects'][n]['data']] for n in originals),'remaining_meshes_checked':len(check['meshes']),'visible_evaluated_meshes_checked':len(check['visible_evaluated']),'differences':diffs,'attribute_schemas':{n:v['attribute_schema'] for n,v in check['meshes'].items()},'scope':'Deep semantic identity of all remaining persisted mesh topology/attribute fields, material slots, deform weights, shape keys, computed corner normals, node graphs, transforms and evaluated visible mesh data. Exact blend file bytes intentionally differ; source/candidate themselves not saved.','seconds':time.time()-start}
allowed_additions={'objects':a.expected_additions,'meshes':a.expected_additions,'materials':0,'lights':0,'visible_evaluated':a.expected_additions}
additions_valid=all(len(diffs.get(k+'_added',[]))==count and all(n.startswith('V017 | main crown ') for n in diffs[k+'_added']) for k,count in allowed_additions.items())
remaining_differences={k:v for k,v in diffs.items() if k not in {c+'_added' for c in allowed_additions}}
r['addition_counts_valid']=additions_valid
r['source_preservation_pass']=removed_objects==allowed and removed_meshes==allowed and additions_valid and not any(remaining_differences.values()) and r['removed_objects_were_hidden'] and r['original_full_forest_and_latest_visible_preserved'] and source_unchanged and candidate_unchanged
Path(a.report).write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in('attribute_schemas',)},ensure_ascii=False));assert r['source_preservation_pass'],'Inspect differences report'
