"""Reviewed exact v029 scope, independent of runtime's editable labels."""
import hashlib,json
from pathlib import Path
from compare_support import require,SOURCE_SHA,NEW
CATALOG='b10ecd91f93b59c71523663e8336b07bf9d7bda6c28950ac643a1ac8100c8424'
INDEX='da82f1ba19d20ebd85bae60edef74961a2f6c04311fe81611c1e9e231aac9368'
SUFFIXES=['mounting plate','wall arm','lower cup','hood rim','rain hood','cage upright 0','cage upright 1','cage upright 2','cage upright 3','luminous flame']
EXPECTED={
 'receiving_shell':{'V029 | receiving shell outside stores guard','V029 | local stores shell'},
 'room_lantern_meshes':{'V028 | room '+str(i)+' '+s for i in (1,2)for s in SUFFIXES},
 'entrance_ceiling':{'V027 | three pointed bays with high wall bands'},
 'near_tree_high':set(NEW),
 'stores_lantern_meshes':{'V029 | stores '+i+' '+s for i in ('south','north')for s in SUFFIXES}}
def validate_scope(catalog,index,tool):
 require(hashlib.sha256((Path(tool)/'catalog.json').read_bytes()).hexdigest()==CATALOG,'Reviewed catalog bytes')
 require(hashlib.sha256((Path(tool)/'edit_index.json').read_bytes()).hexdigest()==INDEX,'Reviewed index bytes')
 require(catalog['source_sha256']==SOURCE_SHA and index['source_sha256']==SOURCE_SHA,'Source binding')
 require(len(catalog['views'])==20 and sum(not v['existing']for v in catalog['views'].values())==19,'20bookmarks/19derived cameras')
 require(set(index['groups'])==set(EXPECTED),'Exact five groups')
 for key,names in EXPECTED.items():
  actual=[s['name']for s in index['groups'][key]['objects']];require(len(actual)==len(names)and set(actual)==names,'Exact reviewed targets '+key)
 require(sum(len(g['objects'])for g in index['groups'].values())==45,'45target entries')
