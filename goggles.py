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

def argmax(l, key):
    m = max(enumerate(l), key=lambda item: key(item[1]))
    return m[0]

def argmin(l, key):
    m = min(enumerate(l), key=lambda item: key(item[1]))
    return m[0]

def ellipsis_perpendicular(a,b,t):
    p = utils.ellipsis(a,b,t)
    return euclid3.Point3(p.x/a**2, p.y/b**2)

def ellipsis_path():
    path = [utils.ellipsis(constants.ELLIPSIS_WIDTH, constants.ELLIPSIS_HEIGHT, t) for t in solid.utils.frange(0, 2*math.pi, constants.NSTEPS, include_end=False)]
    return path

def distance(alpha, threshold=0.5):
    d = alpha/threshold if alpha < threshold else (1-alpha)/(1-threshold)
    d = 1-(1-d)**2
    return d

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
    TOP_ATTACHMENT_RESOLUTION = 40
    BOTTOM_ATTACHMENT_RESOLUTION = 40

    def profile(i, n):
        alpha = i/n
        d = distance(alpha)
        curve = shell_curve(alpha).splinify()

        offset_curve = mg2.Path(path=curve)\
            .offset(constants.SHELL_THICKNESS, left=False)\
            .reverse()

        path = mg2.Path(path=curve)\
            .translate(dx=constants.SHELL_TOP_X)
        p2 = path.points.last + path.normal(left=False) * constants.SHELL_THICKNESS
        path.append(dy=constants.SHELL_THICKNESS)
        p1 = path.points.last + mg2.Point(x=1, y=0) * constants.SHELL_THICKNESS
        path.extend(path=mg2.Path(point=path.points.last)\
                .append(point=p1)\
                .append(point=p2)\
                .splinify()\
            )\
            .extend(path=offset_curve)\
            .append(x=constants.SHELL_TOP_X, y=constants.SHELL_TOP_Y)\
            .append(x=0)\
            .append(dy=constants.SHELL_THICKNESS-constants.SKIRT_THICKNESS/2)\
            .extend_arc(alpha=-math.pi/2, r=constants.SKIRT_THICKNESS/2)
        return utils.eu3(path.reversed_points)

    def top_attachment_profile(i, n):
        attachment_alpha = i/n
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


    path1 = ellipsis_path()
    shapes1 = [profile(i, len(path1)) for i in range(len(path1))]
    o = extrude_along_path(shapes1, path1, connect_ends=True)
#    o = solid.debug(o)

    path2 = [utils.ellipsis(constants.ELLIPSIS_WIDTH, constants.ELLIPSIS_HEIGHT, t) for t in solid.utils.frange(-constants.TOP_ATTACHMENT_WIDTH*2*math.pi, constants.TOP_ATTACHMENT_WIDTH*2*math.pi, TOP_ATTACHMENT_RESOLUTION)]
    shapes2 = [top_attachment_profile(i, len(path2)) for i in range(len(path2))]
    top_attachment = extrude_along_path(shapes2, path2)
    top_attachment = top_attachment -\
        solid.translate([constants.ELLIPSIS_WIDTH+constants.SHELL_TOP_X+constants.SHELL_THICKNESS+constants.TOOTH_WIDTH, 0, -10])(
            rounded_square(1.5*constants.SHELL_THICKNESS, 1.5*constants.SHELL_THICKNESS, 20, constants.SHELL_THICKNESS/2)
        )

    o = o + top_attachment

    BOTTOM_ATTACHMENT_HEIGHT = 5
    def bottom_attachment_profile(i, n):
        attachment_alpha = i / n 
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
        
    path3 = [utils.ellipsis(constants.ELLIPSIS_WIDTH, constants.ELLIPSIS_HEIGHT, t) for t in solid.utils.frange(math.pi-constants.BOTTOM_ATTACHMENT_WIDTH*2*math.pi, math.pi+constants.BOTTOM_ATTACHMENT_WIDTH*2*math.pi, BOTTOM_ATTACHMENT_RESOLUTION)]
    shapes3 = [bottom_attachment_profile(i, len(path3)) for i in range(len(path3))]
    bottom_attachment = extrude_along_path(shapes3, path3)

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


