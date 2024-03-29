#!/usr/bin/python
import math

import solid
import solid.utils

import utils
import mg2
import ggg
import constants


def lens():
    #
    #                A------------------
    #                |      top
    #                B---C  ----
    #                    |  m2
    #  -------  ---- E---D  -----
    #   shell | |  | |
    #  -------  |  | |
    #  ---------   | |      m1
    #  skirt       | |
    #  ------------  |
    #  G-------------F      ------
    #  |               bottom
    #  H---------------------------
    #
    #  AB=constants.LENS_TOP_HEIGHT (1)
    #  CD=constants.LENS_GROOVE_HEIGHT (1)
    #  BC=DE=constants.LENS_GROOVE_DEPTH (1)
    #  EF=constants.SHELL_THICKNESS+constants.SKIRT_SQUASHED_THICKNESS
    #  GF=constants.LENS_BOTTOM_RING_WIDTH*2/3 (2*2/3)
    #  GH=constants.LENS_BOTTOM_RING_HEIGHT (1)
    #  Total height: 1+1+1.2+0.4+1=4.6 ??

    PADDING = 1
    # start at E
    shape = mg2.Path(x=-constants.SKIRT_THICKNESS, y=0) \
        .append(dy=constants.SHELL_THICKNESS+constants.SKIRT_THICKNESS)\
        .append(dx=constants.LENS_BOTTOM_RING_WIDTH)\
        .append(dy=constants.LENS_BOTTOM_RING_HEIGHT)\
        .append(dx=-constants.LENS_BOTTOM_RING_WIDTH-constants.LENS_GROOVE_DEPTH-PADDING)\
        .append(dy=-constants.LENS_HEIGHT)\
        .append(dx=PADDING+constants.LENS_GROOVE_DEPTH)\
        .append(dy=constants.LENS_TOP_HEIGHT)\
        .append(dx=-constants.LENS_GROOVE_DEPTH)\
        .append(dy=constants.LENS_GROOVE_HEIGHT)

    path = utils.ellipsis_path()
    o = ggg.extrude(list(shape.points)).along_closed_path(path).mesh().solidify()
    epsilon = 0
    tmp = utils.ring(constants.LENS_HEIGHT+epsilon*2, -(constants.SKIRT_THICKNESS+constants.LENS_GROOVE_DEPTH+PADDING)+0.3)
    tmp = solid.translate([0, 0, -(constants.LENS_TOP_HEIGHT+constants.LENS_GROOVE_HEIGHT)-epsilon])(tmp)
    o = o + tmp
    offset = constants.LENS_HEIGHT-(constants.LENS_TOP_HEIGHT+constants.LENS_GROOVE_HEIGHT)
    o = solid.translate([0, 0, -offset])(o)
    o = solid.translate([0, 0, offset-constants.SHELL_THICKNESS])(o)
    return o


def generate_lens_svg():
    import cairo
    kerf = 0.1
    laser = 0.01
    spacing = constants.ELLIPSIS_WIDTH/3

    def half_lens(context, delta1, delta2, depth):
        context.save()
        context.translate(-constants.ELLIPSIS_WIDTH, -constants.ELLIPSIS_HEIGHT)
        context.arc(0, 0, 0.5, 0, 2*math.pi)
        context.set_source_rgba(0.5, 0.5, 0.5, 1)
        context.fill()
        context.restore()

        context.save()
        context.save()
        context.scale(constants.ELLIPSIS_WIDTH+delta1, constants.ELLIPSIS_HEIGHT+delta1)
        context.arc(0, 0, 1, 0, 2*math.pi)
        context.restore()
        context.set_source_rgba(1, 0, 0, 1)
        context.set_line_width(laser)
        context.stroke()
        context.restore()

        context.save()
        context.save()
        context.scale(constants.ELLIPSIS_WIDTH+delta2, constants.ELLIPSIS_HEIGHT+delta2)
        context.arc(0, 0, 1, 0, 2*math.pi)
        context.restore()
        context.set_source_rgba(1, 0, 0, 1)
        context.set_line_width(laser)
        context.stroke()
        context.restore()

        context.save()
        context.translate(-constants.ELLIPSIS_WIDTH/2, 0)
        context.set_source_rgb(0, 0, 1)
        context.set_font_size(2)
        context.show_text("depth cut=%.02fmm" % depth)
        context.restore()

    with cairo.SVGSurface("lens.svg", constants.ELLIPSIS_WIDTH*6, constants.ELLIPSIS_HEIGHT*6) as surface:
        surface.set_document_unit(cairo.SVGUnit.MM)
        context = cairo.Context(surface)

        context.save()
        context.translate(constants.ELLIPSIS_WIDTH*3+spacing*2, constants.ELLIPSIS_HEIGHT+spacing)
        half_lens(
            context,
            -constants.SKIRT_THICKNESS+constants.LENS_BOTTOM_RING_WIDTH,
            -constants.SKIRT_THICKNESS,
            constants.LENS_HEIGHT-constants.LENS_BOTTOM_RING_HEIGHT
        )
        context.restore()


def lens_clip(height, width, alpha):
    deltay = constants.LENS_GROOVE_HEIGHT+constants.LENS_TOP_HEIGHT
    deltax = constants.SHELL_MIN_WIDTH+constants.SKIRT_THICKNESS
    shape = mg2.Path(x=constants.SHELL_MIN_WIDTH, y=0)\
        .append(dy=-(deltay), dx=-deltax/2)\
        .append(dx=-(deltax/2))\
        .splinify()\
        .append(dy=constants.LENS_TOP_HEIGHT)\
        .append(dx=-constants.LENS_GROOVE_DEPTH)\
        .append(dy=constants.LENS_GROOVE_HEIGHT)
    path = utils.ellipsis_path()
    a = ggg.extrude(list(shape.reversed_points)).along_closed_path(path).mesh().solidify()
    a = solid.translate([0, 0, constants.LENS_TOP_HEIGHT])(a)

    c = solid.cube([200, 200, 200], center=True)
    c = solid.translate([0, 100, 0])(c)
    d = solid.rotate([0, 0, 360*alpha/2/(2*math.pi)])(c)
    e = solid.rotate([0, 0, -360*alpha/2/(2*math.pi)])(c)
    e = solid.scale([1, 1, 1.01])(e)
    f = d - e
    o = a - f
    o = solid.mirror([1, 0, 0])(o)
    o = solid.translate([0, 0, -height-constants.SHELL_THICKNESS])(o)
    return o


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--resolution', default=40, type=int)
    parser.add_argument('--slice-x', default=None, type=float)
    parser.add_argument('--slice-y', default=None, type=float)
    parser.add_argument('--slice-z', default=None, type=float)
    parser.add_argument('--slice-a', default=None, type=float)
    args = parser.parse_args()

    constants.NSTEPS = args.resolution
    l = lens()
    lc = lens_clip(constants.LENS_GROOVE_HEIGHT, 2, math.pi/100)

    assembly = l + lc

    if args.slice_a is not None or args.slice_x is not None or args.slice_y is not None or args.slice_z is not None:
        cut = utils.slice(args)
        lc = lc - cut
        l = l - cut
        assembly = assembly - cut
    solid.scad_render_to_file(lc, 'lens-clip.scad')
    solid.scad_render_to_file(l, 'lens.scad')
    solid.scad_render_to_file(assembly, 'lens-assembly.scad')

    generate_lens_svg()


if __name__ == '__main__':
    main()
