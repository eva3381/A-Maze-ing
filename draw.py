import os
import random
from mlx import Mlx
import time
from animator import Animator
from player import draw_player_buffer, draw_player_overlay
from timer import draw_timer_overlay
from coins import place_coins, draw_coins, collect_coin


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
        self.wall_thickness = 3

        self.anim_duration = 5.0
        self.anim_start_time = None
        self.play_start_time = None
        self.end_time = None
        self._last_timer_sec = None

        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        if not self.mlx_ptr:
            os._exit(1)

        # Calculamos el tamaño de la ventana asegurando un mínimo para que quepa el texto final
        self.win_w = max(self.width * self.tile_size, 320) 
        self.win_h = max(self.height * self.tile_size, 200)
        
        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr, self.win_w,
            self.win_h, "A-Maze-ing 42 - Premium Visualizer")

        self.img = self.mlx.mlx_new_image(self.mlx_ptr, self.win_w, self.win_h)
        addr = self.mlx.mlx_get_data_addr(self.img)
        self.img_data, self.bpp, self.line_len, self.endian = addr

        self.wall_color = 0xFF1493
        self.solu_color = 0x00FFFF
        self.bg_color = 0x000000
        self.logo_color = 0xFFFFFF

        self.animator = Animator()
        self.player_pos = self.maze_obj.entry
        self.player_color = 0xFFFFFF
        self.game_over = False
        self.coins = set()
        self.coins_collected = 0
        self.moves_count = 0
        self.coin_color = 0xFFD700
        place_coins(self)

    def _put_pixel(self, x, y, color):
        if 0 <= x < self.win_w and 0 <= y < self.win_h:
            offset = (y * self.line_len) + (x * (self.bpp // 8))
            self.img_data[offset] = color & 0xFF
            self.img_data[offset + 1] = (color >> 8) & 0xFF
            self.img_data[offset + 2] = (color >> 16) & 0xFF
            self.img_data[offset + 3] = 0xFF

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
            self._draw_line(0, self.win_h - 1 - t, self.win_w - 1, self.win_h - 1 - t, color)
            self._draw_line(t, 0, t, self.win_h - 1, color)
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
        if t < 1.0:
            self.needs_update = True

    def _fill_tile(self, x, y, color):
        px, py = x * self.tile_size, y * self.tile_size
        for dy in range(self.tile_size):
            for dx in range(self.tile_size):
                self._put_pixel(px + dx, py + dy, color)

    def change_wall_color(self):
        wall_colors = [0xFF8C00, 0x8A2BE2, 0xFF00FF, 0xFFD700, 0x1E90FF, 0xFF69B4, 0x32CD32, 0x4B0082, 0x7FFF00, 0x0000FF]
        logo_colors = [0xFFFFFF, 0xAAAAAA, 0x00FF7F, 0xFF4500, 0x00CED1, 0xADFF2F, 0xFF6347, 0x40E0D0]
        
        new_wall = random.choice(wall_colors)
        while new_wall == self.wall_color:
            new_wall = random.choice(wall_colors)
        self.wall_color = new_wall

        new_logo = random.choice(logo_colors)
        while new_logo == self.wall_color:
            new_logo = random.choice(logo_colors)
        self.logo_color = new_logo

        self.needs_update = True

    def _render_final_screen(self):
        # 1. Limpiar buffer y ventana
        for i in range(len(self.img_data)):
            self.img_data[i] = 0
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, self.img, 0, 0)

        # 2. Selección de mensaje robusta
        if self.width <= 7: 
            msg = "YOU WIN!"
        elif self.width <= 14: 
            msg = "YOU HAVE SOLVED IT!"
        else: 
            msg = "Well Done!!"

        # 3. Centrado manual mejorado (estimando 10px por letra en MLX)
        char_w = 8 
        msg_len = len(msg) * char_w
        msg_x = (self.win_w - msg_len) // 2
        msg_y = self.win_h // 3
        
        # Dibujar mensaje principal
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, max(10, msg_x), msg_y, 0xFFFFFF, msg)

        # 4. Estadísticas finales
        total = int((self.end_time or time.time()) - self.play_start_time)
        stats = f"Time: {total // 60}:{total % 60:02d} | Coins: {self.coins_collected}"
        stats_x = (self.win_w - (len(stats) * char_w)) // 2
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, max(10, stats_x), msg_y + 40, 0x00FFFF, stats)

        hint = "Press (R) Restart | (ESC) Exit"
        hint_x = (self.win_w - (len(hint) * char_w)) // 2
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, max(10, hint_x), msg_y + 80, 0xAAAAAA, hint)
        
        self.needs_update = False

    def render(self, *args):
        if self.game_over:
            self._render_final_screen()
            return 0

        if not self.needs_update:
            self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, self.img, 0, 0)
            draw_player_overlay(self)
            if self.play_start_time and self.width > 5:
                elapsed = int(time.time() - self.play_start_time)
                draw_timer_overlay(self, elapsed)
            return 0

        # Dibujo normal del mapa
        for i in range(len(self.img_data)): self.img_data[i] = 0
        self._fill_tile(*self.maze_obj.entry, 0x00FF00)
        self._fill_tile(*self.maze_obj.exit_pt, 0xFF0000)

        for y in range(self.height):
            for x in range(self.width):
                px, py = x * self.tile_size, y * self.tile_size
                if (x, y) in self.maze_obj.pattern_cells:
                    self._fill_tile(x, y, self.logo_color)
                val = self.grid[y][x]
                if val & 1: self._draw_line(px, py, px + self.tile_size, py, self.wall_color, self.wall_thickness)
                if val & 2: self._draw_line(px + self.tile_size, py, px + self.tile_size, py + self.tile_size, self.wall_color, self.wall_thickness)
                if val & 4: self._draw_line(px, py + self.tile_size, px + self.tile_size, py + self.tile_size, self.wall_color, self.wall_thickness)
                if val & 8: self._draw_line(px, py, px, py + self.tile_size, self.wall_color, self.wall_thickness)

        self._draw_border(0xFFFFFF, thickness=4)
        if self.show_solution: self.draw_path()
        if getattr(self, 'coins', None): draw_coins(self)

        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, self.img, 0, 0)
        
        if self.animator and self.animator.active: self.animator.draw(self)
        draw_player_buffer(self)
        draw_player_overlay(self)

        self.needs_update = False
        return 0

    def handle_keys(self, keycode, *args):
        if keycode in [53, 65307, 0xFF1B]: os._exit(0)
        if self.game_over:
            if keycode in [15, 114, 82]: self._reset_game()
            return 0

        if keycode in [119, 87, 65362, 126]: self._try_move_player(0, -1)
        elif keycode in [115, 83, 65364, 125]: self._try_move_player(0, 1)
        elif keycode in [97, 65, 65361, 123]: self._try_move_player(-1, 0)
        elif keycode in [100, 68, 65363, 124]: self._try_move_player(1, 0)
        elif keycode in [112, 80]:
            self.show_solution = not self.show_solution
            self.anim_start_time = time.time() if self.show_solution else None
            self.needs_update = True
        elif keycode in [8, 99, 67]: self.change_wall_color()
        return 0

    def _reset_game(self):
        from maze_generator import MazeGenerator
        new_maze = MazeGenerator(self.width, self.height, self.maze_obj.entry, self.maze_obj.exit_pt, self.maze_obj.output_file, True)
        new_maze.generate()
        self.maze_obj = new_maze
        self.grid = new_maze.grid
        self.solution = new_maze.solve()
        self.player_pos = self.maze_obj.entry
        self.game_over = False
        self.coins_collected = 0
        self.moves_count = 0
        self.play_start_time = time.time()
        place_coins(self)
        self.needs_update = True

    def _try_move_player(self, dx, dy):
        px, py = self.player_pos
        bit = {(0,-1):1, (1,0):2, (0,1):4, (-1,0):8}.get((dx, dy))
        if not (self.grid[py][px] & bit):
            self.player_pos = (px + dx, py + dy)
            if collect_coin(self, self.player_pos): self.coins_collected += 1
            if self.player_pos == self.maze_obj.exit_pt:
                self.game_over = True
                self.end_time = time.time()
            self.needs_update = True

    def run(self):
        self.play_start_time = time.time()
        self.mlx.mlx_key_hook(self.win_ptr, self.handle_keys, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.render, None)
        self.mlx.mlx_loop(self.mlx_ptr)
