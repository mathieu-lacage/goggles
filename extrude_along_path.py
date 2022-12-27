#! /usr/bin/env python
from math import radians
from solid import OpenSCADObject, Points, Indexes, ScadSize, polyhedron
from solid.utils import euclidify, euc_to_arr, transform_to_point, centroid
from euclid3 import Point2, Point3, Vector2, Vector3

from typing import Dict, Optional, Sequence, Tuple, Union, List, Callable

Tuple2 = Tuple[float, float]
FacetIndices = Tuple[int, int, int]
Point3Transform = Callable[[Point3, Optional[float], Optional[float]], Point3]

# ==========================
# = Extrusion along a path =
# ==========================
def extrude_along_path( shapes_pts:Points, 
                        path_pts:Points, 
                        connect_ends = False,
                        cap_ends = True) -> OpenSCADObject:
    '''
    Extrude the curve defined by shape_pts along path_pts.
    -- For predictable results, shape_pts must be planar, convex, and lie
    in the XY plane centered around the origin. *Some* nonconvexity (e.g, star shapes)
    and nonplanarity will generally work fine
    
    -- if connect_ends is True, the first and last loops of the extrusion will
          be joined, which is useful for toroidal geometries. Overrides cap_ends

    -- if cap_ends is True, each point in the first and last loops of the extrusion
        will be connected to the centroid of that loop. For planar, convex shapes, this
        works nicely. If shape is less planar or convex, some self-intersection may happen.
        Not applied if connect_ends is True
    '''


    polyhedron_pts:Points= []
    facet_indices:List[Tuple[int, int, int]] = []

    # Make sure we've got Euclid Point3's for all elements
    path_pts = euclidify(path_pts, Point3)
    shapes_pts = [euclidify(shape_pts) for shape_pts in shapes_pts]
    assert len(path_pts) == len(shapes_pts)
    shape_pt_count = len(shapes_pts[0])
    for shape_pts in shapes_pts:
        assert shape_pt_count == len(shape_pts)

    src_up = Vector3(0, 0, 1)


    tangent_path_points: List[Point3] = []
    if connect_ends:
        tangent_path_points = [path_pts[-1]] + path_pts + [path_pts[0]]
    else:
        first = Point3(*(path_pts[0] - (path_pts[1] - path_pts[0])))
        last = Point3(*(path_pts[-1] - (path_pts[-2] - path_pts[-1])))
        tangent_path_points = [first] + path_pts + [last]
    tangents = [tangent_path_points[i+2] - tangent_path_points[i] for i in range(len(path_pts))]

    for which_loop in range(len(path_pts)):
        path_pt = path_pts[which_loop]
        tangent = tangents[which_loop]

        this_loop = transform_to_point(shapes_pts[which_loop], dest_point=path_pt, dest_normal=tangent, src_up=src_up)
        loop_start_index = which_loop * shape_pt_count

        if (which_loop < len(path_pts) - 1):
            loop_facets = _loop_facet_indices(loop_start_index, shape_pt_count)
            facet_indices += loop_facets

        # Add the transformed points & facets to our final list
        polyhedron_pts += this_loop

    if connect_ends:
        connect_loop_start_index = len(polyhedron_pts) - shape_pt_count
        loop_facets = _loop_facet_indices(connect_loop_start_index, shape_pt_count, 0)
        facet_indices += loop_facets

    elif cap_ends:
        # OpenSCAD's polyhedron will automatically triangulate faces as needed.
        # So just include all points at each end of the tube 
        last_loop_start_index = len(polyhedron_pts) - shape_pt_count 
        start_loop_indices = list(reversed(range(shape_pt_count)))
        end_loop_indices = list(range(last_loop_start_index, last_loop_start_index + shape_pt_count))   
        facet_indices.append(start_loop_indices)
        facet_indices.append(end_loop_indices)

    return polyhedron(points=euc_to_arr(polyhedron_pts), faces=facet_indices) # type: ignore

def _loop_facet_indices(loop_start_index:int, loop_pt_count:int, next_loop_start_index=None) -> List[FacetIndices]:
    facet_indices: List[FacetIndices] = []
    # nlsi == next_loop_start_index
    if next_loop_start_index == None:
        next_loop_start_index = loop_start_index + loop_pt_count
    loop_indices      = list(range(loop_start_index,      loop_pt_count + loop_start_index)) + [loop_start_index]
    next_loop_indices = list(range(next_loop_start_index, loop_pt_count + next_loop_start_index )) + [next_loop_start_index]

    for i, (a, b) in enumerate(zip(loop_indices[:-1], loop_indices[1:])):
        c, d = next_loop_indices[i: i+2]
        # OpenSCAD's polyhedron will accept quads and do its own triangulation with them,
        # so we could just append (a,b,d,c). 
        # However, this lets OpenSCAD (Or CGAL?) do its own triangulation, leading
        # to some strange outcomes. Prefer to do our own triangulation.
        #   c--d
        #   |\ |
        #   | \|
        #   a--b               
        # facet_indices.append((a,b,d,c))
        facet_indices.append((a,b,c))
        facet_indices.append((b,d,c))
    return facet_indices

def _rotate_loop(points:Sequence[Point3], rotation_degrees:float=None) -> List[Point3]:
    if rotation_degrees is None:
        return points
    up = Vector3(0,0,1)
    rads = radians(rotation_degrees)
    return [p.rotate_around(up, rads) for p in points]

def _scale_loop(points:Sequence[Point3], scale:Union[float, Point2, Tuple2]=None) -> List[Point3]:
    if scale is None:
        return points

    if isinstance(scale, (float, int)):
        scale = [scale] * 2
    return [Point3(point.x * scale[0], point.y * scale[1], point.z) for point in points]

def _transform_loop(points:Sequence[Point3], transform_func:Point3Transform = None, path_normal:float = None) -> List[Point3]:
    # transform_func is a function that takes a point and optionally two floats,
    # a `path_normal`, in [0,1] that indicates where this loop is in a path extrusion,
    # and `loop_normal` in [0,1] that indicates where this point is in a list of points
    if transform_func is None:
        return points

    result = []
    for i, p in enumerate(points):
        # i goes from 0 to 1 across points
        loop_normal = i/(len(points) -1)
        new_p = transform_func(p, path_normal, loop_normal)
        result.append(new_p)
    return result

