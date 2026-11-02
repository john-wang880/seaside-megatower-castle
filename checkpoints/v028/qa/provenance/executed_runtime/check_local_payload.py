import argparse,json,hashlib,time
from pathlib import Path
from axis_reference import build
from exact_axis_boundary import validate
from planar_triangulation import triangulate
p=argparse.ArgumentParser()
for k in ['payload','export','proof','report']:p.add_argument('--'+k,required=True)
a=p.parse_args();paths={k:Path(v) for k,v in vars(a).items()};assert not paths['report'].exists();data={k:json.loads(paths[k].read_text()) for k in ['payload','export','proof']};start=time.time()
reference,rounding=build(data['export'],data['proof']);mesh=next(m for m in data['payload']['meshes'] if m['name']=='V028 | local receiving chamber shell');triangles=[t for f in mesh['faces'] for t in triangulate(mesh['vertices'],f)];result=validate(mesh['vertices'],triangles,reference)
result.update(input_sha256={k:hashlib.sha256(paths[k].read_bytes()).hexdigest() for k in ['payload','export','proof']},quantization=rounding,seconds=time.time()-start,scope='CPU actual payload planar-boundary proof via independent exact ear clipping. Native saved loop triangulation/deep state remains required. No model/Boolean/native operation.');paths['report'].write_text(json.dumps(result,indent=2)+'\n');print('LOCAL PAYLOAD EXACT BOUNDARY PASS',result['saved_float_volume'])
