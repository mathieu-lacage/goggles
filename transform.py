import solid
import solid.utils
import euclid3


def to_path(shapes,
            path,
            connect_ends):

    path = solid.utils.euclidify(path, euclid3.Point3)
    shapes = [solid.utils.euclidify(shape) for shape in shapes]
    assert len(path) == len(shapes)
    tangents = []
    if connect_ends:
        tangents = [path[-1]] + path + [path[0]]
    else:
        first = euclid3.Point3(*(path[0] - (path[1] - path[0])))
        last = euclid3.Point3(*(path[-1] - (path[-2] - path[-1])))
        tangents = [first] + path + [last]
    tangents = [tangents[i+2] - tangents[i] for i in range(len(path))]
    tangents = solid.utils.euclidify(tangents, euclid3.Point3)
    assert len(path) == len(tangents)
    src_up = euclid3.Vector3(0, 0, 1)

    retval = [
        solid.utils.transform_to_point(shape, dest_point=point, dest_normal=tangent, src_up=src_up)
        for shape, point, tangent in zip(shapes, path, tangents)
    ]
    return retval
