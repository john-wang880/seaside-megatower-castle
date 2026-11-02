"""Opt-in additive stores fittings builder. No rendering, source overwrite or auto-run."""
import argparse,collections,hashlib,json,math,os,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
SOURCE='4f838529d32cbf6a0314cc0a23b3dd1703b73d80c5db146fb4d323697b882df5'
PLAN_SHA='4886e670675dc64d56abedffc89196a60d7b349f68201ba402c7c6f3e695da38'
HELPER_SHA='ef8b575c70fbb394bfd76cba93b97bc07a6c03abdfe7f4eb2752cfd236be6249'
COLLECTION='V030 | reversible stores fittings'
MATERIAL='V030 | subdued stores timber'
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def safe(path,existing=False):
 p=Path(path).expanduser().absolute();need('..' not in p.parts and p.resolve()==p and not any(q.is_symlink()for q in [p,*p.parents]),'Aliased path refused')
 need(p.is_file()if existing else p.parent.is_dir()and not os.path.lexists(p),'Missing input or occupied output');return p
def prism(lo,hi,chamfer=.008):
 x,y,z=lo;X,Y,Z=hi;c=chamfer;need(all(math.isfinite(v)for v in lo+hi)and X-x>2*c and Y-y>2*c and Z>z,'Bad primitive')
 ring=[(x+c,y),(X-c,y),(X,y+c),(X,Y-c),(X-c,Y),(x+c,Y),(x,Y-c),(x,y+c)]
 v=[[a,b,h]for h in [z,Z]for a,b in ring];f=[list(reversed(range(8))),list(range(8,16))]+[[i,(i+1)%8,(i+1)%8+8,i+8]for i in range(8)]
 return v,f
def certify(v,f):
 edges=collections.Counter();directions=collections.Counter();volume=0.
 for face in f:
  need(len(set(face))==len(face)>=3,'Repeated face vertex')
  for a,b in zip(face,face[1:]+face[:1]):edges[tuple(sorted((a,b)))]+=1;directions[a,b]+=1
  a=v[face[0]]
  for j in range(1,len(face)-1):
   b=v[face[j]];c=v[face[j+1]];volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
 need(all(n==2 for n in edges.values())and all(directions[a,b]==directions[b,a]==1 for a,b in edges),'Nonclosed/winding edge')
 need(volume>0,'Nonpositive volume');return volume

def geometry(plan):
 need(plan['candidate_sha256']==SOURCE and len(plan['primitive_parts'])==74,'Wrong plan scope')
 result={};counter=0
 for old in plan['primitive_parts']:
  isbin=old['role'].startswith('bin');side=old['name'].split()[0]
  key=('V030 | '+old['name'])if isbin else 'V030 | '+side+' three-bay rack'
  m=result.setdefault(key,{'name':key,'vertices':[],'faces':[],'components':[]})
  lo=list(old['min']);hi=list(old['max']);pieces=[]
  if isbin:
   cut=hi[2]-.04;pieces=[('body',[lo[0]+.006,lo[1]+.006,lo[2]],[hi[0]-.006,hi[1]-.006,cut]),('lid',[lo[0],lo[1],cut],hi)]
  else:pieces=[('whole',lo,hi)]
  for label,a,b in pieces:
   v,f=prism(a,b);volume=certify(v,f);offset=len(m['vertices']);start=len(m['faces']);m['vertices']+=v;m['faces'] +=[[offset+i for i in p]for p in f]
   m['components'].append({'id':counter,'source_primitive':old['name'],'role':old['role'],'part':label,'vertex_range':[offset,len(m['vertices'])],'face_range':[start,len(m['faces'])],'bounds':[a,b],'corner_chamfer_xy':.008,'bottom_seat_z':a[2],'top_z':b[2],'analytic_volume':volume,'triangles':sum(len(p)-2 for p in f)});counter+=1
 need(len(result)==6 and counter==78,'Wrong additive scope');tri=sum(sum(len(f)-2 for f in m['faces'])for m in result.values());need(1500<=tri<=3000 and tri<=5000,'Budget failure')
 return list(result.values())

