#!/usr/bin/python
import math

import solid
import solid.utils


import utils
import constants
import mg2
import ggg


def fheight_short(alpha):
    d = utils.distance(alpha)
    height = constants.SHELL_MIN_HEIGHT+constants.SHELL_MAX_HEIGHT*d**25
    return height


def shell_curve_cut(alpha):
    LENGTH = 20
    curve = utils.shell_curve(alpha).splinify(n=LENGTH)
    cuts = curve.cut(y=fheight_short(alpha))
    curve = cuts[0].resample(LENGTH)
    path = mg2.Path(path=curve)
    return path


def top_hole1():
    r1 = 0.8
    r2 = 3*r1
    h = 9
    shapes = [
        utils.ellipsis_path(r1, r1),
        utils.ellipsis_path(r1, r2),
    ]
    o = ggg.extrude(shapes).along_z(h).mesh().solidify()
    return o


def top_hole2():
    r1 = constants.SHELL_THICKNESS
    r2 = r1
    h = 9
    shapes = [
        utils.ellipsis_path(r1, r1),
        utils.ellipsis_path(r1, r2),
    ]
    o = ggg.extrude(shapes).along_z(h).mesh().solidify()
    return o


def shell(top_hole):
    TOP_ATTACHMENT_RESOLUTION = 40
    BOTTOM_ATTACHMENT_RESOLUTION = 40

    def profile(i, n):
        alpha = i/n
        curve = shell_curve_cut(alpha)

        path = mg2.Path(path=curve)\
            .translate(dx=constants.SHELL_TOP_X)
        return_path = path.copy().reverse()\
            .offset(constants.SHELL_THICKNESS, left=True)
        path.extend_arc(alpha=-math.pi, r=constants.SHELL_THICKNESS/2)\
            .extend(path=return_path)\
            .append(x=constants.SHELL_TOP_X, y=constants.SHELL_TOP_Y)\
            .append(x=0)\
            .append(dy=constants.SHELL_THICKNESS-constants.SKIRT_THICKNESS/2)\
            .extend_arc(alpha=-math.pi/2, r=constants.SKIRT_THICKNESS/2)
        return utils.eu3(path.reversed_points)

    def top_attachment_profile(i, n):
        attachment_alpha = i/(n-1)
        if attachment_alpha > 0.5:
            shell_alpha = 2*constants.TOP_ATTACHMENT_WIDTH*(attachment_alpha-0.5)
            alpha = (attachment_alpha - 0.5)/0.5
        else:
            shell_alpha = 1-constants.TOP_ATTACHMENT_WIDTH+2*constants.TOP_ATTACHMENT_WIDTH*attachment_alpha
            alpha = (0.5-attachment_alpha)/0.5
        curve = shell_curve_cut(shell_alpha)
        top = max(2*constants.UNIT/3*(1-alpha**4), constants.SHELL_THICKNESS)
        tooth_width = constants.TOOTH_WIDTH*(1-alpha**4)
        epsilon = 0.1

        p1 = mg2.Path(x=constants.SHELL_TOP_X+curve.width+constants.SHELL_THICKNESS-epsilon, y=curve.height)\
            .append(dx=tooth_width, y=-top/2)\
            .append(y=-top)\
            .splinify(n=4)\
            .append(dx=-tooth_width)\
            .append(dx=-curve.width/2, y=-constants.SHELL_THICKNESS)\
            .append(dx=-curve.width/2-constants.SHELL_THICKNESS-epsilon)\
            .append(dy=constants.SHELL_THICKNESS-epsilon)\
            .append(dx=curve.width-epsilon)
        return utils.eu3(p1.reversed_points)

    path1 = utils.ellipsis_path_delta()
    shapes1 = [profile(i, len(path1)) for i in range(len(path1))]
    o = ggg.extrude(shapes1).along_closed_path(path1).mesh().solidify()
