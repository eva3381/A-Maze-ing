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
        self.needs_update = True 

        # Lista de colores para los MUROS (rotan con 'C')
        self.wall_colors = [
            0xFF1493,
            0x00FFFF,
            0xFFFF00,
            0xFFFFFF,
            0x8A2BE2,
            0xFF4500
        ]
        self.color_idx = 0
        self.wall_color = self.wall_colors[self.color_idx]
        
        # Colores FIJOS
        self.solu_color = 0xFFFFFF   # Blanco para el camino
        self.entry_color = 0x0000FF  # Azul FIJO para la entrada
        self.exit_color = 0x00FF00   # Verde FIJO para la salida

        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        if not self.mlx_ptr:
            os._exit(1)

        self.win_w = self.width * self.tile_size
        self.win_h = self.height * self.tile_size
        self.win_ptr = self.mlx.mlx_new_window(self.mlx_ptr, self.win_w, self.win_h, "A-Maze-ing 42")

        self.img = self.mlx.mlx_new_image(self.mlx_ptr, self.win_w, self.win_h)
        addr = self.mlx.mlx_get_data_addr(self.img)
        self.img_data, self.bpp, self.line_len, self.endian = addr

    def _put_pixel(self, x, y, color):
        if 0 <= x < self.win_w and 0 <= y < self.win_h:
            offset = (y * self.line_len) + (x * (self.bpp // 8))
            self.img_data[offset] = color & 0xFF
            self.img_data[offset + 1] = (color >> 8) & 0xFF
            self.img_data[offset + 2] = (color >> 16) & 0xFF
            self.img_data[offset + 3] = 0

    def _draw_line(self, x1, y1, x2, y2, color):
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        if x1 == x2:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self._put_pixel(x1, y, color)
        elif y1 == y2:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self._put_pixel(x, y1, color)

    def _fill_rect(self, x, y, w, h, color):
        """Dibuja un cuadrado relleno"""
        for i in range(x, x + w):
            for j in range(y, y + h):
                self._put_pixel(i, j, color)

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
        if not self.needs_update:
            return 0
        
        # Limpiar fondo
        for i in range(len(self.img_data)):
            self.img_data[i] = 0

        # Dibujar celdas y muros
        for y in range(self.height):
            for x in range(self.width):
                px, py = x * self.tile_size, y * self.tile_size
                
                # Pintar fondos fijos de Entrada y Salida
                if (x, y) == self.maze_obj.entry:
                    self._fill_rect(px, py, self.tile_size, self.tile_size, self.entry_color)
                elif (x, y) == self.maze_obj.exit_pt:
                    self._fill_rect(px, py, self.tile_size, self.tile_size, self.exit_color)

                # Dibujar los muros con el color actual de la rotación
                val = self.grid[y][x]
                if val & 1: self._draw_line(px, py, px + self.tile_size, py, self.wall_color)
                if val & 2: self._draw_line(px + self.tile_size, py, px + self.tile_size, py + self.tile_size, self.wall_color)
                if val & 4: self._draw_line(px, py + self.tile_size, px + self.tile_size, py + self.tile_size, self.wall_color)
                if val & 8: self._draw_line(px, py, px, py + self.tile_size, self.wall_color)

        if self.show_solution:
            self.draw_path()

        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, self.img, 0, 0)
        self.needs_update = False 
        return 0

    def handle_keys(self, keycode, *args):
        # ESC
        if keycode in [53, 65307, 0xFF1B]: 
            os._exit(0)
        
        # S (Solución)
        elif keycode in [1, 115, 83, 31]: 
            self.show_solution = not self.show_solution
            self.needs_update = True
            
        # C (Cambiar color de muros - Los puntos de entrada/salida NO cambian)
        elif keycode in [8, 99, 67, 45]: 
            self.color_idx = (self.color_idx + 1) % len(self.wall_colors)
            self.wall_color = self.wall_colors[self.color_idx]
            self.needs_update = True

        # R (Regenerar)
        elif keycode in [15, 114, 82, 40]: 
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
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.render, None)
        self.mlx.mlx_loop(self.mlx_ptr)
