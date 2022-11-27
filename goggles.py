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
import constants


def eu3(path):
    if len(path) == 0:
        return []
    return [euclid3.Point3(p.x, p.y, 0) for p in path]

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
    width = max(constants.SHELL_THICKNESS, constants.MAX_WIDTH*d**7)
    return width
def fheight(alpha):
    d = distance(alpha)
    height = max(constants.SHELL_THICKNESS, constants.MAX_HEIGHT*d**15)
    return height

def shell_curve(alpha):
    width = fwidth(alpha)
    height = fheight(alpha)
    path = mg2.Path(x=0, y=0)\
        .append(dx=width*constants.XALPHA, dy=height*constants.YALPHA)\
        .append(dx=width*(1-constants.XALPHA), dy=height*(1-constants.YALPHA))\
        .splinify(n=20)
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
        curve = shell_curve(alpha)

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
        return eu3(path.reversed_points)

    def top_attachment_profile(attachment_alpha):
        if attachment_alpha > 0.5:
            shell_alpha = 2*constants.TOP_ATTACHMENT_WIDTH*(attachment_alpha-0.5)
            alpha = (attachment_alpha - 0.5)/0.5
        else:
            shell_alpha = 1-constants.TOP_ATTACHMENT_WIDTH+2*constants.TOP_ATTACHMENT_WIDTH*attachment_alpha
            alpha = (0.5-attachment_alpha)/0.5
        d = distance(shell_alpha)
        curve = shell_curve(shell_alpha)
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
        return eu3(p1.reversed_points)


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
        curve = shell_curve(shell_alpha)
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
        return eu3(path.reversed_points)
        
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

    return o


def skirt():
    def bottom_skirt_profile(alpha):
        silicon_skirt_height = 0.75*constants.UNIT
        silicon_skirt_thickness = 4*constants.SHELL_THICKNESS
        epsilon = 0.1
        s = mg2.Path(x=0, y=0)\
            .append(dx=-constants.SHELL_THICKNESS*3,dy=2*constants.SHELL_THICKNESS)\
            .append(dx=constants.SHELL_THICKNESS*2,dy=silicon_skirt_height/2)\
            .append(dx=constants.SHELL_THICKNESS*3,dy=silicon_skirt_height/2)\
            .append(dx=-2*constants.SHELL_THICKNESS)\
            .append(dx=-silicon_skirt_thickness, dy=-silicon_skirt_height)\
            .rotate(alpha=0.5*distance(alpha)**12)\
            .append(x=(-constants.SHELL_THICKNESS)-constants.SKIRT_THICKNESS, y=-constants.SKIRT_THICKNESS)\
            .splinify()
        return eu3(s.points)

    def _profile(alpha):
        curve = shell_curve(alpha)
        path = mg2.Path(path=curve)\
            .translate(constants.SHELL_TOP_X, 0)\
            .append(dx=constants.SHELL_THICKNESS)\
            .append(dy=constants.SKIRT_THICKNESS)\
            .append(dx=-constants.SHELL_THICKNESS-constants.SKIRT_THICKNESS)

        skirt_top_thickness=constants.SKIRT_THICKNESS-constants.SKIRT_RING_PADDING
        delta = mg2.Point(x=constants.SHELL_TOP_X, y=constants.SKIRT_THICKNESS) - path.points.last
        return_path = mg2.Path(x=0, y=0)\
            .append(dx=(1-constants.XALPHA+0.05)*delta.x, dy=(1-constants.YALPHA)*delta.y) \
            .append(x=delta.x, y=delta.y) \
            .splinify()
        path = path.extend(path=return_path)\
            .append(dx=-constants.LENS_BOTTOM_RING_WIDTH)\
            .append(dx=-constants.SKIRT_THICKNESS)\
            .append(dy=-constants.SKIRT_THICKNESS-constants.SHELL_THICKNESS)\
            .extend(path=mg2.Path(x=0, y=0)\
                .append(dx=skirt_top_thickness,dy=-constants.SKIRT_THICKNESS/2)\
                .append(dx=skirt_top_thickness/2, dy=constants.SKIRT_THICKNESS/2)\
                .append(dx=-skirt_top_thickness/2)\
                .splinify()
            )\
            .append(dy=constants.SHELL_THICKNESS)
        return eu3(path.points)

    path = [utils.ellipsis(constants.ELLIPSIS_WIDTH, constants.ELLIPSIS_HEIGHT, t) for t in solid.utils.frange(2*math.pi/constants.NSTEPS, 2*math.pi, constants.NSTEPS, include_end=False)]
    o = extrude_along_path(_profile, path, connect_ends=True)


    epsilon = constants.SKIRT_THICKNESS/10
    n = len(path)
    normals = [ellipsis_perpendicular(constants.ELLIPSIS_WIDTH, constants.ELLIPSIS_HEIGHT, t) for t in solid.utils.frange(2*math.pi/constants.NSTEPS, 2*math.pi, constants.NSTEPS, include_end=False)]
    skirt_path = [
        Point3(x=p.x, y=p.y, z=fheight(float(i)/(n-1))+constants.SKIRT_THICKNESS-epsilon)+normal/mg2.norm2(normal)*(constants.SHELL_TOP_X+constants.SHELL_THICKNESS+fwidth(float(i)/(n-1)))
        for i, (p, normal) in enumerate(zip(path, normals))
    ]
    o = solid.color("grey")(o) + solid.color("yellow")(extrude_along_path(bottom_skirt_profile, skirt_path, connect_ends=True))
