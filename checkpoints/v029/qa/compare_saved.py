"""Full persistent/evaluated semantic equality of rebuilt versus accepted saved file."""
import sys,argparse,hashlib,json
from pathlib import Path
sys.dont_write_bytecode=True
if sys.flags.optimize:raise RuntimeError('Optimization refused')
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent));import snapshot_support as ss
p=argparse.ArgumentParser()
for k in ['accepted','candidate','candidate-sha','report']:p.add_argument('--'+k,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();pins={a.accepted:sha(a.accepted),a.candidate:sha(a.candidate)};assert pins[a.accepted]=='4f838529d32cbf6a0314cc0a23b3dd1703b73d80c5db146fb4d323697b882df5' and pins[a.candidate]==a.candidate_sha;assert not Path(a.report).exists()
def snap(path):
 bpy.ops.wm.open_mainfile(filepath=str(Path(path).resolve()),load_ui=True,use_scripts=False);d=ss.snap();d['collections']=ss.collections_snapshot();d['scene_custom']=dict(bpy.context.scene.items());return d
l=snap(a.accepted);r=snap(a.candidate);ui=[]
for n in ['Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic']:
 assert any(m['type']=='SUBSURF' for m in l['objects'][n]['modifiers']);lv,lu=ss.render_semantic_with_ui_report(l['visible_evaluated'][n]);rv,ru=ss.render_semantic_with_ui_report(r['visible_evaluated'][n]);l['visible_evaluated'][n]=lv;r['visible_evaluated'][n]=rv;ui.append({'object':n,'accepted':lu,'rebuilt':ru})
checks={k:l[k]==r[k] for k in l};assert all(checks.values()),[k for k,v in checks.items() if not v];assert all(sha(p)==h for p,h in pins.items());Path(a.report).write_text(json.dumps({'pass':True,'input_sha256':pins,'checks':checks,'derived_UI_only':ui},indent=2));print('SAVED FULL SEMANTIC REPEAT PASS')
