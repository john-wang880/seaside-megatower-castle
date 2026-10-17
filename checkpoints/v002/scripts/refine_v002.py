"""Rebuild the v002 crown/coast pass from the immutable clean v001 scene.

Run Blender with --disable-autoexec, open the clean baseline, then:
  --python refine_v002.py -- --output <new.blend> --report <report.json>
No external assets, plugins, downloads, or credentials are required.
The script never saves over its input. It only regenerates its own collection.
"""
import argparse
import bpy
import bmesh
import collections
import hashlib
import json
import math
import os
import random
import sys
from mathutils import Vector

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
P = argparse.ArgumentParser()
P.add_argument('--output', required=True)
P.add_argument('--report', required=True)
A = P.parse_args(ARGS)
SOURCE = os.path.abspath(bpy.data.filepath)
OUTPUT = os.path.abspath(A.output)
if SOURCE == OUTPUT:
    raise RuntimeError('Output must be a separate version, never the input baseline.')

PREFIX = 'V002 | '
COLLECTION_NAME = 'REFINEMENT | v002 crowns and solid coast'
old = bpy.data.collections.get(COLLECTION_NAME)
if old:
    for obj in list(old.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old)
for mat in list(bpy.data.materials):
    if mat.name.startswith(PREFIX) and mat.users == 0:
        bpy.data.materials.remove(mat)
C = bpy.data.collections.new(COLLECTION_NAME)
bpy.context.scene.collection.children.link(C)
RNG = random.Random(17018)

M = {
    'body': bpy.data.materials['Citadel • aged gallery grey'],
    'dark': bpy.data.materials['Citadel • deep slate ashlar'],
    'trim': bpy.data.materials['Citadel • pale cornice stone'],
    'carved': bpy.data.materials['Citadel • warm carved stone'],
    'recess': bpy.data.materials['Citadel • aperture darkness'],
    'rock': bpy.data.materials['Fractured coastal grey-blue slate'],
    'bronze': bpy.data.materials['Citadel • old bronze patina'],
}


def slate_material():
    mat = bpy.data.materials.new(PREFIX + 'quiet blue-grey roof slate')
    mat.use_nodes = True
    n, l = mat.node_tree.nodes, mat.node_tree.links
    bs = n.get('Principled BSDF')
    bs.inputs['Roughness'].default_value = .57
    bs.inputs['Metallic'].default_value = 0.0
    tex = n.new('ShaderNodeNewGeometry')
    noise = n.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 2.6
    noise.inputs['Detail'].default_value = 2.2
    ramp = n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = .18
    ramp.color_ramp.elements[0].color = (.041, .066, .079, 1)
    ramp.color_ramp.elements[1].position = .82
    ramp.color_ramp.elements[1].color = (.112, .161, .174, 1)
    bump = n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .17
    bump.inputs['Distance'].default_value = .038
    l.new(tex.outputs['Position'], noise.inputs['Vector'])
    l.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    l.new(ramp.outputs['Color'], bs.inputs['Base Color'])
    l.new(noise.outputs['Fac'], bump.inputs['Height'])
    l.new(bump.outputs['Normal'], bs.inputs['Normal'])
    mat.diffuse_color = (.075, .115, .135, 1)
    return mat


def wet_material():
    mat = M['rock'].copy()
    mat.name = PREFIX + 'tidal slate with wet lower band'
    n, l = mat.node_tree.nodes, mat.node_tree.links
    bs = next(n for n in n if n.bl_idname == 'ShaderNodeBsdfPrincipled')
    base = bs.inputs['Base Color']
    incoming = base.links[0].from_socket if base.is_linked else None
    mix = n.new('ShaderNodeMixRGB')
    mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = 1
    mix.inputs[2].default_value = (.42, .52, .57, 1)
    if incoming:
        l.new(incoming, mix.inputs[1])
    else:
        mix.inputs[1].default_value = base.default_value
    l.new(mix.outputs[0], base)
    bs.inputs['Roughness'].default_value = .29
    mat.diffuse_color = (.10, .15, .16, 1)
    return mat


M['roof'] = slate_material()
M['wet'] = wet_material()


