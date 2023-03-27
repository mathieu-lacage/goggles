import euclid3

from .point import Point3
from .shapes import Shapes

__all__ = ['extrude']


class Extrude:
    def __init__(self, shape):
        self._shape = shape

    def _open_path_tangents(self, path):
        first = Point3(*(path[0] - (path[1] - path[0])))
        last = Point3(*(path[-1] - (path[-2] - path[-1])))
        tmp = [first] + path + [last]
        tangents = [tmp[i+2] - tmp[i] for i in range(len(tmp)-2)]
        return tangents

    def _closed_path_tangents(self, path):
        tmp = [path[-1]] + path + [path[0]]
        tangents = [tmp[i+2] - tmp[i] for i in range(len(tmp)-2)]
        return tangents

    def _transform_matrix(self, dest, dest_normal):
        # https://stackoverflow.com/questions/25027045
        origin = euclid3.Vector3(0, 0, 0)
        y_axis = euclid3.Vector3(0, 1, 0)
        z_axis = euclid3.Vector3(0, 0, 1)
        if dest_normal.cross(z_axis) == origin:
            up = y_axis
        else:
            up = z_axis
        eye = dest
        at = dest + dest_normal
        z = (eye - at).normalized()
        x = up.cross(z).normalized()
        x = x.normalized()
        y = z.cross(x)

        m = euclid3.Matrix4.new_rotate_triple_axis(x, y, z)
        m.d, m.h, m.l = eye.x, eye.y, eye.z
        return m

    def _transform_shapes(self, path, tangents, shapes):
        for path_point, tangent, shape in zip(path, tangents, shapes):
            matrix = self._transform_matrix(path_point, tangent)
            transformed = [matrix * point for point in shape]
            yield transformed

    def _shapes(self, n):
        if callable(self._shape):
            shapes = [self._shape(i, n) for i in range(n)]
        elif isinstance(self._shape, list):
            if isinstance(self._shape[0], list):
                if len(self._shape) != n:
                    raise Exception('There should be as many shapes (%s) as path length (%s)' % (len(self._shape), n))
                shapes = self._shape
            else:
                shapes = [self._shape for i in range(n)]
        else:
            assert False
        shapes = [[Point3(x=p.x, y=p.y, z=0) for p in shape] for shape in shapes]
        return shapes

    def along_closed_path(self, path):
        tangents = self._closed_path_tangents(path)
        return self.along_path(path, tangents, Shapes.ENDS_CONNECT)

    def along_open_path(self, path):
        tangents = self._open_path_tangents(path)
        return self.along_path(path, tangents, Shapes.ENDS_CLOSE)

    def along_path(self, path, tangents, shape_type):
        shapes = self._shapes(len(path))
        transformed_shapes = list(self._transform_shapes(path, tangents, shapes))
        return Shapes(transformed_shapes, type=shape_type)

    def linear(self, h):
        p = [Point3(0, 0, 0), Point3(0, 0, h)]
        return self.along_open_path(p)

    def rotation(self, h):
        assert False
        return None


def extrude(shape):
    return Extrude(shape)
