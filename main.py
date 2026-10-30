import arcade

from constants import *
from game_view import GameView
from instruction_view import InstructionView


def main():
    # Register the bundled "Kenney Rocket" font (arcade 3.3.3 ships it under the
    # :system: handle but has no arcade.load_kenney_fonts() helper). Without this
    # call, arcade.draw_text(font_name="Kenney Rocket") silently falls back to the
    # system default font (see error.md, E9).
    arcade.load_font(":system:fonts/ttf/Kenney/Kenney_Rocket.ttf")

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
