SPRITE_SCALING_PLAYER = 6
SPRITE_SCALING_ENEMY = 6
SPRITE_SCALING_LASER = 6

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Space Invaders"

PLAYER_BULLET_SPEED = 8
BULLET_SPEED = 4
ENEMY_SPEED = 1.5

# Keyboard movement: pixels per frame while an arrow key is held down.
PLAYER_KEYBOARD_SPEED = 8

MAX_PLAYER_BULLETS = 3
MAX_ENEMY_BULLETS = 5

DEATH_PAUSE_TIME = 0.85

# Level scaling: each cleared level makes the next one harder.
LEVEL_CLEAR_TIME = 2.0          # seconds of the "LEVEL CLEAR" banner
ENEMY_SPEED_GROWTH = 0.2        # +20% enemy speed per level
BULLET_SPEED_GROWTH = 1         # +1 px/frame enemy bullet speed per level
MAX_BULLET_SPEED = 8
FIRE_CHANCE_BASE = 30           # base of the per-frame fire roll
FIRE_CHANCE_GROWTH = 2          # -2 (more likely to fire) per level
MIN_FIRE_CHANCE = 10

# A live enemy whose bottom edge drops to this y = game over (classic rule).
ENEMY_BOTTOM_LIMIT = 110

# Mystery ship (UFO): crosses the top of the formation once in a while.
UFO_SPEED = 3                  # px/frame while crossing the screen
UFO_Y = 640                    # flight altitude (above the enemy rows)
UFO_SPAWN_MIN = 20             # seconds until the next UFO can appear
UFO_SPAWN_MAX = 35
UFO_SCORES = (50, 100, 150, 300)

# Power-ups: killed enemies may drop one; it falls down and is
# activated when the player touches it.
POWER_UP_CHANCE = 10           # % chance a kill drops a power-up
POWER_UP_SIZE = 18             # texture size in px
POWER_UP_FALL_SPEED = 3        # px/frame while falling
POWER_UP_DURATION = 10         # seconds for timed effects (double/rapid/slow)
POWER_UP_TYPES = ("double", "rapid", "life", "shield", "slow")
POWER_UP_COLORS = {
    "double": (255, 165, 0),    # orange
    "rapid": (255, 255, 0),     # yellow
    "life": (255, 0, 0),        # red
    "shield": (0, 120, 255),    # blue
    "slow": (160, 32, 240),     # purple
}
PLAYER_SHOOT_COOLDOWN = 0.4    # seconds between player shots (base)
RAPID_SHOOT_COOLDOWN = 0.15    # cooldown while the rapid power-up is active
SLOW_FACTOR = 0.5              # enemy speed multiplier while "slow" is active
DOUBLE_BULLET_OFFSET = 12      # px left/right offset of the twin bullets

# This margin controls how close the enemy gets to the left or right side
# before reversing direction.
ENEMY_HORIZONTAL_MARGIN = 15
RIGHT_ENEMY_BORDER = SCREEN_WIDTH - ENEMY_HORIZONTAL_MARGIN
LEFT_ENEMY_BORDER = ENEMY_HORIZONTAL_MARGIN

# How many pixels to move the enemy down when reversing
ENEMY_MOVE_DOWN_AMOUNT = 30

# Game state
GAME_OVER = 1
PLAY_GAME = 0

PLAYER_COLOR = 24, 255, 24
