"""Глобальные константы проекта"""
import arcade

# Окно
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 900
SCREEN_TITLE = "🧬 Эволюция"
FPS = 60

# Сетка
ROWS = 4
COLS = 4
TILE_MARGIN = 15
TILE_SIZE = (SCREEN_WIDTH - TILE_MARGIN * (COLS + 1)) // COLS

# Цвета
COLORS = {
    "background": arcade.color.ECRU,
    "grid": arcade.color.BROWN,
    "empty_tile": arcade.color.LIGHT_GRAY,
    "text": arcade.color.DARK_BROWN,
    "button": arcade.color.ROYAL_BLUE,
    "button_hover": arcade.color.DODGER_BLUE,
}

# Эволюция
EVOLUTION_CHAIN = [
    {"name": "Амеба", "image": "amoeba.png", "value": 2},
    {"name": "Рыба", "image": "fish.png", "value": 4},
    {"name": "Лягушка", "image": "frog.png", "value": 8},
    {"name": "Ящерица", "image": "lizard.png", "value": 16},
    {"name": "Птица", "image": "bird.png", "value": 32},
    {"name": "Заяц", "image": "hare.png", "value": 64},
    {"name": "Волк", "image": "wolf.png", "value": 128},
    {"name": "Медведь", "image": "bear.png", "value": 256},
    {"name": "Человек", "image": "human.png", "value": 512},
    {"name": "Киборг", "image": "cyborg.png", "value": 1024},
]

# Звуки
SOUNDS = {
    "move": "assets/sounds/move.wav",
    "merge": "assets/sounds/merge.wav",
    "win": "assets/sounds/win.wav",
    "lose": "assets/sounds/lose.wav",
    "bg_music": "assets/sounds/background.mp3",
}