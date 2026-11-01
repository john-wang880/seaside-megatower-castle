import bpy,sys,argparse,json,hashlib
from pathlib import Path
import sys
if sys.flags.optimize:raise RuntimeError('Optimized Python unsupported')
sys.path.insert(0,str(Path(__file__).resolve().parent));import snapshot_support as ss
p=argparse.ArgumentParser()
for k in ['source','candidate','candidate-sha','scope','report']:p.add_argument('--'+k,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);assert not Path(a.report).exists();scope=json.loads(Path(a.scope).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();hashes={k:sha(getattr(a,k))for k in ['source','candidate']};assert hashes['source']==scope['source_sha256']=='89f9f6a8a57103d99100935b96624469ddf1fd52b9703e0d9177a352e735c856'and hashes['candidate']==a.candidate_sha;target=scope['target'];ids=sorted(i for g in scope['groups']for i in g['raw_vertex_ids'])
def ev():
 s=ss.snap()['visible_evaluated']
 for n in ['Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic']:s[n],_=ss.render_semantic_with_ui_report(s[n])
 return s
bpy.ops.wm.open_mainfile(filepath=str(Path(a.source).resolve()),use_scripts=False);base=ev();o=bpy.data.objects[target];g=o.vertex_groups.new(name='QA exact new group propagation');assert g.index==1;g.add(ids,1.,'REPLACE');bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(dg);me=eo.to_mesh();expected=[(i,[(w.group,w.weight)for w in v.groups])for i,v in enumerate(me.vertices)if v.groups];eo.to_mesh_clear();o.vertex_groups.remove(g)
bpy.ops.wm.open_mainfile(filepath=str(Path(a.candidate).resolve()),use_scripts=False);o=bpy.data.objects[target];m=o.modifiers[2];assert m.name==scope['new_modifier'];m.show_viewport=m.show_render=False
for g in scope['groups']:
 u=bpy.data.objects[g['replacement_object']];u.hide_viewport=u.hide_render=True
bpy.context.view_layer.update();low=ev();payload=low[target]['mesh']['debug_payload'];weights=payload['weights'];assert weights==expected,'Inherited new/old weight arrays differ from original native chain';clean=[(i,[(group,w)for group,w in ws if group!=1])for i,ws in weights];clean=[(i,w)for i,w in clean if w];assert clean==base[target]['mesh']['debug_payload']['weights'];payload['weights']=clean;low[target]['mesh']['hash']=ss.digest(payload);assert low==base,('LOW mismatch',[n for n in base if low.get(n)!=base[n]]);assert all(sha(getattr(a,k))==v for k,v in hashes.items());Path(a.report).write_text(json.dumps({'pass':True,'input_sha256':hashes,'native_low_evaluator_exact_to_v024':True,'old_v024_group_and_union_preserved':True,'sole_normalization':'Only owned group1 values, proven bit-exact to original source-chain propagation of160rawweight1 assignments; all oldgroup0 values retained.','inherited_newgroup_vertex_count':sum(any(g==1 for g,w in ws)for i,ws in weights),'inherited_newgroup_values':sorted(set(w for i,ws in weights for g,w in ws if g==1))},indent=2));print('NATIVE V024 LOW EXACT')
