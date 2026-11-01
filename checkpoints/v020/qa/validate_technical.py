"""Actual threshold solids/contact/opening and known cornice interference; no saves."""
import argparse,bpy,hashlib,json,math,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry_support as gs
p=argparse.ArgumentParser()
for k in ['candidate','specification','host-plan','report']:p.add_argument('--'+k,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(a.candidate);cfg=json.loads(Path(a.specification).read_text());plan=json.loads(Path(a.host_plan).read_text());bpy.ops.wm.open_mainfile(filepath=str(Path(a.candidate).resolve()),use_scripts=False);deps=bpy.context.evaluated_depsgraph_get();counts=(len(bpy.data.objects),len(bpy.data.meshes));cache={}
def components(name):
 if name not in cache:cache[name]=gs.evaluated_components(bpy.data.objects[name],deps)
 return cache[name]
def bykey(key):
 name,seed=key.rsplit('::',1);return next(s for s in components(name) if s['seed']==int(seed))
for h in plan['hosts']:
 s=bykey(h['object']+'::'+str(h['component']['seed']));assert {str(i):list(v) for i,v in zip(s['ids'],s['vertices'])}==h['component']['vertices'];assert [list(s['ids'][i] for i in f) for f in s['faces']]==[f['ids'] for f in h['component']['faces']];gs.enrich(s);assert s['closed_oriented'] and s['signed_volume']>0
wall=bykey('V007 | western stonework with actual bridgehead passage::17620');cornice=bykey('V012 | retained west rib facade with buried-route clearance::11768');gs.enrich(cornice)
# Opening knots selected from ACTUAL front-wall vertices, not freshly sampled ellipse.
front=wall['bounds'][0][0];profile=sorted({(v[1],v[2]) for v in wall['vertices'] if abs(v[0]-front)<1e-6 and v[2]>=29.05-2e-5 and abs(((v[1]-38)/2.2)**2+((v[2]-29.05)/2)**2-1)<2e-5});assert len(profile)==25
polygon=[(profile[0][0],26.9),(profile[-1][0],26.9)]+profile[::-1]
def prism(key,xs,poly):
 n=len(poly);vs=[(x,y,z) for x in xs for y,z in poly];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];s=gs.shape(key,vs,fs)
 if s['signed_volume']<0:s=gs.shape(key,vs,[f[::-1] for f in fs])
 assert s['closed_oriented'] and s['signed_volume']>0;return s
aperture=prism('QA unchanged arch aperture extended to new face',[-71.48,-63.8],polygon)
original_aperture=prism('QA original doorway domain',[front,-63.8],polygon)
SEATS=set(cfg['secondary_seat_seeds'])
route=prism('QA conservative central western approach clearance',[-76,-63.8],[(36.6,26),(39.4,26),(39.4,29.5),(36.6,29.5)])
rows=[];failures=[];new=[]
for name in cfg['added_objects']:
 pieces=components(name);assert len(pieces)==cfg['counts'][name];host=bykey(cfg['host_keys'][name])
 for s in pieces:
  new.append(s);gs.enrich(s);assert s['closed_oriented'] and s['signed_volume']>1e-10
  results={'host':gs.intersection(s,host),'opening':gs.intersection(s,original_aperture if 'coping' in name else aperture),'route':gs.intersection(s,route),'existing_cornice':gs.intersection(s,cornice)}
  if 'coping' in name:
   shared=gs.coplanar_triangle_area(s,host);is_wedge=s['seed'] in cfg['retained_terminal_wedge_seeds'];top=[p for p in shared['positive_area_pairs'] if is_wedge or abs(p['normal'][2])>.9];results['host_shared_top']={'area_m2':sum(p['area_m2'] for p in top),'max_plane_deviation_m':max((p['max_plane_deviation_m'] for p in top),default=0),'plane_tolerance_m':6e-6};assert results['host_shared_top']['area_m2']>(1e-5 if is_wedge else .1), ('No actual shared-top area',s['key'])
   side_tests=[gs.coplanar_y_contact(s,host,y) for y in [host['bounds'][0][1],host['bounds'][1][1]]];results['host_exposed_side_overlap']=side_tests
   # The accepted technical clip must eliminate the formerly25mm tall duplicate side patches.
   import numpy as np
   side_roundoff_bound=2*max(float(abs(np.spacing(np.float32(v[2])))) for v in s['vertices'])*(s['bounds'][1][0]-s['bounds'][0][0]);results['host_side_roundoff_area_bound_m2']=side_roundoff_bound
   for side in side_tests:
    if side['sum_actual_triangle_intersection_areas']>side_roundoff_bound:failures.append({'piece':s['key'],'reason':'Remaining coplanar host side patch','side':side})
   if results['host']['volume'] is None or results['host']['volume']>side_roundoff_bound*(s['bounds'][1][1]-s['bounds'][0][1]):failures.append({'piece':s['key'],'reason':'Unexpected residual coping embed','result':results['host']})
  elif not results['host'].get('closed_result') or results['host']['volume']<=1e-10:failures.append({'piece':s['key'],'reason':'No proven positive host overlap'})
  for label in ['opening','route','existing_cornice']:
   r=results[label]
   if label=='existing_cornice' and name=='V020 candidate | west portal radial stones' and s['seed'] in SEATS:
    assert r.get('closed_result') and r['volume']>1e-10, ('Missing exact intended secondary seat',s['key']);continue
   if r['volume'] is None or r['volume']>1e-10:failures.append({'piece':s['key'],'reason':label,'result':r})
  rows.append({'piece':s['key'],'signed_volume':s['signed_volume'],'bounds':s['bounds'],'tests':results})
