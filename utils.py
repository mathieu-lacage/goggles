import math
import subprocess

import solid
import euclid3

import constants
import mg2
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
#    path = ellipsis_path(delta=delta)
#    shape = mg2.Path(x=0, y=0)\
#        .append(dx=-1)\
#        .append(dy=height)\
#        .append(dx=1)
#    o = ggg.extrude(list(shape.points)).along_closed_path(path).mesh().solidify()
#    o = solid.hull()(o)
    path = [ellipsis(constants.ELLIPSIS_WIDTH+delta, constants.ELLIPSIS_HEIGHT+delta, t) for t in solid.utils.frange(-math.pi, math.pi, constants.NSTEPS+1, include_end=True)]
#    print(path)
#    o = ggg.extrude(path).linear(height).mesh().solidify()
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


