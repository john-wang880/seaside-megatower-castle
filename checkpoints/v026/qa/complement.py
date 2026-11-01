import array,hashlib
from snapshot_support import digest,val,primitive
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

