#!/usr/bin/python
import math

import solid
import solid.utils

import ggg
import utils
import constants

MATERIAL_PMMA = 'pmma'
MATERIAL_PC = 'pc'


def diopters_to_radius(diopters, material):
    assert diopters <= 4
    if material == MATERIAL_PMMA:
        n2 = 1.49
    elif material == MATERIAL_PC:
        n2 = 1.56
    else:
        assert False
    n1 = 1  # air
    # lens maker equation applied to a plano-concave lens
    R1 = (n2/n1 - 1) / diopters
    # convert meters to millimeters
    R1 = R1*1000
    return R1


def circle_patch(r, n):
    path = [ggg.Point3(r*math.cos(t), r*math.sin(t), 0) for t in solid.utils.frange(19*math.pi/20, 21*math.pi/20, n, include_end=False)]
    return path


def myopia_correction(diopters, material, x_offset=0, y_offset=0):
    if diopters is None:
        return None
    r = diopters_to_radius(diopters, material)
    c = circle_patch(r, 100)
    o = ggg.extrude(c).around_z_partially(100, -math.pi/20, math.pi/20).mesh().solidify()
    o = solid.translate([r, 0, 0])(o)
    o = solid.rotate([0, -90, 0])(o)
#    o = solid.debug(o)
    half_width = max(constants.ELLIPSIS_WIDTH + math.fabs(x_offset), constants.ELLIPSIS_HEIGHT + math.fabs(y_offset)) - constants.SKIRT_THICKNESS
    delta = r-math.sqrt(r**2-half_width**2)
    o = solid.translate([x_offset, y_offset, -delta])(o)
    return o


def torus(r1, r2, n=constants.NSTEPS):
    c1 = circle_patch(r1, n)
    c2 = circle_patch(r2, n)
    o = ggg.extrude(list(reversed(c1))).along_open_path(c2).mesh().solidify()
    return o


def astigmatism_correction(d1, d2, d2_angle, material, x_offset=0, y_offset=0):
    if d2 is None:
        return myopia_correction(d1, material, x_offset=x_offset, y_offset=y_offset)
    r1 = diopters_to_radius(d1, material)
    r2 = diopters_to_radius(d2, material)
    r1, r2 = (r1, r2) if r1 > r2 else (r2, r1)
    o = torus(r1, r1-r2, n=100)
    o = solid.translate([-r2, 0, 0])(o)
    o = solid.rotate([0, 90, 0])(o)
    o = solid.rotate([0, 0, d2_angle])(o)
    half_width1 = max(constants.ELLIPSIS_WIDTH + math.fabs(x_offset), constants.ELLIPSIS_HEIGHT + math.fabs(y_offset)) - constants.SKIRT_THICKNESS
    half_width2 = max(constants.ELLIPSIS_WIDTH + math.fabs(x_offset), constants.ELLIPSIS_HEIGHT + math.fabs(y_offset)) - constants.SKIRT_THICKNESS
    delta1 = r1-math.sqrt(r1**2-half_width1**2)
    delta2 = r2-math.sqrt(r2**2-half_width2**2)
    delta = min(delta1, delta2)
    o = solid.translate([x_offset, y_offset, -delta])(o)
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
    parser.add_argument('-o', '--output', default=None)
    parser.add_argument('--slice-x', default=None, type=float)
    parser.add_argument('--slice-y', default=None, type=float)
    parser.add_argument('--slice-z', default=None, type=float)
    parser.add_argument('--slice-a', default=None, type=float)
    parser.add_argument('--myopia-diopters', default=None, type=float)
    parser.add_argument('--astigmatism-diopters', default=None, type=float)
    parser.add_argument('--astigmatism-angle', default=None, type=float)
    parser.add_argument('--x-offset', default=0, type=float)
    parser.add_argument('--y-offset', default=0, type=float)
    parser.add_argument('--material', default=MATERIAL_PMMA, choices=[MATERIAL_PMMA, MATERIAL_PC])
    args = parser.parse_args()

    constants.NSTEPS = args.resolution
    correction = astigmatism_correction(
        d1=args.myopia_diopters,
        d2=args.astigmatism_diopters,
        d2_angle=args.astigmatism_angle,
        material=args.material,
        x_offset=args.x_offset,
        y_offset=args.y_offset
    )
    lens = lens_cnc(correction=correction)

    if args.slice_a is not None or args.slice_x is not None or args.slice_y is not None or args.slice_z is not None:
        cut = utils.slice(args)
        lens = lens - cut
    scad_filename = 'lens-cnc' if args.output is None else args.output
    solid.scad_render_to_file(lens, '%s.scad' % scad_filename)


if __name__ == '__main__':
    main()
