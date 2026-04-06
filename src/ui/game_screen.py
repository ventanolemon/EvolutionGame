"""Основной игровой экран"""
import arcade
from config import *
from src.game.board import GameBoard
from src.game.particles import ParticleSystem


class GameScreen:
    def __init__(self, game_window):
        self.game = game_window
        self.board = GameBoard()
        self.particles = ParticleSystem()
        self.game_over = False

    def on_show(self):
        self.board.reset()
        arcade.set_background_color(COLORS["background"])

    def on_hide(self):
        pass

    def draw(self):
        # Рисуем сетку
        for row in range(ROWS + 1):
            y = SCREEN_HEIGHT - 30 - row * (TILE_SIZE + 15)
            arcade.draw_line(15, y, SCREEN_WIDTH - 15, y, COLORS["grid"], 2)
        for col in range(COLS + 1):
            x = 15 + col * (TILE_SIZE + 15)
            arcade.draw_line(x, SCREEN_HEIGHT - 30, x, 30, COLORS["grid"], 2)

        # Рисуем плитки
        for tile in self.board.tiles.values():
            tile.draw()

        # Рисуем счёт
        arcade.draw_text(
            f"Счёт: {self.board.score}", 20, SCREEN_HEIGHT - 25,
            COLORS["text"], font_size=18, bold=True
        )

        # Эффекты частиц
        self.particles.draw()

        # Сообщение о победе/поражении
        if self.board.won:
            arcade.draw_text("🎉 ПОБЕДА! 🎉", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                             arcade.color.GOLD, font_size=36, anchor_x="center")
        elif self.board.game_over:
            arcade.draw_text("😔 ИГРА ОКОНЧЕНА", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                             arcade.color.RED, font_size=32, anchor_x="center")

    def update(self, delta_time: float):
        if not self.game_over:
            for tile in self.board.tiles.values():
                tile.update()
            self.particles.update()

            # Проверка конца игры
            if self.board.is_full() and not self.board.has_moves():
                self.board.game_over = True
                self.game.play_sound("lose")

    def on_key_press(self, key, modifiers):
        if self.game_over or self.board.won:
            if key == arcade.key.R:
                self.on_show()  # Рестарт
            return

        # Управление стрелками
        direction_map = {
            arcade.key.LEFT: "left",
            arcade.key.RIGHT: "right",
            arcade.key.UP: "up",
            arcade.key.DOWN: "down"
        }
        if key in direction_map:
            moved, merged = self.board.move_direction(direction_map[key])
            if moved:
                self.game.play_sound("move")
            if merged:
                self.game.play_sound("merge")
                # Эффект частиц при слиянии
                for tile in self.board.tiles.values():
                    if tile.merge_effect:
                        self.particles.emit(
                            tile.center_x, tile.center_y, arcade.color.GOLD
                        )

    def on_mouse_press(self, x, y, button, modifiers):
        pass  # Можно добавить свайпы позже