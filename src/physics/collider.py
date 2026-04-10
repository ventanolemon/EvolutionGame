"""Модуль коллизий (физика)"""


def check_collision(sprite1, sprite2) -> bool:
    """Проверяет столкновение двух спрайтов"""
    return arcade.check_for_collision(sprite1, sprite2)


def check_for_collision_with_list(sprite, sprite_list) -> list:
    """Проверяет столкновения спрайта со списком"""
    return arcade.check_for_collision_with_list(sprite, sprite_list)