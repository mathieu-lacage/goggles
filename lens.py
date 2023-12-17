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
    #  -------  ----     |
    #   shell | |  | E---D
    #  -------  |  | |
    #  ---------   | |      m1
    #  skirt       | |
    #  ------------  |
    #  G-------------F      ------
    #  |               bottom
    #  H---------------------------
    #
    #  AB=constants.LENS_TOP_HEIGHT (0.5)
    #  CD=constants.LENS_GROOVE_HEIGHT (0.5)
    #  BC=DE=constants.LENS_GROOVE_DEPTH (1)
    #  EF=constants.SHELL_THICKNESS+constants.SKIRT_SQUASHED_THICKNESS
    #  GF=constants.LENS_BOTTOM_RING_WIDTH*2/3 (2*2/3)
    #  GH=constants.LENS_BOTTOM_RING_HEIGHT (1)
    #  Total height: 0.5+1+1.2+0.4+1=4 ??

    PADDING = 1
    # start at E
    shape = mg2.Path(x=-constants.SKIRT_THICKNESS+constants.LENS_HORIZONTAL_SQUASHINESS_OFFSET, y=constants.LENS_GROOVE_HEIGHT-constants.LENS_CLIP_GROOVE_HEIGHT) \
        .append(y=constants.SHELL_THICKNESS+constants.SKIRT_THICKNESS-constants.LENS_VERTICAL_SQUASHINESS_OFFSET-constants.LENS_RADIUS)\
        .extend_arc(alpha=-math.pi/2, r=constants.LENS_RADIUS)\
        .append(dx=constants.LENS_BOTTOM_RING_WIDTH-constants.LENS_RADIUS-constants.LENS_RADIUS)\
        .extend_arc(alpha=math.pi/2, r=constants.LENS_RADIUS)\
        .append(dy=constants.LENS_BOTTOM_RING_HEIGHT-constants.LENS_RADIUS-constants.LENS_RADIUS)\
        .extend_arc(alpha=math.pi/2, r=constants.LENS_RADIUS)\
        .append(dx=-constants.LENS_BOTTOM_RING_WIDTH-constants.LENS_GROOVE_DEPTH-PADDING+constants.LENS_RADIUS)\
        .append(dy=-constants.LENS_HEIGHT)\
        .append(dx=PADDING+constants.LENS_GROOVE_DEPTH)\
        .append(dy=constants.LENS_TOP_HEIGHT-constants.LENS_RADIUS)\
        .extend_arc(alpha=math.pi/2, r=constants.LENS_RADIUS)\
        .append(dx=-constants.LENS_GROOVE_DEPTH+constants.LENS_RADIUS+constants.LENS_RADIUS)\
        .extend_arc(alpha=-math.pi/2, r=constants.LENS_RADIUS)\
        .append(dy=constants.LENS_GROOVE_HEIGHT-constants.LENS_RADIUS-constants.LENS_RADIUS)\
        .extend_arc(alpha=-math.pi/2, r=constants.LENS_RADIUS)\

    path = utils.ellipsis_path_delta()
    o = ggg.extrude(list(shape.points)).along_closed_path(path).mesh().solidify()
    tmp = utils.ring(constants.LENS_HEIGHT, -(constants.SKIRT_THICKNESS+constants.LENS_GROOVE_DEPTH+PADDING/2))
    tmp = solid.translate([0, 0, -(constants.LENS_TOP_HEIGHT+constants.LENS_CLIP_GROOVE_HEIGHT)])(tmp)
    o = o + tmp
    #offset = constants.LENS_HEIGHT-(constants.LENS_TOP_HEIGHT+constants.LENS_GROOVE_HEIGHT)
    #o = solid.translate([0, 0, -offset])(o)
    #o = solid.translate([0, 0, offset-constants.SHELL_THICKNESS])(o)
    return o


