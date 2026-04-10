"""🧬 Эволюция — версия со спрайтами и звуком (Arcade 3.x) — ФИНАЛЬНАЯ"""
import arcade
import random
import math
import warnings
import os

warnings.filterwarnings("ignore", category=UserWarning)

# ==================== КОНФИГ ====================
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, FPS,
    ROWS, COLS, TILE_MARGIN, TILE_SIZE, CELL_STEP,
    GRID_ORIGIN_X, GRID_ORIGIN_Y, COLORS
)
from src.game.evolution_chain import EVOLUTION_CHAIN, BG_COLORS

# Глобальная ссылка на GameView для звуков
_game_view_ref = None


# ==================== ЗАГРУЗКА ТЕКСТУР ====================
def load_evolution_textures() -> list:
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

EVOLUTION_TEXTURES = load_evolution_textures()


# ==================== КООРДИНАТЫ ====================
def get_cell_center(row: float, col: float) -> tuple[float, float]:
    x = GRID_ORIGIN_X + col * CELL_STEP + TILE_SIZE // 2
    y = GRID_ORIGIN_Y - row * CELL_STEP - TILE_SIZE // 2
    return x, y


def lerp(start: float, end: float, t: float) -> float:
    return start + (end - start) * max(0.0, min(1.0, t))


# ==================== ПЛИТКА-СПРАЙТ ====================
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
        if self.row == row and self.col == col:
            return
        self.trow, self.tcol = row, col
        self.is_moving = True
        self.progress = 0.0

    def on_merge(self):
        self.merge_effect = True
        self.merge_timer = 25

    def update(self, delta_time: float):
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
        pass

    def get_key(self) -> str:
        if self.is_moving:
            return f"{self.trow}{self.tcol}"
        return f"{self.row}{self.col}"

    def can_merge_with(self, other: 'EvolutionTile') -> bool:
        return self.stage_index == other.stage_index and not self.merge_effect


# ==================== ИГРОВОЕ ПОЛЕ ====================
class GameBoard:
    def __init__(self):
        self.tiles = arcade.SpriteList(use_spatial_hash=True)
        self.tile_dict: dict[str, EvolutionTile] = {}
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

    def _get_line(self, direction: str, index: int) -> list[EvolutionTile]:
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

    def _process_line(self, tiles: list[EvolutionTile],
                      horizontal: bool, forward: bool) -> bool:
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

                new_texture = EVOLUTION_TEXTURES[last.stage_index]
                if new_texture.width > 0 and new_texture.height > 0:
                    last.scale = (TILE_SIZE * 0.75) / max(new_texture.width, new_texture.height)
                last.texture = new_texture
                last.bg_color = BG_COLORS[last.stage_index % len(BG_COLORS)]

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
        if direction not in ["up","down","left","right"] or self.input_locked:
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
        for tile in list(self.tiles):
            if hasattr(tile, '_marked_for_removal') and tile._marked_for_removal:
                tile.remove_from_sprite_lists()
                key = tile.get_key()
                if key in self.tile_dict:
                    del self.tile_dict[key]

    def _try_finish_move(self):
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
        for tile in self.tile_dict.values():
            for dr, dc in [(0,1),(1,0),(0,-1),(-1,0)]:
                neighbor = self.tile_dict.get(f"{tile.row+dr}{tile.col+dc}")
                if neighbor and tile.can_merge_with(neighbor):
                    return True
        return False

    def reset(self):
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


