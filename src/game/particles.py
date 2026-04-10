"""Модуль частиц для эффектов"""
import arcade
from config import SCREEN_WIDTH, SCREEN_HEIGHT


class Particle:
    """Частица для эффектов"""
    
    def __init__(self, x: float, y: float, color: tuple):
        self.x = x
        self.y = y
        self.color = color
        self.size = arcade.random.uniform(2, 6)
        self.speed_x = arcade.random.uniform(-3, 3)
        self.speed_y = arcade.random.uniform(-3, 3)
        self.alpha = 255
        self.lifetime = arcade.random.uniform(0.3, 0.8)
        self.age = 0.0
    
    def update(self, delta_time: float):
        """Обновляет состояние частицы"""
        self.x += self.speed_x
        self.y += self.speed_y
        self.age += delta_time
        self.alpha = int(255 * (1 - self.age / self.lifetime))
    
    def draw(self):
        """Рисует частицу"""
        if self.alpha > 0:
            arcade.draw_circle_filled(
                self.x, self.y, self.size,
                (*self.color, self.alpha)
            )


class ParticleSystem:
    """Система частиц для визуальных эффектов"""
    
    def __init__(self):
        self.particles = []
    
    def emit(self, x: float, y: float, color: tuple, count: int = 10):
        """Создаёт частицы в указанной позиции"""
        for _ in range(count):
            self.particles.append(Particle(x, y, color))
    
    def update(self, delta_time: float = 1/60):
        """Обновляет все частицы"""
        self.particles = [p for p in self.particles if p.age < p.lifetime]
        for particle in self.particles:
            particle.update(delta_time)
    
    def draw(self):
        """Рисует все частицы"""
        for particle in self.particles:
            particle.draw()