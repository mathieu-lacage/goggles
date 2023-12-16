# the resolution of the resulting model. Use the command-line
# to override this value
NSTEPS = 40
# Some kind of scale-invariant length used a bit everywhere to define 
# other dimensions. Do not change this value. Instead, change the other
# variables
UNIT = 8
# The thickness of the outer shell. This value appears to be
# good enough for a wide range of material (PETG, PLA, and resin).
# I have never felt the need to change this value.
SHELL_THICKNESS = 1.2

# This should create a lens which covers much of a normal-sized eye.
# The half-length of the ellipsis for the lens along the horizontal axis
ELLIPSIS_WIDTH = UNIT*2
# The half-length of the ellipsis for the lens along the vertical axis
# theoretically, the ratio below should be 1.33 because
# typical human field of view ratio between vertical and horizontal field 
# of views is 1.5:1 but I chose 1.3 (call this luck because it is 
# pretty close to 1.333...) randomly initially and I did not want to redo
# all my prints
ELLIPSIS_HEIGHT = UNIT*1.3

# Dimensions for the back clip to attach the goggles with a silicon band.
BACK_CLIP_X = 12
BACK_CLIP_Y = 21
BACK_CLIP_THICKNESS = 2
BACK_CLIP_RADIUS = BACK_CLIP_THICKNESS/2

# Thickness of the skirt. The code does not generate
# a model with a constant skirt thickness but the thickness
# should be, on average, pretty close to this.
SKIRT_THICKNESS = 1
# Thickness of the skirt material when it is
# compressed by the lens. Increase if the material you use
# allows it (it is still possible to assemble the body, skirt, 
# lens, and clip) and if you want to increase the probability
# of having a waterproof skirt. 
# I have experimentally determined that, for the material I 
# use, 20% compression is good.
SKIRT_SQUASHED_THICKNESS = SKIRT_THICKNESS * 0.8
SKIRT_RING_PADDING = 0

TOOTH_WIDTH = 2.5*UNIT/4
TOP_ATTACHMENT_WIDTH = 0.05
BOTTOM_ATTACHMENT_WIDTH = 0.04
SHELL_BOTTOM_HOLE_WIDTH = 8
SHELL_BOTTOM_HOLE_HEIGHT = 3

LENS_TOP_HEIGHT = 0.5
LENS_GROOVE_DEPTH = 1
LENS_BOTTOM_RING_WIDTH = 2
LENS_INNER_RING_WIDTH = 1
LENS_GROOVE_HEIGHT = 1.2
LENS_BOTTOM_RING_HEIGHT = 0.8
LENS_VERTICAL_SQUASHINESS_OFFSET = SKIRT_THICKNESS-SKIRT_SQUASHED_THICKNESS
LENS_HORIZONTAL_SQUASHINESS_OFFSET = LENS_VERTICAL_SQUASHINESS_OFFSET
LENS_RADIUS=0.2
LENS_HEIGHT = LENS_BOTTOM_RING_HEIGHT+LENS_GROOVE_HEIGHT+LENS_TOP_HEIGHT+SHELL_THICKNESS+SKIRT_THICKNESS-LENS_VERTICAL_SQUASHINESS_OFFSET

SHELL_TOP_Y = -SHELL_THICKNESS
SHELL_TOP_X = LENS_BOTTOM_RING_WIDTH

SHELL_MIN_WIDTH = 2*SKIRT_THICKNESS
SHELL_MIN_HEIGHT = 5*SKIRT_THICKNESS

TOLERANCE = 0.1

#####################
# Constants you can change

# Control the shape of the outer shell and inner skirt.
# Lower XALPHA will make the shape less curvy and will
# decrease the internal volume of the skirt which will
# decrease the maximum depth you can dive to.
XALPHA = 0.95
YALPHA = XALPHA*0.03

# Control the size of the shell and skirt. Smaller values
# will decrease the internal volume of the skirt which will 
# decrease the maximum depth you can dive to. 
SHELL_MAX_HEIGHT = UNIT*3
SHELL_MAX_WIDTH = UNIT*2

# Mold bounding box dimensions. Adjust to what you have
MOLD_BB_X = 80
MOLD_BB_Y = 60
MOLD_BB_Z = 55
MOLD_RADIUS = 3
