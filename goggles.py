#!/usr/bin/python
import math
import collections
import solid
import solid.utils
import euclid3
from extrude_along_path import extrude_along_path

import mg2
import utils
import lens
import constants
#import ggg

Point3 = euclid3.Point3


def argmax(items, key):
    m = max(enumerate(items), key=lambda item: key(item[1]))
    return m[0]


def argmin(items, key):
    m = min(enumerate(items), key=lambda item: key(item[1]))
    return m[0]


def ellipsis_perpendicular(a, b, t):
    p = utils.ellipsis(a, b, t)
    return euclid3.Point3(p.x/a**2, p.y/b**2)


def ellipsis_path(delta=0):
    path = [utils.ellipsis(constants.ELLIPSIS_WIDTH+delta, constants.ELLIPSIS_HEIGHT+delta, t) for t in solid.utils.frange(0, 2*math.pi, constants.NSTEPS, include_end=False)]
    return path


def distance(alpha, threshold=0.5):
    d = alpha/threshold if alpha < threshold else (1-alpha)/(1-threshold)
    d = 1-(1-d)**2
    return d


def fwidth(alpha):
    d = distance(alpha)
    width = constants.SHELL_MIN_WIDTH+constants.MAX_WIDTH*d**7
    return width


def fheight(alpha):
    d = distance(alpha)
    height = constants.SHELL_MIN_HEIGHT+constants.MAX_HEIGHT*d**15
    return height


def shell_curve(alpha):
    width = fwidth(alpha)
    height = fheight(alpha)
    path = mg2.Path(x=0, y=0)\
        .append(dx=width*constants.XALPHA, dy=height*constants.YALPHA)\
        .append(dx=width*(1-constants.XALPHA), dy=height*(1-constants.YALPHA))
    return path


def rounded_square(x, y, height, radius, adjust=False):
    if adjust:
        x = x - 2*radius
        y = y - 2*radius
    r = solid.cylinder(radius, height, segments=40)
    o = solid.hull()(
        solid.translate([-x/2, -y/2, 0])(r),
        solid.translate([x/2, -y/2, 0])(r),
        solid.translate([-x/2, y/2, 0])(r),
        solid.translate([x/2, y/2, 0])(r),
    )
    return o


def rounded_square2(x, y, height, radius, adjust=False):
    if adjust:
        x = x - 2*radius
        y = y - 2*radius
        height = height - 2*radius
    r = solid.sphere(radius, segments=40)
    o = solid.hull()(
        solid.translate([-x/2, -y/2, height/2])(r),
        solid.translate([x/2, -y/2, height/2])(r),
        solid.translate([-x/2, y/2, height/2])(r),
        solid.translate([x/2, y/2, height/2])(r),
        solid.translate([-x/2, -y/2, -height/2])(r),
        solid.translate([x/2, -y/2, -height/2])(r),
        solid.translate([-x/2, y/2, -height/2])(r),
        solid.translate([x/2, y/2, -height/2])(r),
    )
    return o


def shell():
    TOP_ATTACHMENT_RESOLUTION = 40
    BOTTOM_ATTACHMENT_RESOLUTION = 40

    def profile(i, n):
        alpha = i/n
        curve = shell_curve(alpha).splinify()

        offset_curve = mg2.Path(path=curve)\
            .offset(constants.SHELL_THICKNESS, left=False)\
            .reverse()

        path = mg2.Path(path=curve)\
            .translate(dx=constants.SHELL_TOP_X)
        p2 = path.points.last + path.normal(left=False) * constants.SHELL_THICKNESS
        path.append(dy=constants.SHELL_THICKNESS)
        p1 = path.points.last + mg2.Point(x=1, y=0) * constants.SHELL_THICKNESS
        path.extend(path=mg2.Path(point=path.points.last)
                            .append(dy=constants.SHELL_THICKNESS)
                            .extend(path=mg2.Path(x=0, y=0)
                                            .append(dx=constants.SHELL_THICKNESS+2)
                                            .append(dy=-constants.SHELL_THICKNESS)
                                            .rotate(alpha=distance(alpha)**7)
                            )
                            .append(point=p1)
                            .append(point=p2)
        )

        path.extend(path=offset_curve)\
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
        curve = shell_curve(shell_alpha).splinify()
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

    path1 = ellipsis_path()
    shapes1 = [profile(i, len(path1)) for i in range(len(path1))]
    o = extrude_along_path(shapes1, path1, connect_ends=True)
