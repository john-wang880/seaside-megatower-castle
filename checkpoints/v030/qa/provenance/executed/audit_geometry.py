"""Independent actual saved convex-prism, exact planar bearing and support graph proof."""
import json,sys,hashlib,struct,itertools,collections,argparse
from pathlib import Path
from fractions import Fraction as F
import numpy as np
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'checkpoints/v028/qa'))
import exact_axis_boundary as e
from continuous_box_cover import oriented_closed,box_inside,solid_winding
from body_support import analyze
D=Path(__file__).parent
SOURCE='4f838529d32cbf6a0314cc0a23b3dd1703b73d80c5db146fb4d323697b882df5'
def need(v,msg):
 if not v:raise RuntimeError(msg)
def f32(v):return struct.unpack('f',struct.pack('f',v))[0]
def signed_normal(poly):return e.cross(tuple(poly[1][k]-poly[0][k]for k in range(3)),tuple(poly[2][k]-poly[0][k]for k in range(3)))
def footprint(lo,hi,c=.008):
 x,y=lo[:2];X,Y=hi[:2];return [(F(f32(a)),F(f32(b)))for a,b in [(x+c,y),(X-c,y),(X,y+c),(X,Y-c),(X-c,Y),(x+c,Y),(x,Y-c),(x,y+c)]]
def coverage(poly,refs):
 pieces=[e.clip_convex(poly,r)for r in refs];pieces=[p for p in pieces if e.area(p)>0];area=e.area(poly);need(sum(map(e.area,pieces),F(0))==area,'Bearing domain uncovered')
 for a,b in itertools.combinations(pieces,2):need(e.area(e.clip_convex(a,b))==0,'Bearing domain multiply covered')
 return area

