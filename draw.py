# draw.py
import sys
from mlx import Mlx

class DrawMaze:
    def __init__(self, width, height, grid, config, solution, maze_obj):
        self.mlx = Mlx()
        self.ptr = self.mlx.mlx_init()
        self.tile_size = 30
        self.win = self.mlx.mlx_new_window(self.ptr, width * self.tile_size, height * self.tile_size, "Eva's Pink Maze 🌸")
        
        self.grid = grid
        self.width = width
        self.height = height
        self.config = config
        self.solution = solution
        self.maze_obj = maze_obj # Guardamos la referencia al generador
        
        self.PINK_WALL = 0xFF1493
        self.PINK_FLOOR = 0xFFC0CB
        self.SOL_COLOR = 0xFFFFFF # Blanco para la solución

        # Registrar los eventos de teclado
        self.mlx.mlx_key_hook(self.win, self.handle_keys)

    def draw_all_tiles(self):
        # Dibujamos las celdas
        for y in range(self.height):
            for x in range(self.width):
                val = self.grid[y][x]
                self._draw_cell(x, y, val)

    def _draw_cell(self, x, y, val):
        px, py = x * self.tile_size, y * self.tile_size
        if val & 1: self._draw_line(px, py, px + self.tile_size, py, self.PINK_WALL)
        if val & 2: self._draw_line(px + self.tile_size, py, px + self.tile_size, py + self.tile_size, self.PINK_WALL)
        if val & 4: self._draw_line(px, py + self.tile_size, px + self.tile_size, py + self.tile_size, self.PINK_WALL)
        if val & 8: self._draw_line(px, py, px, py + self.tile_size, self.PINK_WALL)

    def _draw_line(self, x1, y1, x2, y2, color):
        if x1 == x2:
            for i in range(y1, y2): self.mlx.mlx_pixel_put(self.ptr, self.win, x1, i, color)
        else:
            for i in range(x1, x2): self.mlx.mlx_pixel_put(self.ptr, self.win, i, y1, color)

    def draw_solution(self):
        """Dibuja el camino de la solución en blanco."""
        curr_x, curr_y = self.maze_obj.entry
        half = self.tile_size // 2
        
        for move in self.solution:
            nx, ny = curr_x, curr_y
            if move == 'N': ny -= 1
            elif move == 'E': nx += 1
            elif move == 'S': ny += 1
            elif move == 'W': nx -= 1
            
            # Dibujar línea entre centros de celdas
            self._draw_line(curr_x * self.tile_size + half, curr_y * self.tile_size + half,
                            nx * self.tile_size + half, ny * self.tile_size + half, self.SOL_COLOR)
            curr_x, curr_y = nx, ny

    def handle_keys(self, keycode):
        # ESC para salir (53 en Mac)
        if keycode == 65307:
            sys.exit(0)
        
        # 'R' para regenerar (15 en Mac)
        elif keycode == 114:
            print("Regenerando laberinto...")
            # Limpiar la cuadrícula y volver a generar
            self.maze_obj.grid = [[15 for _ in range(self.width)] for _ in range(self.height)]
            self.maze_obj.generate()
            self.grid = self.maze_obj.grid
            self.solution = self.maze_obj.solve()
            self.mlx.mlx_clear_window(self.ptr, self.win)
            self.draw_all_tiles()
            
        # 'S' para resolver (1 en Mac)
        elif keycode == 115:
            print("Mostrando solución...")
            self.draw_solution()