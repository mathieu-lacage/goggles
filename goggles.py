#!/usr/bin/python
import math
import collections
import bisect
import solid, solid.utils
import euclid3
import transformations
from extrude_along_path import extrude_along_path

import mg2
import utils
import lens
import constants

Point3 = euclid3.Point3

def ellipsis_perpendicular(a,b,t):
    p = utils.ellipsis(a,b,t)
    return euclid3.Point3(p.x/a**2, p.y/b**2)

def distance(alpha, threshold=0.5):
    d = alpha/threshold if alpha < threshold else (1-alpha)/(1-threshold)
    d = 1-(1-d)**2
    return d

def argmin(l, key):
    if len(l) == 0:
        return None
    min_key = key(l[0])
    min_index = 0
    for i, item in enumerate(l[1:]):
        k = key(item)
        if k < min_key:
            min_index = i+1
            min_key = k
    return min_index
def ydistance(alpha):
    def _norm2(v):
        return math.sqrt(v.x**2+v.y**2)
    t = 2*math.pi*alpha
    e = utils.ellipsis(constants.ELLIPSIS_WIDTH, constants.ELLIPSIS_HEIGHT, t)
    ep = ellipsis_perpendicular(constants.ELLIPSIS_WIDTH, constants.ELLIPSIS_HEIGHT, t)
    ep = ep / _norm2(ep)
    p = e + ep * fwidth(alpha)
    return p.y
def fwidth(alpha):
    d = distance(alpha)
    width = constants.SHELL_THICKNESS+constants.MAX_WIDTH*d**7
    return width
def fheight(alpha):
    d = distance(alpha)
    height = constants.SHELL_THICKNESS+constants.MAX_HEIGHT*d**15
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

    def profile(alpha):

        d = distance(alpha)
        curve = shell_curve(alpha).splinify()

        offset_curve = mg2.Path(path=curve)\
            .offset(constants.SHELL_THICKNESS, left=False)\
            .reverse()

        path = mg2.Path(path=curve)\
            .translate(dx=constants.SHELL_TOP_X)\
            .label('forward_path_end')\
            .append(dx=constants.SHELL_THICKNESS)\
            .append_angle(alpha=-math.pi/2, delta=constants.SHELL_THICKNESS, relative_to='forward_path_end')\
            .extend(path=offset_curve)\
            .append(x=constants.SHELL_TOP_X, y=constants.SHELL_TOP_Y)\
            .append(dx=-constants.LENS_BOTTOM_RING_WIDTH)\
            .append(dy=constants.SHELL_THICKNESS)
        return utils.eu3(path.reversed_points)

    def top_attachment_profile(attachment_alpha):
        if attachment_alpha > 0.5:
            shell_alpha = 2*constants.TOP_ATTACHMENT_WIDTH*(attachment_alpha-0.5)
            alpha = (attachment_alpha - 0.5)/0.5
        else:
            shell_alpha = 1-constants.TOP_ATTACHMENT_WIDTH+2*constants.TOP_ATTACHMENT_WIDTH*attachment_alpha
            alpha = (0.5-attachment_alpha)/0.5
        d = distance(shell_alpha)
        curve = shell_curve(shell_alpha).splinify()
        top = max(2*constants.UNIT/3*(1-alpha**4), constants.SHELL_THICKNESS)
        tooth_width = 2.5*constants.TOOTH_WIDTH*(1-alpha**4)
        epsilon = 0.1
        p1 = mg2.Path(x=curve.width+constants.SHELL_TOP_X, y=curve.height)\
            .append(dx=tooth_width, y=-top/2)\
            .append(y=-top)\
            .splinify(n=40)\
            .append(dx=-tooth_width)\
            .append(dx=-curve.width/2, y=-constants.SHELL_THICKNESS)\
            .append(dx=-curve.width/2)\
            .append(dy=constants.SHELL_THICKNESS-epsilon)\
            .append(dx=curve.width-epsilon)
        return utils.eu3(p1.reversed_points)


    path1 = [utils.ellipsis(constants.ELLIPSIS_WIDTH, constants.ELLIPSIS_HEIGHT, t) for t in solid.utils.frange(2*math.pi/constants.NSTEPS, 2*math.pi, constants.NSTEPS, include_end=False)]
    o = extrude_along_path(profile, path1, connect_ends=True)
