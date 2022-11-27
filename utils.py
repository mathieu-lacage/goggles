import math

import solid
import euclid3

import constants

def ellipsis(a, b, t):
    return euclid3.Point3(a*math.cos(t), b*math.sin(t), 0)

def ring(height, delta):
    path = [ellipsis(constants.ELLIPSIS_WIDTH+delta, constants.ELLIPSIS_HEIGHT+delta, t) for t in solid.utils.frange(0, 2*math.pi, constants.NSTEPS, include_end=True)]
    o = solid.linear_extrude(height)(
        solid.polygon(path)
    )
    return o



