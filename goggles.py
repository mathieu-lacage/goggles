#!/usr/bin/python
import math
import collections
import solid
import solid.utils
import euclid3

import mg2
import utils
import lens
import constants
import transform
import ggg

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


def distance(alpha, threshold=0.5):
    d = alpha/threshold if alpha < threshold else (1-alpha)/(1-threshold)
    d = 1-(1-d)**2
    return d


def fwidth(alpha):
    d = distance(alpha)
    width = constants.SHELL_MIN_WIDTH+constants.SHELL_MAX_WIDTH*d**7
    return width


def fheight(alpha):
    d = distance(alpha)
    height = constants.SHELL_MIN_HEIGHT+constants.SHELL_MAX_HEIGHT*d**15
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

        path = mg2.Path(path=curve)\
            .translate(dx=constants.SHELL_TOP_X)\
            .extend(path=shell_extension(0.75))
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

    path1 = utils.ellipsis_path()
    shapes1 = [profile(i, len(path1)) for i in range(len(path1))]
    o = ggg.extrude(shapes1).along_closed_path(path1).mesh().solidify()
#    o = solid.debug(o)

    path2 = [utils.ellipsis(constants.ELLIPSIS_WIDTH, constants.ELLIPSIS_HEIGHT, t) for t in solid.utils.frange(-constants.TOP_ATTACHMENT_WIDTH*2*math.pi, constants.TOP_ATTACHMENT_WIDTH*2*math.pi, TOP_ATTACHMENT_RESOLUTION, include_end=True)]
    shapes2 = [top_attachment_profile(i, len(path2)) for i in range(len(path2))]
    top_attachment = ggg.extrude(shapes2).along_open_path(path2).mesh().solidify()
    top_hole = rounded_square(1.5*constants.SHELL_THICKNESS, 1.5*constants.SHELL_THICKNESS, 20, constants.SHELL_THICKNESS/2)
    top_hole = solid.translate([constants.ELLIPSIS_WIDTH+shell_curve(0).width+constants.SHELL_TOP_X+constants.SHELL_THICKNESS+constants.TOOTH_WIDTH/2-0.2, 0, -10])(top_hole)
    top_attachment = top_attachment - top_hole
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

    bah = rounded_square(constants.SHELL_BOTTOM_HOLE_HEIGHT, constants.SHELL_BOTTOM_HOLE_WIDTH, 20, constants.SHELL_THICKNESS/2)
    c = shell_curve(0.5)
    bah1 = solid.translate([-constants.ELLIPSIS_WIDTH-c.width-constants.SHELL_TOP_X-constants.SHELL_THICKNESS/2, 0, constants.SHELL_MAX_HEIGHT])(bah)
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

    return o

def shell_extension(delta=1):
    zero = shell_curve(0)
    silicon_skirt_height = 0.5*constants.UNIT
    silicon_skirt_width = constants.SHELL_TOP_X+zero.width
    tmp = mg2.Path(x=0, y=0)\
        .append(dy=silicon_skirt_height*delta)\
        .append(dx=silicon_skirt_width*delta)\
        .splinify()
    return tmp

def skirt_profile(i, n):
    alpha = i / n
    curve = shell_curve(alpha)
    path = mg2.Path(path=curve.splinify())\
        .translate(constants.SHELL_TOP_X, 0)
    path.extend(path=shell_extension())
    return_path = path.copy().reverse().offset(constants.SKIRT_THICKNESS, left=False)
    path.extend_arc(alpha=math.pi, r=constants.SKIRT_THICKNESS/2)\
        .extend(path=return_path)\
        .append(x=0+constants.SKIRT_THICKNESS/2)\
        .extend_arc(alpha=math.pi/2, r=constants.SKIRT_THICKNESS+constants.SKIRT_THICKNESS/2)\
        .append(dy=-constants.SHELL_THICKNESS+constants.SKIRT_THICKNESS/2)\
        .append(dx=constants.SKIRT_THICKNESS)\
        .append(dy=constants.SHELL_THICKNESS-constants.SKIRT_THICKNESS/2)\
        .extend_arc(alpha=-math.pi/2, r=constants.SKIRT_THICKNESS/2)

    return path.points


