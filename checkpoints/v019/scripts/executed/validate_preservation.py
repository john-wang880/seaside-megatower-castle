"""Independent bounded v018 Mask/complement preservation QA. Never saves models."""
import argparse, array, bpy, hashlib, json, os, sys, time, copy
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('--baseline', required=True)
p.add_argument('--checkpoint', required=True)
p.add_argument('--report', required=True)
p.add_argument('--source-components', required=True)
p.add_argument('--asset', required=True)
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
TARGET = 'V010 | woodland boughs with gate exit clearance'
GROUP = 'V019 candidate | reversible left tree foliage'
MODIFIER = 'V019 candidate | original foliage rollback mask'
SPEC=json.loads(Path(a.source_components).read_text())
RANGES=[(90395,90693)]
SELECTED=set(range(90395,90693))
assert set(i for c in SPEC['components'] for i in c['ids'])==SELECTED and len(SPEC['components'])==25
ADDED={'V019 candidate | articulated conifer foliage','V019 candidate | connected conifer boughs'}
COLLECTION='UNACCEPTED | v019 specialist foreground conifer'
start = time.time()
source_sha = hashlib.sha256(Path(a.baseline).read_bytes()).hexdigest()
candidate_sha = hashlib.sha256(Path(a.checkpoint).read_bytes()).hexdigest()
assert source_sha == 'c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd'

def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()

def val(x):
    if x is None or isinstance(x, (bool, int, float, str)):
        return x
    if isinstance(x, bytes):
        return x.hex()
    if isinstance(x, set):
        return sorted(x)
    if isinstance(x, bpy.types.ID):
        return {'id_type': x.bl_rna.identifier, 'name': x.name}
    if hasattr(x, 'items'):
        return {str(k): val(v) for k, v in x.items()}
    try:
        return [val(q) for q in x]
    except TypeError:
        return str(type(x).__name__)

def primitive(o, depth=0):
    d = {}
    for prop in o.bl_rna.properties:
        n = prop.identifier
        if n in {'rna_type', 'users', 'session_uid', 'is_updated', 'is_updated_data', 'is_evaluated', 'is_runtime_data', 'original', 'tag', 'is_embedded_data', 'is_missing', 'is_library_indirect', 'is_editable', 'is_editmode'}:
            continue
        if prop.type in {'BOOLEAN', 'INT', 'FLOAT', 'STRING', 'ENUM'}:
            try:
                d[n] = val(getattr(o, n))
            except (AttributeError, TypeError):
                pass
        elif prop.type == 'POINTER':
            target = getattr(o, n, None)
            if target is None or isinstance(target, bpy.types.ID):
                d[n] = val(target)
            elif depth < 2:
                d[n] = primitive(target, depth + 1)
        elif prop.type == 'COLLECTION' and depth < 1 and (n not in {'rna_properties'}):
            collection = getattr(o, n, [])
            d[n] = [primitive(q, depth + 1) if hasattr(q, 'bl_rna') else val(q) for q in collection]
    if hasattr(o, 'items'):
        try:
            d['custom_properties'] = {str(k): val(v) for k, v in o.items()}
        except TypeError:
            d['custom_properties'] = None
    return d

def field_hash(coll, name, kind, width=1):
    if not len(coll):
        return {'count': 0, 'hash': None}
    code = {'FLOAT': 'f', 'INT': 'i', 'BOOLEAN': 'b'}[kind]
    buf = array.array(code, [0]) * (len(coll) * max(1, width))
    coll.foreach_get(name, buf)
    return {'count': len(coll), 'type': kind, 'width': width, 'hash': hashlib.sha256(buf.tobytes()).hexdigest()}