#    o = solid.debug(o)

    path2 = [utils.ellipsis(constants.ELLIPSIS_WIDTH, constants.ELLIPSIS_HEIGHT, t) for t in solid.utils.frange(-constants.TOP_ATTACHMENT_WIDTH*2*math.pi, constants.TOP_ATTACHMENT_WIDTH*2*math.pi, TOP_ATTACHMENT_RESOLUTION, include_end=True)]
    shapes2 = [top_attachment_profile(i, len(path2)) for i in range(len(path2))]
    #top_attachment = ggg.extrude(top_attachment_profile).along_open_path(path2).solidify()
    top_attachment = extrude_along_path(shapes2, path2, connect_ends=False, cap_ends=True)
    top_attachment = top_attachment -\
        solid.translate([constants.ELLIPSIS_WIDTH+constants.SHELL_TOP_X+constants.SHELL_THICKNESS+constants.SHELL_MIN_WIDTH+constants.TOOTH_WIDTH/2, 0, -10])(
            rounded_square(1.5*constants.SHELL_THICKNESS, 1.5*constants.SHELL_THICKNESS, 20, constants.SHELL_THICKNESS/2)
        )
    o = o + top_attachment

    BOTTOM_ATTACHMENT_HEIGHT = 2

    def bottom_attachment_profile(i, n):
        attachment_alpha = i / n
        if attachment_alpha > 0.5:
            shell_alpha = 0.5+2*constants.BOTTOM_ATTACHMENT_WIDTH*(attachment_alpha-0.5)
        else:
            shell_alpha = 0.5-2*constants.BOTTOM_ATTACHMENT_WIDTH*(0.5-attachment_alpha)
        curve = shell_curve(shell_alpha).splinify()
        handle_width = constants.SHELL_THICKNESS*4*distance(attachment_alpha)**2
        handle_height = BOTTOM_ATTACHMENT_HEIGHT
        xalpha = constants.XALPHA
        yalpha = constants.YALPHA
        epsilon = 0.4
        cuts = curve.cut(y=constants.MAX_HEIGHT-handle_height)
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
    bottom_attachment = extrude_along_path(shapes3, path3)

    bah = rounded_square(constants.SHELL_BOTTOM_HOLE_HEIGHT, constants.SHELL_BOTTOM_HOLE_WIDTH, 20, constants.SHELL_THICKNESS/2)
    c = shell_curve(0.5)
    bah1 = solid.translate([-constants.ELLIPSIS_WIDTH-c.width-constants.SHELL_TOP_X-constants.SHELL_THICKNESS/2, 0, constants.ELLIPSIS_HEIGHT])(bah)
    bottom_attachment = bottom_attachment - bah1
    bah2 = solid.translate([-constants.ELLIPSIS_WIDTH-c.width-constants.SHELL_TOP_X-constants.SHELL_THICKNESS - 10, 0, c.height-BOTTOM_ATTACHMENT_HEIGHT-constants.SHELL_BOTTOM_HOLE_WIDTH/2])(
        solid.rotate([0, 90, 0])(bah)
    )
    bottom_attachment = bottom_attachment - bah2
    o = o + bottom_attachment

    # water filling holes
    for y in [1, -1]:
        o = o - solid.translate([-constants.ELLIPSIS_WIDTH-constants.MAX_WIDTH/2, y*1.2*constants.UNIT, -50])(
            solid.scale([2, 1, 1])(
                solid.cylinder(1.5*constants.UNIT/7, 100, segments=30)
            )
        )

    # flip for final rendering
    o = solid.mirror([0, 1, 0])(o)
#    o = solid.translate([0.05, 0, -0.05])(o)

    return o


def skirt_profile(i, n):
    alpha = i / n
    curve = shell_curve(alpha)
    zero = shell_curve(0)
    path = mg2.Path(path=curve.splinify())\
        .translate(constants.SHELL_TOP_X, 0)
    silicon_skirt_height = 0.5*constants.UNIT
    silicon_skirt_width = constants.SHELL_TOP_X+zero.width
    tmp = mg2.Path(x=0, y=0)\
        .append(dy=silicon_skirt_height)\
        .append(dx=silicon_skirt_width)\
        .splinify()