def generate_lens_svg(filename, offset):
    import cairo
    width = 0.01
    spacing = constants.ELLIPSIS_WIDTH/3

    def half_lens(context, delta1, delta2):
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
        context.set_line_width(width)
        context.stroke()
        context.restore()

        context.save()
        context.save()
        context.scale(constants.ELLIPSIS_WIDTH+delta2, constants.ELLIPSIS_HEIGHT+delta2)
        context.arc(0, 0, 1, 0, 2*math.pi)
        context.restore()
        context.set_source_rgba(1, 0, 0, 1)
        context.set_line_width(width)
        context.stroke()
        context.restore()

    with cairo.SVGSurface(filename, constants.ELLIPSIS_WIDTH*6, constants.ELLIPSIS_HEIGHT*6) as surface:
        surface.set_document_unit(cairo.SVGUnit.MM)
        context = cairo.Context(surface)

        context.save()
        context.translate(constants.ELLIPSIS_WIDTH*3+spacing*2, constants.ELLIPSIS_HEIGHT+spacing)
        half_lens(
            context,
            -constants.SKIRT_THICKNESS+constants.LENS_BOTTOM_RING_WIDTH+offset,
            -constants.SKIRT_THICKNESS+offset,
        )
        context.restore()


def lens_clip(offset):
    #
    # D-----O-----------B
    # |                 /
    # E-----F          /
    #       |        /
    #       |      /
    #       A----/
    #
    groove_depth = constants.LENS_GROOVE_DEPTH*0.9
    groove_height = constants.LENS_CLIP_GROOVE_HEIGHT+offset
    ABx = constants.SHELL_MIN_WIDTH
    ABy = constants.LENS_TOP_HEIGHT+groove_height
    # start at A
    shape = mg2.Path(x=-(constants.SKIRT_THICKNESS-constants.LENS_HORIZONTAL_SQUASHINESS_OFFSET), y=-ABy)\
        .append(dx=ABx/2)\
        .append(dx=ABx/2, dy=ABy)\
        .splinify()\
        .append(dx=-ABx-groove_depth+constants.LENS_RADIUS)\
        .extend_arc(alpha=math.pi/2, r=constants.LENS_RADIUS)\
        .append(dy=-(groove_height-constants.LENS_RADIUS-constants.LENS_RADIUS))\
        .extend_arc(alpha=math.pi/2, r=constants.LENS_RADIUS)\
        .append(dx=groove_depth-constants.LENS_RADIUS)
    path = utils.ellipsis_path_delta(0)
    a = ggg.extrude(list(shape.points)).along_closed_path(path).mesh().solidify()
    a = solid.translate([0, 0, offset])(a)

    alpha = math.pi/10
    c = solid.cube([200, 200, 200], center=True)
    c = solid.translate([0, 100, 0])(c)
    d = solid.rotate([0, 0, 360*alpha/2/(2*math.pi)])(c)
    e = solid.rotate([0, 0, -360*alpha/2/(2*math.pi)])(c)
    e = solid.scale([1, 1, 1.01])(e)
    f = d - e
    o = a - f
    #o = solid.mirror([1, 0, 0])(o)
    #o = solid.translate([0, 0, -constants.LENS_GROOVE_HEIGHT-constants.LENS_TOP_HEIGHT])(o)
    return o


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--resolution', default=40, type=int)
    parser.add_argument('--slice-x', default=None, type=float)
    parser.add_argument('--slice-y', default=None, type=float)
    parser.add_argument('--slice-z', default=None, type=float)
    parser.add_argument('--slice-a', default=None, type=float)
    parser.add_argument('--offset', default=0, type=float)
    args = parser.parse_args()

    constants.NSTEPS = args.resolution
    l = lens()
    lc = lens_clip(args.offset)

    assembly = l + lc

    if args.slice_a is not None or args.slice_x is not None or args.slice_y is not None or args.slice_z is not None:
        cut = utils.slice(args)
        lc = lc - cut
        l = l - cut
        assembly = assembly - cut
    solid.scad_render_to_file(lc, 'lens-clip.scad')
    solid.scad_render_to_file(l, 'lens.scad')
    solid.scad_render_to_file(assembly, 'lens-assembly.scad')

    generate_lens_svg('lens.svg', constants.SKIRT_THICKNESS-constants.SKIRT_SQUASHED_THICKNESS)


#def main():
#    for o in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
#        generate_lens_svg('lens-%f.svg' % o, o)


if __name__ == '__main__':
    main()
