import argparse,json,hashlib,collections
from pathlib import Path
p=argparse.ArgumentParser()
for k in ['rays','geometry','report']:p.add_argument('--'+k,required=True)
a=p.parse_args();assert not Path(a.report).exists();r=json.loads(Path(a.rays).read_text());g=json.loads(Path(a.geometry).read_text());assert r['source_sha256']==g['input_sha256']['candidate'];ceiling=g['objects']['V012 | entrance hall ceiling lining'];z=min(v[2]for v in ceiling['vertices']);seats=[]
for op in g['authored_operands_native_loop_triangles']:
 if not op['label'].startswith('arch'):continue
 vs=op['vertices'];profile=[(vs[i+2][1],vs[i+2][2])for i in range(0,len(vs),4)];parts=[]
 for a0,b in zip(profile,profile[1:]):
  if a0[1]<z and b[1]<z:continue
  aa,bb=a0[0],b[0]
  if a0[1]<z:aa=a0[0]+(b[0]-a0[0])*(z-a0[1])/(b[1]-a0[1])
  if b[1]<z:bb=a0[0]+(b[0]-a0[0])*(z-a0[1])/(b[1]-a0[1])
  parts.append([aa,bb])
 assert parts;y0=min(x[0]for x in parts);y1=max(x[1]for x in parts);assert y1>y0;seats.append({'operand':op['label'],'ceiling_underside':z,'contact_y_interval':[y0,y1],'width':y1-y0,'vertical_embed':max(y[1]for y in profile)-z})
assert len(seats)==3 and all(x['vertical_embed']>0 for x in seats)
dark=[x for x in r['rays']if sum(x['rgb'])<=20 and x['label']!='adjacent_control'];assert dark and all(x['first_hit']['object']=='V012 | entrance hall ceiling lining'for x in dark)
out={'pass':r['pass_all_pixels_hit_geometry']and r['source_unchanged'],'source_sha256':r['source_sha256'],'image_sha256':r['image_sha256'],'ray_report_sha256':hashlib.sha256(Path(a.rays).read_bytes()).hexdigest(),'pixel_count':len(r['rays']),'first_hit_objects':dict(collections.Counter(x['first_hit']['object']for x in r['rays'])),'crown_seating_profiles':seats,'dark_actual_pixel_samples':dark,'scope':'Bounded archived actual-image pixel rays on exact accepted geometry or independently semantically equal rebuild. Dark sampled strips hit intact ceiling; curved haunch airspace remains intentional, crown seats positive. Nearby light-center occlusions support shadows, not a complete Cycles radiometric decomposition.'};Path(a.report).write_text(json.dumps(out,indent=2));assert out['pass']
