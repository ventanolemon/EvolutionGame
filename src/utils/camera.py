"""Модуль камеры"""


class Camera:
    """Камера для отслеживания игрока"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.position_x = 0
        self.position_y = 0
    
    def move_to(self, x: float, y: float):
        """Перемещает камеру к указанной позиции"""
        self.position_x = x
        self.position_y = y
    
    def apply(self):
        """Применяет камеру (для рендеринга)"""
        # Arcade handles camera internally
        pass