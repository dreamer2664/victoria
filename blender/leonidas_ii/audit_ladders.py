"""Independent final-mesh tests for all five exterior climbing ladders.

The rung and frame are separate emitted objects. Each actual rung-cap ray
must terminate inside the separately ray-tested side frame. Each pole/shell/
deck/nest interface is checked against independent actual carrier geometry.
No generator geometry functions are imported. Not a strength or avatar test.
"""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def mesh_tree(objects):
    vertices, triangles = [], []
    for ob in objects:
        mesh = ob.data
        mesh.calc_loop_triangles()
        offset = len(vertices)
        vertices.extend(tuple(ob.matrix_world @ v.co) for v in mesh.vertices)
        triangles.extend(tuple(offset+i for i in face.vertices)
                         for face in mesh.loop_triangles)
    return (BVHTree.FromPolygons(vertices, triangles, all_triangles=True)
            if triangles else None)


def inspect_access_ladders(data):
    expected = {'Mast_Fore', 'Mast_Main', 'Mast_Mizzen', 'Funnel_4.5', 'Funnel_30'}
    entries = data.get('access_ladders', [])
    objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    rows, issues, carriers = [], [], {}
    names = [a.get('id') for a in entries]
    if len(names) != len(expected) or set(names) != expected:
        issues.append(dict(issue='Missing/duplicate exterior ladder registry', ids=names))
    for entry in entries:
        identifier = entry['id']
        frame = mesh_tree([o for o in objects if o.name.startswith(entry['frame_prefix'])])
        rungs = mesh_tree([o for o in objects if o.name.startswith(entry['rungs_prefix'])])
        rung_rows, mount_rows = [], []
        if not frame or not rungs:
            issues.append(dict(id=identifier, issue='Missing separate emitted frame/rungs'))
            continue
        for index, rung in enumerate(entry.get('rungs', [])):
            center, half_width = Vector(rung['center']), rung['half_width']
            for side in (-1, 1):
                direction = Vector((0, side, 0))
                cap = rungs.ray_cast(center, direction, half_width+.04)
                rail = (frame.ray_cast(cap[0]+direction*.08, -direction, .16)
                        if cap[0] is not None else (None, None, None, None))
                cap_error = (abs((cap[0]-center).length-half_width)
                             if cap[0] is not None else None)
                embed = ((rail[0]-cap[0]).dot(direction)
                         if rail[0] is not None else None)
                okay = (cap_error is not None and cap_error <= .001 and
                        embed is not None and .005 <= embed <= .040)
                row = dict(rung=index, side=side, cap_datum_error_m=cap_error,
                           actual_cap_position=list(cap[0]) if cap[0] is not None else None,
                           frame_overlap_m=embed, status='PASS' if okay else 'FAIL')
                rung_rows.append(row)
                if not okay:
                    issues.append(dict(id=identifier, issue='Rung/frame joint', **row))
        for index, mount in enumerate(entry.get('mounts', [])):
            key = (mount.get('target_prefix'), mount.get('target_kind'), mount.get('target_deck'))
            if key not in carriers:
                selection = [o for o in objects if (
                    o.name.startswith(key[0]) if key[0] else
                    o.get('LII_kind') == key[1] and o.get('LII_deck') == key[2])]
                carriers[key] = mesh_tree(selection)
            carrier = carriers[key]
            hit = (carrier.ray_cast(Vector(mount['origin']), Vector(mount['direction']),
                                    mount['distance']) if carrier else
                   (None, None, None, None))
            near = (frame.find_nearest(hit[0], .05) if hit[0] is not None else
                    (None, None, None, None))
            gap = near[3]
            okay = gap is not None and gap <= .032
            row = dict(mount=index, role=mount['role'], carrier_selector=key,
                       actual_carrier_position=list(hit[0]) if hit[0] is not None else None,
                       frame_surface_distance_m=gap, status='PASS' if okay else 'FAIL')
            mount_rows.append(row)
            if not okay:
                issues.append(dict(id=identifier, issue='Frame/carrier support', **row))
        if len(rung_rows) < 40 or len(mount_rows) < 8:
            issues.append(dict(id=identifier, issue='Incomplete contact coverage',
                               rung_ends=len(rung_rows), mounts=len(mount_rows)))
        rows.append(dict(id=identifier, rung_ends=rung_rows, frame_mounts=mount_rows))
    return dict(ladders=rows, issues=issues,
                summary=dict(ladders=len(rows),
                             rung_ends=sum(len(r['rung_ends']) for r in rows),
                             frame_mounts=sum(len(r['frame_mounts']) for r in rows),
                             failures=len(issues)),
                limits='Rung cap/side-frame rays and actual carrier-interface proximity only; '
                       'not universal internal connectivity, climbable nest hatches, '
                       'load rating, rigging safety or Studio avatar climbing acceptance.')
