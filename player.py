"""Helpers to draw and manage the player overlay.

These are thin helpers that operate on the `DrawMaze` instance so the
rendering code is easier to read and the player logic lives in a
separate file.
"""
from typing import Any


def draw_player_buffer(draw_maze: Any) -> None:
    """Draw the player into the image buffer (so it's present when the
    image is put to window)."""
    px, py = draw_maze.player_pos
    topx, topy = px * draw_maze.tile_size, py * draw_maze.tile_size
    margin = max(1, draw_maze.tile_size // 4)
    for dy in range(margin, draw_maze.tile_size - margin):
        for dx in range(margin, draw_maze.tile_size - margin):
            draw_maze._put_pixel(topx + dx, topy + dy, draw_maze.player_color)
    # Debug: if the game is over but this was called, log once
    if getattr(draw_maze, '_debug_player_calls', False) and draw_maze.game_over:
        print('DEBUG: draw_player_buffer called after game_over')


def draw_player_overlay(draw_maze: Any) -> None:
    """Draw the player directly to the window using `mlx_pixel_put` so
    it appears above the main image. Some MLX backends require this to
    guarantee overlay visibility.
    """
    px, py = draw_maze.player_pos
    topx, topy = px * draw_maze.tile_size, py * draw_maze.tile_size
    margin = max(1, draw_maze.tile_size // 4)
    for dy in range(margin, draw_maze.tile_size - margin):
        for dx in range(margin, draw_maze.tile_size - margin):
            draw_maze.mlx.mlx_pixel_put(draw_maze.mlx_ptr, draw_maze.win_ptr,
                                        topx + dx, topy + dy,
                                        draw_maze.player_color)
    if getattr(draw_maze, '_debug_player_calls', False) and draw_maze.game_over:
        print('DEBUG: draw_player_overlay called after game_over')
