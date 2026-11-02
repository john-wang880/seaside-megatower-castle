"""Reviewed exact v030 scope, independent of runtime's editable labels."""
import hashlib,json
from pathlib import Path
from compare_support import require,SOURCE_SHA,NEW
CATALOG='0f672d7de20ff37d32f9922cbaa26d4e58d1e7dbd7bb9abf7a0e3c3879ec7d1b'
INDEX='4dc06df86511e8abb4109aac9b793cbafcdf5e2da0662a94ae6a1590a234e060'
SUFFIXES=['mounting plate','wall arm','lower cup','hood rim','rain hood','cage upright 0','cage upright 1','cage upright 2','cage upright 3','luminous flame']
EXPECTED={
 'receiving_shell':{'V029 | receiving shell outside stores guard','V029 | local stores shell'},
 'room_lantern_meshes':{'V028 | room '+str(i)+' '+s for i in (1,2)for s in SUFFIXES},
 'entrance_ceiling':{'V027 | three pointed bays with high wall bands'},
 'near_tree_high':set(NEW),
 'stores_lantern_meshes':{'V029 | stores '+i+' '+s for i in ('south','north')for s in SUFFIXES}}
EXPECTED['stores_fittings']={f'V030 | {side} three-bay rack' for side in ('south','north')} | {f'V030 | {side} supply bin {bay}' for side in ('south','north') for bay in (0,2)}
def validate_scope(catalog,index,tool):
 require(hashlib.sha256((Path(tool)/'catalog.json').read_bytes()).hexdigest()==CATALOG,'Reviewed catalog bytes')
 require(hashlib.sha256((Path(tool)/'edit_index.json').read_bytes()).hexdigest()==INDEX,'Reviewed index bytes')
 require(catalog['source_sha256']==SOURCE_SHA and index['source_sha256']==SOURCE_SHA,'Source binding')
 require(len(catalog['views'])==20 and sum(not v['existing']for v in catalog['views'].values())==19,'20bookmarks/19derived cameras')
 require(set(index['groups'])==set(EXPECTED),'Exact six groups')
 for key,names in EXPECTED.items():
  actual=[s['name']for s in index['groups'][key]['objects']];require(len(actual)==len(names)and set(actual)==names,'Exact reviewed targets '+key)
 require(sum(len(g['objects'])for g in index['groups'].values())==51,'51target entries')

 # Predecessor acceptance remains exact; new labels cannot silently replace old mappings.
 prior=json.loads((Path(__file__).parent/'predecessor.json').read_text())
 require(catalog['views']==prior['views'],'All20 predecessor camera records exact')
 require({k:index['groups'][k] for k in prior['groups']}==prior['groups'],'All5 predecessor group records exact')
 require(catalog['source_bytes']==47842841,'Exact source byte count')
 for name,digest in json.loads((Path(__file__).parent/'runtime_pins.json').read_text()).items():
  require(hashlib.sha256((Path(tool)/name).read_bytes()).hexdigest()==digest,'Exact reviewed runtime '+name)