BoundingBox = collections.namedtuple('BoundingBox', ['xmin', 'xmax', 'ymin', 'ymax', 'zmin', 'zmax'])


def skirt_bounding_box():
    path = utils.ellipsis_path()
    shapes = [utils.eu3(skirt_profile(i, constants.NSTEPS)) for i in range(len(path))]
    transformed = transform.to_path(shapes, path, True)

    xmin = min([p.x for shape in transformed for p in shape])
    xmax = max([p.x for shape in transformed for p in shape])
    ymin = min([p.y for shape in transformed for p in shape])
    ymax = max([p.y for shape in transformed for p in shape])
    zmin = min([p.z for shape in transformed for p in shape])
    zmax = max([p.z for shape in transformed for p in shape])

    return BoundingBox(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax)


def skirt():
    path = utils.ellipsis_path()
    shapes = [utils.eu3(skirt_profile(i, constants.NSTEPS)) for i in range(len(path))]
    o = ggg.extrude(shapes).along_closed_path(path).mesh().solidify()
    o = solid.mirror([0, 1, 0])(o)
    o = solid.translate([0, 0, 0])(o)
    o = solid.color("grey")(o)
#    o = solid.debug(o)
    return o


def skirt_mold_bounding_box():
    bb = skirt_bounding_box()
    assert (bb.xmax-bb.xmin) <= constants.MOLD_BB_X
    assert (bb.ymax-bb.ymin) <= constants.MOLD_BB_Y
    assert (bb.zmax-bb.zmin) <= constants.MOLD_BB_Z
    xmin = bb.xmin-(constants.MOLD_BB_X-(bb.xmax-bb.xmin))/2
    xmax = bb.xmax+(constants.MOLD_BB_X-(bb.xmax-bb.xmin))/2
    ymin = bb.ymin-(constants.MOLD_BB_Y-(bb.ymax-bb.ymin))/2
    ymax = bb.ymax+(constants.MOLD_BB_Y-(bb.ymax-bb.ymin))/2
    zmin = bb.zmin-(constants.MOLD_BB_Z-(bb.zmax-bb.zmin))/2
    zmax = bb.zmax+(constants.MOLD_BB_Z-(bb.zmax-bb.zmin))/2
    return BoundingBox(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax)


def skirt_mold_bounded():
    corner = solid.cylinder(r=constants.MOLD_RADIUS, h=constants.MOLD_BB_Y, segments=40)
    corner = solid.rotate([90, 0, 0])(corner)
    corner = solid.translate([constants.MOLD_RADIUS, constants.MOLD_BB_Y, constants.MOLD_RADIUS])(corner)

    c1 = corner
    c2 = solid.translate([constants.MOLD_BB_X-constants.MOLD_RADIUS*2, 0, 0])(c1)
    c3 = solid.translate([0, 0, constants.MOLD_BB_Z-constants.MOLD_RADIUS*2])(c1)
    c4 = solid.translate([constants.MOLD_BB_X-constants.MOLD_RADIUS*2, 0, constants.MOLD_BB_Z-constants.MOLD_RADIUS*2])(c1)
    o = solid.hull()([c1, c2, c3, c4])

    bb = skirt_mold_bounding_box()
    o = solid.translate([bb.xmin, bb.ymin, bb.zmin])(o)
    return o


def top_split(split):
    left_top = _split(split, False)
    right_top = solid.mirror([0, 1, 0])(left_top)
    return left_top + right_top


def bottom_split(split):
    left_bottom = _split(split, True)
    right_bottom = solid.mirror([0, 1, 0])(left_bottom)
    return left_bottom + right_bottom


def alignment_pin(x, y, z):
    Pin = collections.namedtuple('Pin', ['male', 'female'])
    pin_height = 4
    pin_radius = 4
    pin_tolerance = constants.TOLERANCE

    def pin(height, radius):
        filet_radius = 1
        profile = mg2.Path(x=radius, y=0)\
            .append(dy=height-filet_radius)\
            .extend_arc(alpha=math.pi/2, r=filet_radius)
        path = [euclid3.Point3(x=math.cos(t), y=math.sin(t), z=0) for t in solid.utils.frange(0, 2*math.pi, constants.NSTEPS, include_end=False)]
        shapes = [utils.eu3(profile.points) for i in range(len(path))]
        o = ggg.extrude(shapes).along_closed_path(path).mesh().solidify()
        o = solid.hull()(o)
        return o

    male = pin(pin_height, pin_radius)
    female = pin(pin_height+pin_tolerance, pin_radius+pin_tolerance)
    male = solid.translate([x, y, z])(male)
    female = solid.translate([x, y, z])(female)
    return Pin(male=male, female=female)

