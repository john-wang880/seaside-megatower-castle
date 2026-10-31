"""Bounded north L-passage prototype; preserve source scene and tower silhouette."""
import argparse,bpy,bmesh,hashlib,json,math,sys
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(bpy.data.filepath);out=Path(a.output).resolve();assert out!=source.resolve();assert not any(o.name.startswith('V012 |') for o in bpy.data.objects)
col=bpy.data.collections.new('REFINEMENT | v012 north covered terrace connection');bpy.context.scene.collection.children.link(col)
F=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def plain_mesh(name,verts,faces,materials):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 for m in materials:me.materials.append(m)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);col.objects.link(ob);return ob

def components(me):
 adj=[[] for _ in me.vertices]
 for e in me.edges:
  a,b=e.vertices;adj[a].append(b);adj[b].append(a)
 done=set()
 for seed in range(len(adj)):
  if seed in done:continue
  ids=set();q=[seed]
  while q:
   i=q.pop()
   if i in ids:continue
   ids.add(i);q.extend(j for j in adj[i] if j not in ids)
  done.update(ids);yield ids

mat=bpy.data.materials['Citadel • weathered limestone'];wood=bpy.data.materials['Pine bark'];iron=bpy.data.materials['Citadel • deep slate ashlar']
def box(name,x0,x1,y0,y1,z0,z1,material=mat):
 return plain_mesh(name,[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],F,[material])
def extrude_yz(name,profile,x0,x1,material=mat):
 n=len(profile);return plain_mesh(name,[(x,y,z) for x in(x0,x1) for y,z in profile],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],[material])