def toned_copy(source, name, low, high=None, scale=.18):
    mat=source.copy(); mat.name=PREFIX+name
    nodes,links=mat.node_tree.nodes,mat.node_tree.links
    bs=next(n for n in nodes if n.bl_idname=='ShaderNodeBsdfPrincipled')
    incoming=bs.inputs['Base Color'].links[0].from_socket if bs.inputs['Base Color'].is_linked else None
    mix=nodes.new('ShaderNodeMixRGB'); mix.blend_type='MULTIPLY'; mix.inputs[0].default_value=1
    if incoming: links.new(incoming,mix.inputs[1])
    else: mix.inputs[1].default_value=bs.inputs['Base Color'].default_value
    if high is None:
        mix.inputs[2].default_value=(*low,1)
    else:
        geo=nodes.new('ShaderNodeNewGeometry'); noise=nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value=scale; noise.inputs['Detail'].default_value=2.0
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color=(*low,1); ramp.color_ramp.elements[1].color=(*high,1)
        links.new(geo.outputs['Position'],noise.inputs['Vector'])
        links.new(noise.outputs['Fac'],ramp.inputs['Fac']); links.new(ramp.outputs['Color'],mix.inputs[2])
    links.new(mix.outputs[0],bs.inputs['Base Color'])
    return mat


M['cornice']=toned_copy(M['trim'],'subdued crown cornice stone',(.75,.80,.82))
M['rock']=toned_copy(M['rock'],'varied salt-weathered coastal slate',(.43,.50,.49),(.90,.94,.87),.21)


