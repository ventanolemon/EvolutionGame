"""Модуль плитки эволюции"""
import arcade
import os
from config import TILE_SIZE, TILE_MARGIN, SCREEN_HEIGHT
from src.game.evolution_chain import EVOLUTION_CHAIN, BG_COLORS
from src.utils.helpers import load_evolution_textures

EVOLUTION_TEXTURES = load_evolution_textures()


def get_cell_center(row: float, col: float) -> tuple[float, float]:
    """Вычисляет центр ячейки сетки"""
    x = TILE_MARGIN + col * (TILE_SIZE + TILE_MARGIN) + TILE_SIZE // 2
    y = SCREEN_HEIGHT - TILE_MARGIN - row * (TILE_SIZE + TILE_MARGIN) - TILE_SIZE // 2
    return x, y


class EvolutionTile(arcade.Sprite):
    """Плитка-спрайт с животным и анимацией"""

    def __init__(self, stage_index: int, row: int, col: int, animate_spawn: bool = True):
        texture = EVOLUTION_TEXTURES[stage_index]

        if texture.width > 0 and texture.height > 0:
            scale = (TILE_SIZE * 0.75) / max(texture.width, texture.height)
        else:
            scale = 1.0

        super().__init__(texture, scale=scale)

        self.stage_index = stage_index
        self.row = row
        self.col = col
        self.vrow = float(row)
        self.vcol = float(col)
        self.trow = row
        self.tcol = col

        self.is_moving = False
        self.progress = 0.0
        self.move_speed = 0.18
        self.merge_effect = False
        self.merge_timer = 0
        self.spawn_anim = animate_spawn
        self.spawn_scale = 0.0 if animate_spawn else 1.0

        self.center_x, self.center_y = get_cell_center(row, col)
        self.bg_color = BG_COLORS[stage_index % len(BG_COLORS)]
        self._marked_for_removal = False

    def start_move_to(self, row: int, col: int):
        """Начинает движение к целевой позиции"""
        if self.row == row and self.col == col:
            return
        self.trow, self.tcol = row, col
        self.is_moving = True
        self.progress = 0.0

    def on_merge(self):
        """Активирует эффект слияния"""
        self.merge_effect = True
        self.merge_timer = 25

    def update(self, delta_time: float):
        """Обновляет состояние плитки"""
        if self.spawn_anim:
            self.spawn_scale = min(1.0, self.spawn_scale + 0.12)
            if self.spawn_scale >= 1.0:
                self.spawn_anim = False

        if self.is_moving:
            self.progress += self.move_speed
            if self.progress >= 1.0:
                self.progress = 1.0
                self.is_moving = False
                self.row, self.col = self.trow, self.tcol
                self.vrow, self.vcol = float(self.row), float(self.col)
            else:
                from src.utils.helpers import lerp
                self.vrow = lerp(self.vrow, self.trow, self.progress)
                self.vcol = lerp(self.vcol, self.tcol, self.progress)
            self.center_x, self.center_y = get_cell_center(self.vrow, self.vcol)
        else:
            self.center_x, self.center_y = get_cell_center(self.row, self.col)

        if self.merge_effect:
            self.merge_timer -= 1
            if self.merge_timer <= 0:
                self.merge_effect = False

    def update_animation(self, delta_time: float):
        """Обновляет анимацию (заглушка)"""
        pass

    def get_key(self) -> str:
        """Возвращает ключ плитки для словаря"""
        if self.is_moving:
            return f"{self.trow}{self.tcol}"
        return f"{self.row}{self.col}"

    def can_merge_with(self, other: 'EvolutionTile') -> bool:
        """Проверяет возможность слияния с другой плиткой"""
        return self.stage_index == other.stage_index and not self.merge_effect