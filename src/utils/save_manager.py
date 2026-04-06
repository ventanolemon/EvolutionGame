"""Менеджер сохранения данных"""
import sqlite3
import json
from pathlib import Path
from config import EVOLUTION_CHAIN


class SaveManager:
    """Работа с сохранением прогресса"""

    def __init__(self, db_path: str = "data/progress.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Создаёт таблицы БД"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS player_stats (
                    id INTEGER PRIMARY KEY,
                    best_score INTEGER DEFAULT 0,
                    max_stage INTEGER DEFAULT 0,
                    games_played INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS unlocked_animals (
                    stage_index INTEGER PRIMARY KEY,
                    unlocked BOOLEAN DEFAULT FALSE
                )
            """)
            # Инициализация цепочки эволюции
            for i in range(len(EVOLUTION_CHAIN)):
                conn.execute(
                    "INSERT OR IGNORE INTO unlocked_animals VALUES (?, ?)",
                    (i, i == 0)  # Первая стадия открыта сразу
                )
            conn.execute(
                "INSERT OR IGNORE INTO player_stats DEFAULT VALUES"
            )

    def save_game_result(self, score: int, max_stage: int, won: bool):
        """Сохраняет результат партии"""
        with sqlite3.connect(self.db_path) as conn:
            # Обновляем статистику
            conn.execute("""
                UPDATE player_stats 
                SET 
                    best_score = MAX(best_score, ?),
                    max_stage = MAX(max_stage, ?),
                    games_played = games_played + 1,
                    wins = wins + ?
                WHERE id = 1
            """, (score, max_stage, 1 if won else 0))

            # Открываем новые стадии
            for i in range(max_stage + 1):
                conn.execute(
                    "UPDATE unlocked_animals SET unlocked = TRUE WHERE stage_index = ?",
                    (i,)
                )

    def get_stats(self) -> dict:
        """Возвращает статистику игрока"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT best_score, max_stage, games_played, wins FROM player_stats WHERE id = 1"
            )
            row = cursor.fetchone()
            return {
                "best_score": row[0],
                "max_stage": row[1],
                "games_played": row[2],
                "wins": row[3],
            }

    def is_animal_unlocked(self, stage_index: int) -> bool:
        """Проверяет, открыто ли животное"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT unlocked FROM unlocked_animals WHERE stage_index = ?",
                (stage_index,)
            )
            row = cursor.fetchone()
            return bool(row and row[0])