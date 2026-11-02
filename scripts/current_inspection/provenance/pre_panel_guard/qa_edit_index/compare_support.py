"""Pure exact comparison helpers. No bpy import, broad attribute exclusions or I/O."""
import copy, hashlib,json
SOURCE_SHA='f0d135e0c6e554b5ae7c520ef9ccefc61e2a7c4abc3129eef1d3d4118bca8096'
BASE_SHA='c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd'
TARGET='V010 | woodland boughs with gate exit clearance'
GROUP='V019 candidate | reversible left tree foliage'
MASK='V019 candidate | original foliage rollback mask'
NEW=('V019 candidate | articulated conifer foliage','V019 candidate | connected conifer boughs')
SELECTED=range(90395,90693)
def require(ok,message):
 if not ok:raise RuntimeError(message)
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def normalize_owned_weights(mesh,group_index=0,allow_empty=False):
 out=copy.deepcopy(mesh);payload=out['debug_payload'];actual=payload['weights'];expected=[(i,[(group_index,1.0)]) for i in SELECTED]
 require(actual==expected or (allow_empty and actual==[]),'Unexpected owned deform values; no normalization allowed')
 payload['weights']=[];out['hash']=digest(payload)
 return out,{'count':len(actual),'group_index':group_index,'values':'unit weights only' if actual else 'empty'}
def normalize_display(snapshot,canonical):
 out=copy.deepcopy(snapshot)
 for name in NEW:
  for record in (out['objects'][name],out['objects'][name]['properties']):
   for key in ('hide_viewport','hide_render'):record[key]=canonical['objects'][name][key]
 for bucket in (out['objects'][TARGET]['modifiers'],out['objects'][TARGET]['properties'].get('modifiers',[])):
  require(len(bucket)==1 and bucket[0]['name']==MASK,'Unexpected modifier normalization scope')
  for key in ('show_viewport','show_render'):bucket[0][key]=True
 return out
def strip_inspection(snapshot,canonical,catalog):
 out=copy.deepcopy(snapshot);owned=[v['camera_name'] for v in catalog['views'].values() if not v['existing']]
 require(set(out['objects'])-set(canonical['objects'])==set(owned),'Unexpected added objects')
 require(set(out['cameras'])-set(canonical['cameras'])=={n+' data' for n in owned},'Unexpected added camera data')
 for name in owned:out['objects'].pop(name);out['cameras'].pop(name+' data')
 require(len([t for t in out['texts'] if t[0]==catalog['text']])==1,'Owned Text inventory')
 out['texts']=[t for t in out['texts'] if t[0]!=catalog['text']]
 out['scene_custom'].pop(catalog['marker'])
 out['collections']['collections'].pop(catalog['collection']);out['collections']['root_children'].remove(catalog['collection'])
 for layer in out['visibility'].values():
  for name in owned:layer['objects'].pop(name)
  layer['layer']['children']=[c for c in layer['layer']['children'] if c['collection']!=catalog['collection']]
 return out