def skirt_profile(i, n):
    alpha = i / n
    curve = shell_curve(alpha)
    zero = shell_curve(0)
    path = mg2.Path(path=curve.splinify())\
        .translate(constants.SHELL_TOP_X, 0)
    if False:
        silicon_skirt_height = 0.75*constants.UNIT
        silicon_skirt_width = constants.SHELL_TOP_X+zero.width+curve.width/3
        tmp = mg2.Path(x=0, y=0)\
            .append(dy=silicon_skirt_height)\
            .append(dx=-silicon_skirt_width)\
            .append(dy=-silicon_skirt_height/2)\
            .splinify()
    else:
        silicon_skirt_height = 0.5*constants.UNIT
        silicon_skirt_width = constants.SHELL_TOP_X+zero.width+curve.width/3
        tmp = mg2.Path(x=0, y=0)\
            .append(dy=silicon_skirt_height)\
            .append(dx=-silicon_skirt_width)\
            .append(dy=silicon_skirt_width)\
            .append(dx=(constants.SHELL_TOP_X+zero.width)*(1-distance(alpha)))\
            .splinify()
#            .append(dx=constants.SHELL_TOP_X+zero.width)\
    path.extend(path=tmp)
    return_path = path.copy().reverse().offset(constants.SKIRT_THICKNESS, left=False)
#append_angle(alpha=math.pi/2, delta=constants.SKIRT_THICKNESS)\
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
    #o = solid.debug(o)
    return o


def alignment_pin(x, y, z):
    Pin = collections.namedtuple('Pin', ['male', 'female'])
    pin_height = 3
    pin_radius = 1.5
    epsilon = 0.001
    def pin(height, radius):
        filet_radius = 0.5
        profile = mg2.Path(x=radius, y=0)\
            .append(dy=height-filet_radius)\
            .extend_arc(alpha=math.pi/2, r=filet_radius)
        path = [euclid3.Point3(x=math.cos(t), y=math.sin(t), z = 0) for t in solid.utils.frange(0, 2*math.pi, constants.NSTEPS, include_end=False)]
        shapes = [utils.eu3(profile.points) for i in range(len(path))]
        o = extrude_along_path(shapes, path, connect_ends=True)
        o = solid.hull()(o)
        o = solid.rotate([-90, 0, 0])(o)
        return o
    male = pin(pin_height, pin_radius)
    female = pin(pin_height+0.1, pin_radius+0.1)
    male = solid.translate([x, y, z])(male)
    female = solid.translate([x, y, z])(female)
    return Pin(male=male, female=female)


MOLD_PADDING = 10
MOLD_Y_TOP = -MOLD_PADDING
SPRUE_TOP_RADIUS = 1.5
SPRUE_BOT_RADIUS = 2
SPRUE_SLUG_LENGTH = 2
SPRUE_HEIGHT = MOLD_PADDING+2
RING_RUNNER_RADIUS = 1
RING_GATE_LAND_LENGTH = 0.5
RING_GATE_LAND_THICKNESS = 0.5