# Existing geometric support chain: parapet side → stair body → threshold → wall body.
stairs=bykey('V009 | nine broad western approach treads::0');threshold=bykey('V007 | continuous stone passage threshold::0');roots={}
for side,y in [('south',stairs['bounds'][0][1]),('north',stairs['bounds'][1][1])]:
 s=bykey('V009 | '+side+' approach parapet::0');roots[side+'_parapet_to_stair']=gs.coplanar_y_contact(s,stairs,y);assert roots[side+'_parapet_to_stair']['maximum_actual_triangle_intersection_area']>1e-8
roots['cornice_to_primary_wall']=gs.intersection(cornice,wall);assert roots['cornice_to_primary_wall'].get('closed_result') and roots['cornice_to_primary_wall']['volume']>1e-10
roots['stairs_to_threshold']=gs.intersection(stairs,threshold);roots['threshold_to_wall']=gs.intersection(threshold,wall)
for key in ['stairs_to_threshold','threshold_to_wall']:assert roots[key]['closed_result'] and roots[key]['volume']>1e-10
# All render-enabled nearby meshes: evaluated bound_box BEFORE broadphase cull.
from mathutils import Vector
all_bounds=[[min(s['bounds'][0][k] for s in new) for k in range(3)],[max(s['bounds'][1][k] for s in new) for k in range(3)]]
neighbor_rows=[];neighbors=[];visible_objects=[]
def render_objects(coll,enabled=True):
 enabled=enabled and not coll.hide_render
 if enabled:
  for obj in coll.objects:
   if not obj.hide_render and obj.type=='MESH':visible_objects.append(obj)
 for child in coll.children:render_objects(child,enabled)
render_objects(bpy.context.scene.collection)
for obj in {o.name:o for o in visible_objects}.values():
 if obj.name in cfg['added_objects']:continue
 eo=obj.evaluated_get(deps);bb=[eo.matrix_world@Vector(v) for v in eo.bound_box];bounds=[[min(v[k] for v in bb) for k in range(3)],[max(v[k] for v in bb) for k in range(3)]]
 if not gs.overlap(bounds,all_bounds,-1e-7):continue
 for other in components(obj.name):
  if gs.overlap(other['bounds'],all_bounds,-1e-7):neighbors.append(other)
for s in new:
 for other in neighbors:
  if not gs.overlap(s['bounds'],other['bounds'],-1e-7):continue
  intended=other['key']==cfg['host_keys'][s['object']] or (other['key']==cornice['key'] and s['object']=='V020 candidate | west portal radial stones' and s['seed'] in SEATS)
  if intended:continue # Positive closed volume already independently required above.
  gs.enrich(other)
  result=gs.intersection(s,other) if other['closed_oriented'] else {'volume':None,'reason':'surface-only operand'}
  if result['volume'] is None or result['volume']<=1e-10:result['surface_test']=gs.triangle_surface_contact(s,other)
  collision=(result['volume'] is not None and result['volume']>1e-10) or result.get('surface_test',{}).get('state') not in (None,'no_surface_contact')
  neighbor_rows.append({'piece':s['key'],'neighbor':other['key'],'result':result,'unexpected_contact':collision})
  if collision:failures.append({'piece':s['key'],'reason':'unapproved_neighbor_contact','neighbor':other['key'],'result':result})
# New-new contacts are listed independently, not blanket-excluded.
new_pair_contacts=[]
for i,s in enumerate(new):
 for t in new[i+1:]:
  if not gs.overlap(s['bounds'],t['bounds'],-1e-7):continue
  result=gs.intersection(s,t)
  if result['volume']>1e-10:new_pair_contacts.append({'pieces':[s['key'],t['key']],'result':result})

if new_pair_contacts:failures.append({'reason':'new_pair_contacts_require_explicit_review','pairs':new_pair_contacts})
# Bounded negative controls use synthetic copies of measured solids, not saved models.
first=new[0];detached=dict(first,key='QA displaced first stone',vertices=[(v[0]-10,v[1],v[2]) for v in first['vertices']],bounds=[[v[0]-10,v[1],v[2]] for v in first['bounds']]);assert gs.intersection(detached,wall)['volume']==0
bad=gs.shape('QA reversed face',first['vertices'],[first['faces'][0][::-1]]+first['faces'][1:],first['triangles']);assert not bad['closed_oriented']
assert counts==(len(bpy.data.objects),len(bpy.data.meshes)) and sha(a.candidate)==before
r={'candidate_sha256':before,'host_plan_sha256':sha(a.host_plan),'focused_geometry_pass':not failures,'failures':failures,'new_piece_count':len(new),'pieces':rows,'actual_opening_knots_yz':profile,'opening_domains':{'arch_imposts':[-71.48,-63.8],'copings_original_doorway':[front,-63.8],'central_approach_y':[36.6,39.4]},'nearby_full_components':len(neighbors),'neighbor_tests':neighbor_rows,'new_pair_contacts':new_pair_contacts,'root_contact_chain':roots,'negative_controls':{'displaced_stone_no_host':True,'reversed_face_rejected':True},'source_file_unchanged':True,'scope':'Actual evaluated closed-piece host overlap and unchanged opening/central west strip, with explicitly measured known cornice interference. Numerical volume threshold1e-10m3. All render-enabled nearby evaluated components checked; open source sheets tested for actual triangle surface contact, not fictional solid volume. Exact five cornice secondary seats explicitly allowed, with cornice root volume verified. New-new contacts reported for explicit review. No global collision/engineering acceptance.'};Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps({'pass':not failures,'failures':failures,'pieces':len(new)},indent=2))