#    o = solid.debug(o)

    path2 = [utils.ellipsis(constants.ELLIPSIS_WIDTH, constants.ELLIPSIS_HEIGHT, t) for t in solid.utils.frange(-constants.TOP_ATTACHMENT_WIDTH*2*math.pi, constants.TOP_ATTACHMENT_WIDTH*2*math.pi, TOP_ATTACHMENT_RESOLUTION, include_end=True)]
    shapes2 = [top_attachment_profile(i, len(path2)) for i in range(len(path2))]
    top_attachment = ggg.extrude(shapes2).along_open_path(path2).mesh().solidify()
    th = top_hole()
    th = solid.translate([constants.ELLIPSIS_WIDTH+shell_curve_cut(0).width+constants.SHELL_TOP_X+constants.SHELL_THICKNESS+constants.TOOTH_WIDTH/2-0.2, 0, -5.5])(th)
    top_attachment = top_attachment - th
    o = o + top_attachment

    BOTTOM_ATTACHMENT_HEIGHT = 2

    def bottom_attachment_profile(i, n):
        attachment_alpha = i / n
        if attachment_alpha > 0.5:
            shell_alpha = 0.5+2*constants.BOTTOM_ATTACHMENT_WIDTH*(attachment_alpha-0.5)
        else:
            shell_alpha = 0.5-2*constants.BOTTOM_ATTACHMENT_WIDTH*(0.5-attachment_alpha)
        curve = shell_curve_cut(shell_alpha)
        handle_width = constants.SHELL_THICKNESS*4*utils.distance(attachment_alpha)**2
        handle_height = BOTTOM_ATTACHMENT_HEIGHT
        xalpha = constants.XALPHA
        yalpha = constants.YALPHA
        epsilon = 0.4
        cuts = curve.cut(y=constants.SHELL_MAX_HEIGHT-handle_height)
        delta_x = cuts[1].width
        delta_y = cuts[1].height
        path = mg2.Path(x=cuts[1].points.first.x+constants.LENS_BOTTOM_RING_WIDTH+constants.SHELL_THICKNESS-epsilon, y=cuts[1].points.first.y)\
            .append(dx=delta_x, dy=delta_y)\
            .append(dx=handle_width)\
            .extend(mg2.Path(x=0, y=0)
                    .append(dx=-(1-xalpha)*(delta_x+handle_width)*3/4, dy=-(1-yalpha)*delta_y)
                    .append(dx=-(xalpha)*(delta_x+handle_width)*3/4, dy=-(yalpha)*delta_y)
                    .splinify())
        return utils.eu3(path.reversed_points)

    path3 = [utils.ellipsis(constants.ELLIPSIS_WIDTH, constants.ELLIPSIS_HEIGHT, t) for t in solid.utils.frange(math.pi-constants.BOTTOM_ATTACHMENT_WIDTH*2*math.pi, math.pi+constants.BOTTOM_ATTACHMENT_WIDTH*2*math.pi, BOTTOM_ATTACHMENT_RESOLUTION)]
    shapes3 = [bottom_attachment_profile(i, len(path3)) for i in range(len(path3))]
    bottom_attachment = ggg.extrude(shapes3).along_open_path(path3).mesh().solidify()

    bah = utils.rounded_square(constants.SHELL_BOTTOM_HOLE_HEIGHT, constants.SHELL_BOTTOM_HOLE_WIDTH, 20, constants.SHELL_THICKNESS/2)
    c = shell_curve_cut(0.5)
    bah1 = solid.translate([-constants.ELLIPSIS_WIDTH-c.width-constants.SHELL_TOP_X-constants.SHELL_THICKNESS/2, 0, c.height-10])(bah)
    bottom_attachment = bottom_attachment - bah1
    bah2 = solid.translate([-constants.ELLIPSIS_WIDTH-c.width-constants.SHELL_TOP_X-constants.SHELL_THICKNESS - 10, 0, c.height-BOTTOM_ATTACHMENT_HEIGHT-constants.SHELL_BOTTOM_HOLE_WIDTH/2])(
        solid.rotate([0, 90, 0])(bah)
    )
    bottom_attachment = bottom_attachment - bah2
    o = o + bottom_attachment

    # water filling holes
    for y in [1, -1]:
        o = o - solid.translate([-constants.ELLIPSIS_WIDTH-constants.SHELL_MAX_WIDTH/2, y*1.2*constants.UNIT, -50])(
            solid.scale([2, 1, 1])(
                solid.cylinder(1.5*constants.UNIT/7, 100, segments=30)
            )
        )

    # flip for final rendering
    o = solid.mirror([0, 1, 0])(o)
#    o = solid.translate([0.05, 0, -0.05])(o)
#    c = solid.cube([15, 15, 15], center=True)
#    c = solid.translate([20, 0, 0])(c)
#    o = solid.intersection()([o, c])

    return o


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--resolution', default=40, type=int)
    parser.add_argument('--slice-x', default=None, type=float)
    parser.add_argument('--slice-y', default=None, type=float)
    parser.add_argument('--slice-z', default=None, type=float)
    parser.add_argument('--slice-a', default=None, type=float)
    parser.add_argument('--top-hole', choices=['1', '2'], default='1')
    args = parser.parse_args()

    constants.NSTEPS = args.resolution
    if args.top_hole == '1':
        top_hole = top_hole1
    elif args.top_hole == '2':
        top_hole = top_hole2

    sh = shell(top_hole)

    if args.slice_a is not None or args.slice_x is not None or args.slice_y is not None or args.slice_z is not None:
        cut = utils.slice(args)
        sh = sh - cut

    solid.scad_render_to_file(sh, 'shell.scad')


if __name__ == '__main__':
    main()