def skirt_mold():
    epsilon = 0.001
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
    middle_shape = exterior_shapes[int(len(exterior_shapes)/4)]
    max_skirt_x = max([p.max_x for p in exterior_shapes])
    max_skirt_y = max([p.max_y for p in exterior_shapes])
    mold_left_x = -(constants.ELLIPSIS_WIDTH + max_skirt_x)
    mold_right_x = constants.ELLIPSIS_WIDTH + max([p.x for p in exterior_shapes[0].points])

    # exterior mold bounding box
    tmp = max([p.x for p in middle_shape.points])
    exterior_bounding_box = solid.translate([mold_left_x-MOLD_PADDING, -tmp-2*MOLD_PADDING, -MOLD_PADDING])(solid.cube([
        mold_right_x-mold_left_x+2*MOLD_PADDING,
        2*tmp+4*MOLD_PADDING,
        max_skirt_y+2*MOLD_PADDING
    ]))

    # exterior mold
    a = exterior_mold(exterior_shapes, max_skirt_x, max_skirt_y)
    a = solid.intersection()([a, exterior_bounding_box])
    bottom = a - solid.translate([-100,0,-100])(solid.cube([200,200,200]))
    top = a - solid.translate([-100,-200,-100])(solid.cube([200,200,200]))

    # basic interior mold with feeder holes
    b = interior_mold(interior_shapes, max_skirt_y)
    c = feeder(exterior_shapes[0].points[0], exterior_shapes[int(constants.NSTEPS/2)].points[0])
    b = b - c

    # split interior mold in 4 parts
    interior_top = solid.intersection()([
        b, 
        solid.translate([-50, -100, -100-constants.SHELL_THICKNESS+RING_GATE_LAND_THICKNESS/2])(solid.cube([100, 100, 100]))
    ])
    interior_cone_thickness = constants.SKIRT_THICKNESS+RING_GATE_LAND_LENGTH+RING_RUNNER_RADIUS*2*2
    interior_cone = utils.ring(200, -interior_cone_thickness)
    interior_cone = solid.translate([0, 0, -200])(interior_cone)
    interior_top_a = interior_top - interior_cone
    interior_top_b = solid.intersection()([interior_top, interior_cone])

    interior_tmp = b - solid.translate([-50, -100, -100-constants.SHELL_THICKNESS+RING_GATE_LAND_THICKNESS/2])(solid.cube([100, 100, 100]))
    interior_bottom_tmp = solid.translate([-50, -epsilon, -100-constants.SHELL_THICKNESS+RING_GATE_LAND_THICKNESS/2])(solid.cube([100, 100, 100])) - interior_cone
    interior = interior_tmp - interior_bottom_tmp
    interior_bottom = solid.intersection()([interior_tmp, interior_bottom_tmp])

    # pins
    pin_left_x = mold_left_x - MOLD_PADDING/2
    pin_right_x = mold_right_x + MOLD_PADDING/2
    pin_top_z = MOLD_Y_TOP/2
    pin_middle_z = middle_shape.points[-1].y + MOLD_PADDING
    pin_bottom_z = max_skirt_y + MOLD_PADDING/2
    pin_top_y = constants.ELLIPSIS_HEIGHT-constants.SKIRT_THICKNESS
    pin_top_padding = 0.3
    pin_middle_padding = 1
    pin_bottom_padding = pin_middle_padding
    pin_middle_y = constants.ELLIPSIS_HEIGHT+middle_shape.points[-1].x
    pin_bottom_y = pin_middle_y
    pin_topa_y = constants.ELLIPSIS_HEIGHT-interior_cone_thickness-0.1 # XXX: not sure why I need a -0.1 here
    pin_topb_left_x = -(constants.ELLIPSIS_WIDTH-interior_cone_thickness)/2
    pin_topb_right_x = -pin_topb_left_x

    for z in [pin_top_z, pin_middle_z, pin_bottom_z]:
        pin = alignment_pin(pin_left_x, 0-epsilon, z)
        bottom = bottom + pin.male
        top = top - pin.female
    for z in [pin_top_z, pin_middle_z, pin_bottom_z]:
        pin = alignment_pin(pin_right_x, 0-epsilon, z)
        bottom = bottom + pin.male
        top = top - pin.female

    pin = alignment_pin(0, -pin_top_y-pin_top_padding-epsilon, pin_top_z)
    bottom = bottom + pin.male
    interior_top_a = interior_top_a - pin.female

    pin = alignment_pin(0, -pin_middle_y-pin_middle_padding-epsilon, pin_middle_z)
    bottom = bottom + pin.male
    interior = interior - pin.female

    pin = alignment_pin(0, -pin_bottom_y-pin_bottom_padding-epsilon, pin_bottom_z)
    bottom = bottom + pin.male
    interior = interior - pin.female

    pin = alignment_pin(0, -pin_topa_y-epsilon, pin_top_z)
    interior_top_a = interior_top_a + pin.male
    interior_top_b = interior_top_b - pin.female

    pin = alignment_pin(pin_topb_left_x, 0-epsilon, pin_top_z)
    interior_top_b = interior_top_b + pin.male
    interior = interior - pin.female

    pin = alignment_pin(pin_topb_right_x, 0-epsilon, pin_top_z)
    interior_top_b = interior_top_b + pin.male
    interior = interior - pin.female

    pin = alignment_pin(0, pin_topa_y-epsilon, pin_top_z)
    interior = interior + pin.male
    interior_bottom = interior_bottom - pin.female
    
    pin = alignment_pin(0, pin_top_y-pin_top_padding-epsilon, pin_top_z)
    interior_bottom = interior_bottom + pin.male
    top =  top - pin.female

    pin = alignment_pin(0, pin_middle_y-pin_middle_padding-epsilon, pin_middle_z)
    interior = interior + pin.male
    top = top - pin.female

    pin = alignment_pin(0, pin_bottom_y-pin_bottom_padding-epsilon, pin_bottom_z)
    interior = interior + pin.male
    top = top - pin.female

    return bottom, top, interior, interior_top_a, interior_top_b, interior_bottom


