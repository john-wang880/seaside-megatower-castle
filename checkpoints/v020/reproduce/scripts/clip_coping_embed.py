"""Subtract only actual host cross-section from new coping. No source edits/render."""
import bpy,bmesh,json,sys,hashlib,math,argparse
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));from geometry_support import evaluated_components,coplanar_y_contact,intersection,enrich
from deep_snapshot import mesh_snapshot,tree_snapshot,digest
from planar_boolean import boolean,area
p=argparse.ArgumentParser();[p.add_argument('--'+n,required=True)for n in ['input','input-sha256','union-report','output','report']];args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);assert not Path(args.output).is_symlink() and not Path(args.report).is_symlink();src=Path(args.input).resolve();out=Path(args.output).resolve();report=Path(args.report).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(src);assert len(args.input_sha256)==64 and before==args.input_sha256 and not out.exists() and not out.is_symlink() and not report.exists() and not report.is_symlink() and len({src,out,report})==3;parent=json.load(open(args.union_report));assert parent['candidate_sha256']==before and parent['source_canonical_sha256']=='e71778349c4c65eafbda3eb0a3d0753cd11e1b368a3456c4de1db2f4c0f8647a'
bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),use_scripts=False);names=['V020 candidate | '+s+' short approach coping'for s in ['south','north']];others={m.name:mesh_snapshot(m)for m in bpy.data.meshes if m not in[bpy.data.objects[n].data for n in names]};mats={m.name:digest(tree_snapshot(m.node_tree))for m in bpy.data.materials};rows=[]
def profile(s):
 y=s['bounds'][0][1];f=max((f for f in s['faces']if all(abs(s['vertices'][i][1]-y)<1e-8 for i in f)),key=len);return [tuple(s['vertices'][i][::2])for i in f]
for side,name in zip(['south','north'],names):
 o=bpy.data.objects[name];hostobj=bpy.data.objects['V009 | '+side+' approach parapet'];dg=bpy.context.evaluated_depsgraph_get();host=evaluated_components(hostobj,dg)[0];oldparts=evaluated_components(o,dg);hostpoly=profile(host);verts=[];faces=[];plans=[]
 for old in oldparts:
  poly=profile(old);newloops,edges=boolean(poly,hostpoly,'DIFFERENCE');interloops,iedges=boolean(poly,hostpoly,'INTERSECT');newarea=sum(area(x)for x in newloops);interarea=sum(area(x)for x in interloops);assert abs(newarea+interarea-area(poly))<1e-10
  y0,y1=old['bounds'][0][1],old['bounds'][1][1]
  for number,new in enumerate(sorted(newloops,key=area,reverse=True)):
   n=len(new);vs=[(x,y,z)for y in [y0,y1]for x,z in new];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
   bm=bmesh.new();bv=[bm.verts.new(v)for v in vs]
   for f in fs:bm.faces.new([bv[i]for i in f])
   bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.verts.index_update();fs=[[v.index for v in f.verts]for f in bm.faces];assert all(e.is_manifold for e in bm.edges);bm.free()
   cycle_edges=list(zip(new,new[1:]+new[:1]));seats=[e for e in edges if e['source']=='B' and any(math.dist(e['ends'][0],a)<1e-8 and math.dist(e['ends'][1],b)<1e-8 for a,b in cycle_edges)];seatarea=sum(math.dist(*e['ends'])*(y1-y0)for e in seats);assert seatarea>1e-10
   off=len(verts);verts.extend(vs);faces.extend([[off+i for i in f]for f in fs]);plans.append({'old':old,'new_seed':off,'new_vertex_count':len(vs),'ideal_vertices':vs,'old_area':area(poly),'whole_parent_difference_area':newarea,'new_piece_area':area(new),'intersection_area':interarea,'parent_area_identity_error':newarea+interarea-area(poly),'role':'upper_coping' if number==0 else 'retained_external_terminal_wedge','parent_old_seed':old['seed'],'host_seat_area_from_actual_source_edge_m2':seatarea,'host_seat_source_intervals':seats,'exterior_boundary_source_intervals':edges,'intersection_boundary_source_intervals':iedges})
 oldmesh=o.data;newmesh=bpy.data.meshes.new(oldmesh.name+' clean');newmesh.from_pydata(verts,[],faces);newmesh.materials.append(oldmesh.materials[0]);newmesh.update();o.data=newmesh;oldname=oldmesh.name;bpy.data.meshes.remove(oldmesh);newmesh.name=oldname;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();newparts=evaluated_components(o,dg)
 for p,new in zip(plans,newparts):
  old=p.pop('old');ideal=p.pop('ideal_vertices');b=enrich(new);assert b['closed_oriented'] and b['signed_volume']>0;maxerror=max(math.dist(v,w)for v,w in zip(ideal,new['vertices']));perimeter=sum(math.dist(a,b)for a,b in zip(profile(new),profile(new)[1:]+profile(new)[:1]));bound=perimeter*maxerror*2+1e-8;sides=[coplanar_y_contact(new,host,y)for y in [new['bounds'][0][1],new['bounds'][1][1]]];assert all(s['sum_actual_triangle_intersection_areas']<=bound for s in sides),(sides,bound)
  combined=lambda cap:[[min(cap['bounds'][0][k],host['bounds'][0][k])for k in range(3)],[max(cap['bounds'][1][k],host['bounds'][1][k])for k in range(3)]]
  if p['role']=='upper_coping':assert combined(new)==combined(old),'Combined host/cap bounds changed'
  rows.append({**p,'object':name,'old_seed':old['seed'],'new_host_intersection':intersection(new,host),'float32_max_vertex_rounding_m':maxerror,'actual_side_overlap_after':sides,'side_overlap_roundoff_bound_m2':bound,'closed_oriented_positive':True,'occupied_union_identity_area_error':p['parent_area_identity_error'],'bounds':new['bounds'],'volume':b['signed_volume'],'semantic':'Only newcap minus actualhost crosssection; terminal exposed wedge retained, widths/top/exterior source edges preserved; new contact is actual shared top/end surface.'})
assert all(mesh_snapshot(bpy.data.meshes[n])==v for n,v in others.items());assert {m.name:digest(tree_snapshot(m.node_tree))for m in bpy.data.materials}==mats
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out.resolve()),copy=True);assert sha(src)==before
report.write_text(json.dumps({'status':'TECHNICAL COPING CLEANUP; INDEPENDENT QA PENDING','input_sha256':before,'input_unchanged':True,'candidate_sha256':sha(out),'candidate_bytes':out.stat().st_size,'component_count':23,'main_components':21,'retained_terminal_wedges':2,'rows':rows,'other_meshes_and_material_graphs_exact':True,'scope':'Actualhost planar subtraction only. No source/width/top/style changes; float32 boundary residual quantified; no renders'},indent=2));print('COPING_CLEANUP_PASS',sha(out))