#            .append(dx=constants.SHELL_TOP_X+zero.width)\
    path.extend(path=tmp)
    return_path = path.copy().reverse().offset(constants.SKIRT_THICKNESS, left=False)
#   append_angle(alpha=math.pi/2, delta=constants.SKIRT_THICKNESS)\
    path.extend_arc(alpha=math.pi, r=constants.SKIRT_THICKNESS/2)\
        .extend(path=return_path)\
        .append(x=constants.SHELL_TOP_X)\
        .append(x=0+constants.SKIRT_THICKNESS/2)\
        .extend_arc(alpha=math.pi/2, r=constants.SKIRT_THICKNESS+constants.SKIRT_THICKNESS/2)\
        .append(dy=-constants.SHELL_THICKNESS+constants.SKIRT_THICKNESS/2)\
        .append(dx=constants.SKIRT_THICKNESS)\
        .append(dy=constants.SHELL_THICKNESS-constants.SKIRT_THICKNESS/2)\
        .extend_arc(alpha=-math.pi/2, r=constants.SKIRT_THICKNESS/2)
#            .append(dx=-constants.SKIRT_THICKNESS)

    return path.points


def skirt():
    path = ellipsis_path()
    shapes = [utils.eu3(skirt_profile(i, constants.NSTEPS)) for i in range(len(path))]
    o = extrude_along_path(shapes, path, connect_ends=True)
    o = solid.mirror([0, 1, 0])(o)
    o = solid.translate([0, 0, 0])(o)
    o = solid.color("grey")(o)
#    o = solid.debug(o)
    return o

GASKET_U_DEPTH = 2
GASKET_U_WIDTH_BOTTOM = constants.SHELL_THICKNESS * 1.1
GASKET_U_WIDTH_TOP = constants.SHELL_THICKNESS * 0.7
GASKET_THICKNESS = 2
GASKET_U_DEPTH_EXTRA = 1


def gasket_profile():
    #
    #    ------------
    #   /           |
    #  /    ---------
    # |     |
    #  \    Z-------A--/
    #   \             /
    #    ------------/
    offset = (GASKET_U_WIDTH_BOTTOM-GASKET_U_WIDTH_TOP)/2
    path = mg2.Path(x=0, y=0)\
        .append(dx=-GASKET_U_DEPTH_EXTRA)\
        .extend(path=mg2.Path(x=0, y=0)
            .append(dy=GASKET_THICKNESS)
            .append(dx=+(GASKET_U_DEPTH+GASKET_U_DEPTH_EXTRA+GASKET_THICKNESS), dy=offset)
            .append(dy=-(GASKET_THICKNESS+GASKET_THICKNESS+GASKET_U_WIDTH_BOTTOM))
            .append(dx=-(GASKET_U_DEPTH+GASKET_THICKNESS), dy=offset)
            .append(dy=GASKET_THICKNESS)
            .splinify()
        )\
        .append(dx=GASKET_U_DEPTH, dy=-offset)\
        .append(dy=GASKET_U_WIDTH_BOTTOM)
    return path

def gasket():
    path = [Point3(0, 0, 0), Point3(0, 0, 10)]
    shapes = [utils.eu3(gasket_profile().reversed_points) for i in range(len(path))]
    o = extrude_along_path(shapes, path, connect_ends=False)
    return o


def wrapped_gasket_profile(i, n):
    alpha = i / n
    curve = shell_curve(alpha)
    start_anchor_x = curve.width + constants.SHELL_TOP_X + constants.SHELL_THICKNESS
    start_anchor_y = curve.height + constants.SHELL_THICKNESS + constants.SHELL_THICKNESS
    path = mg2.Path(x=start_anchor_x, y=start_anchor_y)
    path.extend(gasket_profile().rotate(alpha=distance(alpha)**7))
    return path.reversed_points


def wrapped_gasket():
    path = ellipsis_path()
    shapes = [utils.eu3(wrapped_gasket_profile(i, constants.NSTEPS)) for i in range(len(path))]
    o = extrude_along_path(shapes, path, connect_ends=True)
    o = solid.color('blue')(o)
    return o


MOLD_PADDING = 1


