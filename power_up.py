import arcade
from PIL import Image, ImageDraw

from constants import *


def _make_power_up_texture(color):
    """ A small glowing circle, colored per power-up type. """
    image = Image.new("RGBA", (POWER_UP_SIZE, POWER_UP_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse([1, 1, POWER_UP_SIZE - 2, POWER_UP_SIZE - 2], fill=color)
    draw.ellipse([0, 0, POWER_UP_SIZE - 1, POWER_UP_SIZE - 1],
                 outline=(255, 255, 255, 255))
    return arcade.Texture(image)


class PowerUp(arcade.Sprite):
    """ A falling power-up dropped by a killed enemy (extra.md pkt 4). """

    def __init__(self, power_type, center_x, center_y):
        super().__init__()
        self.power_type = power_type
        self.texture = _make_power_up_texture(POWER_UP_COLORS[power_type])
        self.change_y = -POWER_UP_FALL_SPEED
        self.center_x = center_x
        self.center_y = center_y

    def update(self, delta_time):
        # change_y is applied only when super().update() is called
        # (arcade 3.x gotcha, see AGENTS.md).
        super().update(delta_time)
