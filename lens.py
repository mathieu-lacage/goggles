#!/usr/bin/python
import math

import solid
import solid.utils

from extrude_along_path import extrude_along_path
import mg2
import utils
import constants

def lens_top(delta=0):
    epsilon = 0.01
    m2 = utils.ring(constants.LENS_GROOVE_HEIGHT+epsilon*2, -constants.LENS_GROOVE_DEPTH-constants.SKIRT_THICKNESS+delta)
    top = utils.ring(constants.LENS_TOP_HEIGHT, -constants.SKIRT_THICKNESS+delta)

    l = solid.translate([0, 0, 0])(m2) + \
        solid.translate([0, 0, constants.LENS_GROOVE_HEIGHT])(top)

    l = solid.mirror([0, 0, 1])(l)
    l = solid.translate([0, 0, 0])(l)
    l = solid.color("grey", 0.7)(l)
    return l

def lens_bottom(delta=0):
#    print(2*(constants.ELLIPSIS_WIDTH-constants.SKIRT_THICKNESS), 2*(constants.ELLIPSIS_HEIGHT-constants.SKIRT_THICKNESS))
    epsilon = 0.01
    bottom = utils.ring(constants.LENS_BOTTOM_RING_HEIGHT, constants.LENS_BOTTOM_RING_WIDTH*2/3)
    m1 = utils.ring(constants.SHELL_THICKNESS+constants.SKIRT_SQUASHED_THICKNESS+epsilon, -constants.SKIRT_THICKNESS+delta)
    l = bottom + \
        solid.translate([0, 0, constants.LENS_BOTTOM_RING_HEIGHT-epsilon])(m1)
    

    l = solid.mirror([0, 0, 1])(l)
    l = solid.translate([0, 0, 0])(l)
    l = solid.color("grey", 0.7)(l)
    return l

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

    bot = lens_bottom()
    top = lens_top()

    l = bot
    l = l + solid.translate([0, 0, -(constants.LENS_BOTTOM_RING_HEIGHT+constants.SHELL_THICKNESS+constants.SKIRT_SQUASHED_THICKNESS)])(top)
    l = solid.translate([0, 0, constants.LENS_BOTTOM_RING_HEIGHT+constants.SKIRT_SQUASHED_THICKNESS])(l)
    return l



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
        context.scale(constants.ELLIPSIS_WIDTH+delta1, constants.ELLIPSIS_HEIGHT+delta1)
        context.arc(0, 0, 1, 0, 2*math.pi)
        context.set_source_rgba(0.5, 0.5, 0.5, 1)
        context.fill()
        context.restore()

        context.save()
        context.save()
        context.scale(constants.ELLIPSIS_WIDTH+delta1+kerf/2, constants.ELLIPSIS_HEIGHT+delta1+kerf/2)
        context.arc(0, 0, 1, 0, 2*math.pi)
        context.restore()
        context.set_source_rgba(1, 0, 0, 1)
        context.set_line_width(laser)
        context.stroke()
        context.restore()

        context.save()
        context.scale(constants.ELLIPSIS_WIDTH+delta2, constants.ELLIPSIS_HEIGHT+delta2)
        context.arc(0, 0, 1, 0, 2*math.pi)
        context.set_source_rgba(1, 1, 1, 1)
        context.fill()
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
        context.translate(constants.ELLIPSIS_WIDTH+spacing, constants.ELLIPSIS_HEIGHT+spacing)
        half_lens(context, 0, -constants.LENS_GROOVE_DEPTH, constants.LENS_GROOVE_HEIGHT)
        context.restore()

        context.save()
        context.translate(constants.ELLIPSIS_WIDTH*3+spacing*2, constants.ELLIPSIS_HEIGHT+spacing)
        half_lens(context, constants.LENS_BOTTOM_RING_WIDTH*2/3, 0, constants.SHELL_THICKNESS+constants.SKIRT_SQUASHED_THICKNESS)
        context.restore()



def lens_alignment():
    bottom_width = constants.LENS_BOTTOM_RING_WIDTH*2/3
    profile = mg2.Path(x=bottom_width, y=0)\
        .label("start") \
        .append(dy=constants.LENS_BOTTOM_RING_HEIGHT)\
        .append(dx=-bottom_width, dy=constants.SHELL_THICKNESS+constants.SKIRT_SQUASHED_THICKNESS+constants.LENS_GROOVE_HEIGHT)\
        .append(dy=constants.LENS_TOP_HEIGHT)\
        .append(dx=bottom_width+1)\
        .append(dy=0, dx=1, relative_to="start")
    path = [utils.ellipsis(constants.ELLIPSIS_WIDTH, constants.ELLIPSIS_HEIGHT, t) for t in solid.utils.frange(2*math.pi/constants.NSTEPS, 2*math.pi, constants.NSTEPS, include_end=False)]
    o = extrude_along_path(utils.eu3(profile.reversed_points), path, connect_ends=True)
    return o


def lens_clip(height, thickness, alpha):
    a = utils.ring(height, thickness)
    b = utils.ring(height+2, -constants.LENS_GROOVE_DEPTH)
    b = solid.translate([0, 0, -1])(b)
    c = solid.cube([200, 200, 200], center=True)
    c = solid.translate([0, 100, 0])(c)
    d = solid.rotate([0, 0, 360*alpha/2/(2*math.pi)])(c)
    e = solid.rotate([0, 0, -360*alpha/2/(2*math.pi)])(c)
    f = d - e
    o = a - b - f
    o = solid.mirror([1, 0, 0])(o)
    o = solid.translate([0, 0, -height-constants.SHELL_THICKNESS])(o)
    return o


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--resolution', default=40, type=int)
    parser.add_argument('-e', '--export', action='store_true')
    parser.add_argument('--slice-h', default=None, type=float)
    parser.add_argument('--slice-v', default=None, type=float)
    args = parser.parse_args()

    constants.NSTEPS = args.resolution
    l = lens()
    ltop = lens_top()
    lbot = lens_bottom()
    la = lens_alignment()
    lc = lens_clip(constants.LENS_GROOVE_HEIGHT, 3, math.pi/4)

    if args.slice_v is not None or args.slice_h is not None:
        if args.slice_v is not None:
            cut = solid.rotate([0,0,args.slice_v])(solid.translate([-100,0,-100])(solid.cube([200,200,200])))
        else:
            cut = solid.cube([0,0,0])
        if args.slice_h is not None:
            cut = cut + solid.translate([-100,-50,args.slice_h])(solid.cube([200,200,200]))
        lc = lc - cut
        ltop = ltop - cut
        lbot = lbot - cut
        l = l - cut
        la = la - cut
    solid.scad_render_to_file(lc, 'lens-clip.scad')
    solid.scad_render_to_file(l, 'lens.scad')
    solid.scad_render_to_file(ltop, 'lens-top.scad')
    solid.scad_render_to_file(lbot, 'lens-bot.scad')
    solid.scad_render_to_file(la, 'lens-alignment.scad')

    if args.export:
        export('lens', 'stl')
        export('lens-top', 'stl')
        export('lens-bot', 'stl')
        export('lens-clip', 'stl')
        export('lens-alignment', 'stl')

    generate_lens_svg()

if __name__ == '__main__':
    main()

