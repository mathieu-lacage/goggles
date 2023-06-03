#!/usr/bin/python
import math

import solid
import solid.utils

import utils
import constants


def myopia_correction(diopters, x_offset=0, y_offset=0):
    if diopters is None:
        return None
    assert diopters <= 4
    n2 = 1.49 # PMMA
    n1 = 1 # air
    # lens maker equation applied to a plano-concave lens
    R1 = (n2/n1 - 1) / diopters
    # convert meters to millimeters
    R1 = R1*1000

    half_width = max(constants.ELLIPSIS_WIDTH + math.fabs(x_offset), constants.ELLIPSIS_HEIGHT + math.fabs(y_offset)) - constants.SKIRT_THICKNESS
    delta = math.sqrt(R1**2-half_width**2)
    o = solid.sphere(r=R1, segments=500)
    o = solid.translate([x_offset, y_offset, delta])(o)
    #o = solid.debug(o)
    return o


def lens_cnc(correction=None):
    o = solid.cube([constants.ELLIPSIS_WIDTH*2, constants.ELLIPSIS_HEIGHT*2, constants.LENS_HEIGHT], center=True)
    o = solid.translate([0, 0, -constants.LENS_HEIGHT/2])(o)
    if correction is not None:
        tmp = utils.ring(100, -constants.LENS_BOTTOM_RING_WIDTH)
        tmp = solid.translate([0, 0, -50])(tmp)
        x = solid.intersection()([tmp, correction])
        o = o - x
    return o


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--resolution', default=40, type=int)
    parser.add_argument('-e', '--export', action='store_true')
    parser.add_argument('--slice-x', default=None, type=float)
    parser.add_argument('--slice-y', default=None, type=float)
    parser.add_argument('--slice-z', default=None, type=float)
    parser.add_argument('--slice-a', default=None, type=float)
    parser.add_argument('--diopters', default=None, type=float)
    parser.add_argument('--x-offset', default=0, type=float)
    parser.add_argument('--y-offset', default=0, type=float)
    args = parser.parse_args()

    constants.NSTEPS = args.resolution
    correction = myopia_correction(diopters=args.diopters, x_offset=args.x_offset, y_offset=args.y_offset)
    l = lens_cnc(correction=correction)

    if args.slice_a is not None or args.slice_x is not None or args.slice_y is not None or args.slice_z is not None:
        cut = utils.slice(args)
        l = l - cut
    solid.scad_render_to_file(l, 'lens-cnc.scad')

    if args.export:
        utils.export('lens-cnc', 'stl', args.resolution)


if __name__ == '__main__':
    main()
