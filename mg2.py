import math

import numpy as np
import scipy.interpolate as si
import euclid3
import solid.utils

Point = euclid3.Point2

def _translate(xd, yd):
    def inner(path):
        return [Point(x=p.x+xd, y=p.y+yd) for p in path]
    return inner

def _rotate(alpha):
    def inner(path):
        c = math.cos(alpha)
        s = math.sin(alpha)
        return [Point(x=c*p.x-s*p.y, y=s*p.x+c*p.y) for p in path]
    return inner

def norm2(v):
    return math.sqrt(v.x**2+v.y**2)

def perpendicular(v, left, normalize=False):
    import numpy
    s = -1 if left else 1
    z = (0, 0, s)
    retval = numpy.cross(v, z)
    retval = Point(retval[0], retval[1])
    if normalize:
        retval = retval / norm2(retval)
    return retval

def _thicker_path(path, thickness=0.05, left=True):
    n = len(path)
    tangents = \
        [path[1]-path[0]] + \
        [(path[i+1]-path[i-1])/2 for i in range(1, n-1)] + \
        [path[n-1]-path[n-2]]
    orthogonal = [perpendicular(tangents[i],left, normalize=True) for i in range(n)]
    shifted = [path[i]+orthogonal[i]*thickness for i in range(n)]
    return shifted

def _bezier_spline(cv, max_y=None, n=100, degree=3):
    cv = np.asarray([[p.x, p.y] for p in cv])
    count = cv.shape[0]
    degree = np.clip(degree,1,count-1)
    kv = np.array([0]*degree + list(range(count-degree+1)) + [count-degree]*degree,dtype='int')
    u = np.linspace(0,(count-degree),n)
    path = [Point(x=p[0], y=p[1]) for p in np.array(si.splev(u, (kv,cv.T,degree))).T]
    return path

class _Points:
    def __init__(self, path, labels):
        self._p = path
        self._labels = labels

    @property
    def first(self):
        return self._p[0]

    @property
    def last(self):
        return self._p[-1]

    def __iter__(self):
        for i in self._p:
            yield i

    def __len__(self):
        return len(self._p)

    def __getitem__(self, key):
        return self._p[key]

    def __getattr__(self, name):
        return self._p[self._labels[name]]

class Path:
    def __init__(self, x=None, y=None, path=None, point=None, labels=None):
        if point is not None:
            assert isinstance(point, Point)
            self._p = [point]
            self._labels = {}
        elif path is not None:
            if isinstance(path, Path):
                self._p = [p for p in path._p]
                self._labels = {k: v for k, v in path._labels.items()}
            else:
                self._p = [p for p in path]
                self._labels = {k:v for k, v in labels.items()} if labels is not None else {}
        else:
            assert not isinstance(x, list)
            assert not isinstance(y, list)
            x = 0 if x is None else x
            y = 0 if y is None else y
            self._p = [Point(x,y)]
            self._labels = {}

    @property
    def points(self):
        return _Points(path=self._p, labels=self._labels)

    @property
    def reversed_points(self):
        return _Points(path=list(reversed(self._p)), labels={k: len(self._p)-v for k, v in self._labels.items()})

    @property
    def height(self):
        max_y = max(p.y for p in self._p)
        min_y = min(p.y for p in self._p)
        return abs(max_y-min_y)

    @property
    def width(self):
        max_x = max(p.x for p in self._p)
        min_x = min(p.x for p in self._p)
        return abs(max_x-min_x)

    def copy(self):
        return Path(path=self._p, labels=self._labels)

    def extend(self, path):
        if isinstance(path, Path):
            p = path._p
        else:
            p = path
        last = self._p[-1]
        self._p.extend(_translate(last.x-p[0].x, last.y-p[0].y)(p))
        return self

    def append(self, dx=None, dy=None, x=None, y=None, point=None, relative_to=None):
        assert point is not None or (dx is not None and x is None) or (dx is None and x is not None) or (dx is None and x is None)
        assert point is not None or (dy is not None and y is None) or (dy is None and y is not None) or (dy is None and y is None)
        assert point is not None or not (dx is None and dy is None and x is None and y is None)
        assert len(self._p) > 0
        if point is not None:
            self._p.append(point)
        else:
            if relative_to is not None:
                last = self._p[self._labels[relative_to]]
            else:
                last = self._p[-1]
            if dx is not None:
                x = last.x + dx
            elif x is None:
                x = last.x
            if dy is not None:
                y = last.y + dy
            elif y is None:
                y = last.y
            self._p.append(Point(x,y))
        return self

    def extend_arc(self, alpha, r, n=10):
        assert(len(self._p) >= 2)
        center = self._p[-1] + r * perpendicular(self._p[-1] - self._p[-2], left=alpha>0, normalize=True)
        start = self._p[-1] - center
        arc = []
        for i in range(n):
            beta = alpha/n * (i+1)
            arc.append(center + _rotate(beta)([start])[0])
        for p in arc:
            self.append(point=p)
        return self

    def append_angle(self, alpha, delta, relative_to=None):
        if relative_to is not None:
            i = self._labels[relative_to]
        else:
            i = -1
        v = self._p[i] - self._p[i-1]
        v = Point(x=math.cos(alpha)*v.x - math.sin(alpha)*v.y, y=math.sin(alpha)*v.x + math.cos(alpha)*v.y)
        v = v / norm2(v) * delta
        self.append(dx=v.x, dy=v.y, relative_to=relative_to)
        return self

    def label(self, label):
        assert len(self._p) > 0
        self._labels[label] = len(self._p)-1
        return self

    def reverse(self):
        self._p = list(reversed(self._p))
        self._labels = {k: len(self._p)-v for k, v in self._labels.items()}
        return self

    def splinify(self, n=20):
        spline = _bezier_spline(self._p, n=n)
        self._p = spline
        self._labels = {}
        return self

    def update_origin(self):
        last = self._p[-1]
        self.translate(-last.x, -last.y)
        return self

    def translate(self, dx=0, dy=0):
        self._p = _translate(dx, dy)(self._p)
        return self

    def rotate(self, alpha=0):
        self._p = _rotate(alpha)(self._p)
        return self

    def offset(self, offset, left):
        self._p = _thicker_path(self._p, thickness=offset, left=left)
        return self

    def cut(self, x=None, y=None):
        output = []
        current = Path(x=self._p[0].x, y=self._p[0].y)
        output.append(current)
        for i in range(len(self._p)-1):
            segment = self._p[i:i+2]
            intersections = []
            if x is not None and x >= segment[0].x and x < segment[1].x:
                intersections.append(Point(x=x, y=segment[0].y+(segment[1].y-segment[0].y)/(segment[1].x-segment[0].x)*(x-segment[0].x)))
            if y is not None and y >= segment[0].y and y < segment[1].y:
                intersections.append(Point(x=segment[0].x+(segment[1].x-segment[0].x)/(segment[1].y-segment[0].y)*(y-segment[0].y), y=y))
            for intersection in intersections:
                if current.points.last.x != intersection.x or current.points.last.y != intersection.y:
                    current.append(x=intersection.x, y=intersection.y)
                current = Path(x=intersection.x, y=intersection.y)
                output.append(current)
            current.append(x=segment[1].x, y=segment[1].y)
        return output

