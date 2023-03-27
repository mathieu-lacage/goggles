import solid


class Mesh:
    def __init__(self, points, triangles):
        self._points = points
        self._triangles = triangles

    def solidify(self):
        return solid.polyhedron(self._points, self._triangles)
