"""Вспомогательные функции для игры"""
import math
import arcade
import os
from config import EVOLUTION_CHAIN, BG_COLORS


def lerp(start: float, end: float, t: float) -> float:
    """Линейная интерполяция: t=0 → start, t=1 → end"""
    return start + (end - start) * min(max(t, 0), 1)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Ограничивает значение диапазоном"""
    return max(min_val, min(value, max_val))


def load_evolution_textures() -> list:
    """Загружает текстуры для всех стадий эволюции"""
    textures = []
    for stage in EVOLUTION_CHAIN:
        try:
            if os.path.exists(stage["image"]):
                texture = arcade.load_texture(stage["image"])
                textures.append(texture)
                print(f"✓ {stage['image']}")
            else:
                print(f"⚠️ Не найдено: {stage['image']}, создаём заглушку")
                img = arcade.make_circle_texture(64, BG_COLORS[len(textures) % len(BG_COLORS)])
                textures.append(img)
        except Exception as e:
            print(f"⚠️ Ошибка загрузки {stage['image']}: {e}")
            img = arcade.make_circle_texture(64, BG_COLORS[len(textures) % len(BG_COLORS)])
            textures.append(img)
    return textures