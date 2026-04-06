"""Стартовый экран"""
import arcade
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, FONT_COLOR


class StartScreen:
    def __init__(self, game_window):
        self.game = game_window
        self.title = "🧬 ЭВОЛЮЦИЯ"
        self.subtitle = "Нажми ПРОБЕЛ чтобы начать"

    def on_show(self):
        arcade.set_background_color(COLORS["background"])

    def on_hide(self):
        pass

    def draw(self):
        arcade.draw_text(
            self.title, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
            COLORS["text"], font_size=48, anchor_x="center", bold=True
        )
        arcade.draw_text(
            self.subtitle, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20,
            COLORS["text"], font_size=24, anchor_x="center"
        )

    def update(self, delta_time: float):
        pass

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.game.switch_screen("game")

    def on_mouse_press(self, x, y, button, modifiers):
        self.on_key_press(arcade.key.SPACE, None)