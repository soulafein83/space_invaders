import arcade
from PIL import Image, ImageDraw

from constants import *


def _make_ufo_texture():
    """ Draw the mystery ship at runtime: red body + light dome. """
    width, height = 40, 16
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse([0, 6, width - 1, height - 1], fill=(255, 40, 40, 255))
    draw.ellipse([12, 0, 27, 10], fill=(255, 190, 190, 255))
    return arcade.Texture(image)


class UFO(arcade.Sprite):
    """ Mystery ship that crosses the top of the formation (extra.md pkt 3). """

    def __init__(self):
        super().__init__()
        self.texture = _make_ufo_texture()
        self.scale = 3
        self.score = 0

    def update(self, delta_time):
        # change_x is applied only when super().update() is called
        # (arcade 3.x gotcha, see AGENTS.md).
        super().update(delta_time)