def _split(split, is_bottom):
    epsilon = 0.001
    filtered = [p for p in split if p.y >= 0]

    bottom_sign = 1 if is_bottom else -1
    shapes = []
    for p in filtered:
        path =     [ggg.Point3(x=p.x, y=p.y-epsilon,     z=p.z)]
        path.append(ggg.Point3(x=p.x, y=p.y-epsilon+100, z=p.z))
        path.append(ggg.Point3(x=p.x, y=p.y-epsilon+100, z=p.z+bottom_sign*100))
        path.append(ggg.Point3(x=p.x, y=p.y-epsilon,     z=p.z+bottom_sign*100))
        path = path if is_bottom else list(reversed(path))
        shapes.append(path)
    m = ggg.Shapes(shapes, ggg.Shapes.ENDS_CLOSE).mesh()

    ydelta = (constants.MOLD_BB_Y+20)/2
    tmp = solid.cube([30, ydelta, constants.MOLD_BB_Z+20], center=True)
    reference = filtered[0]
    tmp1 = solid.translate([reference.x-epsilon+30/2, ydelta/2, reference.z+bottom_sign*(constants.MOLD_BB_Z+20)/2])(tmp)
    reference = filtered[-1]
    tmp2 = solid.translate([reference.x+epsilon-30/2, ydelta/2, reference.z+bottom_sign*(constants.MOLD_BB_Z+20)/2])(tmp)

    a = screwdriver_hole(filtered[0], x_positive=True)
    b = screwdriver_hole(filtered[-1], x_positive=False)
    o = m.solidify() + tmp1 + tmp2 - a - b

    bb = skirt_mold_bounding_box()
    pin = alignment_pin(bb.xmax-10, bb.ymax-10, filtered[0].z-1)
    if is_bottom:
        o = o - pin.female
    else:
        o = o + pin.male
    return o


def skirt_mold():
    path = utils.ellipsis_path()
    shapes = [skirt_profile(i, constants.NSTEPS) for i in range(len(path))]
    top_shapes = []
    bottom_shapes = []
    for shape in shapes:
        top = argmin(shape, key=lambda i: (i.y, i.x))
        bottom = argmax(shape, key=lambda i: (i.x, i.y))
        top_shape = shape[top:] + shape[:bottom+1]
        bottom_shape = shape[bottom:top]
        bottom_shapes.append(bottom_shape)
        top_shapes.append(top_shape)

    bottom_shapes = normalize_shapes(bottom_shapes)
    top_shapes = normalize_shapes(top_shapes)
    max_skirt_y = max([p.max_y for p in top_shapes])

    bottom = bottom_mold(bottom_shapes, max_skirt_y)
    top = top_mold(top_shapes)

    bb = skirt_mold_bounded()
    top = solid.intersection()([top, bb])
    bottom = solid.intersection()([bottom, bb])

    return bottom, top


def normalize_shapes(shapes):
    maxlen = max([len(shape) for shape in shapes])
    for shape in shapes:
        for i in range(len(shape), maxlen):
            shape.append(shape[-1])
    shapes = [mg2.Path(path=shape) for shape in shapes]
    return shapes


def screwdriver_hole(p, x_positive):
    bb = skirt_mold_bounding_box()
    if x_positive:
        x = bb.xmax-1.8
    else:
        x = bb.xmin+1.8
    tmp = solid.cube([4, 6, 2], center=True)
    o = solid.translate([x, 10, p.z])(tmp)
    #o = solid.debug(o)
    return o


MOLD_OVERLAP = 2


