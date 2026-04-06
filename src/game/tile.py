# src/game/tile.py — минимальная версия
import arcade
from config import TILE_SIZE, EVOLUTION_CHAIN, COLORS

class EvolutionTile(arcade.SpriteSolidColor):
    def __init__(self, stage_index: int, row: int, col: int):
        # Цвет фона зависит от стадии эволюции
        hue = (stage_index * 25) % 360
        color = arcade.color_from_hsl(hue, 0.6, 0.7)
        
        super().__init__(TILE_SIZE, TILE_SIZE, color)
        
        self.stage_index = stage_index
        self.row = row
        self.col = col
        self.center_x = self._calc_x(col)
        self.center_y = self._calc_y(row)
        self.merge_effect = False
    
    def _calc_x(self, col: int) -> float:
        margin = 15
        return margin + col * (TILE_SIZE + margin) + TILE_SIZE // 2
    
    def _calc_y(self, row: int) -> float:
        margin = 15
        from config import SCREEN_HEIGHT
        return SCREEN_HEIGHT - margin - TILE_SIZE - row * (TILE_SIZE + margin) - TILE_SIZE // 2
    
    def update_position(self):
        """Плавное обновление позиции (для анимации)"""
        target_x = self._calc_x(self.col)
        target_y = self._calc_y(self.row)
        
        # Простая интерполяция
        self.center_x += (target_x - self.center_x) * 0.2
        self.center_y += (target_y - self.center_y) * 0.2
    
    def draw(self):
        super().draw()  # фон
        
        # Название животного
        name = EVOLUTION_CHAIN[self.stage_index]["name"]
        arcade.draw_text(
            name, self.center_x, self.center_y,
            COLORS["text"], font_size=11,
            anchor_x="center", anchor_y="center",
            bold=True, width=TILE_SIZE - 20, align="center"
        )
        
        # Эффект слияния
        if self.merge_effect:
            arcade.draw_circle_filled(
                self.center_x, self.center_y,
                TILE_SIZE // 2 + 5,
                arcade.color.GOLD, alpha=100
            )