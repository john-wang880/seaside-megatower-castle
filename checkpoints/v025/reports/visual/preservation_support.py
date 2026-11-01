"""Standalone exact raw-mesh/node snapshots used by western-cap builder.
Builder calls mesh_snapshot with default False: no evaluated UI exclusions or tolerances.
"""
import array,hashlib,json,bpy

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

def mesh_snapshot(m, omit_evaluated_edge_selection=False):
    attrs = []
    for attr in m.attributes:
        if omit_evaluated_edge_selection and attr.name == ".select_edge":
            assert attr.data_type == "BOOLEAN" and attr.domain == "EDGE" and len(attr.data) == len(m.edges)
            continue
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
        topology[label] = {n: field_hash(coll, n, k, w) for n, k, w in props if (not len(coll) or hasattr(coll[0], n)) and not (omit_evaluated_edge_selection and label=="edges" and n=="select")}
    weights = [(i, [(q.group, q.weight) for q in v.groups]) for i, v in enumerate(m.vertices) if len(v.groups)]
    shapes = None
    if m.shape_keys:
        shapes = [{'name': k.name, 'value': k.value, 'relative_key': k.relative_key.name, 'coordinates': field_hash(k.data, 'co', 'FLOAT', 3)} for k in m.shape_keys.key_blocks]
    return {'hash': digest({'attributes': attrs, 'topology': topology, 'corner_normals': field_hash(m.corner_normals, 'vector', 'FLOAT', 3), 'materials': [q.name if q else None for q in m.materials], 'weights': weights, 'shapes': shapes, 'uv_layers': [primitive(q) for q in m.uv_layers], 'uv_active_index': m.uv_layers.active_index, 'custom_properties': {k: val(v) for k, v in m.items()}}), 'attribute_schema': [(q['name'], q['type'], q['domain'], q['count']) for q in attrs], 'vertices': len(m.vertices), 'polygons': len(m.polygons)}

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