#    for p in skirt_path:
#        o = o + solid.translate(p)(solid.sphere(1))
    o = solid.mirror([0, 1, 0])(o)
    o = solid.translate([0, 0, 0])(o)
#    o = solid.color("grey")(o)
    #o = solid.debug(o)
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
    o = extrude_along_path(eu3(profile.reversed_points), path, connect_ends=True)
    return o


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
    l = lens()
    ltop = lens_top()
    lbot = lens_bottom()
    la = lens_alignment()

    lc = lens_clip(constants.LENS_GROOVE_HEIGHT, 3, math.pi/4)
    bc = back_clip()

    output = sk + l + lc + sh
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
        sh = sh - cut
        sk = sk - cut
        l = l - cut
        la = la - cut
        output = output - cut
    solid.scad_render_to_file(output, 'goggles.scad')
    solid.scad_render_to_file(lc, 'lens-clip.scad')
    solid.scad_render_to_file(sh, 'shell.scad')
    solid.scad_render_to_file(sk, 'skirt.scad')
    solid.scad_render_to_file(l, 'lens.scad')
    solid.scad_render_to_file(ltop, 'lens-top.scad')
    solid.scad_render_to_file(lbot, 'lens-bot.scad')
    solid.scad_render_to_file(la, 'lens-alignment.scad')
    solid.scad_render_to_file(bc, 'back-clip.scad')

    def export(name, type):
        import subprocess
        import os
        try:
            os.mkdir('%s-%s' % (type, args.resolution))
        except:
            pass
        subprocess.check_output(['/usr/bin/openscad', '-o', '%s-%s/%s.%s' % (type, args.resolution, name, type), '%s.scad' % name])

    if args.export:
        export('shell', 'stl')
        export('skirt', 'stl')
        export('lens', 'stl')
        export('lens-top', 'stl')
        export('lens-bot', 'stl')
        export('lens-clip', 'stl')
        export('lens-alignment', 'stl')
        export('back-clip', 'stl')

    generate_lens_svg()

def main2():
    import subprocess

    constants.NSTEPS = 400

    for i in [0, -0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7]:
        l = lens(i)
        solid.scad_render_to_file(l, 'lens.scad')
        subprocess.check_output(['/usr/bin/openscad', '-o', 'lens-variants/%s.stl' % abs(i), 'lens.scad'])


def main3():
    import subprocess

    constants.NSTEPS = 400

    for i in [0, 0.1, 0.2, 0.3, 0.4, 0.5]:
        c = clip3(constants.LENS_GROOVE_HEIGHT-i, 3, math.pi/4)
        solid.scad_render_to_file(c, 'clip.scad')
        subprocess.check_output(['/usr/bin/openscad', '-o', 'clip-variants/%s.stl' % i, 'clip.scad'])


main()