import unittest

class CutTestCase(unittest.TestCase):
    def _check(self, got, expected):
        got = [list(path.points) for path in got]
        self.assertEqual(got, expected)

    def _test(self, path, cut, expected):
        p = Path(x=path[0][0], y=path[0][1])
        for i in path[1:]:
            p.append(x=i[0], y=i[1])
        got = p.cut(x=cut[0], y=cut[1])
        self._check(got=got, expected=[[Point(x=x, y=y) for x,y in path] for path in expected])

    def test_no_segment(self):
        self._test(
            [(0, 0)],
            (None, None),
            [[(0, 0)]]
        )

    def test_no_segment_cutx(self):
        self._test(
            [(0, 0)],
            (1, None),
            [[(0, 0)]]
        )

    def test_no_segment_cuty(self):
        self._test(
            [(0, 0)],
            (None, 1),
            [[(0, 0)]]
        )

    def test_no_segment_cutxy(self):
        self._test(
            [(0, 0)],
            (0, 1),
            [[(0, 0)]]
        )

    def test_no_segment_cut_point(self):
        self._test(
            [(0, 0)],
            (0, None),
            [[(0, 0)]]
        )

    def test_x_no_cut(self):
        self._test(
            [(0, 0), (2, 0)],
            (3, None),
            [[(0, 0), (2, 0)]]
        )

    def test_x_cut(self):
        self._test(
            [(0, 0), (2, 0)],
            (1, None),
            [[(0, 0), (1, 0)], [(1, 0), (2, 0)]]
        )

    def test_x_cut_start(self):
        self._test(
            [(0, 0), (2, 0)],
            (0, None),
            [[(0, 0)], [(0, 0), (2, 0)]]
        )

    def test_5(self):
        self._test(
            [(0, 0), (2, 0)],
            (2, None),
            [[(0, 0), (2, 0)]]
        )

    def test_4(self):
        self._test(
            [(0, 0), (2, 0), (4, 0)],
            (2, None),
            [[(0, 0), (2, 0)], [(2, 0), (4, 0)]]
        )

    def test_3(self):
        self._test(
            [(0, 0), (2, 0), (4, 0)],
            (2.1, None),
            [[(0, 0), (2, 0), (2.1, 0)], [(2.1, 0), (4, 0)]]
        )

    def test_1(self):
        self._test(
            [(0, 0), (2, 0), (2, 4)],
            (2, None),
            [[(0, 0), (2, 0), (2, 4)]]
        )

    def test_2(self):
        self._test(
            [(0, 0), (2, 0), (2, 4), (2.1, 4)],
            (2, None),
            [[(0, 0), (2, 0), (2, 4)], [(2, 4), (2.1, 4)]]
        )

if __name__ == '__main__':
    unittest.main()

