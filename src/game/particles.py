"""Модуль игрового поля"""
import random
from typing import Dict, Optional, Tuple
from src.game.tile import EvolutionTile
from config import ROWS, COLS, EVOLUTION_CHAIN


class GameBoard:
    """Логика игрового поля 4x4"""

    def __init__(self):
        self.tiles: Dict[str, EvolutionTile] = {}
        self.score = 0
        self.level = 1
        self.game_over = False
        self.won = False

    def add_random_tile(self) -> bool:
        """Добавляет новую плитку в случайную пустую ячейку"""
        empty_cells = [
            (r, c) for r in range(ROWS) for c in range(COLS)
            if f"{r}{c}" not in self.tiles
        ]
        if not empty_cells:
            return False

        row, col = random.choice(empty_cells)
        # 90% шанс на первую стадию, 10% — на вторую
        stage = 0 if random.random() < 0.9 else 1
        self.tiles[f"{row}{col}"] = EvolutionTile(stage, row, col)
        return True

    def move_direction(self, direction: str) -> Tuple[bool, bool]:
        """
        Выполняет движение в указанном направлении.
        Возвращает (было_движение, было_слияние)
        """
        if direction not in ["up", "down", "left", "right"]:
            return False, False

        moved = False
        merged = False

        # Определяем порядок обработки плиток
        if direction in ["left", "up"]:
            reverse = False
        else:
            reverse = True

        # Группируем по рядам/столбцам
        groups = self._get_groups(direction)

        for group in groups:
            group_moved, group_merged = self._process_group(
                group, direction, reverse
            )
            moved = moved or group_moved
            merged = merged or group_merged

        if moved:
            self.add_random_tile()
            self._check_win_condition()

        return moved, merged

    def _get_groups(self, direction: str) -> list:
        """Группирует плитки по линиям движения"""
        groups = []
        if direction in ["left", "right"]:
            for row in range(ROWS):
                group = [
                    self.tiles[f"{row}{col}"]
                    for col in range(COLS)
                    if f"{row}{col}" in self.tiles
                ]
                if direction == "right":
                    group.reverse()
                groups.append((row, group))
        else:  # up/down
            for col in range(COLS):
                group = [
                    self.tiles[f"{row}{col}"]
                    for row in range(ROWS)
                    if f"{row}{col}" in self.tiles
                ]
                if direction == "down":
                    group.reverse()
                groups.append((col, group))
        return groups

    def _process_group(self, group_data, direction: str, reverse: bool) -> Tuple[bool, bool]:
        """Обрабатывает одну линию плиток"""
        idx, tiles = group_data
        if not tiles:
            return False, False

        moved = False
        merged = False
        merged_indices = set()

        # Сдвиг и слияние
        result = []
        for tile in tiles:
            if result and (
                    result[-1].stage_index == tile.stage_index
                    and len(result) - 1 not in merged_indices
            ):
                # Слияние
                result[-1].stage_index += 1
                result[-1].on_merge()
                self.score += EVOLUTION_CHAIN[result[-1].stage_index]["value"]
                merged_indices.add(len(result) - 1)
                merged = True
            else:
                result.append(tile)

        # Обновление позиций
        for new_pos, tile in enumerate(result):
            old_key = tile.get_key()

            if direction in ["left", "right"]:
                new_col = new_pos if direction == "left" else COLS - 1 - new_pos
                new_row = idx
            else:
                new_row = new_pos if direction == "up" else ROWS - 1 - new_pos
                new_col = idx

            if tile.row != new_row or tile.col != new_col:
                tile.start_move_to(new_row, new_col)
                moved = True

            # Обновляем ключ в словаре
            new_key = f"{new_row}{new_col}"
            if old_key != new_key:
                del self.tiles[old_key]
                self.tiles[new_key] = tile

        return moved, merged

    def _check_win_condition(self):
        """Проверяет победу (достигнута максимальная эволюция)"""
        max_stage = max(
            (tile.stage_index for tile in self.tiles.values()),
            default=-1
        )
        if max_stage >= len(EVOLUTION_CHAIN) - 1:
            self.won = True

    def is_full(self) -> bool:
        """Проверяет, заполнено ли поле"""
        return len(self.tiles) == ROWS * COLS

    def has_moves(self) -> bool:
        """Проверяет, есть ли возможные ходы"""
        if not self.is_full():
            return True

        # Проверяем соседние плитки на возможность слияния
        for tile in self.tiles.values():
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor_key = f"{tile.row + dr}{tile.col + dc}"
                neighbor = self.tiles.get(neighbor_key)
                if neighbor and tile.can_merge_with(neighbor):
                    return True
        return False

    def reset(self):
        """Сброс игры"""
        self.tiles.clear()
        self.score = 0
        self.level = 1
        self.game_over = False
        self.won = False
        # Добавляем две начальные плитки
        for _ in range(2):
            self.add_random_tile()