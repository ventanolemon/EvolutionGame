"""Модуль HUD (интерфейс)"""
import arcade
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS


def draw_hud(score: int, timer: float):
    """Рисует интерфейс (счёт и таймер)"""
    # Счёт
    arcade.draw_text(
        f"Счёт: {score}", 25, SCREEN_HEIGHT - 25,
        COLORS["text"], font_size=20, bold=True
    )
    
    # Таймер
    timer_color = arcade.color.RED if timer < 10 else arcade.color.GREEN
    arcade.draw_text(
        f"⏱ Время: {timer:.1f}", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 25,
        timer_color, font_size=20, bold=True
    )


def draw_music_hint(music_enabled: bool):
    """Рисует подсказку управления музыкой"""
    music_status = "🔊" if music_enabled else "🔇"
    arcade.draw_text(
        f"{music_status} M — музыка", 25, 25,
        arcade.color.GRAY, font_size=12
    )


def draw_game_over(won: bool):
    """Рисует экран конца игры"""
    if won:
        arcade.draw_text(
            "🎉 ПОБЕДА! Киборг достигнут! 🎉",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            arcade.color.GOLD, font_size=28, anchor_x="center", bold=True
        )
        arcade.draw_text(
            "R — новая игра",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40,
            COLORS["text"], font_size=18, anchor_x="center"
        )
    else:
        arcade.draw_text(
            "😔 Игра окончена",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            arcade.color.RED, font_size=32, anchor_x="center", bold=True
        )
        arcade.draw_text(
            "R — новая игра",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40,
            COLORS["text"], font_size=18, anchor_x="center"
        )