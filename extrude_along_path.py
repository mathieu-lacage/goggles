import transform
from solid import OpenSCADObject, Points, polyhedron
from solid.utils import euclidify, euc_to_arr, transform_to_point
from euclid3 import Point3, Vector3

from typing import Tuple, List

FacetIndices = Tuple[int, int, int]

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

    transformed = transform.to_path(shapes_pts, path_pts, connect_ends)
    for i, transformed_shape in enumerate(transformed):
        loop_start_index = i * shape_pt_count

        if (i < len(path_pts) - 1):
            loop_facets = _loop_facet_indices(loop_start_index, shape_pt_count)
            facet_indices += loop_facets

        # Add the transformed points & facets to our final list
        polyhedron_pts += transformed_shape

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