def mesh_snapshot(m, ignore_owned_weights=False):
    attrs = []
    for attr in m.attributes:
        fields = {}
        if len(attr.data):
            for prop in attr.data[0].bl_rna.properties:
                if prop.identifier == 'rna_type':
                    continue
                if prop.type in {'FLOAT', 'INT', 'BOOLEAN'}:
                    fields[prop.identifier] = field_hash(attr.data, prop.identifier, prop.type, prop.array_length)
                elif prop.type == 'STRING':
                    fields[prop.identifier] = digest([val(getattr(q, prop.identifier)) for q in attr.data])
                else:
                    raise AssertionError(('Unsupported attribute field', attr.name, prop.identifier, prop.type))
        attrs.append({'name': attr.name, 'type': attr.data_type, 'domain': attr.domain, 'count': len(attr.data), 'fields': fields})
    topology = {}
    for label, coll, props in [('vertices', m.vertices, [('co', 'FLOAT', 3), ('select', 'BOOLEAN', 1), ('hide', 'BOOLEAN', 1)]), ('edges', m.edges, [('vertices', 'INT', 2), ('select', 'BOOLEAN', 1), ('hide', 'BOOLEAN', 1), ('use_seam', 'BOOLEAN', 1), ('use_edge_sharp', 'BOOLEAN', 1)]), ('loops', m.loops, [('vertex_index', 'INT', 1), ('edge_index', 'INT', 1)]), ('polygons', m.polygons, [('loop_start', 'INT', 1), ('loop_total', 'INT', 1), ('material_index', 'INT', 1), ('use_smooth', 'BOOLEAN', 1), ('select', 'BOOLEAN', 1), ('hide', 'BOOLEAN', 1)])]:
        topology[label] = {n: field_hash(coll, n, k, w) for n, k, w in props if not len(coll) or hasattr(coll[0], n)}
    weights = [] if ignore_owned_weights else [(i, [(q.group, q.weight) for q in v.groups]) for i, v in enumerate(m.vertices) if len(v.groups)]
    shapes = None
    if m.shape_keys:
        shapes = [{'name': k.name, 'value': k.value, 'relative_key': k.relative_key.name, 'coordinates': field_hash(k.data, 'co', 'FLOAT', 3)} for k in m.shape_keys.key_blocks]
    return {'hash': digest({'attributes': attrs, 'topology': topology, 'corner_normals': field_hash(m.corner_normals, 'vector', 'FLOAT', 3), 'materials': [q.name if q else None for q in m.materials], 'weights': weights, 'shapes': shapes, 'uv_layers': [primitive(q) for q in m.uv_layers], 'uv_active_index': m.uv_layers.active_index, 'custom_properties': {k: val(v) for k, v in m.items()}}), 'attribute_schema': [(q['name'], q['type'], q['domain'], q['count']) for q in attrs], 'vertices': len(m.vertices), 'polygons': len(m.polygons), 'debug_payload': {'attributes': attrs, 'topology': topology, 'corner_normals': field_hash(m.corner_normals, 'vector', 'FLOAT', 3), 'materials': [q.name if q else None for q in m.materials], 'weights': weights, 'shapes': shapes, 'uv_layers': [primitive(q) for q in m.uv_layers], 'uv_active_index': m.uv_layers.active_index, 'custom_properties': {k: val(v) for k, v in m.items()}}}

def tree_snapshot(t, seen=None):
    if t is None:
        return None
    seen = set() if seen is None else seen
    if t.name in seen:
        return {'recursive_reference': t.name}
    seen = seen | {t.name}
    nodes = []
    for n in t.nodes:
        d = {'properties': primitive(n), 'inputs': [{'name': s.name, 'identifier': s.identifier, 'type': s.bl_idname, 'value': val(s.default_value) if hasattr(s, 'default_value') else None} for s in n.inputs]}
        if hasattr(n, 'node_tree') and n.node_tree:
            d['group'] = tree_snapshot(n.node_tree, seen)
        if hasattr(n, 'color_ramp'):
            d['ramp'] = {'properties': primitive(n.color_ramp), 'elements': [primitive(e) for e in n.color_ramp.elements]}
        if hasattr(n, 'mapping') and hasattr(n.mapping, 'curves'):
            d['curves'] = {'properties': primitive(n.mapping), 'curves': [[primitive(p) for p in c.points] for c in n.mapping.curves]}
        nodes.append(d)
    return {'nodes': nodes, 'links': sorted(((l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier) for l in t.links))}

