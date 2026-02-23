"""Helper para dibujar el temporizador en la ventana.

Funciona junto a la instancia `DrawMaze` (usa atributos públicos mínimos).
"""
from typing import Any


def draw_timer_overlay(draw_maze: Any, elapsed_sec: int) -> None:
    """Limpia y dibuja el temporizador en la ventana.

    Actualiza `draw_maze._last_timer_sec` con el valor usado.
    """
    mins = elapsed_sec // 60
    secs = elapsed_sec % 60
    timer_text = f"Time: {mins}:{secs:02d}"
    char_w = 10
    char_h = 14
    tx = max(10, draw_maze.win_w - (len(timer_text) * char_w) - 10)
    ty = 10

    # Limpiar rectángulo de fondo del temporizador en la ventana
    width_px = len(timer_text) * char_w
    for yy in range(ty, ty + char_h):
        for xx in range(tx, tx + width_px):
            draw_maze.mlx.mlx_pixel_put(draw_maze.mlx_ptr, draw_maze.win_ptr,
                                        xx, yy, draw_maze.bg_color)

    # Dibujar el texto encima
    draw_maze.mlx.mlx_string_put(draw_maze.mlx_ptr, draw_maze.win_ptr,
                                 tx, ty, 0xFFFFFF, timer_text)
    draw_maze._last_timer_sec = elapsed_sec
