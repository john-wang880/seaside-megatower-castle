import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path('work/conifer_specialist');fol=bpy.data.objects['CONCEPT | radial articulated needle sprays'].data;wood=bpy.data.objects['CONCEPT | tapering connected boughs and shoots'].data;old=bpy.data.objects['SOURCE | exact target trunk and bough context'].data
W=[v.co.copy() for v in wood.vertices];N=[fol.vertices[i].co.copy() for i in range(0,len(fol.vertices),5)]
def mean(vs):return sum(vs,Vector())/len(vs)
def centers(offset,count):return [mean(W[offset+j*5:offset+(j+1)*5]) for j in range(count)]
def dist(p,points):
 best=1e9
 for a,b in zip(points,points[1:]):
  u=max(0,min(1,(p-a).dot(b-a)/(b-a).length_squared));best=min(best,(p-a.lerp(b,u)).length)
 return best
oldaxis=[mean([v.co for v in old.vertices[:5]]),mean([v.co for v in old.vertices[5:10]])]
wi=ni=fi=0;nd=[];sd=[];pd=[];upper=[];mapping=[];shootroots=[];primaryroots=[]
def shoot(scale,support):
 global wi,ni,fi
 pts=centers(wi,3);count=max(22,int(32*scale))+1
 for p in N[ni:ni+count]:nd.append(dist(p,pts))
 sd.append(dist(pts[0],support));shootroots.append((pts[0],support))
 mapping.append({'role':'needle_shoot','vertex_start':wi,'vertex_count':15,'face_start':fi,'face_count':12,'needle_blade_start':ni,'needle_blade_count':count,'support_polyline':[list(p) for p in support]});wi+=15;ni+=count;fi+=12
for tier in range(28):
 t=tier/28
 for k in range(6 if tier<12 else 5):
  primary=centers(wi,6);primaryroots.append(primary[0]);mapping.append({'role':'primary_bough','vertex_start':wi,'vertex_count':30,'face_start':fi,'face_count':27});wi+=30;fi+=27
  for j in range(9 if tier<13 else 7):
   for sign in [-1,1]:shoot(.94*(1-t*.22),primary)
   if j%3==1:shoot(.85*(1-t*.20),primary)
  shoot(.85*(1-t*.25),primary)
leader=centers(wi,3);mapping.append({'role':'leader_extension','vertex_start':wi,'vertex_count':15,'face_start':fi,'face_count':12});wi+=15;fi+=12
axis=[oldaxis[0],oldaxis[1],leader[-1]]
pd=[dist(p,axis) for p in primaryroots]
for j in range(57):shoot(.85 if 27+j*.118<32.9 else .63,axis)
for k in range(19):shoot(.48,axis)
shoot(.28,axis)
assert wi==len(W),(wi,len(W));assert ni==len(N),(ni,len(N))
# Distances are from independent actual mesh ring means, not generator intentions.
report={'needle_bases_tested':len(nd),'max_needle_base_centerline_distance_m':max(nd),'shoot_roots_tested':len(sd),'max_shoot_root_support_axis_distance_m':max(sd),'primary_roots_tested':len(pd),'max_primary_root_source_trunk_axis_distance_m':max(pd),'source_trunk_axis_endpoints':[list(p) for p in oldaxis],'leader_extension_axis':[list(p) for p in leader],'leader_bottom_below_original_top_m':oldaxis[1].z-leader[0].z,'all_needle_bases_within_1e_5m_of_actual_shoot_centerline':max(nd)<1e-5,'root_centerline_offsets_disclosed_not_exact':True,'scope':'Independent saved-mesh geometric centerline attachment test; does not certify manifold source wood or every triangle intersection. Authored tubes are capped; source trunk retained unchanged.'}
(P/'component_contact_mapping.json').write_text(json.dumps({'wood_components':mapping,'needle_vertex_layout':'Each blade has5vertices, base isfirst; fourtriangles perblade.','source_trunk_vertices':[26760,26770],'leader_supports_above_z':33.30},indent=2))
(P/'attachment_verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