class MeshBatch:
    def __init__(self, name):
        self.name, self.v, self.f, self.mi, self.mats = name, [], [], [], []

    def add(self, verts, faces, mat):
        if mat not in self.mats:
            self.mats.append(mat)
        index, off = self.mats.index(mat), len(self.v)
        self.v.extend([tuple(v) for v in verts])
        self.f.extend([tuple(off + i for i in f) for f in faces])
        self.mi.extend([index] * len(faces))

    def box(self, center, size, mat):
        x, y, z = center
        a, b, c = (v / 2 for v in size)
        v = [(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c),
             (x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
        f = [(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
        self.add(v, f, mat)

    def prism(self, polygon, z0, z1, mat):
        k = len(polygon)
        v = [(x,y,z0) for x,y in polygon] + [(x,y,z1) for x,y in polygon]
        f = [tuple(range(k-1,-1,-1)), tuple(range(k,2*k))]
        f += [(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)]
        self.add(v, f, mat)

    def cone(self, center, r0, r1, z0, z1, mat, sides=8, angle=math.pi/8):
        x, y = center
        verts = [(x+r*math.cos(angle+2*math.pi*i/sides),
                  y+r*math.sin(angle+2*math.pi*i/sides),z)
                 for r,z in [(r0,z0),(r1,z1)] for i in range(sides)]
        faces = [tuple(range(sides-1,-1,-1)), tuple(range(sides,2*sides))]
        faces += [(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)]
        self.add(verts, faces, mat)

    def beam(self, a, b, radius, mat, sides=8):
        a, b = Vector(a), Vector(b)
        axis = (b-a).normalized()
        ref = Vector((0,0,1)) if abs(axis.z) < .98 else Vector((0,1,0))
        u = axis.cross(ref).normalized()
        w = axis.cross(u).normalized()
        vs = [p + radius*(math.cos(i*math.tau/sides)*u+math.sin(i*math.tau/sides)*w)
              for p in (a,b) for i in range(sides)]
        fs = [tuple(range(sides-1,-1,-1)),tuple(range(sides,2*sides))]
        fs += [(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)]
        self.add(vs, fs, mat)

    def face_extrude(self, polygon, origin, u, normal, depth, mat, forward=0):
        origin, u, normal = Vector(origin), Vector(u), Vector(normal)
        verts = []
        for d in (-depth, forward):
            for x, z in polygon:
                p = origin + u*x + normal*d
                verts.append((p.x,p.y,z))
        k = len(polygon)
        faces = [tuple(range(k-1,-1,-1)),tuple(range(k,2*k))]
        faces += [(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)]
        self.add(verts, faces, mat)

    def finish(self):
        mesh = bpy.data.meshes.new(self.name)
        mesh.from_pydata(self.v, [], self.f)
        mesh.update()
        for mat in self.mats:
            mesh.materials.append(mat)
        for p, mat_index in zip(mesh.polygons, self.mi):
            p.material_index = mat_index
        obj = bpy.data.objects.new(self.name, mesh)
        C.objects.link(obj)
        obj['refinement_version'] = 'v002'
        return obj


def arch_curve(width, shoulder, apex, steps=8):
    # Two pointed circular-arc halves, vertically fitted to a true lancet proportion.
    h, r = width/2, apex-shoulder
    left = []
    for i in range(steps+1):
        angle=math.pi-i/steps*math.pi/3
        left.append((h+width*math.cos(angle),shoulder+r*math.sin(angle)/(math.sqrt(3)/2)))
    return left + [(-x,z) for x,z in left[-2::-1]]


def arch_ring(batch, width, bottom, shoulder, apex, origin, u, normal, material, thickness=.34, depth=.25):
    outer = [(-width/2-thickness,bottom)] + arch_curve(width+thickness*2,shoulder,apex+thickness*1.3) + [(width/2+thickness,bottom)]
    inner = [(-width/2,bottom)] + arch_curve(width,shoulder,apex) + [(width/2,bottom)]
    batch.face_extrude(outer+inner[::-1],origin,u,normal,depth,material,forward=.20)


def arcade_wall(batch, width, z0, z1, count, open_width, shoulder, apex, origin, u, normal):
    bottom = z0+.95
    gap = (width-count*open_width)/(count+1)
    # Continuous load-bearing lower sill.
    batch.face_extrude([(-width/2,z0),(width/2,z0),(width/2,bottom),(-width/2,bottom)],origin,u,normal,1.15,M['body'])
    cursor = -width/2
    for i in range(count+1):
        batch.face_extrude([(cursor,bottom),(cursor+gap,bottom),(cursor+gap,z1),(cursor,z1)],origin,u,normal,1.15,M['body'])
        cursor += gap
        if i == count:
            break
        center = cursor+open_width/2
        curve = [(x+center,z) for x,z in arch_curve(open_width,shoulder,apex)]
        for (x0,za),(x1,zb) in zip(curve[:-1],curve[1:]):
            batch.face_extrude([(x0,za),(x1,zb),(x1,z1),(x0,z1)],origin,u,normal,1.15,M['body'])
        local_origin = Vector(origin)+Vector(u)*center
        arch_ring(batch,open_width,bottom,shoulder,apex,local_origin,u,normal,M['trim'])
        cursor += open_width


def hipped_roof(batch, x, y, width, depth, z, rise, ridge, mat):
    w, d = width/2, depth/2
    v = [(x-w,y-d,z),(x+w,y-d,z),(x+w,y+d,z),(x-w,y+d,z),
         (x,y-ridge/2,z+rise),(x,y+ridge/2,z+rise)]
    batch.add(v,[(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5),(3,2,1,0)],mat)
    for a,b in [(0,4),(1,4),(2,5),(3,5),(4,5)]:
        batch.beam(Vector(v[a])+Vector((0,0,.05)),Vector(v[b])+Vector((0,0,.05)),.12,M['bronze'])


def clipped_rectangle(x,y,w,d,chamfer):
    a,b,c=w/2,d/2,chamfer
    return [(x-a+c,y-b),(x+a-c,y-b),(x+a,y-b+c),(x+a,y+b-c),
            (x+a-c,y+b),(x-a+c,y+b),(x-a,y+b-c),(x-a,y-b+c)]


# Main crown: broad masonry belfry, a short-ridge hipped roof, four lower pinnacles.
main = MeshBatch(PREFIX+'main crown masonry and terraces')
roof = MeshBatch(PREFIX+'main crown slate and roof seams')
mx,my=35.85,44.9
for w,d,z,h in [(39.0,38.0,179.9,.65),(40.1,39.0,180.5,.45),(38.9,37.8,181.0,.60)]:
    main.box((mx,my,z),(w,d,h),M['cornice'])

cx,cy=35.0,46.5
wallw,walld=25.6,25.4
main.box((cx,cy,181.65),(27.0,26.8,.75),M['dark'])
arcade_wall(main,wallw,182.0,191.2,3,4.2,186.8,190.4,(cx,cy-walld/2,0),(1,0,0),(0,-1,0))
arcade_wall(main,wallw,182.0,191.2,3,4.2,186.8,190.4,(cx,cy+walld/2,0),(-1,0,0),(0,1,0))
arcade_wall(main,walld,182.0,191.2,3,4.1,186.8,190.4,(cx+wallw/2,cy,0),(0,1,0),(1,0,0))
arcade_wall(main,walld,182.0,191.2,3,4.1,186.8,190.4,(cx-wallw/2,cy,0),(0,-1,0),(-1,0,0))
for x in [cx-wallw/2,cx+wallw/2]:
    for y in [cy-walld/2,cy+walld/2]:
        main.box((x,y,186.5),(1.65,1.65,10.7),M['trim'])
        main.box((x,y,191.5),(2.05,2.05,.55),M['trim'])
for w,d,z,h in [(27.4,27.2,191.3,.55),(28.1,27.9,191.85,.40),(27.5,27.3,192.30,.55)]:
    main.box((cx,cy,z),(w,d,h),M['cornice'])
hipped_roof(roof,cx,cy,28.0,27.8,192.55,18.0,8.5,M['roof'])
roof.beam((cx,cy,210.5),(cx,cy,212.7),.16,M['bronze'])

for x in [18.8,53.0]:
    for y in [28.7,61.2]:
        main.box((x,y,182.05),(3.55,3.55,1.20),M['trim'])
        main.box((x,y,185.0),(2.40,2.40,4.8),M['body'])
        # Thin corner ribs make the short pinnacles belong to the existing buttress grammar.
        for dx,dy in [(-1.1,-1.1),(1.1,-1.1),(1.1,1.1),(-1.1,1.1)]:
            main.box((x+dx,y+dy,185.0),(.38,.38,4.8),M['trim'])
        main.box((x,y,187.65),(3.25,3.25,.50),M['trim'])
        main.cone((x,y),1.72,1.36,187.9,189.1,M['trim'])
        roof.cone((x,y),1.50,.07,189.1,198.0,M['roof'])

# A quiet pierced parapet around the setback, kept low beneath the belfry windows.
par = MeshBatch(PREFIX+'main roof terrace parapet')
for origin,u,normal,width in [((mx,27.4,0),(1,0,0),(0,-1,0),30.8),
                             ((mx,62.5,0),(-1,0,0),(0,1,0),30.8),
                             ((17.7,my,0),(0,-1,0),(-1,0,0),29.0),
                             ((54.0,my,0),(0,1,0),(1,0,0),29.0)]:
    par.face_extrude([(-width/2,181.35),(width/2,181.35),(width/2,181.85),(-width/2,181.85)],origin,u,normal,.48,M['trim'])
    par.face_extrude([(-width/2,183.55),(width/2,183.55),(width/2,183.95),(-width/2,183.95)],origin,u,normal,.48,M['trim'])
    for i in range(9):
        t=-width/2+i*width/8
        par.face_extrude([(t-.28,181.75),(t+.28,181.75),(t+.28,183.65),(t-.28,183.65)],origin,u,normal,.50,M['trim'])

# West crown: an octagonal lantern with a low faceted slate cap, no copied corner spires.
west=MeshBatch(PREFIX+'western octagonal lantern masonry')
wroof=MeshBatch(PREFIX+'western lantern low slate cap')
wx,wy=-133.0,100.0
for w,d,z,h,c in [(28.8,30.8,167.1,.6,2.9),(29.7,31.7,167.65,.45,3.0),(28.6,30.6,168.15,.5,2.8)]:
    west.prism(clipped_rectangle(wx,wy,w,d,c),z-h/2,z+h/2,M['cornice'])
poly=[(wx+10.3*math.cos(math.pi/8+i*math.tau/8),wy+10.3*math.sin(math.pi/8+i*math.tau/8)) for i in range(8)]
west.prism(poly,168.35,169.0,M['dark'])
for i in range(8):
    a,b=Vector((*poly[i],0)),Vector((*poly[(i+1)%8],0))
    u=(b-a).normalized(); normal=Vector((u.y,-u.x,0)); center=(a+b)/2
    arcade_wall(west,(b-a).length,169.0,176.6,1,3.2,173.0,175.75,center,u,normal)
    west.cone(poly[i],.62,.54,168.8,176.95,M['trim'],sides=6)
for r,z0,z1 in [(10.8,176.6,177.05),(11.1,177.05,177.4),(10.6,177.4,177.75)]:
    west.cone((wx,wy),r,r,z0,z1,M['cornice'])
wroof.cone((wx,wy),10.8,.16,177.75,186.5,M['roof'])
wroof.beam((wx,wy,186.4),(wx,wy,188.0),.14,M['bronze'])
for i in range(8):
    ang=math.pi/8+i*math.tau/8
    wroof.beam((wx+10.8*math.cos(ang),wy+10.8*math.sin(ang),177.8),(wx,wy,186.55),.09,M['bronze'])

NEW_ARCH=[b.finish() for b in [main,roof,par,west,wroof]]


# Replace the western sheet with a closed shore, keeping the interior and selectively
# reshaping the front waterline into coves. The original object and mesh remain hidden.
source=bpy.data.objects['Western foreground | sweeping grassy slope']
source.hide_render=False
source.hide_viewport=False
mesh=source.data
counts=collections.Counter()
directions={}
for p in mesh.polygons:
    for i,a in enumerate(p.vertices):
        b=p.vertices[(i+1)%len(p.vertices)]
        e=tuple(sorted((a,b))); counts[e]+=1; directions[e]=(a,b)
boundary=[directions[e] for e,c in counts.items() if c==1]
nxt={a:b for a,b in boundary}
start=min(nxt); order=[start]
while nxt[order[-1]]!=start:
    order.append(nxt[order[-1]])
    if len(order)>len(boundary):
        raise RuntimeError('The coastline boundary is not one simple closed loop.')
if len(order)!=len(boundary):
    raise RuntimeError('Unexpected additional open boundary loops.')
verts=[tuple(source.matrix_world@v.co) for v in mesh.vertices]
original_verts=list(verts)
original_boundary=[Vector(verts[i]) for i in order]
boundary_center=Vector((sum(v.x for v in original_boundary)/len(order),sum(v.y for v in original_boundary)/len(order),0))


def shore_deformation(p):
    """Only the front shoreline's outer 14-unit strip is eligible; the interior is untouched."""
    if p.y>=-95 or p.z>=16: return Vector((0,0,0))
    nearest=None; best=14.0**2
    # Closest segment gives a continuous falloff rather than a repeated vertex scallop.
    for a,b in zip(original_boundary,original_boundary[1:]+original_boundary[:1]):
        dx,dy=b.x-a.x,b.y-a.y; length2=dx*dx+dy*dy
        t=max(0,min(1,((p.x-a.x)*dx+(p.y-a.y)*dy)/length2)) if length2 else 0
        q=a+(b-a)*t; d2=(p.x-q.x)**2+(p.y-q.y)**2
        if d2<best: best=d2; nearest=q
    if nearest is None: return Vector((0,0,0))
    weight=(1-math.sqrt(best)/14.0)
    weight=weight*weight*(3-2*weight)
    weight*=min(1,max(0,(-p.y-95)/35))*min(1,max(0,(16-p.z)/10))
    cove=min(1,max(0,(math.sin((nearest.x+180)/13)+.45*math.sin((nearest.x+75)/5.5)))/1.25)
    dz=-min(max(nearest.z+.75,0),7.5)*cove*weight
    radial=Vector((nearest.x-boundary_center.x,nearest.y-boundary_center.y,0)).normalized()
    return radial*(-2.7*cove*weight)+Vector((0,0,dz))


changed_top=0
for i,p in enumerate(original_verts):
    delta=shore_deformation(Vector(p))
    if delta.length>1e-5:
        verts[i]=tuple(Vector(p)+delta); changed_top+=1
faces=[tuple(p.vertices) for p in mesh.polygons]
matids=[p.material_index for p in mesh.polygons]
smooth=[p.use_smooth for p in mesh.polygons]
mats=list(mesh.materials)+[M['rock'],M['wet']]
dry_index,wet_index=len(mats)-2,len(mats)-1
center=Vector((sum(verts[i][0] for i in order)/len(order),sum(verts[i][1] for i in order)/len(order),0))
ring_ids=[order]
for band in range(1,6):
    ring=[]
    for j,idx in enumerate(order):
        x,y,h=verts[idx]
        radial=Vector((x-center.x,y-center.y,0)).normalized()
        # Long, medium and short variations follow a consistent coastal grain.
        wave=math.sin(j*.183+.8)+.44*math.sin(j*.71)+.22*math.sin(j*1.73)
        z1=h-.32
        z2=min(z1-.30,.65*h-.25+1.3*math.sin(j*.61))
        z3=min(z2-.30,.23*h-.70+1.1*math.sin(j*.83))
        z4=min(z3-.30,-1.20+.30*math.sin(j*.37))
        if band==1:
            z=z1; out=.24+.18*wave
        elif band==2:
            z=z2; out=max(.25,1.5+1.4*wave)
        elif band==3:
            z=z3; out=max(.45,3.4+2.1*wave)
        elif band==4:
            z=z4; out=max(.8,4.6+2.4*wave)
        else:
            z=-6.5; out=6.5+1.8*wave
        ring.append(len(verts)); verts.append((x+radial.x*out,y+radial.y*out,z))
    ring_ids.append(ring)
for band,(upper,lower) in enumerate(zip(ring_ids[:-1],ring_ids[1:])):
    for j in range(len(order)):
        k=(j+1)%len(order); a,b,c,d=upper[j],lower[j],lower[k],upper[k]
        # Slightly varied diagonal topology avoids a regularly repeated faceted skirt.
        tris=[(a,b,c),(a,c,d)] if (j+band)%3 else [(a,b,d),(b,c,d)]
        for tri in tris:
            faces.append(tri)
            avgz=sum(verts[v][2] for v in tri)/3
            matids.append(wet_index if avgz<.80 else dry_index)
            smooth.append(False)
bottom=len(verts); verts.append((center.x,center.y,-6.5))
for j,a in enumerate(ring_ids[-1]):
    b=ring_ids[-1][(j+1)%len(order)]
    faces.append((bottom,b,a)); matids.append(wet_index); smooth.append(False)
hullmesh=bpy.data.meshes.new(PREFIX+'closed western headland mesh')
hullmesh.from_pydata(verts,[],faces); hullmesh.update()
for mat in mats: hullmesh.materials.append(mat)
for p,mi,sm in zip(hullmesh.polygons,matids,smooth):
    p.material_index=mi; p.use_smooth=sm
# The source sheet was wound inward. A closed solid needs consistently outward normals.
bm=bmesh.new(); bm.from_mesh(hullmesh)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
if bm.calc_volume(signed=True)<0:
    bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
bm.to_mesh(hullmesh); bm.free(); hullmesh.update()
hull=bpy.data.objects.new(PREFIX+'western headland with solid rock shore',hullmesh)
C.objects.link(hull)
hull['source_object']=source.name
hull['interior_top_surface_preserved']=True
hull['front_shoreline_vertices_reshaped']=changed_top
hull['waterline_level']=-.33
source.hide_render=True
source.hide_viewport=True
source['v002_replaced_by']=hull.name

# Keep the few grass blades within the sculpted shoreline strip attached to the ground.
# Forest, path, flowers, bridge and traveler lie outside this strip and are left untouched.
grass_source=bpy.data.objects.get('Fine meadow grass blades')
grass_adjusted_faces=0
if grass_source:
    grass_source.hide_render=False; grass_source.hide_viewport=False
    gm=grass_source.data.copy()
    for face in gm.polygons:
        coords=[grass_source.matrix_world@gm.vertices[i].co for i in face.vertices]
        p=sum(coords,Vector())/len(coords); p.z=min(v.z for v in coords)
        delta=shore_deformation(p)
        if delta.length>1e-5:
            local_delta=grass_source.matrix_world.to_3x3().inverted()@delta
            for idx in face.vertices: gm.vertices[idx].co+=local_delta
            grass_adjusted_faces+=1
    if grass_adjusted_faces:
        go=bpy.data.objects.new(PREFIX+'grass conformed to front shore',gm)
        go.matrix_world=grass_source.matrix_world.copy(); C.objects.link(go)
        grass_source.hide_render=True; grass_source.hide_viewport=True
    else:
        bpy.data.meshes.remove(gm)

# Preserve every original camera. Add the tested full-silhouette camera in this collection.
cd=bpy.data.cameras.new(PREFIX+'full coastal skyline camera')
cam=bpy.data.objects.new(PREFIX+'full coastal skyline camera',cd)
C.objects.link(cam)
cam.location=(115,-470,24)
cam.rotation_euler=(Vector((-35,35,85))-cam.location).to_track_quat('-Z','Y').to_euler()
cd.lens=43; cd.clip_end=3000
cd['reference_preview_aspect']='3:2'
scene=bpy.context.scene
scene.camera=cam
scene['v002_scope']='Distinct tower crowns; closed western coastline; full-silhouette camera. Other art unchanged.'
scene['baseline_resolution']='2560x1290; original cameras preserved in baseline and this version.'
scene.render.resolution_x=2400; scene.render.resolution_y=1600; scene.render.resolution_percentage=100
scene.cycles.device='CPU'; scene.cycles.samples=80; scene.cycles.use_denoising=True
scene.render.filepath='//previews/v002_full_coastal_skyline.png'
scene.render.threads_mode='FIXED'; scene.render.threads=3
scene.render.use_stamp=False
for key in ['use_stamp_filename','use_stamp_date','use_stamp_time']:
    if hasattr(scene.render,key): setattr(scene.render,key,False)
for screen in bpy.data.screens:
    for area in screen.areas:
        for space in area.spaces:
            if space.type=='FILE_BROWSER' and space.params:
                space.params.directory=b'//'


def topology(obj):
    bm=bmesh.new(); bm.from_mesh(obj.data)
    r={'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),
       'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges)}
    if not r['boundary_edges']:
        r['signed_volume']=bm.calc_volume(signed=True)
    bm.free(); return r


shore_check=topology(hull)
if shore_check['boundary_edges'] or shore_check['nonmanifold_edges'] or shore_check['signed_volume']<=0:
    raise RuntimeError('Coast hull did not pass the closed-manifold check: '+str(shore_check))
interior_preserved=all((Vector(verts[i])-Vector(p)).length<1e-6 for i,p in enumerate(original_verts) if p[1]>=-95 or p[2]>=16)
if not interior_preserved:
    raise RuntimeError('Interior terrain outside the front shore zone must be unchanged.')
report={
    'version':'v002',
    'source_filename':os.path.basename(SOURCE),
    'output_filename':os.path.basename(OUTPUT),
    'source_sha256':hashlib.sha256(open(SOURCE,'rb').read()).hexdigest(),
    'autoexec_enabled':bpy.context.preferences.filepaths.use_scripts_auto_execute,
    'new_collection':COLLECTION_NAME,
    'changes':['Main stepped masonry belfry, short-ridge hipped slate roof, four lower corner pinnacles',
               'Lower western octagonal lantern and faceted cap; no copied corner pinnacles',
               'Western front shoreline gently reshaped into shallow coves; interior terrain retained; closed rock shore extends below sea',
               'Dedicated darker wet tidal slate; full coastal skyline camera'],
    'main_crown_top':212.7,'western_crown_top':188.0,
    'western_original_open_boundary_edges':len(boundary),
    'western_solid_hull':shore_check,
    'interior_terrain_top_preserved':interior_preserved,
    'front_shoreline_vertices_reshaped':changed_top,
    'nearshore_grass_faces_conformed':grass_adjusted_faces,
    'closed_hull_normals_outward':True,
    'original_terrain_object_retained_hidden':True,
    'added_architecture_objects':[{ 'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons)} for o in NEW_ARCH],
    'all_original_cameras_retained':all(n in bpy.data.objects for n in ['Hero Camera - reference composition','02 | Gothic facade and carved buttresses','03 | Stone bridge and western curtain wall','04 | Full three dimensional scene']),
    'images':len(bpy.data.images),'libraries':len(bpy.data.libraries),'texts':len(bpy.data.texts),
    'notes':['Early structural art pass, not final detail or project completion.',
             'Material/light/weather refinements and multi-view high-resolution checks remain.']
}
os.makedirs(os.path.dirname(OUTPUT),exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT,compress=True)
report['output_sha256']=hashlib.sha256(open(OUTPUT,'rb').read()).hexdigest()
with open(A.report,'w',encoding='utf8') as f: json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
