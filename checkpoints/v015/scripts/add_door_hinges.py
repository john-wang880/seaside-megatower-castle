"""Four bounded static door-support hinges; preserve all existing scene data."""
import bpy,sys,argparse,hashlib,json,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
src=Path(bpy.data.filepath);out=Path(a.output).resolve();sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha=='83ea4d898b232e1f9d5f3ee314d16227a3fb31b954f88e4e5c3bdb5be8c2add5';assert src.resolve()!=out and not out.exists();assert not any(o.name.startswith('V015 |') for o in bpy.data.objects)
mat=bpy.data.materials['V013 | dark forged lantern iron'];made=[]
def prism(name,poly,lo,hi,side):
 vs=[(x, y if side=='south' else 76-y,z) for z in(lo,hi) for x,y in poly];n=len(poly);fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 if side=='north':fs=[tuple(reversed(f)) for f in fs]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(mat);me.update();ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob);made.append(name);return ob
for side in('south','north'):
 for level,z in(('lower',29.69),('upper',30.59)):
  name=f'V015 | {side} hinge {level} '
  prism(name+'neck',[(-3.73,35.705),(-3.51,35.705),(-3.51,35.94),(-3.59,35.94),(-3.59,35.725),(-3.73,35.725)],z-.04,z+.04,side)
  def cylinder(suffix,r,lo,hi):return prism(name+suffix,[(-3.55+r*math.cos(2*math.pi*i/24),35.9+r*math.sin(2*math.pi*i/24)) for i in range(24)],lo,hi,side)
  cylinder('barrel',.055,z-.07,z+.07)
  prism(name+'pintle',[(-3.545,35.85),(-3.43,35.85),(-3.43,35.94),(-3.545,35.94)],z-.10,z-.05,side)
  prism(name+'wall anchor',[(-3.50,35.78),(-3.43,35.78),(-3.43,35.90),(-3.50,35.90)],z-.16,z+.10,side)
  cylinder('pin cap',.045,z+.06,z+.09)
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
Path(a.report).write_text(json.dumps({'source_sha256':sha,'model_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'objects_added':made,'material_shared':mat.name,'scope':'Four static support assemblies outside central passage; original door meshes, materials, lights and world unchanged. No hinge animation, structural-load or mechanical articulation certification.'},indent=2))
