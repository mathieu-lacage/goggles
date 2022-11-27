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
ELLIPSIS_HEIGHT = UNIT*1.3

# Dimensions for the back clip to attach the goggles with a silicon band.
BACK_CLIP_X = 12
BACK_CLIP_Y = 21
BACK_CLIP_THICKNESS = 2
BACK_CLIP_RADIUS = BACK_CLIP_THICKNESS/2

# Thickness of the skirt. The code does not generate
# a model which a constant skirt thickness but the thickness
# should be, on average, pretty close to this.
SKIRT_THICKNESS = 0.6
# Thickness of the skirt material when it is
# compressed by the lens. Increase if the material you use
# allows it (it is still possible to assemble the body, skirt, 
# lens, and clip) and if you want to increase the probability
# of having a waterproof skirt. When I made this value
# small than SKIRT_THICKNESS, I have never been able to assemble
# the skirt with the other pieces.
SKIRT_SQUASHED_THICKNESS = SKIRT_THICKNESS
SKIRT_RING_PADDING=0

TOOTH_WIDTH = UNIT/4
TOP_ATTACHMENT_WIDTH = 0.05
BOTTOM_ATTACHMENT_WIDTH = 0.04
SHELL_BOTTOM_HOLE_WIDTH = 8
SHELL_BOTTOM_HOLE_HEIGHT = 3

LENS_TOP_HEIGHT=1
LENS_GROOVE_DEPTH=1
LENS_BOTTOM_RING_WIDTH=2
LENS_BOTTOM_RING_HEIGHT=3-SHELL_THICKNESS-SKIRT_SQUASHED_THICKNESS
LENS_INNER_RING_WIDTH=1
LENS_GROOVE_HEIGHT=3-LENS_TOP_HEIGHT

SHELL_TOP_Y = -SHELL_THICKNESS
SHELL_TOP_X = LENS_BOTTOM_RING_WIDTH

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
MAX_HEIGHT = UNIT*3
MAX_WIDTH = UNIT*2.5




