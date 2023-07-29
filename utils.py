import math

import solid
import euclid3

import constants
import ggg
import mg2


def eu3(path):
    if len(path) == 0:
        return []
    return [euclid3.Point3(p.x, p.y, 0) for p in path]


def ellipsis(a, b, t):
    return euclid3.Point3(a*math.cos(t), b*math.sin(t), 0)


def ellipsis_path(a, b):
    path = [ellipsis(a, b, t) for t in solid.utils.frange(0, 2*math.pi, constants.NSTEPS, include_end=False)]
    return path


def ellipsis_path_delta(delta=0):
    return ellipsis_path(a=constants.ELLIPSIS_WIDTH+delta, b=constants.ELLIPSIS_HEIGHT+delta)


def ring(height, delta):
    path = [ellipsis(constants.ELLIPSIS_WIDTH+delta, constants.ELLIPSIS_HEIGHT+delta, t) for t in solid.utils.frange(-math.pi, math.pi, constants.NSTEPS+1, include_end=True)]
    o = ggg.extrude(path).along_z(height).mesh().solidify()
    return o


def slice(args):
    if args.slice_a is not None:
        cut = solid.rotate([0, 0, args.slice_a])(solid.translate([-0, 0, -100])(solid.cube([200, 200, 200])))
    else:
        cut = solid.cube([0, 0, 0])
    if args.slice_x is not None:
        cut = cut + solid.translate([args.slice_x, -50, -100])(solid.cube([200, 200, 200]))
    if args.slice_y is not None:
        cut = cut + solid.translate([-100, args.slice_y, -100])(solid.cube([200, 200, 200]))
    if args.slice_z is not None:
        cut = cut + solid.translate([-100, -50, args.slice_z])(solid.cube([200, 200, 200]))
    return cut


def distance(alpha, threshold=0.5):
    d = alpha/threshold if alpha < threshold else (1-alpha)/(1-threshold)
    d = 1-(1-d)**2
    return d


def fwidth(alpha):
    d = distance(alpha)
    width = constants.SHELL_MIN_WIDTH+constants.SHELL_MAX_WIDTH*d**7
    return width


def fheight(alpha):
    d = distance(alpha)
    height = constants.SHELL_MIN_HEIGHT+constants.SHELL_MAX_HEIGHT*d**15
    return height


def shell_curve(alpha):
    width = fwidth(alpha)
    height = fheight(alpha)
    path = mg2.Path(x=0, y=0)\
        .append(dx=width*constants.XALPHA, dy=height*constants.YALPHA)\
        .append(dx=width*(1-constants.XALPHA), dy=height*(1-constants.YALPHA))
    return path


def rounded_square(x, y, height, radius, adjust=False):
    if adjust:
        x = x - 2*radius
        y = y - 2*radius
    r = solid.cylinder(radius, height, segments=40)
    o = solid.hull()(
        solid.translate([-x/2, -y/2, 0])(r),
        solid.translate([x/2, -y/2, 0])(r),
        solid.translate([-x/2, y/2, 0])(r),
        solid.translate([x/2, y/2, 0])(r),
    )
    return o


