"""Read-only detailed proof of the two isolated rib replacements. Load v006 with autoexec off."""
import argparse,bmesh,bpy,collections,hashlib,json,os,sys
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
configs=[('main','Citadel | carved ivory tracery',list(range(7576,7584)),[125.62,127.78,129.94,132.10,134.26,136.42]),('west','Western citadel_West_Sunlit ivory carved stone',list(range(48,56)),[137.95,139.85,141.75,143.65,145.55,147.45])]
checks=[]
def sig(o,p):return (tuple(sorted(tuple(float(x) for x in o.data.vertices[i].co) for i in p.vertices)),o.material_slots[p.material_index].material.name)
for tower,name,ids,cuts in configs:
 src=bpy.data.objects[name];target=bpy.data.objects['V006 | '+tower+' facade with one short jointed rib sample'];group=set(ids)
 excluded=[p for p in src.data.polygons if any(i in group for i in p.vertices)]
 assert len(excluded)==6 and all(set(p.vertices)<=group for p in excluded)
 old=collections.Counter(sig(src,p) for p in src.data.polygons if not any(i in group for i in p.vertices));new=collections.Counter(sig(target,p) for p in target.data.polygons)
 missing=old-new;assert not missing
 extras=new-old;assert sum(extras.values())==148
 bm=bmesh.new();bm.from_mesh(target.data);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free();assert boundary==nonmanifold==0
 pts=[src.data.vertices[i].co for i in ids];cx=sum(v.x for v in pts)/8;y=min(v.y for v in pts)
 low=sorted(pts,key=lambda p:p.z)[:4];tilt_offset=min(p.z for p in low)-sum(p.z for p in low)/4
 gaps=[]
 for nominal in cuts[1:-1]:
  z=nominal+tilt_offset;origin=Vector((cx,y+.020,z))
  hu,pu,nu,fu=target.ray_cast(origin,Vector((0,0,1)));hd,pd,nd,fd=target.ray_cast(origin,Vector((0,0,-1)))
  assert hu and hd and abs((pu.z-pd.z)-.018)<.0001,(tower,nominal,pu,pd)
  assert target.data.polygons[fu].material_index==1 and target.data.polygons[fd].material_index==1
  hit,back,n,f=target.ray_cast(Vector((cx,y-1,z)),Vector((0,1,0)))
  assert hit and abs(back.y-y-.035)<.0001 and target.data.polygons[f].material_index==2
  gaps.append({'nominal_z':nominal,'measured_clear_joint_width':pu.z-pd.z,'measured_backing_recess':back.y-y})
 contacts=[]
 for nominal in [cuts[0],cuts[-1]]:
  z=nominal+tilt_offset
  hu,pu,nu,fu=target.ray_cast(Vector((cx,y+.025,z-.020)),Vector((0,0,1)))
  hd,pd,nd,fd=target.ray_cast(Vector((cx,y+.025,z+.020)),Vector((0,0,-1)))
  assert hu and hd and abs(pu.z-pd.z)<.0001 and abs(pu.z-z)<.0001,(tower,nominal,pu,pd)
  contacts.append({'nominal_z':nominal,'lower_hit_z':pu.z,'upper_hit_z':pd.z,'actual_end_gap':abs(pu.z-pd.z)})
 checks.append({'tower':tower,'untouched_source_faces_matched_exactly':sum(old.values()),'removed_original_component_faces':len(excluded),'new_sample_component_faces':sum(extras.values()),'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'joint_width_and_backing_checks':gaps,'continuation_contact_checks':contacts})
r={'checkpoint_filename':os.path.basename(bpy.data.filepath),'checkpoint_sha256':hashlib.sha256(open(bpy.data.filepath,'rb').read()).hexdigest(),'read_only':True,'samples':checks,'all_checks_passed':True}
with open(a.report,'w',encoding='utf8') as f:json.dump(r,f,ensure_ascii=False,indent=2)
print(json.dumps(r,ensure_ascii=False,indent=2),flush=True)
