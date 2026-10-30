import arcade

import game_view
import highscore


class InstructionView(arcade.View):
    """ View to show instructions """

    def on_show_view(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.csscolor.BLACK)
        self.high_score = highscore.load_high_score()

    def on_draw(self):
        """ Draw this view """
        arcade.draw_text("Space Invaders", self.window.width / 2, self.window.height / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Click to Start", self.window.width / 2, self.window.height / 2-75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")
        arcade.draw_text("or Press Space", self.window.width / 2, self.window.height / 2 - 95,
                         arcade.color.WHITE, font_size=20, anchor_x="center")
        arcade.draw_text(f"High Score: {self.high_score:04}", self.window.width / 2,
                         self.window.height / 2 + 60,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, button, _modifiers):
        """ If the user presses the left mouse button, start the game. """
        # Ignore right/middle button presses
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        self.start_game()

    def on_key_press(self, symbol: int, modifiers: int):
        """ Space starts the game, just like a click. """
        if symbol == arcade.key.SPACE:
            self.start_game()

    def start_game(self):
        my_game_view = game_view.GameView()
        my_game_view.setup()
        self.window.show_view(my_game_view)