def normalize_shapes(shapes):
    maxlen = max([len(shape) for shape in shapes])
    for shape in shapes:
        for i in range(len(shape), maxlen):
            shape.append(shape[-1])
    shapes = [mg2.Path(path=shape) for shape in shapes]
    return shapes


def feeder(a, b):
    FEEDER_RUNNER_LENGTH = constants.ELLIPSIS_WIDTH*2-constants.LENS_BOTTOM_RING_WIDTH-3/2*constants.SKIRT_THICKNESS-RING_GATE_LAND_LENGTH-RING_RUNNER_RADIUS
    FEEDER_RUNNER_RADIUS = RING_RUNNER_RADIUS
    NOZZLE_TOP_RADIUS = 8
    NOZZLE_BOT_RADIUS = 2
    NOZZLE_HEIGHT = 6

    nozzle = solid.cylinder(h=NOZZLE_HEIGHT, r1=NOZZLE_TOP_RADIUS, r2=NOZZLE_BOT_RADIUS, segments=20)
    nozzle = solid.translate([0, 0, -SPRUE_HEIGHT-constants.SHELL_THICKNESS+SPRUE_SLUG_LENGTH-0.66*NOZZLE_HEIGHT])(nozzle)
    sprue = solid.cylinder(h=SPRUE_HEIGHT, r1=SPRUE_TOP_RADIUS, r2=SPRUE_BOT_RADIUS, segments=20)
    sprue = solid.translate([0, 0, -SPRUE_HEIGHT-constants.SHELL_THICKNESS+SPRUE_SLUG_LENGTH])(sprue)
    feeder_runner = solid.cylinder(h=FEEDER_RUNNER_LENGTH, r=FEEDER_RUNNER_RADIUS, segments=20)
    feeder_runner = solid.rotate([0, 90, 0])(feeder_runner)
    feeder_runner = solid.translate([-FEEDER_RUNNER_LENGTH/2, 0, -constants.SHELL_THICKNESS+RING_GATE_LAND_THICKNESS/2])(feeder_runner)

    def ring_gate_profile(i, n):
        alpha = i / n
        epsilon = 0.001
        p = mg2.Path(x=-3/2*constants.SKIRT_THICKNESS+epsilon, y=-constants.SHELL_THICKNESS)\
            .append(dx=-RING_GATE_LAND_LENGTH-epsilon)\
            .append(dy=RING_GATE_LAND_THICKNESS)\
            .append(dx=RING_GATE_LAND_LENGTH+epsilon*2)
        return utils.eu3(p.reversed_points)
    path = ellipsis_path()
    ring_gate_shapes = [ring_gate_profile(i, len(path)) for i in range(len(path))]
    ring_gate = extrude_along_path(ring_gate_shapes, path, connect_ends=True)

    def ring_runner_profile(i, n):
        alpha = i / n
        epsilon = 0.001
        offset = RING_RUNNER_RADIUS-math.sqrt(RING_RUNNER_RADIUS**2-(RING_GATE_LAND_THICKNESS/2)**2)
        p = mg2.Path(x=-3/2*constants.SKIRT_THICKNESS-RING_GATE_LAND_LENGTH+offset+epsilon, y=-constants.SHELL_THICKNESS+RING_GATE_LAND_THICKNESS/2)\
            .extend_arc(alpha=2*math.pi, r=RING_RUNNER_RADIUS, reference=mg2.Point(x=0, y=1), n=20)
        return utils.eu3(p.points)
    path = ellipsis_path()
    ring_runner_shapes = [ring_runner_profile(i, len(path)) for i in range(len(path))]
    ring_runner = extrude_along_path(ring_runner_shapes, path, connect_ends=True)
    
    return nozzle + sprue + ring_gate + ring_runner + feeder_runner


