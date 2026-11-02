"""Read-only saved architecture audit: exact simulated native mask, full rollback, geometry export."""
import argparse,copy,hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
if sys.flags.optimize:raise RuntimeError('Optimization refused')
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
import snapshot_support as ss
SOURCE='37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255'
PAYLOAD='0d07d8ceb27f44cd3c612392d56b40921e60c7f8afaa522aa04f74c17df817f2'
COLL='V028 | reversible receiving chamber'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(x,msg):
 if not x:raise RuntimeError(msg)
def controls(payload,add):
 for t in payload['targets']:
  o=bpy.data.objects[t['object']]
  if add:
   need(not o.modifiers and not o.vertex_groups,'Unexpected source controls')
   g=o.vertex_groups.new(name=t['group_name']);g.add(t['raw_vertex_ids'],1.,'REPLACE');m=o.modifiers.new(t['mask_name'],'MASK');m.mode='VERTEX_GROUP';m.vertex_group=g.name;m.invert_vertex_group=True;m.threshold=.5;m.use_smooth=False
  else:
   need(len(o.modifiers)==1 and len(o.vertex_groups)==1,'Wrong target control count')
   g=o.vertex_groups[t['group_name']];m=o.modifiers[t['mask_name']]
   need([(v.index,[(w.group,w.weight) for w in v.groups]) for v in o.data.vertices if v.groups]==[(i,[(g.index,1.)]) for i in t['raw_vertex_ids']],'Wrong exact weights')
   bpy.data.objects[t['object']].modifiers.remove(m);o.vertex_groups.remove(g)
 bpy.context.view_layer.update()
def snap():
 d=ss.snap();d['collections']=ss.collections_snapshot();d['scene_custom']=dict(bpy.context.scene.items());return d
def compare(left,right,names):
 left=copy.deepcopy(left);right=copy.deepcopy(right);ui=[]
 for cat in ('objects','meshes','visible_evaluated'):
  need(set(right[cat])-set(left[cat])==set(names),'Unexpected added '+cat)
  for n in names:right[cat].pop(n)
 need(set(right['collections']['collections'])-set(left['collections']['collections'])=={COLL},'Wrong collections')
 c=right['collections']['collections'].pop(COLL);need(c['objects']==sorted(names) and c['children']==[] and not any(c[k] for k in ['hide_render','hide_viewport','hide_select']) and c['properties']=={},'Owned collection drift')
 right['collections']['root_children'].remove(COLL)
 for n in ['Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic']:
  need(any(m['type']=='SUBSURF' for m in left['objects'][n]['modifiers']),'UI exception wrong object')
  l,lu=ss.render_semantic_with_ui_report(left['visible_evaluated'][n]);r,ru=ss.render_semantic_with_ui_report(right['visible_evaluated'][n]);left['visible_evaluated'][n]=l;right['visible_evaluated'][n]=r;ui.append({'object':n,'source':lu,'candidate':ru})
 checks={k:left[k]==right[k] for k in left};changed={k:[n for n in set(left[k])|set(right[k]) if left[k].get(n)!=right[k].get(n)] for k in left if isinstance(left[k],dict) and not checks[k]}
 need(all(checks.values()),repr(changed));return {'categories':checks,'derived_UI_only':ui}
def main():
 p=argparse.ArgumentParser()
 for k in ['source','candidate','candidate-sha','payload','report','geometry']:p.add_argument('--'+k,required=True)
 a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);need(sha(a.source)==SOURCE and sha(a.payload)==PAYLOAD and sha(a.candidate)==a.candidate_sha,'Wrong inputs')
 need(not Path(a.report).exists() and not Path(a.geometry).exists(),'Output exists');payload=json.loads(Path(a.payload).read_text());names=[m['name'] for m in payload['meshes']]
 bpy.ops.wm.open_mainfile(filepath=str(Path(a.source).resolve()),load_ui=True,use_scripts=False);original=snap();controls(payload,True);expected=snap()
 bpy.ops.wm.open_mainfile(filepath=str(Path(a.candidate).resolve()),load_ui=True,use_scripts=False);high=snap();highcheck=compare(expected,high,names)
 exports=[]
 for spec in payload['meshes']:
  o=bpy.data.objects[spec['name']];me=o.data;need(me.name==o.name and me.users==1 and not o.modifiers and not o.constraints and not o.vertex_groups and o.parent is None and not o.hide_render and not o.hide_viewport and not o.hide_get(),'New object state drift')
  need([list(row) for row in o.matrix_world]==[[float(i==j) for j in range(4)] for i in range(4)],'New transform changed')
  need([list(v.co) for v in me.vertices]==spec['vertices'] and [list(f.vertices) for f in me.polygons]==spec['faces'],'Saved payload geometry drift')
  need([(s.link,s.material.name) for s in o.material_slots]==[('DATA','Citadel • weathered limestone')],'New material drift')
  need(all(f.material_index==0 and not f.use_smooth and f.select and not f.hide for f in me.polygons),'Face flags drift')
  me.calc_loop_triangles();exports.append({'name':o.name,'vertices':[list(v.co) for v in me.vertices],'faces':[list(f.vertices) for f in me.polygons],'triangles':[list(t.vertices) for t in me.loop_triangles],'triangle_polygons':[t.polygon_index for t in me.loop_triangles],'face_lineage':spec['face_lineage']})
 controls(payload,False);low=snap();lowcheck=compare(original,low,names);controls(payload,True);repeat=snap();repeatcheck=compare(expected,repeat,names)
 need(sha(a.source)==SOURCE and sha(a.candidate)==a.candidate_sha and sha(a.payload)==PAYLOAD,'Inputs changed')
 out={'pass':True,'source_sha256':SOURCE,'candidate_sha256':a.candidate_sha,'payload_sha256':PAYLOAD,'high_full_simulated_native_mask':highcheck,'native_control_removal_full_source_rollback':lowcheck,'repeat_high':repeatcheck,'owned_weights':148,'saved_meshes_exact_payload':True,'limits':'Rollback proof restores original source data/evaluation; added objects remain stored. No rendering, structural or global navigation certification.'}
 Path(a.geometry).write_text(json.dumps({'candidate_sha256':a.candidate_sha,'meshes':exports}));Path(a.report).write_text(json.dumps(out,indent=2));print('NATIVE ARCHITECTURE PRESERVATION PASS',flush=True)
if __name__=='__main__':main()
