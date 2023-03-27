import shapely

from .mesh import Mesh


class Shapes:

    ENDS_CLOSE, ENDS_CONNECT = (0, 1)

    def __init__(self, shapes, type):
        self._shapes = shapes
        self._ends = type

    @property
    def shapes(self):
        return self._shapes

    def _slice_triangles(self, current, previous, delta):
        triangles = []
        for i in range(1, delta):
            triangles.append((previous+i-1, previous+i, current+i-1))
            triangles.append((previous+i, current+i, current+i-1))
        triangles.append((previous+delta-1, previous, current+delta-1))
        triangles.append((previous, current, current+delta-1))
        return triangles

    def mesh(self):
        points = [point for shape in self._shapes for point in shape]
        delta = len(self._shapes[0])
        n = len(self._shapes) * delta
        previous = 0
        current = delta
        triangles = []
        while current < n:
            triangles.extend(self._slice_triangles(current, previous, delta))
            previous = current
            current += delta

        if self._ends == Shapes.ENDS_CLOSE:
            # XXX should project onto face plane, triangulate, and 
            # then do the inverse transformation to get back triangles
            # in the original space
            triangles.append(list(reversed(range(0, delta))))
            triangles.append(list(range(n-delta, n)))
            #triangles.append(list(range(n-delta, n)))
            #first = shapely.delaunay_triangles([(p.x, p.y) for p in self._shapes[0]])
            #last = shapely.delaunay_triangles([(p.x, p.y) for p in self._shapes[-1]])
        elif self._ends == Shapes.ENDS_CONNECT:
            triangles.extend(self._slice_triangles(0, n-delta, delta))
        else:
            assert False

        return Mesh(points, triangles)
