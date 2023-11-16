
# Basic window and render size.
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
RENDER_WIDTH = 320
RENDER_HEIGHT = 180
FRAME_RATE = 60

# What rendering engine to use.
USE_OPENGL = False

# How many subpixels to use for game logic.
SUBPIXELS = 16

# Rendering details.
MAX_LIGHTS = 20

# How quickly should the viewport pan to where it wants to be.
VIEWPORT_PAN_SPEED = 5 * SUBPIXELS

# Horizontal speed.
TARGET_WALK_SPEED = 24 * SUBPIXELS//16
WALK_SPEED_ACCELERATION = 1 * SUBPIXELS//16
WALK_SPEED_DECELERATION = 3 * SUBPIXELS//16
SLIDE_SPEED_DECELERATION = 1 * SUBPIXELS//16

# Vertical speed.
COYOTE_TIME = 6       # How long to hover in the air before officially falling.
JUMP_GRACE_TIME = 12  # How long to remember jump was pressed while falling.
JUMP_INITIAL_SPEED = 48 * SUBPIXELS//16
JUMP_ACCELERATION = 2 * SUBPIXELS//16
JUMP_MAX_GRAVITY = 32 * SUBPIXELS//16
FALL_ACCELERATION = 5 * SUBPIXELS//16
FALL_MAX_GRAVITY = 32 * SUBPIXELS//16

# Wall sliding.
WALL_SLIDE_SPEED = 4 * SUBPIXELS//16
WALL_JUMP_HORIZONTAL_SPEED = 48 * SUBPIXELS//16
WALL_JUMP_VERTICAL_SPEED = 48 * SUBPIXELS//16
WALL_STICK_TIME = 30
WALL_SLIDE_TIME = 60

# Player appearance.
IDLE_TIME = 240              # How long before showing idle animation.
PLAYER_FRAMES_PER_FRAME = 8  # How fast to animate the player.

# How the "toast" text pops up at the top of the screen.
TOAST_TIME = 150
TOAST_HEIGHT = 12 * SUBPIXELS
TOAST_SPEED = 8 * SUBPIXELS//16

# Button switches.
BUTTON_DELAY = 2                     # How slowly the button goes down.
BUTTON_MAX_LEVEL = BUTTON_DELAY * 3  # There are 4 frames of animation.

# Falling platforms that look like bagels.
BAGEL_WAIT_TIME = 30
BAGEL_FALL_TIME = 150
BAGEL_MAX_GRAVITY = 11 * SUBPIXELS//16
BAGEL_GRAVITY_ACCELERATION = 1

# Springs that bounce you.
SPRING_STEPS = 4                   # This should match the spring animation.
SPRING_STALL_FRAMES = 10           # How long the spring stays at the bottom.
SPRING_SPEED = 16 * SUBPIXELS//16  # How fast the spring itself moves.
SPRING_BOUNCE_DURATION = 30        # How long to jump when bouncing.
SPRING_BOUNCE_VELOCITY = JUMP_INITIAL_SPEED
SPRING_JUMP_DURATION = 10          # How long to jump when jumping from spring.
SPRING_JUMP_VELOCITY = 78 * SUBPIXELS//16

# Doors.
DOOR_SPEED = 3
DOOR_CLOSING_FRAMES = 9    # The should match the door animation frames.
DOOR_UNLOCKING_FRAMES = 9
