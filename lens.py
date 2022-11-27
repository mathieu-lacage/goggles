import solid

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
