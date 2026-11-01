import argparse,json,hashlib
from pathlib import Path
import numpy as np
from geometry_checks import *
import coplanar_predicate as cp
p=argparse.ArgumentParser()
for k in ['geometry','plan','report']:p.add_argument('--'+k,required=True)
p.add_argument('--neighbor-report',required=True)
a=p.parse_args();assert not Path(a.report).exists();g=json.loads(Path(a.geometry).read_text());plan=json.loads(Path(a.plan).read_text());name=plan['object'];d=g['objects'][name];v=np.array(d['vertices']);ts=np.array(d['triangles']);t=v[ts];issues=[]
top,edges=topology(v,ts);cross=self_intersections(v,ts)
if top['bad_oriented_edges']or len(top['components'])!=1 or top['minimum_triangle_area']<=0 or top['signed_volume']<=0:issues.append('invalid saved solid')
if cross['strict_transverse_crossings']or cross['positive_area_coplanar_overlaps']:issues.append('new self intersection')
ulp=float(np.spacing(np.float32(np.abs(v).max())));bounds=np.array(plan['bounds']);over=np.maximum(bounds[0]-v,0)+np.maximum(v-bounds[1],0)
if over.max()>ulp:issues.append('envelope outside one saved-coordinate ULP')
assert len(ts)<=plan['triangle_budget'];assert d['materials']==[plan['material']]and set(d['face_materials'])=={0}
operands=g['authored_operands_native_loop_triangles'];ops={x['label']:np.array(x['vertices'])[x['triangles']]for x in operands}
hostnames=['V012 | hall south stone lining','V012 | hall north stone lining','V012 | entrance hall ceiling lining'];hosts={n:np.array(g['objects'][n]['vertices'])[g['objects'][n]['triangles']]for n in hostnames}
for n in hostnames:
 h=g['objects'][n];z,_=topology(h['vertices'],h['triangles']);assert not z['bad_oriented_edges']and z['signed_volume']>0
witnesses=[]
def witness(label,pt,op,host=None):
 members={'saved_union':inside(pt,t),'actual_operand':inside(pt,ops[op])}
 if host:members['actual_host']=inside(pt,hosts[host])
 ok=all(x['state']=='inside'and x['surface_margin']>.0001 for x in members.values());witnesses.append({'label':label,'point':pt,'operand':op,'host':host,'members':members,'minimum_radius':min(x['surface_margin']for x in members.values()),'pass':ok})
 if not ok:issues.append('witness failure '+label)
for station in plan['stations']:
 op='arch '+str(station);witness(op+' crown',[station,38,32.81],op,hostnames[2]);witness(op+' south heel',[station,36.58,32.18],op,hostnames[0]);witness(op+' north heel',[station,39.42,32.18],op,hostnames[1])
for label,y,host in [('south band',36.58,hostnames[0]),('north band',39.42,hostnames[1])]:witness(label+' seat',[.4,y,32.10],label,host)
for op in operands:
 if not op['label'].startswith('arch'):continue
 station=float(op['label'].split()[1]);grooves=[x for x in op['sections']if x['groove_weight']>.99]
 assert len(grooves)==6,('groove count',len(grooves))
 for i,s in enumerate(grooves):witness(op['label']+' backed joint '+str(i),[station,s['y'],(s['intrados']+s['extrados'])/2],op['label'])
# Direct exact saved geometry candidates against all render-visible nearby source objects.
neighbor=json.loads(Path(a.neighbor_report).read_text());assert neighbor['pass']and neighbor['geometry_sha256']==hashlib.sha256(Path(a.geometry).read_bytes()).hexdigest();resolved={x['object']for x in neighbor['actual_triangle_box_separation']};contacts={};lo=v.min(0);hi=v.max(0)
for n,o in g['objects'].items():
 if n==name:continue
 ot=np.array(o['vertices'])[o['triangles']];ol=ot.min(1);oh=ot.max(1);ids=np.where(np.all(oh>=lo-1e-7,1)&np.all(ol<=hi+1e-7,1))[0];hits=[];cop=[]
 for i,tri in enumerate(t):
  js=ids[np.all(oh[ids]>=tri.min(0)-1e-7,1)&np.all(ol[ids]<=tri.max(0)+1e-7,1)]
  for j in js:
   points=pair_crossings(tri,ot[j])
   if points:hits.append({'new_triangle':i,'source_triangle':int(j),'points':points})
   c=cp.contact(tri.tolist(),ot[j].tolist(),1e-7)
   if c:cop.append({'new_triangle':i,'source_triangle':int(j),**c})
 contacts[n]={'triangle_box_candidates':len(ids),'transverse_pairs':hits,'coplanar_pairs':cop}
 if n not in hostnames and len(ids) and n not in resolved:issues.append('unexpected source neighbor requires classification: '+n)
 if cop:issues.append('coplanar source overlap requires burial/exposure classification: '+n)
r={'pass':not issues,'issues':issues,'input_sha256':g['input_sha256'],'geometry_sha256':hashlib.sha256(Path(a.geometry).read_bytes()).hexdigest(),'neighbor_classification_sha256':hashlib.sha256(Path(a.neighbor_report).read_bytes()).hexdigest(),'topology':top,'self_intersections':cross,'witnesses':witnesses,'contacts':contacts,'all_render_visible_broadphase':g['broadphase'],'actual_bounds':[v.min(0).tolist(),v.max(0).tolist()],'maximum_envelope_rounding_residual':float(over.max()),'numerics':{'float32_max_coordinate_ulp':ulp,'coplanar_plane_epsilon':1e-7,'inside_uncertain_margin':1e-5,'required_witness_radius':.0001,'units':'Scene coordinate units, not calibrated physical metres/millimetres'},'scope':'One connected new-only union with separately witnessed3crowns/6heels/2bands and18backed joints. Positive contact is bounded geometric support, not structural capacity; original hosts remain separate unchanged meshes.'};Path(a.report).write_text(json.dumps(r,indent=2));print('HALL GEOMETRY',r['pass'],issues);assert r['pass'],issues