def bottom_mold(bottom_shapes, max_skirt_y):
    path = utils.ellipsis_path()

    epsilon = 0
    output = []
    for shape in bottom_shapes:
        shape.append(y=-constants.SHELL_THICKNESS+epsilon)
        shape.append(x=-2)
        shape.append(y=max_skirt_y+100)
        shape.append(x=shape.points[0].x)
        shape.append(y=shape.points[0].y)
        output.append(utils.eu3(shape.reversed_points))

    shapes = ggg.extrude(output).along_closed_path(path)

    o = shapes.mesh().solidify()

    filler = utils.ring(max_skirt_y+constants.SHELL_THICKNESS+100+2*epsilon, -constants.SKIRT_THICKNESS-0.5)
    filler = solid.translate([0, 0, -constants.SHELL_THICKNESS-epsilon])(filler)
    o = o + filler

    mold_overlap_tolerance = 0.1
    filler2 = utils.ring(MOLD_OVERLAP, -constants.SKIRT_THICKNESS-mold_overlap_tolerance)
    filler2 = solid.translate([0, 0, -MOLD_OVERLAP-constants.SHELL_THICKNESS-epsilon])(filler2)
    o = o + filler2

    split = []
    for shape in shapes.shapes:
        max_index = argmax(shape, key=lambda p: (p.x**2+p.y**2, -p.z))
        split.append(shape[max_index])
    tmp = bottom_split(split)

    return o + tmp


def feeder():
    bb = skirt_mold_bounding_box()

    o = solid.cylinder(h=40, r1=2.75, r2=2, center=True, segments=20)
    o = solid.translate([-constants.ELLIPSIS_WIDTH-4, 0, 0])(o)

    base = solid.cylinder(h=2, r=7.1, center=True, segments=20)
    base = solid.translate([-constants.ELLIPSIS_WIDTH-4, 0, bb.zmin])(base)

    return o + base


def top_mold(top_shapes):
    output = []
    for shape in top_shapes:
        shape = shape.copy()
        shape.append(dy=-100)
        shape.append(x=shape.points[0].x)
        output.append(utils.eu3(shape.reversed_points))

    path = utils.ellipsis_path()
    shapes = ggg.extrude(output).along_closed_path(path)

    o = shapes.mesh().solidify()

    epsilon = 0.01
    filler = utils.ring(100-constants.SHELL_THICKNESS+constants.TOLERANCE, 0)
    filler = solid.translate([0, 0, -MOLD_OVERLAP-100-epsilon-constants.TOLERANCE])(filler)
    o = o + filler

    split = []
    for shape in shapes.shapes:
        max_index = argmax(shape, key=lambda p: (p.x**2+p.y**2, p.z))
        split.append(shape[max_index])
    tmp = top_split(split)

    return o + tmp - feeder()


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
    l = lens.lens()
#    l = solid.translate([-0.2, 0, 0.05])(l)
    lc = lens.lens_clip(constants.LENS_GROOVE_HEIGHT, 3, math.pi/4)
    bc = back_clip()
    bottom_mold, top_mold = skirt_mold()
    #top_mold = solid.translate([0, 0, -0.3])(top_mold)
    mold = bottom_mold + top_mold

    output = l + sh + lc
    #output = sh + l + lc
    if args.slice_a is not None or args.slice_x is not None or args.slice_y is not None or args.slice_z is not None:
        cut = utils.slice(args)
        lc = lc - cut
        sh = sh - cut
        sk = sk - cut
        l = l - cut
        top_mold = top_mold - cut
        bottom_mold = bottom_mold - cut
        mold = mold - cut
        output = output - cut

    solid.scad_render_to_file(output, 'goggles.scad')
    solid.scad_render_to_file(sh, 'shell.scad')
    solid.scad_render_to_file(sk, 'skirt.scad')
    solid.scad_render_to_file(bc, 'back-clip.scad')
    solid.scad_render_to_file(top_mold, 'top-mold.scad')
    solid.scad_render_to_file(bottom_mold, 'bottom-mold.scad')
    solid.scad_render_to_file(mold, 'mold.scad')

    if args.export:
        utils.export('shell', 'stl', args.resolution)
        utils.export('skirt', 'stl', args.resolution)
        utils.export('top-mold', 'stl', args.resolution)
        utils.export('bottom-mold', 'stl', args.resolution)
        utils.export('back-clip', 'stl', args.resolution)


main()
