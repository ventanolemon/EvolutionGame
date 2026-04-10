"""Модуль игрового поля с таймером и счётчиком слияний"""
import random
import arcade
from typing import Dict, Optional, Tuple
from config import ROWS, COLS, EVOLUTION_CHAIN, SCREEN_WIDTH, SCREEN_HEIGHT, TILE_MARGIN, COLORS
from src.game.tile import EvolutionTile, get_cell_center

# Глобальная ссылка на GameView для звуков
_game_view_ref = None


class GameBoard:
    """Логика игрового поля 4x4 с таймером"""

    def __init__(self):
        self.tiles = arcade.SpriteList(use_spatial_hash=True)
        self.tile_dict: Dict[str, EvolutionTile] = {}
        self.score = 0
        self.game_over = False
        self.won = False
        self.input_locked = False
        self.spawn_pending = False
        self.wait_counter = 0
        self.max_wait_frames = 120
        self.timer = 60.0  # Начальное время в секундах
        self.merges_this_move = 0  # Счётчик слияний за текущий ход

    def add_random_tile(self, animate: bool = True) -> bool:
        """Добавляет новую плитку в случайную пустую ячейку"""
        empty = [(r, c) for r in range(ROWS) for c in range(COLS)
                 if f"{r}{c}" not in self.tile_dict]
        if not empty:
            return False
        row, col = random.choice(empty)
        stage = 0 if random.random() < 0.9 else 1
        tile = EvolutionTile(stage, row, col, animate_spawn=animate)
        self.tiles.append(tile)
        self.tile_dict[f"{row}{col}"] = tile
        return True

    def _get_line(self, direction: str, index: int) -> list:
        """Получает линию плиток для обработки"""
        tiles = []
        if direction in ["left", "right"]:
            cols = range(COLS) if direction == "left" else reversed(range(COLS))
            for c in cols:
                key = f"{index}{c}"
                if key in self.tile_dict:
                    tiles.append(self.tile_dict[key])
        else:
            rows = range(ROWS) if direction == "up" else reversed(range(ROWS))
            for r in rows:
                key = f"{r}{index}"
                if key in self.tile_dict:
                    tiles.append(self.tile_dict[key])
        return tiles

    def _process_line(self, tiles: list, horizontal: bool, forward: bool) -> bool:
        """Обрабатывает одну линию плиток"""
        if not tiles:
            return False
        changed = False
        merged_keys = set()
        result = []

        for tile in tiles:
            if not result:
                result.append(tile)
                continue
            last = result[-1]
            if tile.can_merge_with(last) and last.get_key() not in merged_keys:
                last.stage_index += 1
                last.on_merge()
                self.score += 2 ** (last.stage_index + 1)
                self.merges_this_move += 1  # Увеличиваем счётчик слияний за ход
                merged_keys.add(last.get_key())

                from src.game.evolution_chain import EVOLUTION_TEXTURES
                new_texture = EVOLUTION_TEXTURES[last.stage_index]
                if new_texture.width > 0 and new_texture.height > 0:
                    from config import TILE_SIZE
                    last.scale = (TILE_SIZE * 0.75) / max(new_texture.width, new_texture.height)
                last.texture = new_texture
                last.bg_color = last.bg_color  # Оставляем цвет

                tile._marked_for_removal = True
                if tile.get_key() in self.tile_dict:
                    del self.tile_dict[tile.get_key()]
                tile.remove_from_sprite_lists()

                # 🎵 Звук слияния
                if _game_view_ref:
                    _game_view_ref._play_sound("merge", volume=0.7)

                changed = True
            else:
                result.append(tile)

        for new_pos, tile in enumerate(result):
            if tile._marked_for_removal:
                continue

            if horizontal:
                new_c = new_pos if not forward else COLS - 1 - new_pos
                new_r = tile.row
            else:
                new_r = new_pos if not forward else ROWS - 1 - new_pos
                new_c = tile.col

            if tile.row != new_r or tile.col != new_c:
                old_key = f"{tile.row}{tile.col}"
                tile.start_move_to(new_r, new_c)

                if old_key in self.tile_dict:
                    del self.tile_dict[old_key]

                new_key = f"{new_r}{new_c}"
                self.tile_dict[new_key] = tile
                changed = True
        return changed

    def move_direction(self, direction: str) -> bool:
        """Выполняет движение в указанном направлении"""
        if direction not in ["up", "down", "left", "right"] or self.input_locked:
            return False
        self.input_locked = True
        self.spawn_pending = False
        self.wait_counter = 0
        moved_any = False

        if direction in ["left", "right"]:
            horizontal, forward = True, (direction == "right")
            indices = range(ROWS)
        else:
            horizontal, forward = False, (direction == "down")
            indices = range(COLS)

        for idx in indices:
            line = self._get_line(direction, idx)
            if self._process_line(line, horizontal, forward):
                moved_any = True

        self._remove_merged_tiles()
        if moved_any:
            self.spawn_pending = True
            # 🎵 Звук успешного хода
            if _game_view_ref:
                _game_view_ref._play_sound("move", volume=0.3)
        else:
            self.input_locked = False
        return moved_any

    def _remove_merged_tiles(self):
        """Удаляет объединённые плитки"""
        for tile in list(self.tiles):
            if hasattr(tile, '_marked_for_removal') and tile._marked_for_removal:
                tile.remove_from_sprite_lists()
                key = tile.get_key()
                if key in self.tile_dict:
                    del self.tile_dict[key]

    def _try_finish_move(self):
        """Пытается завершить ход"""
        if not self.spawn_pending or not self.input_locked:
            return
        self.wait_counter += 1
        if self.wait_counter >= self.max_wait_frames:
            self._force_finish_move()
            return
        active = [t for t in self.tile_dict.values() if not t._marked_for_removal]
        if all(not t.is_moving and not t.spawn_anim for t in active):
            self._force_finish_move()

    def _force_finish_move(self):
        """Завершает текущий ход"""
        if self.spawn_pending:
            # Добавляем время за слияния: по 2 секунды за каждое слияние
            time_bonus = self.merges_this_move * 2.0
            self.timer += time_bonus
            self.merges_this_move = 0  # Сбрасываем счётчик слияний
            self.add_random_tile(animate=True)
            self.spawn_pending = False
            self._check_game_state()
        self.input_locked = False
        self.wait_counter = 0

    def _check_game_state(self):
        """Проверяет состояние игры (победа/поражение)"""
        max_stage = max((t.stage_index for t in self.tile_dict.values()), default=-1)
        if max_stage >= len(EVOLUTION_CHAIN) - 1:
            self.won = True
            # 🎵 Звук победы
            if _game_view_ref:
                _game_view_ref._play_sound("win", volume=0.9)
            return
        if len(self.tile_dict) >= ROWS * COLS and not self._has_moves():
            self.game_over = True
            # 🎵 Звук поражения
            if _game_view_ref:
                _game_view_ref._play_sound("lose", volume=0.6)

    def _has_moves(self) -> bool:
        """Проверяет наличие возможных ходов"""
        for tile in self.tile_dict.values():
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = self.tile_dict.get(f"{tile.row + dr}{tile.col + dc}")
                if neighbor and tile.can_merge_with(neighbor):
                    return True
        return False

    def reset(self):
        """Сбрасывает игру в начальное состояние"""
        self.tiles = arcade.SpriteList(use_spatial_hash=True)
        self.tile_dict.clear()
        self.score = 0
        self.game_over = self.won = False
        self.input_locked = self.spawn_pending = False
        self.wait_counter = 0
        self.timer = 60.0  # Сбрасываем таймер до начального значения
        self.merges_this_move = 0  # Сбрасываем счётчик слияний
        for _ in range(2):
            self.add_random_tile(animate=True)