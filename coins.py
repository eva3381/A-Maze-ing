"""Helpers para gestionar monedas en el laberinto.
Funciones:
- place_coins(draw_maze): genera y asigna `draw_maze.coins`.
- draw_coins(draw_maze): dibuja las monedas en el buffer de imagen.
- collect_coin(draw_maze, pos): elimina moneda si existe y devuelve True/False.
"""
from typing import Any, Tuple
import random


def place_coins(draw_maze: Any) -> None:
    """Genera posiciones de monedas evitando entrada, salida y logo."""
    max_coins = max(5, (draw_maze.width * draw_maze.height) // 40)
    candidates = [
        (x, y)
        for y in range(draw_maze.height)
        for x in range(draw_maze.width)
        if (x, y) not in draw_maze.maze_obj.pattern_cells
        and (x, y) != draw_maze.maze_obj.entry
        and (x, y) != draw_maze.maze_obj.exit_pt
    ]
    if not candidates:
        draw_maze.coins = set()
        return
    chosen = random.sample(candidates, min(len(candidates), max_coins))
    draw_maze.coins = set(chosen)


def draw_coins(draw_maze: Any) -> None:
    """Dibuja las monedas en el buffer de imagen (no overlay)."""
    color = getattr(draw_maze, 'coin_color', 0xFFD700)
    for cx, cy in draw_maze.coins:
        topx, topy = cx * draw_maze.tile_size, cy * draw_maze.tile_size
        margin = max(1, draw_maze.tile_size // 4)
        for dy in range(margin, draw_maze.tile_size - margin):
            for dx in range(margin, draw_maze.tile_size - margin):
                draw_maze._put_pixel(topx + dx, topy + dy, color)


def collect_coin(draw_maze: Any, pos: Tuple[int, int]) -> bool:
    """Si `pos` contiene una moneda, la elimina y devuelve True."""
    if pos in getattr(draw_maze, 'coins', set()):
        draw_maze.coins.remove(pos)
        return True
    return False
