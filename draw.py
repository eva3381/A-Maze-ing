import sys
import os
from mlx import Mlx

class DrawMaze:
    def __init__(self, width, height, grid, config, solution, maze_obj):
        self.maze_obj = maze_obj
        self.grid = grid
        self.width = width
        self.height = height
        self.config = config
        self.solution = solution
        self.tile_size = 20
        self.show_solution = False
        self.needs_update = True  # Bandera para forzar el primer dibujado

        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        if not self.mlx_ptr:
            os._exit(1)

        self.win_w = self.width * self.tile_size
        self.win_h = self.height * self.tile_size
        self.win_ptr = self.mlx.mlx_new_window(self.mlx_ptr, self.win_w, self.win_h, "A-Maze-ing 42")

        # Buffer de imagen para evitar parpadeos y pantalla negra
        self.img = self.mlx.mlx_new_image(self.mlx_ptr, self.win_w, self.win_h)
        addr = self.mlx.mlx_get_data_addr(self.img)
        self.img_data, self.bpp, self.line_len, self.endian = addr

        self.wall_color = 0xFF1493 
        self.solu_color = 0xFFFFFF 

    def _put_pixel(self, x, y, color):
        if 0 <= x < self.win_w and 0 <= y < self.win_h:
            offset = (y * self.line_len) + (x * (self.bpp // 8))
            # Formato BGRA típico de MLX
            self.img_data[offset] = color & 0xFF          # Blue
            self.img_data[offset + 1] = (color >> 8) & 0xFF  # Green
            self.img_data[offset + 2] = (color >> 16) & 0xFF # Red
            self.img_data[offset + 3] = 0                  # Alpha

    def _draw_line(self, x1, y1, x2, y2, color):
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        if x1 == x2:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self._put_pixel(x1, y, color)
        elif y1 == y2:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self._put_pixel(x, y1, color)

    def draw_path(self):
        if not self.solution:
            self.solution = self.maze_obj.solve()
        curr_x, curr_y = self.maze_obj.entry
        half = self.tile_size // 2
        for move in self.solution:
            sx, sy = curr_x * self.tile_size + half, curr_y * self.tile_size + half
            if move == 'N': curr_y -= 1
            elif move == 'S': curr_y += 1
            elif move == 'E': curr_x += 1
            elif move == 'W': curr_x -= 1
            ex, ey = curr_x * self.tile_size + half, curr_y * self.tile_size + half
            self._draw_line(sx, sy, ex, ey, self.solu_color)

    def render(self, *args):
        """Dibuja solo cuando la bandera needs_update es True"""
        if not self.needs_update:
            return 0
        
        # Limpiar buffer
        for i in range(len(self.img_data)):
            self.img_data[i] = 0

        # Dibujar laberinto
        for y in range(self.height):
            for x in range(self.width):
                px, py = x * self.tile_size, y * self.tile_size
                val = self.grid[y][x]
                if val & 1: self._draw_line(px, py, px + self.tile_size, py, self.wall_color)
                if val & 2: self._draw_line(px + self.tile_size, py, px + self.tile_size, py + self.tile_size, self.wall_color)
                if val & 4: self._draw_line(px, py + self.tile_size, px + self.tile_size, py + self.tile_size, self.wall_color)
                if val & 8: self._draw_line(px, py, px, py + self.tile_size, self.wall_color)

        if self.show_solution:
            self.draw_path()

        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, self.img, 0, 0)
        self.needs_update = False # Resetear bandera
        return 0

    def handle_keys(self, keycode, *args):
        # ESTE PRINT ES CLAVE: Si la 'S' no funciona, mira qué número sale aquí
        print(f"DEBUG: Tecla pulsada = {keycode}")

        if keycode in [53, 65307, 0xFF1B]: # ESC
            os._exit(0)
        elif keycode in [1, 115, 83, 31]: # S
            self.show_solution = not self.show_solution
            self.needs_update = True
        elif keycode in [15, 114, 82, 40]: # R
            print("Regenerando laberinto...")
            self.maze_obj.grid = [[15 for _ in range(self.width)] for _ in range(self.height)]
            if self.config.get('ALGORITHM') == 'PRIM':
                self.maze_obj.generate_prim()
            else:
                self.maze_obj.generate()
            self.grid = self.maze_obj.grid
            self.solution = self.maze_obj.solve()
            self.show_solution = False
            self.needs_update = True
        return 0

    def run(self):
        self.mlx.mlx_key_hook(self.win_ptr, self.handle_keys, None)
        # El loop_hook se encarga de pintar en cuanto la ventana esté lista
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.render, None)
        self.mlx.mlx_loop(self.mlx_ptr)