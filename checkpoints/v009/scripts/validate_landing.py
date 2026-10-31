import bpy,json,argparse,sys
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
body=bpy.data.objects['V009 | nine broad western approach treads'];slab=bpy.data.objects['V007 | continuous stone passage threshold']
def hit(o,x,y):
 inv=o.matrix_world.inverted();h,v,n,i=o.ray_cast(inv@Vector((x,y,40)),inv.to_3x3()@Vector((0,0,-1)));assert h;return(o.matrix_world@v).z
r={'landing_samples':[{'x':x,'y':y,'height':hit(body,x,y)} for x in (-71.9,-71.5,-71.25) for y in (36.6,38,39.4)],'overlap_samples':[{'y':y,'height_delta':abs(hit(body,-71.25,y)-hit(slab,-71.25,y))} for y in(36.6,38,39.4)]}
r['continuous_gate_connection']=all(abs(q['height']-27.4)<.002 for q in r['landing_samples']) and all(q['height_delta']<.002 for q in r['overlap_samples']);Path(a.report).write_text(json.dumps(r,indent=2));print(r);assert r['continuous_gate_connection']