# Three individually closed cutters, applied sequentially per independent solid;
# never treat overlapping cutters/legacy mass components as one ambiguous shell.
cutters=[box('TEMP entrance hall clearance',-3.6,5.55,36.5,39.5,28.75,32.9),box('TEMP north corridor clearance',3.4,5.5,39.35,45.55,28.75,31.65)]
ceiling=[(45.45,31.7),(57.6,35.175),(58.0,35.175)]
cutters.append(extrude_yz('TEMP north stairwell clearance',ceiling+[(58.0,28.75),(45.45,28.75)],3.4,5.5))
def bounds(points):return ([min(v[k] for v in points) for k in range(3)],[max(v[k] for v in points) for k in range(3)])
cut_bounds=[bounds([c.matrix_world@v.co for v in c.data.vertices]) for c in cutters]
def overlap(a,b):return all(a[1][k]>b[0][k]+.00001 and a[0][k]<b[1][k]-.00001 for k in range(3))
def excavate(src,label):
 # Freeze original evaluated bevel before local cuts. Re-evaluating a single
 # global bevel after excavation clamps remote facade radii unintentionally.
 deps=bpy.context.evaluated_depsgraph_get();evaluated=src.evaluated_get(deps)
 me=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=deps);groups=[];details=[]
 for group in components(me):
  if len(group)<4:continue
  bb=bounds([src.matrix_world@me.vertices[i].co for i in group])
  if not any(overlap(bb,b) for b in cut_bounds):continue
  old=[p for p in me.polygons if all(i in group for i in p.vertices)]
  if not old:continue
  groups.append(group);details.append({'seed':min(group),'vertices':len(group),'faces':len(old),'bounds':bb})
 assert groups,src.name
 removed=set().union(*groups);kept=[p for p in me.polygons if not all(i in removed for i in p.vertices)]
 verts=[tuple(v.co) for v in me.vertices];faces=[tuple(p.vertices) for p in kept];mats=[p.material_index for p in kept];smooth=[p.use_smooth for p in kept];inverse=src.matrix_world.inverted()
 for group,detail in zip(groups,details):
  order=sorted(group);mapping={v:i for i,v in enumerate(order)};old=[p for p in me.polygons if all(i in group for i in p.vertices)]
  piece=plain_mesh('TEMP independent solid',[tuple(src.matrix_world@me.vertices[i].co) for i in order],[[mapping[i] for i in p.vertices] for p in old],list(me.materials))
  for p,q in zip(piece.data.polygons,old):p.material_index=q.material_index;p.use_smooth=q.use_smooth
  bm=bmesh.new();bm.from_mesh(piece.data);assert all(e.is_manifold for e in bm.edges),(src.name,min(group),'source not closed');bm.free()
  bpy.context.view_layer.objects.active=piece;piece.select_set(True)
  for cutter in cutters:
   mod=piece.modifiers.new('Bounded independent passage excavation','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name)
  bm=bmesh.new();bm.from_mesh(piece.data);assert all(e.is_manifold for e in bm.edges),(src.name,min(group),'result not closed');bm.free();detail['result_vertices']=len(piece.data.vertices);detail['result_faces']=len(piece.data.polygons)
  offset=len(verts);verts.extend(tuple(inverse@v.co) for v in piece.data.vertices);faces.extend(tuple(offset+i for i in p.vertices) for p in piece.data.polygons);mats.extend(p.material_index for p in piece.data.polygons);smooth.extend(p.use_smooth for p in piece.data.polygons)
  data=piece.data;bpy.data.objects.remove(piece,do_unlink=True);bpy.data.meshes.remove(data)
 ob=src.copy();ob.name=label;ob.data=bpy.data.meshes.new(label);ob.data.from_pydata(verts,[],faces);ob.data.update()
 for m in me.materials:ob.data.materials.append(m)
 for p,mi,sm in zip(ob.data.polygons,mats,smooth):p.material_index=mi;p.use_smooth=sm
 for mod in list(ob.modifiers):ob.modifiers.remove(mod)
 col.objects.link(ob);ob.hide_render=False;ob.hide_set(False);src.hide_render=True;src.hide_set(True)
 bpy.data.meshes.remove(me)
 return {'source':src.name,'replacement':ob.name,'untouched_faces':len(kept),'selected_components':details,'original_modifiers_baked_before_local_cuts':[m.type for m in src.modifiers],'remaining_modifiers':[m.type for m in ob.modifiers]}
excavations=[]
for name,label in [('Citadel | ashlar masonry','V012 | ashlar with bounded entrance and north stairwell'),('Citadel | limestone ledges','V012 | terrace ledges with bounded stair opening'),('V006 | west facade with one short jointed rib sample','V012 | retained west rib facade with buried-route clearance'),('V010 | foundation with clear eastern entrance vestibule','V012 | foundation with continuous L-shaped passage'),('Western citadel_West_Ashlar stone variation','V012 | legacy ashlar with buried-route clearance')]:excavations.append(excavate(bpy.data.objects[name],label))
for c in cutters:
 me=c.data;bpy.data.objects.remove(c,do_unlink=True);bpy.data.meshes.remove(me)
# New floors are supported by the remaining source foundation, not floating.
box('V012 | entrance hall limestone floor',-3.3,5.4,36.6,39.4,28.70,29.0)
box('V012 | north corridor limestone floor',3.5,5.4,39.4,45.5,28.70,29.0)
profile=[]
for i in range(20):
 z=29+(i+1)*.18125;profile.extend([(45.5+i*.6,z),(46.1+i*.6,z)])
profile.extend([(58.0,32.625),(58.0,28.70),(45.5,28.70)])
extrude_yz('V012 | twenty north stair treads',profile,3.5,5.4)
# Real lining sits 0.1m inside coincident legacy cut surfaces, avoiding dark
# coplanar self-shadow bands. Side walls continue as terrace-height guards.
box('V012 | hall south stone lining',-3.3,5.4,36.5,36.6,28.7,32.9)
box('V012 | hall north stone lining',-3.3,3.5,39.4,39.5,28.7,32.9)
box('V012 | hall east stone lining',5.4,5.5,36.6,39.4,28.7,32.9)
box('V012 | entrance hall ceiling lining',-3.3,5.4,36.6,39.4,32.8,32.9)
for label,x0,x1 in [('west',3.4,3.5),('east',5.4,5.5)]:
 box('V012 | '+label+' north corridor stone lining',x0,x1,39.4,45.5,28.7,31.65)
box('V012 | north corridor ceiling lining',3.5,5.4,39.4,45.5,31.55,31.65)
def ceiling_z(y):return 31.7+(y-45.45)*(35.175-31.7)/(57.6-45.45)
rail=[(45.5,ceiling_z(45.5)),(51.5,ceiling_z(51.5)),(51.5,33.525),(58.0,33.525),(58.0,28.7),(45.5,28.7)]
for label,x0,x1 in [('west',3.4,3.5),('east',5.4,5.5)]:extrude_yz('V012 | '+label+' lined stairwell and terrace guard',rail,x0,x1)
extrude_yz('V012 | stairwell ceiling lining',[(45.5,ceiling_z(45.5)),(51.5,ceiling_z(51.5)),(51.5,ceiling_z(51.5)-.1),(45.5,ceiling_z(45.5)-.1)],3.5,5.4)
# Baked original bevels leave the NEW landing join sharp and level; no global
# modifier or weighted-bevel rewrite can change untouched upper facades.
flat_join_edges=[]
# Replace closed leaves/straps only. Original frame stays; new outward-open leaves
# sit outside the walking width and are retained as real thickness meshes.
hidden=[]
for o in list(bpy.data.objects):
 if o.name=='V010 | deliberately closed eastern timber entry' or o.name=='V010 | double-door central seam' or o.name.startswith('V010 | entry iron strap'):
  o.hide_render=True;o.hide_set(True);hidden.append(o.name)
for side in ('south','north'):
 if side=='south':
  cross=[(35.9,29.04),(38,29.04),(38,32.5)]
  for i in range(1,13):t=math.pi/2+math.pi/2*i/12;cross.append((38+2.1*math.cos(t),31+1.5*math.sin(t)))
 else:
  cross=[(38,29.04),(40.1,29.04),(40.1,31)]
  for i in range(1,13):t=math.pi/2*i/12;cross.append((38+2.1*math.cos(t),31+1.5*math.sin(t)))
 vs=[]
 for depth in(-.18,0):
  for y,z in cross:
   hinge=35.9 if side=='south' else 40.1;angle=math.radians(90 if side=='south' else -90);dy=y-hinge
   vs.append((-3.55+depth*math.cos(angle)-dy*math.sin(angle),hinge+depth*math.sin(angle)+dy*math.cos(angle),z))
 n=len(cross);plain_mesh('V012 | '+side+' outward-open timber leaf',vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],[wood])
 for z in(29.65,30.55):
  ya,yb=(.15,1.95) if side=='south' else (-1.95,-.15);angle=math.radians(90 if side=='south' else -90);hinge=35.9 if side=='south' else 40.1
  local=[(-.21,ya,z),(-.18,ya,z),(-.18,yb,z),(-.21,yb,z),(-.21,ya,z+.08),(-.18,ya,z+.08),(-.18,yb,z+.08),(-.21,yb,z+.08)]
  plain_mesh('V012 | '+side+' open-leaf iron strap',[(-3.55+x*math.cos(angle)-y*math.sin(angle),hinge+x*math.sin(angle)+y*math.cos(angle),h) for x,y,h in local],F,[iron])
# No lights/cameras/world or tower mass edits.
bpy.context.preferences.filepaths.use_scripts_auto_execute=False;bpy.context.scene.render.filepath='//preview.png';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
r={'version':'v012','runtime':bpy.app.version_string,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'excavations':excavations,'hidden_closed_door_parts':hidden,'flat_landing_join_edge_ids':flat_join_edges,'door_bottom_elevation':29.04,'outward_door_angle_degrees':90,'stair_risers':20,'rise':.18125,'tread_length':.6,'clear_width':1.9,'destination':'existing northern covered terrace, z32.625; not an open-sky courtyard','scope':'Bounded entrance-to-covered-terrace route; publish only with matching validation and fresh restore evidence. Not dynamic navigation or construction certification.'};Path(a.report).write_text(json.dumps(r,indent=2));print('V012_BUILT',json.dumps(r))