def interior_mold(interior_shapes, max_skirt_y):
    air_vent_thickness = constants.SKIRT_THICKNESS/2
    path = ellipsis_path()

    bottom = [shape.points[0] for shape in interior_shapes]
    outer_most = argmax(bottom, key=lambda i: i.x)
    delta = int(5*constants.NSTEPS/100)
    air_vent_path = path[outer_most-delta+1:outer_most+delta]
    air_vent_shapes = []
    for b in bottom[outer_most-delta+1:outer_most+delta]:
        p = mg2.Path(x=b.x+0.2, y=b.y-0.1)
        p.append(y=max_skirt_y+MOLD_PADDING+1)
        p.append(dx=-air_vent_thickness-0.2)
        p.append(y=b.y-0.1)
        air_vent_shapes.append(utils.eu3(p.points))
    air_vent = extrude_along_path(air_vent_shapes, air_vent_path)


    output = []
    for shape in interior_shapes:
        shape.append(y=MOLD_Y_TOP)
        shape.append(x=-2)
        shape.append(y=max_skirt_y+MOLD_PADDING)
        shape.append(x=shape.points[0].x)
        output.append(utils.eu3(shape.reversed_points))
        #print(top, bottom, len(interior), len(exterior))


    o = extrude_along_path(output, path, connect_ends=True)
    o = o - air_vent

    epsilon = 0.01
    filler = utils.ring(max_skirt_y-MOLD_Y_TOP+MOLD_PADDING+2*epsilon, -constants.SKIRT_THICKNESS-1)
    filler = solid.translate([0, 0, -MOLD_PADDING-epsilon])(filler)
#    filler = solid.debug(filler)
    o = o + filler

    return o


def exterior_mold(exterior_shapes, max_skirt_x, max_skirt_y):
    output = []
    for shape in exterior_shapes:
        shape = shape.copy()
        shape.append(y=max_skirt_y+50)
        shape.append(x=max_skirt_x+50)
        shape.append(y=MOLD_Y_TOP)
        shape.append(x=shape.points[0].x)
        output.append(utils.eu3(shape.reversed_points))
        #print(top, bottom, len(interior), len(exterior))
        
    path = ellipsis_path()
    o = extrude_along_path(output, path, connect_ends=True)
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
    l = lens.lens()
#    l = solid.translate([-0.2, 0, 0.05])(l)
    lc = lens.lens_clip(constants.LENS_GROOVE_HEIGHT, 3, math.pi/4)
    bc = back_clip()
    bottom_mold, top_mold, interior_mold, interior_mold_top_a, interior_mold_top_b, interior_mold_bottom = skirt_mold()
    mold = bottom_mold + interior_mold + interior_mold_bottom

    output = sk + sh# + lc + l
    if args.slice_a is not None or args.slice_x is not None or args.slice_y is not None or args.slice_z is not None:
        if args.slice_a is not None:
            cut = solid.rotate([0,0,args.slice_a])(solid.translate([-100,0,-100])(solid.cube([200,200,200])))
        else:
            cut = solid.cube([0,0,0])
        if args.slice_x is not None:
            cut = cut + solid.translate([args.slice_x,-50,-100])(solid.cube([200,200,200]))
        if args.slice_y is not None:
            cut = cut + solid.translate([-100,args.slice_y,-100])(solid.cube([200,200,200]))
        if args.slice_z is not None:
            cut = cut + solid.translate([-100,-50,args.slice_z])(solid.cube([200,200,200]))
        lc = lc - cut
        sh = sh - cut
        sk = sk - cut
        l = l - cut
        bottom_mold = bottom_mold - cut
        top_mold = top_mold - cut
        interior_mold = interior_mold - cut
        interior_mold_top_a = interior_mold_top_a - cut
        interior_mold_top_b = interior_mold_top_b - cut
        interior_mold_bottom = interior_mold_bottom - cut
        mold = mold - cut
        output = output - cut

    solid.scad_render_to_file(output, 'goggles.scad')
    solid.scad_render_to_file(sh, 'shell.scad')
    solid.scad_render_to_file(sk, 'skirt.scad')
    solid.scad_render_to_file(bc, 'back-clip.scad')
    solid.scad_render_to_file(interior_mold_top_a, 'interior-mold-top-a.scad')
    solid.scad_render_to_file(interior_mold_top_b, 'interior-mold-top-b.scad')
    solid.scad_render_to_file(interior_mold_bottom, 'interior-mold-bottom.scad')
    solid.scad_render_to_file(interior_mold, 'interior-mold.scad')
    solid.scad_render_to_file(bottom_mold, 'bottom-mold.scad')
    solid.scad_render_to_file(top_mold, 'top-mold.scad')
    solid.scad_render_to_file(mold, 'mold.scad')

    if args.export:
        utils.export('shell', 'stl')
        utils.export('skirt', 'stl')
        utils.export('top-mold', 'stl')
        utils.export('bottom-mold', 'stl')
        utils.export('interior-mold', 'stl')
        utils.export('interior-mold-top-a', 'stl')
        utils.export('interior-mold-top-b', 'stl')
        utils.export('interior-mold-bottom', 'stl')
        utils.export('back-clip', 'stl')


main()