def snap():
    deps = bpy.context.evaluated_depsgraph_get()
    evaluated = {}
    objects = {}
    for o in bpy.data.objects:
        objects[o.name] = {'properties': primitive(o), 'type': o.type, 'data': o.data.name if o.data else None, 'matrix': [list(row) for row in o.matrix_world], 'hide_render': o.hide_render, 'hide_viewport': o.hide_viewport, 'hidden': o.hide_get(), 'parent': o.parent.name if o.parent else None, 'parent_inverse': [list(row) for row in o.matrix_parent_inverse], 'slots': [(s.link, s.material.name if s.material else None) for s in o.material_slots], 'modifiers': [primitive(m) for m in o.modifiers], 'constraints': [primitive(c) for c in o.constraints], 'vertex_groups': [primitive(g) for g in o.vertex_groups], 'custom_properties': {k: val(v) for k, v in o.items()}}
        if o.type == 'MESH' and (not o.hide_render):
            eo = o.evaluated_get(deps)
            me = eo.to_mesh(preserve_all_data_layers=True, depsgraph=deps)
            evaluated[o.name] = {'matrix': [list(row) for row in eo.matrix_world], 'mesh': mesh_snapshot(me)}
            eo.to_mesh_clear()
    scene = bpy.context.scene
    return {'meshes': {m.name: mesh_snapshot(m, ignore_owned_weights=m.name == TARGET) for m in bpy.data.meshes}, 'objects': objects, 'materials': {m.name: digest({'properties': primitive(m), 'nodes': tree_snapshot(m.node_tree)}) for m in bpy.data.materials}, 'lights': {l.name: digest({'properties': primitive(l), 'nodes': tree_snapshot(l.node_tree)}) for l in bpy.data.lights}, 'cameras': {c.name: digest({'properties': primitive(c), 'dof': primitive(c.dof)}) for c in bpy.data.cameras}, 'worlds': {w.name: digest({'properties': primitive(w), 'nodes': tree_snapshot(w.node_tree)}) for w in bpy.data.worlds}, 'visible_evaluated': evaluated, 'scene': {'world': scene.world.name if scene.world else None, 'camera': scene.camera.name if scene.camera else None, 'render': primitive(scene.render), 'cycles': primitive(scene.cycles), 'view': primitive(scene.view_settings), 'frame': scene.frame_current, 'unit': primitive(scene.unit_settings)}, 'libraries': [l.filepath for l in bpy.data.libraries], 'texts': [(t.name, hashlib.sha256(t.as_string().encode()).hexdigest()) for t in bpy.data.texts]}

def maps_from_source(me):
    assert len(SELECTED) == 298
    faces_remove = []
    straddles = []
    for f in me.polygons:
        mask = [i in SELECTED for i in f.vertices]
        if any(mask):
            if not all(mask):
                straddles.append(f.index)
            faces_remove.append(f.index)
    assert not straddles and len(faces_remove) == 496, (straddles, len(faces_remove))
    return {'POINT': [i for i in range(len(me.vertices)) if i not in SELECTED], 'EDGE': [e.index for e in me.edges if all((i not in SELECTED for i in e.vertices))], 'FACE': [f.index for f in me.polygons if f.index not in set(faces_remove)], 'CORNER': [li for f in me.polygons if f.index not in set(faces_remove) for li in f.loop_indices]}

