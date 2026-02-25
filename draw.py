import os
import random
from mlx import Mlx
import time
from animator import Animator
from player import draw_player_buffer, draw_player_overlay


class DrawMaze:
    def __init__(self, width, height, grid, config, solution, maze_obj):
        self.maze_obj = maze_obj
        self.grid = grid
        self.width = width
        self.height = height
        self.config = config
        self.solution = solution
        self.tile_size = 25
        self.show_solution = False
        self.needs_update = True
        self.wall_thickness = 5

        self.anim_duration = 5.0
        self.anim_start_time = None

        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        if not self.mlx_ptr:
            os._exit(1)

        self.win_w = self.width * self.tile_size
        self.win_h = self.height * self.tile_size
        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr, self.win_w,
            self.win_h, "A-Maze-ing 42 - Premium Visualizer")

        self.img = self.mlx.mlx_new_image(self.mlx_ptr, self.win_w, self.win_h)
        addr = self.mlx.mlx_get_data_addr(self.img)
        self.img_data, self.bpp, self.line_len, self.endian = addr

        self.wall_color = 0xFF1493
        self.solu_color = 0x00FFFF
        self.bg_color = 0x000000
        self.animator = Animator()
        self.player_pos = self.maze_obj.entry
        self.player_color = 0xFFFF00
        self.game_over = False
        self.step_count = 0

    def _put_pixel(self, x, y, color):
        if 0 <= x < self.win_w and 0 <= y < self.win_h:
            offset = (y * self.line_len) + (x * (self.bpp // 8))
            self.img_data[offset] = color & 0xFF
            self.img_data[offset + 1] = (color >> 8) & 0xFF
            self.img_data[offset + 2] = (color >> 16) & 0xFF
            self.img_data[offset + 3] = 0xFF

    def _clear_buffer(self):
        """Limpia el buffer de imagen a negro absoluto."""
        for y in range(self.win_h):
            for x in range(self.win_w):
                self._put_pixel(x, y, 0x000000)

    def _draw_line(self, x1, y1, x2, y2, color, thickness=1):
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        th = max(1, int(thickness))
        if x1 == x2:
            half = th // 2
            for off in range(th):
                dx = off - half
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    self._put_pixel(x1 + dx, y, color)
        elif y1 == y2:
            half = th // 2
            for off in range(th):
                dy = off - half
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    self._put_pixel(x, y1 + dy, color)

    def _draw_border(self, color, thickness=3):
        for t in range(thickness):
            self._draw_line(0, t, self.win_w - 1, t, color)
        for t in range(thickness):
            self._draw_line(0, self.win_h - 1 - t, self.win_w - 1, self.win_h - 1 - t, color)
        for t in range(thickness):
            self._draw_line(t, 0, t, self.win_h - 1, color)
        for t in range(thickness):
            self._draw_line(self.win_w - 1 - t, 0, self.win_w - 1 - t, self.win_h - 1, color)

    def draw_path(self):
        if not self.solution:
            self.solution = self.maze_obj.solve()
        if self.anim_start_time is None:
            return
        elapsed = time.time() - self.anim_start_time
        t = min(1.0, elapsed / self.anim_duration)
        steps_to_draw = int(len(self.solution) * t)
        curr_x, curr_y = self.maze_obj.entry
        half = self.tile_size // 2
        for i in range(steps_to_draw):
            move = self.solution[i]
            sx, sy = (curr_x * self.tile_size + half, curr_y * self.tile_size + half)
            if move == 'N': curr_y -= 1
            elif move == 'S': curr_y += 1
            elif move == 'E': curr_x += 1
            elif move == 'W': curr_x -= 1
            ex, ey = (curr_x * self.tile_size + half, curr_y * self.tile_size + half)
            self._draw_line(sx, sy, ex, ey, self.solu_color)
        if t < 1.0: self.needs_update = True

    def _fill_tile(self, x, y, color):
        px, py = x * self.tile_size, y * self.tile_size
        for dy in range(self.tile_size):
            for dx in range(self.tile_size):
                self._put_pixel(px + dx, py + dy, color)

    def change_wall_color(self) -> None:
        colors = [0xFF8C00, 0x8A2BE2, 0xFF00FF, 0xFFD700, 0x1E90FF, 0xFF69B4, 0x32CD32, 0x4B0082, 0x7FFF00, 0x0000FF]
        new_color = random.choice(colors)
        while new_color == self.wall_color:
            new_color = random.choice(colors)
        self.wall_color = new_color
        self.needs_update = True

    def render(self, *args):
        # --- CASO 1: PANTALLA FINAL (GAME OVER) ---
        if self.game_over:
            self._clear_buffer()
            self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
            self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, self.img, 0, 0)
            
            char_w = 10
            msg = "You have solved the A-Maze-Ing!"
            steps_msg = f"Total steps: {self.step_count}"
            hint = "Press (R) Play again | (Esc) Exit"
            
            # Cálculo de centrado con margen mínimo de 5px para ventanas pequeñas
            msg_x = max(5, (self.win_w - len(msg) * char_w) // 2)
            steps_x = max(5, (self.win_w - len(steps_msg) * char_w) // 2)
            hint_x = max(5, (self.win_w - len(hint) * char_w) // 2)
            msg_y = self.win_h // 2
            
            self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, msg_x, msg_y, 0xFFFFFF, msg)
            self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, steps_x, msg_y + 30, 0x00FF00, steps_msg)
            self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, hint_x, msg_y + 60, 0xFFFFFF, hint)
            
            self.needs_update = False
            return 0

        # --- CASO 2: SIN CAMBIOS (OPTIMIZACIÓN) ---
        if not self.needs_update:
            self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, self.img, 0, 0)
            draw_player_buffer(self)
            draw_player_overlay(self)
            return 0

        # --- CASO 3: DIBUJADO NORMAL DEL JUEGO ---
        self._clear_buffer()

        # Entrada y Salida
        self._fill_tile(self.maze_obj.entry[0], self.maze_obj.entry[1], 0x00FF00)
        self._fill_tile(self.maze_obj.exit_pt[0], self.maze_obj.exit_pt[1], 0xFF0000)

        # Celdas del Logo 42 y Muros
        for y in range(self.height):
            for x in range(self.width):
                px, py = x * self.tile_size, y * self.tile_size
                if (x, y) in self.maze_obj.pattern_cells:
                    for ry in range(self.tile_size):
                        for rx in range(self.tile_size):
                            self._put_pixel(px + rx, py + ry, 0xFFFFFF)
                val = self.grid[y][x]
                if val & 1: self._draw_line(px, py, px + self.tile_size, py, self.wall_color, self.wall_thickness)
                if val & 2: self._draw_line(px + self.tile_size, py, px + self.tile_size, py + self.tile_size, self.wall_color, self.wall_thickness)
                if val & 4: self._draw_line(px, py + self.tile_size, px + self.tile_size, py + self.tile_size, self.wall_color, self.wall_thickness)
                if val & 8: self._draw_line(px, py, px, py + self.tile_size, self.wall_color, self.wall_thickness)

        self._draw_border(0xFFFFFF, thickness=4)

        if self.show_solution:
            self.draw_path()
            if self.solution and not self.animator.active:
                curr_x, curr_y = self.maze_obj.entry
                path_cells = [(curr_x, curr_y)]
                for move in self.solution:
                    if move == 'N': curr_y -= 1
                    elif move == 'S': curr_y += 1
                    elif move == 'E': curr_x += 1
                    elif move == 'W': curr_x -= 1
                    path_cells.append((curr_x, curr_y))
                self.animator.start(path_cells, duration=self.anim_duration)

        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, self.img, 0, 0)
        
        if self.animator and self.animator.active:
            self.animator.draw(self)
        
        draw_player_buffer(self)
        draw_player_overlay(self)

        header = "A-MAZE-ING"
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, max(5, (self.win_w - len(header)*10)//2), 15, 0xFFFFFF, header)
        
        self.needs_update = self.show_solution and self.anim_start_time is not None
        return 0

    def handle_keys(self, keycode, *args):
        if keycode in [53, 65307, 0xFF1B]:
            os._exit(0)

        if not self.game_over:
            if keycode in [119, 87, 65362, 126]: self._try_move_player(0, -1)
            elif keycode in [115, 83, 65364, 125]: self._try_move_player(0, 1)
            elif keycode in [97, 65, 65361, 123]: self._try_move_player(-1, 0)
            elif keycode in [100, 68, 65363, 124]: self._try_move_player(1, 0)

        # --- TECLAS ESPECIALES CON PRINTS ---
        if keycode in [112, 80]: # P
            self.show_solution = not self.show_solution
            if self.show_solution:
                print("Showing the solution")
                self.anim_start_time = time.time()
            else:
                print("Hiding the solution")
                self.anim_start_time = None
            self.needs_update = True

        elif keycode in [15, 114, 82, 40]: # R
            print("Regenerating the maze")
            from maze_generator import MazeGenerator
            new_maze = MazeGenerator(self.width, self.height, self.maze_obj.entry, self.maze_obj.exit_pt, self.maze_obj.output_file, perfect=True)
            algo = self.config.get('ALGORITHM', 'DFS').upper()
            if algo == 'PRIM': new_maze.generate_prim()
            else: new_maze.generate()
            self.maze_obj = new_maze
            self.grid = new_maze.grid
            self.solution = self.maze_obj.solve()
            self.player_pos = self.maze_obj.entry
            self.game_over = False
            self.step_count = 0
            self.show_solution = False
            self.anim_start_time = None
            if self.animator: self.animator.active = False
            self.needs_update = True

        elif keycode in [8, 99, 67, 14]: # C
            print("Changing colors")
            self.change_wall_color()
        return 0

    def run(self):
        self.mlx.mlx_key_hook(self.win_ptr, self.handle_keys, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.render, None)
        self.mlx.mlx_loop(self.mlx_ptr)

    def _can_move_from(self, x: int, y: int, direction_bit: int) -> bool:
        if not (0 <= x < self.width and 0 <= y < self.height): return False
        return not (self.grid[y][x] & direction_bit)

    def _try_move_player(self, dx: int, dy: int) -> None:
        px, py = self.player_pos
        bits = {(0, -1): 1, (1, 0): 2, (0, 1): 4, (-1, 0): 8}
        bit = bits.get((dx, dy))
        if bit and self._can_move_from(px, py, bit):
            self.player_pos = (px + dx, py + dy)
            self.step_count += 1
            self.needs_update = True
            if self.player_pos == self.maze_obj.exit_pt:
                self.game_over = True
                if self.animator: self.animator.active = False
                self.needs_update = True