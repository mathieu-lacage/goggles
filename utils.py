import math
import subprocess

import solid
import euclid3

import constants

def eu3(path):
    if len(path) == 0:
        return []
    return [euclid3.Point3(p.x, p.y, 0) for p in path]

def ellipsis(a, b, t):
    return euclid3.Point3(a*math.cos(t), b*math.sin(t), 0)

def ring(height, delta):
    path = [ellipsis(constants.ELLIPSIS_WIDTH+delta, constants.ELLIPSIS_HEIGHT+delta, t) for t in solid.utils.frange(0, 2*math.pi, constants.NSTEPS, include_end=True)]
    o = solid.linear_extrude(height)(
        solid.polygon(path)
    )
    return o


def export(name, type):
    import subprocess
    import os
    try:
        os.mkdir('%s-%s' % (type, args.resolution))
    except:
        pass
    subprocess.check_output(['/usr/bin/openscad', '-o', '%s-%s/%s.%s' % (type, constants.NSTEPS, name, type), '%s.scad' % name])


