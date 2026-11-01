"""Read-only datablock and editability inventory; never purge or save."""
import bpy,json,hashlib,time,collections
from pathlib import Path
src=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(src);assert before=='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd'
def block(b):return {'name':b.name,'users':b.users,'fake_user':b.use_fake_user,'library':b.library.filepath if b.library else None}
r={'source_sha256':before,'file_bytes':src.stat().st_size,'datablocks':{},'modifiers':[],'collections':[],'hidden_meshes':[]}
for category in ['meshes','materials','images','actions','node_groups','curves','cameras','lights','textures']:
 items=list(getattr(bpy.data,category));r['datablocks'][category]={'count':len(items),'zero_users':[block(b) for b in items if b.users==0],'fake_users':[block(b) for b in items if b.use_fake_user]}
# Hash complete serialized mesh payload via established deep validator; non-mesh resources inspected only, not guessed duplicates.
import sys
sys.path.insert(0,str(Path('work/navigation_v015').resolve()))
from deep_snapshot import mesh_snapshot,digest
byhash=collections.defaultdict(list)
for m in bpy.data.meshes:
 payload=mesh_snapshot(m);byhash[digest(payload)].append(block(m)|{'vertices':len(m.vertices),'polygons':len(m.polygons)})
r['exact_mesh_payload_duplicates']=[v for v in byhash.values() if len(v)>1]
for o in bpy.data.objects:
 if o.type=='MESH' and (o.hide_render or o.hide_viewport):r['hidden_meshes'].append(block(o)|{'mesh':o.data.name,'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)})
 for m in o.modifiers:r['modifiers'].append({'object':o.name,'name':m.name,'type':m.type,'show_render':m.show_render,'show_viewport':m.show_viewport,'properties':{k:getattr(m,k) for k in ['levels','render_levels','width','segments','strength'] if hasattr(m,k)}})
for c in bpy.data.collections:r['collections'].append(block(c)|{'objects':len(c.objects),'children':[x.name for x in c.children],'hide_render':c.hide_render,'hide_viewport':c.hide_viewport})
r['images']=[block(i)|{'size':list(i.size),'source':i.source,'filepath':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images]
r['material_usage']=[block(m) for m in bpy.data.materials]
r['object_type_counts']=dict(collections.Counter(o.type for o in bpy.data.objects));r['source_unchanged']=sha(src)==before;r['model_saved']=False;r['limitations']='No delete/merge, no measured post-cleanup file/runtime savings. Exact mesh payload hashes include data attributes but object/material/collection semantics still require independent validation before any dedup. Hidden originals are recoverable baseline, not cleanup candidates.'
Path('work/performance_editability_v018/inventory.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:r[k] for k in ['datablocks','exact_mesh_payload_duplicates','object_type_counts','source_unchanged']},indent=2))
