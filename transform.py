import solid
import solid.utils
import euclid3

def to_path(shapes:solid.Points, 
            path:solid.Points,
            tangents:solid.Points):

    path = solid.utils.euclidify(path, euclid3.Point3)
    tangents = solid.utils.euclidify(tangents, euclid3.Point3)
    shapes = [solid.utils.euclidify(shape) for shape in shapes]
    assert len(path) == len(shapes)
    assert len(path) == len(tangents)
    src_up = euclid3.Vector3(0, 0, 1)

    retval = [
        solid.utils.transform_to_point(shape,dest_point=point, dest_normal=tangent, src_up=src_up)
        for shape, point, tangent in zip(shapes, path, tangents)
    ]
    return retval