def skirt_mold():
    path = ellipsis_path()
    shapes = [skirt_profile(i, constants.NSTEPS) for i in range(len(path))]
    exterior_shapes = []
    interior_shapes = []
    for shape in shapes:
        top = argmin(shape, key=lambda i: (i.y, i.x))
        bottom = argmax(shape, key=lambda i: (i.y, -i.x))
        exterior = shape[top:] + shape[:bottom+1]
        interior = shape[bottom:top]
        interior_shapes.append(interior)
        exterior_shapes.append(exterior)

    interior_shapes = normalize_shapes(interior_shapes)
    exterior_shapes = normalize_shapes(exterior_shapes)
    max_skirt_y = max([p.max_y for p in exterior_shapes])
    # interior mold
    interior = interior_mold(interior_shapes, max_skirt_y)
    return interior 


def normalize_shapes(shapes):
    maxlen = max([len(shape) for shape in shapes])
    for shape in shapes:
        for i in range(len(shape), maxlen):
            shape.append(shape[-1])
    shapes = [mg2.Path(path=shape) for shape in shapes]
    return shapes


def interior_mold(interior_shapes, max_skirt_y):
    path = ellipsis_path()

    epsilon = 0.001
    output = []
    for shape in interior_shapes:
        shape.append(y=-constants.SHELL_THICKNESS+epsilon)
        shape.append(x=-2)
        shape.append(y=max_skirt_y+MOLD_PADDING)
        shape.append(x=shape.points[0].x)
        output.append(utils.eu3(shape.reversed_points))

    o = extrude_along_path(output, path, connect_ends=True)

    epsilon = 0.01
    filler = utils.ring(max_skirt_y+constants.SHELL_THICKNESS+MOLD_PADDING+2*epsilon, -constants.SKIRT_THICKNESS-1)
    filler = solid.translate([0, 0, -constants.SHELL_THICKNESS-epsilon])(filler)
    o = o + filler

    # air gaps
    gap_path = ellipsis_path(delta=1)
    for i in range(0, len(gap_path), int(len(gap_path)/10)):
        gap = solid.cylinder(0.3, 100, segments=30)
        gap = solid.translate([-gap_path[i].x, -gap_path[i].y, 0])(gap)
        o = o - gap

    return o


def back_clip():
    o = rounded_square2(constants.BACK_CLIP_X, constants.BACK_CLIP_Y, constants.BACK_CLIP_THICKNESS, constants.BACK_CLIP_RADIUS, adjust=True)
    a = rounded_square(constants.BACK_CLIP_X-constants.BACK_CLIP_THICKNESS*2-constants.BACK_CLIP_RADIUS, constants.BACK_CLIP_THICKNESS, 100, constants.BACK_CLIP_RADIUS, adjust=True)
    a = solid.translate([0, 0, -50])(a)
    for i in [-constants.BACK_CLIP_Y/4-constants.BACK_CLIP_THICKNESS, -3*constants.BACK_CLIP_THICKNESS/2, 3*constants.BACK_CLIP_THICKNESS/2, constants.BACK_CLIP_Y/4+constants.BACK_CLIP_THICKNESS]:
        b = solid.translate([0, i, 0])(a)
        o = o - b
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
    args = parser.parse_args()

    constants.NSTEPS = args.resolution
    sh = shell()
    sk = skirt()
    g = gasket()
    wg = wrapped_gasket()
    l = lens.lens()
#    l = solid.translate([-0.2, 0, 0.05])(l)
    lc = lens.lens_clip(constants.LENS_GROOVE_HEIGHT, 3, math.pi/4)
    bc = back_clip()
    mold = skirt_mold()

    output = sh + wg + sk # + lc + l
    if args.slice_a is not None or args.slice_x is not None or args.slice_y is not None or args.slice_z is not None:
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
        lc = lc - cut
        sh = sh - cut
        sk = sk - cut
        l = l - cut
        g = g - cut
        wg = wg - cut
        mold = mold - cut
        output = output - cut

    solid.scad_render_to_file(output, 'goggles.scad')
    solid.scad_render_to_file(sh, 'shell.scad')
    solid.scad_render_to_file(sk, 'skirt.scad')
    solid.scad_render_to_file(bc, 'back-clip.scad')
    solid.scad_render_to_file(g, 'gasket.scad')
    solid.scad_render_to_file(wg, 'wrapped-gasket.scad')
    solid.scad_render_to_file(mold, 'mold.scad')

    if args.export:
        utils.export('shell', 'stl')
        utils.export('skirt', 'stl')
        utils.export('mold', 'stl')
        utils.export('back-clip', 'stl')


main()