def field(coll, name, kind, width, indices=None, index_map=None):
    code = {'FLOAT': 'f', 'INT': 'i', 'BOOLEAN': 'b'}[kind]
    data = array.array(code, [0]) * (len(coll) * max(1, width))
    coll.foreach_get(name, data)
    width = max(1, width)
    if indices is not None:
        data = array.array(code, (data[i * width + j] for i in indices for j in range(width)))
    if index_map is not None:
        data = array.array(code, (index_map[i] for i in data))
    return {'count': len(data) // width, 'width': width, 'type': kind, 'sha256': hashlib.sha256(data.tobytes()).hexdigest()}

def complement_snapshot(me, maps, candidate=False):
    counts = {'POINT': len(me.vertices), 'EDGE': len(me.edges), 'FACE': len(me.polygons), 'CORNER': len(me.loops)}
    if candidate:
        assert counts == {k: len(v) for k, v in maps.items()}, ('Mask counts/order contract', counts)
    attrs = []
    remap_attrs = {'.edge_verts': 'POINT', '.corner_vert': 'POINT', '.corner_edge': 'EDGE'}
    for attr in me.attributes:
        assert attr.domain in maps, ('Unsupported domain', attr.name, attr.domain)
        fields = {}
        idx = None if candidate else maps[attr.domain]
        if len(attr.data):
            for prop in attr.data[0].bl_rna.properties:
                if prop.identifier == 'rna_type':
                    continue
                if prop.type in {'FLOAT', 'INT', 'BOOLEAN'}:
                    fields[prop.identifier] = field(attr.data, prop.identifier, prop.type, prop.array_length, idx, maps[remap_attrs[attr.name]] if candidate and attr.name in remap_attrs else None)
                elif prop.type == 'STRING':
                    fields[prop.identifier] = digest([val(getattr(attr.data[i], prop.identifier)) for i in (range(len(attr.data)) if candidate else idx)])
                else:
                    raise AssertionError(('Unsupported attribute', attr.name, prop.type))
        attrs.append({'name': attr.name, 'type': attr.data_type, 'domain': attr.domain, 'fields': fields})
    topology = {}
    definitions = [('POINT', me.vertices, [('co', 'FLOAT', 3, None), ('select', 'BOOLEAN', 1, None), ('hide', 'BOOLEAN', 1, None)]), ('EDGE', me.edges, [('vertices', 'INT', 2, 'POINT'), ('select', 'BOOLEAN', 1, None), ('hide', 'BOOLEAN', 1, None), ('use_seam', 'BOOLEAN', 1, None), ('use_edge_sharp', 'BOOLEAN', 1, None)]), ('CORNER', me.loops, [('vertex_index', 'INT', 1, 'POINT'), ('edge_index', 'INT', 1, 'EDGE')]), ('FACE', me.polygons, [('loop_start', 'INT', 1, 'CORNER'), ('loop_total', 'INT', 1, None), ('material_index', 'INT', 1, None), ('use_smooth', 'BOOLEAN', 1, None), ('select', 'BOOLEAN', 1, None), ('hide', 'BOOLEAN', 1, None)])]
    for domain, coll, props in definitions:
        topology[domain] = {n: field(coll, n, k, w, None if candidate else maps[domain], maps[remap] if candidate and remap else None) for n, k, w, remap in props if not len(coll) or hasattr(coll[0], n)}
    return {'attributes': sorted(attrs,key=lambda q:q['name']), 'topology': topology, 'corner_normals': field(me.corner_normals, 'vector', 'FLOAT', 3, None if candidate else maps['CORNER']), 'materials': [m.name if m else None for m in me.materials], 'uv_layers': [primitive(v) for v in me.uv_layers], 'custom_properties': {k: val(v) for k, v in me.items()}}

def collections_snapshot():
    return {'collections': {c.name: {'children': sorted((x.name for x in c.children)), 'objects': sorted((x.name for x in c.objects)), 'hide_render': c.hide_render, 'hide_viewport': c.hide_viewport, 'hide_select': c.hide_select, 'properties': {k: val(v) for k, v in c.items()}} for c in bpy.data.collections}, 'root_children': sorted((c.name for c in bpy.context.scene.collection.children)), 'root_objects': sorted((o.name for o in bpy.context.scene.collection.objects))}

def normalized_target(o):
    d = copy.deepcopy(o)
    for k in ('vertex_groups', 'modifiers'):
        d[k] = []
        d['properties'].pop(k, None)
    return d
asset_sha=hashlib.sha256(Path(a.asset).read_bytes()).hexdigest()
assert asset_sha=='641651d02c994d2c65dc3b79dae2704ad9509af455b8a039aa46620f293faf88'
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a.asset), load_ui=False, use_scripts=False)
asset_meshes={new:mesh_snapshot(bpy.data.objects[old].data) for new,old in [('V019 candidate | articulated conifer foliage','CONCEPT | radial articulated needle sprays'),('V019 candidate | connected conifer boughs','CONCEPT | tapering connected boughs and shoots')]}
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a.baseline), load_ui=True, use_scripts=False)
counts_before_control = (len(bpy.data.objects), len(bpy.data.meshes))
control_mesh = bpy.data.meshes.new('TEMP independent Mask defaults')
control_object = bpy.data.objects.new(control_mesh.name, control_mesh)
try:
    control_modifier = control_object.modifiers.new('TEMP independent Mask defaults', 'MASK')
    native_mask_defaults = {k: getattr(control_modifier, k) for k in ('show_in_editmode', 'show_on_cage', 'use_smooth')}
finally:
    bpy.data.objects.remove(control_object, do_unlink=True)
    bpy.data.meshes.remove(control_mesh)
