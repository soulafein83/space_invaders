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