# ==================== VIEW: СТАРТ ====================
class StartView(arcade.View):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.background_music = None
        self.music_player = None

    def on_show(self):
        arcade.set_background_color(COLORS["background"])
        self._load_menu_music()

    def _load_menu_music(self):
        """Загрузка фоновой музыки для меню"""
        try:
            self.background_music = arcade.load_sound(":resources:sounds/ambient_cave.mp3")
            self.music_player = arcade.play_sound(self.background_music, volume=0.3, loop=True)
            print("✓ Музыка меню загружена")
        except Exception as e:
            print(f"⚠️ Не удалось загрузить музыку меню: {e}")

    def on_hide(self):
        """Остановка музыки при уходе с экрана"""
        if self.music_player:
            arcade.stop_sound(self.music_player)

    def on_draw(self):
        self.clear()
        arcade.draw_text("🧬 ЭВОЛЮЦИЯ", self.window.width//2, self.window.height//2 + 60,
                        COLORS["text"], font_size=48, anchor_x="center", bold=True)
        arcade.draw_text("Соединяй животных одной стадии,\nчтобы эволюционировать!",
                        self.window.width//2, self.window.height//2,
                        COLORS["text"], font_size=18, anchor_x="center", align="center")
        arcade.draw_text("▶ ПРОБЕЛ или КЛИК для старта ◀",
                        self.window.width//2, self.window.height//2 - 80,
                        arcade.color.DARK_BLUE, font_size=20, anchor_x="center", bold=True)
        arcade.draw_text("🎵 M — вкл/выкл музыку",
                        self.window.width//2, self.window.height//2 - 120,
                        arcade.color.GRAY, font_size=14, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.M:
            if self.music_player:
                arcade.stop_sound(self.music_player)
                self.music_player = None
            elif self.background_music:
                self.music_player = arcade.play_sound(self.background_music, volume=0.3, loop=True)
            return
        if key in [arcade.key.SPACE, arcade.key.RETURN]:
            game_view = GameView(self.window)
            game_view.setup()
            self.window.show_view(game_view)

    def on_mouse_press(self, x, y, button, modifiers):
        game_view = GameView(self.window)
        game_view.setup()
        self.window.show_view(game_view)


# ==================== VIEW: ИГРА ====================
class GameView(arcade.View):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.board = GameBoard()
        # 🎵 Звуки и музыка
        self.background_music = None
        self.merge_sound = None
        self.move_sound = None
        self.win_sound = None
        self.lose_sound = None
        self.music_player = None
        self.music_enabled = True

    def setup(self):
        global _game_view_ref
        print("⚙️ GameView.setup()")
        _game_view_ref = self
        self.board.reset()
        self._load_sounds()

    def _load_sounds(self):
        """🎵 Загрузка всех звуковых эффектов и музыки"""
        # Фоновая музыка
        try:
            self.background_music = arcade.load_sound(":resources:sounds/ambient_cave.mp3")
            if self.music_enabled:
                self.music_player = arcade.play_sound(self.background_music, volume=0.4, loop=True)
            print("✓ Фоновая музыка загружена")
        except Exception as e:
            print(f"⚠️ Не удалось загрузить музыку: {e}")
            self.background_music = None

        # Звуковые эффекты (используем встроенные ресурсы)
        sound_effects = {
            "merge": ":resources:sounds/jump1.wav",
            "move": ":resources:sounds/phaseJump1.wav",
            "win": ":resources:sounds/upgrade1.wav",
            "lose": ":resources:sounds/error2.wav",
        }

        for name, path in sound_effects.items():
            try:
                setattr(self, f"{name}_sound", arcade.load_sound(path))
                print(f"✓ Звук '{name}' загружен")
            except Exception as e:
                print(f"⚠️ Не удалось загрузить звук {name}: {e}")
                setattr(self, f"{name}_sound", None)

    def _play_sound(self, sound_name: str, volume: float = 0.5):
        """🔊 Вспомогательный метод для воспроизведения звуков"""
        sound = getattr(self, f"{sound_name}_sound", None)
        if sound:
            arcade.play_sound(sound, volume=volume)

    def _toggle_music(self):
        """🔇 Переключение фоновой музыки"""
        self.music_enabled = not self.music_enabled
        if self.music_enabled and self.background_music:
            self.music_player = arcade.play_sound(self.background_music, volume=0.4, loop=True)
            print("🔊 Музыка включена")
        elif self.music_player:
            arcade.stop_sound(self.music_player)
            self.music_player = None
            print("🔇 Музыка выключена")

    def on_show(self):
        arcade.set_background_color(COLORS["background"])
        if not self.board.tile_dict:
            self.setup()

    def on_hide(self):
        """Остановка музыки при уходе с экрана игры"""
        if self.music_player:
            arcade.stop_sound(self.music_player)

    def on_draw(self):
        self.clear()

        # Сетка
        for i in range(ROWS + 1):
            y = GRID_ORIGIN_Y - i * CELL_STEP
            arcade.draw_line(GRID_ORIGIN_X, y,
                           GRID_ORIGIN_X + COLS * CELL_STEP, y,
                           COLORS["grid"], 2)
        for j in range(COLS + 1):
            x = GRID_ORIGIN_X + j * CELL_STEP
            arcade.draw_line(x, GRID_ORIGIN_Y,
                           x, GRID_ORIGIN_Y - ROWS * CELL_STEP,
                           COLORS["grid"], 2)

        # Плитки через SpriteList
        self.board.tiles.draw()

        # Эффекты и текст поверх спрайтов
        for tile in self.board.tile_dict.values():
            if tile._marked_for_removal:
                continue

            if tile.merge_effect:
                pulse = 1.0 + 0.15 * abs(math.sin(tile.merge_timer * 0.4))
                size = TILE_SIZE * tile.spawn_scale * pulse * 1.4
                arcade.draw_lrbt_rectangle_filled(
                    tile.center_x - size/2, tile.center_x + size/2,
                    tile.center_y - size/2, tile.center_y + size/2,
                    (255, 215, 0, 120)
                )
            name = EVOLUTION_CHAIN[tile.stage_index]["name"]
            arcade.draw_text(
                name, tile.center_x, tile.center_y - TILE_SIZE//3,
                COLORS["text"], font_size=9,
                anchor_x="center", anchor_y="center", bold=True,
                width=int(TILE_SIZE * 0.9), align="center"
            )

        # Счёт
        arcade.draw_text(f"Счёт: {self.board.score}", 25, SCREEN_HEIGHT - 25,
                        COLORS["text"], font_size=20, bold=True)

        # Таймер
        timer_color = arcade.color.RED if self.board.timer < 10 else arcade.color.GREEN
        arcade.draw_text(f"⏱ Время: {self.board.timer:.1f}", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 25,
                        timer_color, font_size=20, bold=True)

        # Подсказка управления звуком
        music_status = "🔊" if self.music_enabled else "🔇"
        arcade.draw_text(f"{music_status} M — музыка", 25, 25,
                        arcade.color.GRAY, font_size=12)

        # Статус
        if self.board.won:
            arcade.draw_text("🎉 ПОБЕДА! Киборг достигнут! 🎉",
                           self.window.width//2, self.window.height//2,
                           arcade.color.GOLD, font_size=28, anchor_x="center", bold=True)
            arcade.draw_text("R — новая игра",
                           self.window.width//2, self.window.height//2 - 40,
                           COLORS["text"], font_size=18, anchor_x="center")
        elif self.board.game_over:
            arcade.draw_text("😔 Игра окончена",
                           self.window.width//2, self.window.height//2,
                           arcade.color.RED, font_size=32, anchor_x="center", bold=True)
            arcade.draw_text("R — новая игра",
                           self.window.width//2, self.window.height//2 - 40,
                           COLORS["text"], font_size=18, anchor_x="center")

    def on_update(self, delta_time: float):
        if not self.board.won and not self.board.game_over:
            self.board.tiles.update(delta_time)
            self.board.tiles.update_animation(delta_time)
            self.board._try_finish_move()
            # Уменьшаем таймер
            self.board.timer -= delta_time
            # Проверка на истечение времени
            if self.board.timer <= 0:
                self.board.timer = 0
                self.board.game_over = True
                if _game_view_ref:
                    _game_view_ref._play_sound("lose", volume=0.6)

    def on_key_press(self, key, modifiers):
        # 🔇 Управление музыкой
        if key == arcade.key.M:
            self._toggle_music()
            return

        if self.board.won or self.board.game_over:
            if key == arcade.key.R:
                print("🔄 Рестарт")
                self.setup()
            return
        dirs = {arcade.key.LEFT:"left", arcade.key.RIGHT:"right",
               arcade.key.UP:"up", arcade.key.DOWN:"down"}
        if key in dirs and not self.board.input_locked:
            self.board.move_direction(dirs[key])


# ==================== ГЛАВНОЕ ОКНО ====================
class EvolutionGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
        arcade.set_background_color(COLORS["background"])
        self.show_view(StartView(self))


# ==================== ЗАПУСК ====================
def main():
    print("🚀 Эволюция: спрайты + звук активированы!")
    print("🎮 ← ↑ → ↓ — ходы, R — рестарт, M — вкл/выкл музыку")
    print(f"📦 Текстур загружено: {len(EVOLUTION_TEXTURES)}")
    game = EvolutionGame()
    arcade.run()

if __name__ == "__main__":
    main()