assert counts_before_control == (len(bpy.data.objects), len(bpy.data.meshes))
base = snap()
basecols = collections_snapshot()
target = bpy.data.objects[TARGET]
assert target.data.name == TARGET and (not target.vertex_groups) and (not target.modifiers) and (not any((v.groups for v in target.data.vertices)))
maps = maps_from_source(target.data)
expected_complement = complement_snapshot(target.data, maps)
used = {i for e in target.data.edges for i in e.vertices} | {i for f in target.data.polygons for i in f.vertices}
unselected_isolated = sorted(set(maps['POINT']) - used)
isolated_removed_maps = dict(maps, POINT=[i for i in maps['POINT'] if i not in set(unselected_isolated)])
isolated_removed_expected = complement_snapshot(target.data, isolated_removed_maps)
bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a.checkpoint), load_ui=True, use_scripts=False)
check = snap()
asset_meshes_exact=all(check['meshes'][name]==expected for name,expected in asset_meshes.items())
assert asset_meshes_exact, 'Integrated authored mesh differs from approved isolated asset'
checkcols = collections_snapshot()
target = bpy.data.objects[TARGET]
groups = [(g.name, g.index, g.lock_weight) for g in target.vertex_groups]
weights = [(v.index, [(g.group, g.weight) for g in v.groups]) for v in target.data.vertices if v.groups]
weights_expected = [(i, [(0, 1.0)]) for i in sorted(SELECTED)]
assert groups == [(GROUP, 0, False)] and weights == weights_expected, ('Unexpected owned group/weight set', groups, len(weights))
assert len(target.modifiers) == 1
mod = target.modifiers[0]
modifier_actual = primitive(mod)
settings = {'name': MODIFIER, 'type': 'MASK', 'mode': 'VERTEX_GROUP', 'vertex_group': GROUP, 'invert_vertex_group': True, 'threshold': 0.5, 'show_render': True, 'show_viewport': True, **native_mask_defaults}
for k, v in settings.items():
    assert getattr(mod, k) == v, ('Modifier setting', k, getattr(mod, k), v)
assert mod.armature is None
dg = bpy.context.evaluated_depsgraph_get()
eo = target.evaluated_get(dg)
me = eo.to_mesh(preserve_all_data_layers=True, depsgraph=dg)
isolated_removed = False
if len(me.vertices) == len(isolated_removed_maps['POINT']) and len(me.vertices) != len(maps['POINT']):
    maps = isolated_removed_maps
    expected_complement = isolated_removed_expected
    isolated_removed = True
actual_complement = complement_snapshot(me, maps, True)
eo.to_mesh_clear()
complement_differences = [k for k in expected_complement if expected_complement[k] != actual_complement[k]]
UI_OBJECTS={'Traveler | full length ivory skirt','Traveler | purple-red shoulder cape','Traveler | white tunic'}
ui_edge_reports={}
def render_semantic_with_ui_report(record):
 payload=copy.deepcopy(record['mesh']['debug_payload']);attr=next(x for x in payload['attributes'] if x['name']=='.select_edge');edge=payload['topology']['edges']['select']
 assert attr['type']=='BOOLEAN' and attr['domain']=='EDGE' and attr['count']==payload['topology']['edges']['vertices']['count']
 assert all(attr['fields']['value'][k]==edge[k] for k in ('hash','count','type')) and max(1,attr['fields']['value']['width'])==edge['width']
 ui={'attribute':attr,'edges_select':edge}
 payload['attributes']=[x for x in payload['attributes'] if x['name']!='.select_edge'];payload['topology']['edges'].pop('select')
 return {'matrix':record['matrix'],'mesh':payload},ui
differences = {}
additions = {}
removals = {}
for cat in ('objects', 'meshes', 'materials', 'lights', 'cameras', 'worlds', 'visible_evaluated'):
    additions[cat] = sorted(set(check[cat]) - set(base[cat]))
    removals[cat] = sorted(set(base[cat]) - set(check[cat]))
    changed = []
    for name in set(base[cat]) & set(check[cat]):
        if cat == 'visible_evaluated' and name == TARGET:
            continue
        left, right = (base[cat][name], check[cat][name])
        if cat=='visible_evaluated' and name in UI_OBJECTS:
            assert any(m['type']=='SUBSURF' for m in base['objects'][name]['modifiers']) and any(m['type']=='SUBSURF' for m in check['objects'][name]['modifiers'])
            left,lui=render_semantic_with_ui_report(left);right,rui=render_semantic_with_ui_report(right)
            lschema=copy.deepcopy(lui);rschema=copy.deepcopy(rui)
            for q in (lschema,rschema):q['attribute']['fields']['value']['hash']=None;q['edges_select']['hash']=None
            assert lschema==rschema
            ui_edge_reports[name]={'before':lui,'after':rui,'changed':lui!=rui,'render_semantic_payload_exact':left==right}

        if cat == 'objects' and name == TARGET:
            left, right = (normalized_target(left), normalized_target(right))
        if left != right:
            changed.append(name)
    differences[cat] = sorted(changed)
