"""Ayudantes para dibujar y gestionar la superposición del reproductor.

Estos son ayudantes ligeros que operan en la instancia de DrawMaze,
 lo que facilita la lectura del código de renderizado y permite que
   la lógica del reproductor se guarde en un archivo separado.
"""
from typing import Any


def draw_player_buffer(draw_maze: Any) -> None:
    """Dibujar el reproductor en el búfer de imagen (para que esté presente
      cuando la imagen se coloca en la ventana))."""
    px, py = draw_maze.player_pos
    topx, topy = px * draw_maze.tile_size, py * draw_maze.tile_size
    margin = max(1, draw_maze.tile_size // 4)
    for dy in range(margin, draw_maze.tile_size - margin):
        for dx in range(margin, draw_maze.tile_size - margin):
            draw_maze._put_pixel(topx + dx, topy + dy, draw_maze.player_color)
    # Depuración: si el juego ha terminado pero se llamó a
    # esto, registrar una vez
    if (
       getattr(
           draw_maze, '_debug_player_calls', False) and draw_maze.game_over):
        print('DEBUG: draw_player_buffer called after game_over')


def draw_player_overlay(draw_maze: Any) -> None:
    """Dibuja el reproductor directamente en la ventana usando `mlx_pixel_put`
      para que aparezca sobre la imagen principal. Algunos backends MLX
        requieren esto para garantizar la visibilidad de la superposición.
    """
    px, py = draw_maze.player_pos
    topx, topy = px * draw_maze.tile_size, py * draw_maze.tile_size
    margin = max(1, draw_maze.tile_size // 4)
    for dy in range(margin, draw_maze.tile_size - margin):
        for dx in range(margin, draw_maze.tile_size - margin):
            draw_maze.mlx.mlx_pixel_put(draw_maze.mlx_ptr, draw_maze.win_ptr,
                                        topx + dx, topy + dy,
                                        draw_maze.player_color)
    if (
     getattr(draw_maze, '_debug_player_calls', False) and draw_maze.game_over):
        print('DEBUG: draw_player_overlay called after game_over')
