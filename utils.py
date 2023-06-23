import math

import solid
import euclid3

import constants
import ggg


def eu3(path):
    if len(path) == 0:
        return []
    return [euclid3.Point3(p.x, p.y, 0) for p in path]


def ellipsis(a, b, t):
    return euclid3.Point3(a*math.cos(t), b*math.sin(t), 0)


def ellipsis_path(delta=0):
    path = [ellipsis(constants.ELLIPSIS_WIDTH+delta, constants.ELLIPSIS_HEIGHT+delta, t) for t in solid.utils.frange(0, 2*math.pi, constants.NSTEPS, include_end=False)]
    return path


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