for cat in ('scene', 'libraries', 'texts'):
    differences[cat] = [] if base[cat] == check[cat] else ['changed']
for name, v in basecols['collections'].items():
    if checkcols['collections'].get(name) != v:
        differences.setdefault('existing_collections', []).append(name)
collection_ok = set(checkcols['collections']) - set(basecols['collections']) == {COLLECTION} and checkcols['collections'][COLLECTION]['objects'] == sorted(ADDED) and (not checkcols['collections'][COLLECTION]['children']) and (checkcols['root_children'] == sorted(basecols['root_children'] + [COLLECTION])) and (checkcols['root_objects'] == basecols['root_objects'])
additions_ok = all((set(additions[k]) == (ADDED if k in ('objects', 'meshes', 'visible_evaluated') else set()) for k in additions))
def detailed_diff(left,right,path=''):
 if type(left)!=type(right):return [{'path':path,'before':left,'after':right}]
 if isinstance(left,dict):
  return sum((detailed_diff(left.get(k),right.get(k),path+'/'+str(k)) for k in sorted(set(left)|set(right))),[])
 if isinstance(left,list):
  if len(left)!=len(right):return [{'path':path+'/length','before':len(left),'after':len(right)}]
  return sum((detailed_diff(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(left,right))),[])
 return [] if left==right else [{'path':path,'before':left,'after':right}]
localized={name:detailed_diff(base['visible_evaluated'][name]['mesh']['debug_payload'],check['visible_evaluated'][name]['mesh']['debug_payload']) for name in differences['visible_evaluated']}
r = {'authored_asset_sha256':asset_sha,'integrated_new_meshes_match_asset_exact':asset_meshes_exact,'asset_file_unchanged':asset_sha==hashlib.sha256(Path(a.asset).read_bytes()).hexdigest(),'localized_evaluated_differences':localized,'complement_attribute_details':{'expected':expected_complement['attributes'],'actual':actual_complement['attributes']},'source_sha256': source_sha, 'candidate_sha256': candidate_sha, 'target': TARGET, 'exact_owned_group': groups, 'selected_vertex_ranges': RANGES, 'selected_vertex_count': 298, 'removed_complete_original_faces': 496, 'precise_weights_verified': True, 'modifier_settings_verified': settings, 'full_modifier_snapshot': modifier_actual, 'raw_target_except_owned_deform_weights_exact': not differences['meshes'], 'evaluated_non_target_complement_exact': not complement_differences, 'complement_field_differences': complement_differences, 'expected_complement_digest': digest(expected_complement), 'actual_complement_digest': digest(actual_complement), 'unselected_isolated_vertex_count': len(unselected_isolated), 'evaluator_removed_only_these_unselected_isolated_vertices': isolated_removed, 'isolated_vertex_policy': 'Raw source always exact. Evaluated complement may preserve all unselected vertices or omit exactly source degree-zero/unfaced vertices; retained coordinate/topology/attribute maps must still match exactly. No non-target faced/edged vertex omission allowed.', 'kept_element_counts': {k: len(v) for k, v in maps.items()}, 'source_differences': differences, 'additions': additions, 'removals': removals, 'additions_exact': additions_ok, 'collection_change_exact': collection_ok, 'source_file_unchanged': source_sha == hashlib.sha256(Path(a.baseline).read_bytes()).hexdigest(), 'candidate_file_unchanged': candidate_sha == hashlib.sha256(Path(a.checkpoint).read_bytes()).hexdigest(), 'scope': 'All persisted source meshes/attributes/weights and evaluated non-target objects exact; only validated target deform weights/group/Mask allowed. Actual evaluated complement mapped to independently retained original vertex/edge/face/corner IDs and all attributes/materials/normals/topology checked, not counts alone. Original hidden forests and all trunks included in ordinary exact comparisons. Replacement visual/contact QA separate.', 'seconds': time.time() - start}
r['pass'] = not any(differences.values()) and (not any(removals.values())) and (not complement_differences) and additions_ok and collection_ok and r['source_file_unchanged'] and r['candidate_file_unchanged']
Path(a.report).write_text(json.dumps(r, indent=2))
print(json.dumps(r, indent=2))
assert r['pass'], 'Inspect independent preservation differences'