def main():
 need(not sys.flags.optimize,'Optimized Python refused')
 ap=argparse.ArgumentParser();[ap.add_argument('--'+k,required=True)for k in ['source','output','report']]
 a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else sys.argv[1:]);src=safe(a.source,True);out=safe(a.output);rp=safe(a.report)
 need(len({src,out,rp})==3 and out.suffix=='.blend'and rp.suffix=='.json','Output role mismatch')
 pp=ROOT/'PLAN.json';hp=ROOT/'snapshot_support.py';need(sha(src)==SOURCE,'Wrong source hash');need(sha(pp)==PLAN_SHA and sha(hp)==HELPER_SHA,'Frozen helper/plan changed')
 pins={str(p):sha(p)for p in [src,pp,hp,Path(__file__)]};specs=geometry(json.loads(pp.read_text()))
 import bpy
 need(bpy.app.version==(5,2,3),'Requires reviewed Blender5.2.3');need(not bpy.data.filepath,'Factory-empty Blender required')
 bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
 sys.path.insert(0,str(ROOT));import snapshot_support as sn
 need(COLLECTION not in bpy.data.collections and MATERIAL not in bpy.data.materials,'Owned namespace collision')
 need(all(m['name']not in bpy.data.objects and m['name']not in bpy.data.meshes for m in specs),'Owned object/mesh collision')
 before=sn.snap();beforecols=sn.collections_snapshot();selection=[o.name for o in bpy.context.selected_objects];active=bpy.context.view_layer.objects.active.name if bpy.context.view_layer.objects.active else None
 mat=bpy.data.materials.new(MATERIAL);mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links
 outnode=nodes.new('ShaderNodeOutputMaterial');bsdf=nodes.new('ShaderNodeBsdfPrincipled');bsdf.inputs['Roughness'].default_value=.82;links.new(bsdf.outputs['BSDF'],outnode.inputs['Surface'])
 geo=nodes.new('ShaderNodeNewGeometry');noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2.;noise.inputs['Detail'].default_value=1.;links.new(geo.outputs['Position'],noise.inputs['Vector'])
 ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.14,.095,.06,1);ramp.color_ramp.elements[1].color=(.20,.145,.095,1);links.new(noise.outputs['Fac'],ramp.inputs['Fac']);links.new(ramp.outputs['Color'],bsdf.inputs['Base Color'])
 coll=bpy.data.collections.new(COLLECTION);bpy.context.scene.collection.children.link(coll);actual=[]
 for spec in specs:
  me=bpy.data.meshes.new(spec['name']);me.from_pydata(spec['vertices'],[],spec['faces']);me.update();me.materials.append(mat);o=bpy.data.objects.new(spec['name'],me);coll.objects.link(o)
  for p in me.polygons:p.use_smooth=False;p.material_index=0
  me.calc_loop_triangles();need(len(me.loop_triangles)==sum(len(p)-2 for p in spec['faces']),'Native triangle count changed')
  av=[list(v.co)for v in me.vertices];af=[list(p.vertices)for p in me.polygons]
  for c in spec['components']:
   a,b=c['vertex_range'];f0,f1=c['face_range'];certify(av[a:b],[[i-a for i in f]for f in af[f0:f1]])
  actual.append({'name':o.name,'vertices':av,'faces':af,'triangles':[list(t.vertices)for t in me.loop_triangles],'components':spec['components'],'material':mat.name,'matrix_world':[list(r)for r in o.matrix_world]})
 bpy.context.view_layer.update();after=sn.snap()
 for category,old in before.items():
  if isinstance(old,dict):need(all(after[category].get(k)==v for k,v in old.items()),'Original source changed: '+category)
  else:need(after[category]==old,'Original source changed: '+category)
 cs=sn.collections_snapshot();need(all(cs['collections'].get(k)==v for k,v in beforecols['collections'].items()),'Original collections changed');need(cs['root_objects']==beforecols['root_objects']and sorted(cs['root_children'])==sorted(beforecols['root_children']+[COLLECTION]),'Collection delta wrong')
 need([o.name for o in bpy.context.selected_objects]==selection and (bpy.context.view_layer.objects.active.name if bpy.context.view_layer.objects.active else None)==active,'Source selection changed')
 need(all(sha(p)==h for p,h in pins.items()),'Inputs changed')
 report={'status':'UNACCEPTED fittings candidate; independent saved support/visibility/art gates required','source_sha256':SOURCE,'inputs':pins,'source_preservation_pass':True,'source_selection_preserved':True,'collection':COLLECTION,'material':MATERIAL,'new_meshes':actual,'components':78,'triangles':sum(len(m['triangles'])for m in actual),'braces_added':False,'source_saved':False,'rendered':False,'geometry_semantic_sha256':sn.digest(actual),'material_graph_sha256':sn.digest(sn.tree_snapshot(mat.node_tree))}
 temps=[];published=[]
 try:
  def temp(dest,suffix):
   fd,n=tempfile.mkstemp(prefix='.v030-',suffix=suffix,dir=dest.parent);os.close(fd);p=Path(n);temps.append(p);return p
  model=temp(out,'.blend');model.unlink();res=bpy.ops.wm.save_as_mainfile(filepath=str(model),copy=True,compress=True,check_existing=False);need('FINISHED'in res,'Save failed');need(all(sha(p)==h for p,h in pins.items()),'Input changed during save')
  report.update(candidate_sha256=sha(model),candidate_bytes=model.stat().st_size);rr=temp(rp,'.json');rr.write_text(json.dumps(report,indent=2)+'\n')
  for source,dest in [(model,out),(rr,rp)]:safe(dest);st=os.stat(source);os.link(source,dest);published.append((dest,st))
 except BaseException:
  for dest,st in reversed(published):
   now=os.lstat(dest)
   if (now.st_dev,now.st_ino)==(st.st_dev,st.st_ino):dest.unlink()
  raise
 finally:
  for p in temps:p.unlink(missing_ok=True)
 print(json.dumps({'candidate':str(out),'sha256':report['candidate_sha256'],'triangles':report['triangles']}),flush=True)
if __name__=='__main__':main()