def audit(data,plan):
 old={p['name']:p for p in plan['primitive_parts']};parts=[];ids=set();zero=[];parent_count=0
 for mesh in data['meshes']:
  verts=[e.fraction3(v)for v in mesh['vertices']];usedv=[];usedf=[]
  for c in mesh['components']:
   need(c['id']not in ids,'Duplicate component identity');ids.add(c['id']);v0,v1=c['vertex_range'];f0,f1=c['face_range'];usedv+=list(range(v0,v1));usedf+=list(range(f0,f1));v=verts[v0:v1];faces=[[i-v0 for i in f]for f in mesh['faces'][f0:f1]];need(v1-v0==16 and f1-f0==10 and oriented_closed(faces),'Closed 16vertex/10face prism');p=old[c['source_primitive']];lo=list(p['min']);hi=list(p['max']);part=c['part'];isbin=' supply bin 'in p['name']
   if isbin:
    cut=hi[2]-.04
    if part=='body':lo[:2]=[x+.006 for x in lo[:2]];hi[:2]=[x-.006 for x in hi[:2]];hi[2]=cut
    elif part=='lid':lo[2]=cut
    else:raise RuntimeError('Bin body/lid mapping')
   else:need(part=='whole','Unexpected nonbin split')
   poly=footprint(lo,hi);low=F(f32(lo[2]));high=F(f32(hi[2]));expected=[(x,y,z)for z in [low,high]for x,y in poly];need(sorted(v)==sorted(expected),'Actual profile not prescribed quantized chamfer');need(high>low and e.area(poly)>0,'Positive prism volume')
   # Every actual saved polygon is planar/outward supporting convex boundary.
   for j,face in enumerate(faces):
    pts=[v[i]for i in face];normal=signed_normal(pts);need(any(normal),'Zero parent normal');need(all(sum(normal[k]*(x[k]-pts[0][k])for k in range(3))==0 for x in pts),'Nonplanar parent');need(all(sum(normal[k]*(x[k]-pts[0][k])for k in range(3))<=0 for x in v),'Nonconvex or reversed parent');axis=max(range(3),key=lambda k:abs(normal[k]));other=[k for k in range(3)if k!=axis];parent=[tuple(x[k]for k in other)for x in pts];need(e.area(parent)>0,'Zero parent');actual=[]
    for ti,fi in enumerate(mesh['triangle_polygons']):
     if fi!=f0+j:continue
     tv=[verts[i]for i in mesh['triangles'][ti]];tp=[tuple(x[k]for k in other)for x in tv];ar=e.area(tp)
     if ar==0:need(not any(signed_normal(tv)),'Projected zero nonzero triangle');zero.append({'mesh':mesh['name'],'parent':fi,'triangle':ti,'coordinates':[[float(z)for z in x]for x in tv]});continue
     need(sum(signed_normal(tv)[k]*normal[k]for k in range(3))>0,'Native triangle orientation');need(e.area(e.clip_convex(tp,parent))==ar,'Native triangle outside parent');actual.append(tp)
    coverage(parent,actual);parent_count+=1
   uid=p['name']+'/'+part;kind='bin '+part if isbin else next(k for k in ['post','shelf','rail']if ' '+k+' 'in p['name']);parts.append({'id':uid,'primitive':p['name'],'kind':kind,'part':part,'poly':poly,'lo':low,'hi':high,'vertices':[[float(x)for x in row]for row in v],'local_faces':faces,'local_triangles':[[i-v0 for i in t]for ti,t in enumerate(mesh['triangles'])if f0<=mesh['triangle_polygons'][ti]<f1],'object':uid,'seed':0,'volume':e.area(poly)*(high-low)})
  need(sorted(usedv)==list(range(len(verts)))and sorted(usedf)==list(range(len(mesh['faces']))),'Component partition incomplete/overlap')
 need(len(parts)==78 and len(ids)==78,'78 actual components');need(sum(len(p['local_triangles'])for p in parts)==2184,'2184 actual triangles');need(collections.Counter(p['kind']for p in parts)=={'post':16,'shelf':18,'rail':36,'bin body':4,'bin lid':4},'Role inventory')
 g=json.loads((R/'work/v029_interior_qa/saved_geometry.json').read_text());need(g['candidate_sha256']==SOURCE,'Saved floor source');floor=[]
 for m in g['meshes']:
  for t in m['triangles']:
   v=[e.fraction3(m['vertices'][i])for i in t]
   if all(x[2]==29 for x in v)and signed_normal(v)[2]>0:floor.append([(x[0],x[1])for x in v])
 graph=collections.defaultdict(set);contacts=[];embeds=[];feet=[];bearings=[]
 for p in parts:
  if p['kind']=='post':
   need(p['lo']==29,'Foot plane');area=coverage(p['poly'],floor);graph[p['id']].add('floor');graph['floor'].add(p['id']);feet.append({'part':p['id'],'full_actual_foot_area':float(area),'uncovered_area':0,'multiple_area':0})
 for a,b in itertools.combinations(parts,2):
  poly=e.clip_convex(a['poly'],b['poly']);area=e.area(poly);z=min(a['hi'],b['hi'])-max(a['lo'],b['lo'])
  if area>0 and z>0:
   need({a['kind'],b['kind']}=={'post','rail'},'Unintended actual positive volume overlap');graph[a['id']].add(b['id']);graph[b['id']].add(a['id']);embeds.append({'a':a['id'],'b':b['id'],'volume':float(area*z)})
  if area>0 and (a['hi']==b['lo']or b['hi']==a['lo']):
   graph[a['id']].add(b['id']);graph[b['id']].add(a['id']);contacts.append({'a':a['id'],'b':b['id'],'area':float(area),'axis':2})
 for p in parts:
  if p['kind']=='rail':need(sum(n.endswith('/whole')and ' post 'in n for n in graph[p['id']])==2,'Actual rail not positively embedded in two posts')
  elif p['kind']=='shelf':
   rows=[c for c in contacts if (c['a']==p['id']and ' rail 'in c['b'])or(c['b']==p['id']and ' rail 'in c['a'])];need(len(rows)==2 and min(c['area']for c in rows)>0,'Two actual shelf rail bearings required');bearings.append({'part':p['id'],'two_rail_areas':[x['area']for x in rows]})
  elif p['kind']=='bin body':
   hosts=[s for s in parts if s['kind']=='shelf'and s['hi']==p['lo']and e.area(e.clip_convex(p['poly'],s['poly']))==e.area(p['poly'])];need(len(hosts)==1,'Full actual bin bottom support');bearings.append({'part':p['id'],'full_bottom_host':hosts[0]['id'],'area':float(coverage(p['poly'],[hosts[0]['poly']]))})
  elif p['kind']=='bin lid':
   body=next(b for b in parts if b['primitive']==p['primitive']and b['kind']=='bin body');need(body['hi']==p['lo'],'Lid gap');area=coverage(body['poly'],[p['poly']]);bearings.append({'part':p['id'],'full_body_top_contact':float(area),'lid_total_bottom_area':float(e.area(p['poly']))})
 reached={'floor'};todo=['floor']
 while todo:
  for v in graph[todo.pop()]-reached:reached.add(v);todo.append(v)
 need(len(reached)==79,'Unrooted actual component')
 return {'pass':True,'closed_convex_components':78,'native_parent_coverage':parent_count,'exact_zero_native_triangles':zero,'triangles':2184,'actual_feet':feet,'post_rail_positive_intersections':embeds,'bearing_relationships':bearings,'rooted_components':78,'summed_component_volume_not_union':float(sum((p['volume']for p in parts),F(0))),'limits':'Individual actual convex prisms and exact horizontal bearing domains; intentional post/rail embeddings retained. Cross-component exposed coplanars, source clearance and fixed rays are separate checks.'},parts
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--geometry',required=True);ap.add_argument('--report',required=True);a=ap.parse_args();data=json.loads(Path(a.geometry).read_text());plan=json.loads((R/'work/v030_fittings/PLAN.json').read_text());result,_=audit(data,plan);result['candidate_sha256']=data['candidate_sha256'];result['geometry_sha256']=hashlib.sha256(Path(a.geometry).read_bytes()).hexdigest();Path(a.report).write_text(json.dumps(result,indent=2)+'\n');print('ACTUAL FITTINGS BEARING PASS')
