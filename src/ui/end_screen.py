"""Экран конца игры"""
import arcade
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS


class EndScreen:
    def __init__(self, game_window):
        self.game = game_window

    def on_show(self):
        arcade.set_background_color(COLORS["background"])

    def on_hide(self):
        pass

    def draw(self):
        arcade.draw_text(
            "🎮 Игра завершена", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30,
            COLORS["text"], font_size=32, anchor_x="center"
        )
        arcade.draw_text(
            "Кликни или нажми ПРОБЕЛ для рестарта",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20,
            COLORS["text"], font_size=18, anchor_x="center"
        )

    def update(self, delta_time: float):
        pass

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.game.switch_screen("game")

    def on_mouse_press(self, x, y, button, modifiers):
        self.game.switch_screen("game")