#    o = solid.debug(o)

    path2 = [utils.ellipsis(constants.ELLIPSIS_WIDTH, constants.ELLIPSIS_HEIGHT, t) for t in solid.utils.frange(-constants.TOP_ATTACHMENT_WIDTH*2*math.pi, constants.TOP_ATTACHMENT_WIDTH*2*math.pi, 40)]
    top_attachment = extrude_along_path(top_attachment_profile, path2)
    top_attachment = top_attachment -\
        solid.translate([constants.ELLIPSIS_WIDTH+constants.SHELL_TOP_X+constants.SHELL_THICKNESS+constants.TOOTH_WIDTH, 0, -10])(
            rounded_square(1.5*constants.SHELL_THICKNESS, 1.5*constants.SHELL_THICKNESS, 20, constants.SHELL_THICKNESS/2)
        )

    o = o + top_attachment

    BOTTOM_ATTACHMENT_HEIGHT = 5
    def bottom_attachment_profile(attachment_alpha):
        if attachment_alpha > 0.5:
            shell_alpha = 0.5+2*constants.BOTTOM_ATTACHMENT_WIDTH*(attachment_alpha-0.5)
            alpha = (attachment_alpha - 0.5)/0.5
        else:
            shell_alpha = 0.5-2*constants.BOTTOM_ATTACHMENT_WIDTH*(0.5-attachment_alpha)
            alpha = (0.5-attachment_alpha)/0.5
        d = distance(shell_alpha)
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
            .extend(mg2.Path(x=0, y=0)\
                .append(dx=-(1-xalpha)*(delta_x+handle_width)*3/4, dy=-(1-yalpha)*delta_y)\
                .append(dx=-(xalpha)*(delta_x+handle_width)*3/4, dy=-(yalpha)*delta_y)\
                .splinify()\
            )
        return utils.eu3(path.reversed_points)
        
    path3 = [utils.ellipsis(constants.ELLIPSIS_WIDTH, constants.ELLIPSIS_HEIGHT, t) for t in solid.utils.frange(math.pi-constants.BOTTOM_ATTACHMENT_WIDTH*2*math.pi, math.pi+constants.BOTTOM_ATTACHMENT_WIDTH*2*math.pi, 40)]
    bottom_attachment = extrude_along_path(bottom_attachment_profile, path3)

    bah = rounded_square(constants.SHELL_BOTTOM_HOLE_HEIGHT, constants.SHELL_BOTTOM_HOLE_WIDTH, 20, constants.SHELL_THICKNESS/2)
    c = shell_curve(0.5)
    bah1 = solid.translate([-constants.ELLIPSIS_WIDTH-c.width-constants.SHELL_TOP_X-constants.SHELL_THICKNESS/2, 0, constants.ELLIPSIS_HEIGHT-3])(bah)
    bottom_attachment = bottom_attachment - bah1
    bah2 = solid.translate([-constants.ELLIPSIS_WIDTH-c.width-constants.SHELL_TOP_X-constants.SHELL_THICKNESS - 10, 0, c.height-BOTTOM_ATTACHMENT_HEIGHT])(
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


def skirt():
    def _profile(alpha):
        curve = shell_curve(alpha)
        zero = shell_curve(0)
        silicon_skirt_height = 0.75*constants.UNIT
        silicon_skirt_width = constants.SHELL_TOP_X+zero.width+curve.width/3
 
        path = mg2.Path(path=curve.splinify())\
            .translate(constants.SHELL_TOP_X, 0)
        tmp = mg2.Path(x=0, y=0)\
            .append(dy=silicon_skirt_height)\
            .append(dx=-silicon_skirt_width)\
            .append(dy=-silicon_skirt_height/2)\
            .splinify()
        path.extend(path=tmp)
        return_path = path.copy().reverse().offset(constants.SKIRT_THICKNESS, left=False)
        path.append_angle(alpha=math.pi/2, delta=constants.SKIRT_THICKNESS)\
            .extend(path=return_path)\
            .append(x=constants.SHELL_TOP_X)\
            .append(dx=-constants.LENS_BOTTOM_RING_WIDTH-constants.SKIRT_THICKNESS)\
            .append(dy=-constants.SHELL_THICKNESS-constants.SKIRT_THICKNESS)\
            .append(dx=constants.SKIRT_THICKNESS)\
            .append(dy=constants.SHELL_THICKNESS)
#            .append(dx=-constants.SKIRT_THICKNESS)

        return utils.eu3(path.points)

    path = [utils.ellipsis(constants.ELLIPSIS_WIDTH, constants.ELLIPSIS_HEIGHT, t) for t in solid.utils.frange(2*math.pi/constants.NSTEPS, 2*math.pi, constants.NSTEPS, include_end=False)]
    o = extrude_along_path(_profile, path, connect_ends=True)
    o = solid.mirror([0, 1, 0])(o)
    o = solid.translate([0, 0, 0])(o)
    o = solid.color("grey")(o)
    #o = solid.debug(o)
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
    parser.add_argument('--slice-h', default=None, type=float)
    parser.add_argument('--slice-v', default=None, type=float)
    args = parser.parse_args()

    constants.NSTEPS = args.resolution
    sh = shell()
    sk = skirt()
    l = lens.lens()
#    l = solid.translate([-0.2, 0, 0.05])(l)
    lc = lens.lens_clip(constants.LENS_GROOVE_HEIGHT, 3, math.pi/4)
    bc = back_clip()

    output = sk + l + sh + lc
    if args.slice_v is not None or args.slice_h is not None:
        if args.slice_v is not None:
            cut = solid.rotate([0,0,args.slice_v])(solid.translate([-100,0,-100])(solid.cube([200,200,200])))
        else:
            cut = solid.cube([0,0,0])
        if args.slice_h is not None:
            cut = cut + solid.translate([-100,-50,args.slice_h])(solid.cube([200,200,200]))
        lc = lc - cut
        sh = sh - cut
        sk = sk - cut
        l = l - cut
        output = output - cut
    solid.scad_render_to_file(output, 'goggles.scad')
    solid.scad_render_to_file(sh, 'shell.scad')
    solid.scad_render_to_file(sk, 'skirt.scad')
    solid.scad_render_to_file(bc, 'back-clip.scad')

    if args.export:
        utils.export('shell', 'stl')
        utils.export('skirt', 'stl')
        utils.export('back-clip', 'stl')


main()
