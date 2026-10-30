import arcade

import game_view


class InstructionView(arcade.View):
    """ View to show instructions """

    def on_show_view(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.csscolor.BLACK)

    def on_draw(self):
        """ Draw this view """
        arcade.draw_text("Space Invaders", self.window.width / 2, self.window.height / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Click to Start", self.window.width / 2, self.window.height / 2-75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, button, _modifiers):
        """ If the user presses the left mouse button, start the game. """
        # Ignore right/middle button presses
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        my_game_view = game_view.GameView()
        my_game_view.setup()
        self.window.show_view(my_game_view)
