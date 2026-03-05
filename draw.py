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

        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        if not self.mlx_ptr:
            os._exit(1)

        self.win_w = max(self.width * self.tile_size, 320)
        self.win_h = max(self.height * self.tile_size, 200)

        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr, self.win_w, self.win_h, "A-Maze-Ing 42")

        self.img = self.mlx.mlx_new_image(self.mlx_ptr, self.win_w, self.win_h)
        addr = self.mlx.mlx_get_data_addr(self.img)
        self.img_data, self.bpp, self.line_len, self.endian = addr

        self.wall_color = 0xFF1493
        self.solu_color = 0x00FFFF
        self.bg_color = 0x000000
        self.logo_color = 0xFFFFFF
        self.player_color = 0xFFFFFF
        self.coin_color = 0xFFD700

        self.animator = Animator()
        self.player_pos = self.maze_obj.entry
        self.game_over = False
        self.coins = set()
        self.coins_collected = 0
        self.moves_count = 0

        place_coins(self)

    def exit_program(self, *args):
        """Cierra el programa limpiamente (usado por ESC y por el botón X)."""
        print("\nClosing game... See you next time!")
        # Destruir ventana antes de salir para evitar procesos zombies
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        os._exit(0)
        return 0

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
        half = th // 2
        if x1 == x2:
            for off in range(th):
                dx = off - half
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    self._put_pixel(x1 + dx, y, color)
        elif y1 == y2:
            for off in range(th):
                dy = off - half
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    self._put_pixel(x, y1 + dy, color)

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
            sx, sy = (curr_x * self.tile_size + half, curr_y * self.tile_size
                      + half)
            if move == 'N':
                curr_y -= 1
            elif move == 'S':
                curr_y += 1
            elif move == 'E':
                curr_x += 1
            elif move == 'W':
                curr_x -= 1
            ex, ey = (curr_x * self.tile_size + half, curr_y *
                      self.tile_size + half)
            self._draw_line(sx, sy, ex, ey, self.solu_color, 2)
        if t < 1.0:
            self.needs_update = True

    def _fill_tile(self, x, y, color):
        px, py = x * self.tile_size, y * self.tile_size
        for dy in range(self.tile_size):
            for dx in range(self.tile_size):
                self._put_pixel(px + dx, py + dy, color)

    def change_wall_color(self):
        """Cambia los colores de las paredes y el logo a colores aleatorios."""
        print("Changing wall color...")
        # Paleta de colores disponibles para las paredes
        wall_colors = [0xFF8C00, 0x8A2BE2, 0xFF00FF, 0xFFD700, 0x1E90FF,
                       0xFF69B4, 0x32CD32, 0x4B0082, 0x7FFF00, 0x0000FF]
        # Paleta de colores disponibles para el logo
        logo_colors = [0xFFFFFF, 0xAAAAAA, 0x00FF7F, 0xFF4500, 0x00CED1,
                       0xADFF2F, 0xFF6347, 0x40E0D0]
        self.wall_color = random.choice(wall_colors)
        self.logo_color = random.choice(logo_colors)
        self.needs_update = True

    def _render_final_screen(self):
        """ Renderiza la pantalla final con estadísticas del juego
          completado."""
        # 1. Limpiar pantalla
        for i in range(len(self.img_data)):
            self.img_data[i] = 0
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, self.img,
                                         0, 0)

        mid_x, mid_y = self.win_w // 2, self.win_h // 2

        # --- PANEL DE VICTORIA (Aparece en todos los tamaños) ---

        # Centrar el mensaje
        wow_text = "WOW!"
        wow_offset = (len(wow_text) * 10) // 2
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr,
                                mid_x - wow_offset - 1, mid_y - 40 + 1,
                                0x000000, wow_text)
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, mid_x - wow_offset,
                                mid_y - 40, 0xFFFF00, wow_text)

        # Estadísticas: Pasos y Monedas
        stats = f"Moves: {self.moves_count} | Coins: {self.coins_collected}"
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, mid_x - 85, mid_y,
                                0x00FFFF, stats)

        # Tiempo transcurrido
        total_time = int(self.end_time - self.play_start_time)
        time_str = f"Time: {total_time}s"
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, mid_x - 35,
                                mid_y + 25, 0x00FF00, time_str)

        # --- INSTRUCCIONES DINÁMICAS (Lo único que depende del tamaño) ---
        if self.width < 20 or self.height < 20:
            instr_text = "R | ESC"
            offset_x = 25
        else:
            instr_text = "Press R to Restart | ESC to Exit"
            offset_x = 110

        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, mid_x - offset_x,
                                mid_y + 65, 0xAAAAAA, instr_text)

    def render(self, *args):
        if self.game_over:
            self._render_final_screen()
            return 0
        if self.show_solution and self.anim_start_time:
            self.needs_update = True
        if not self.needs_update:
            self.mlx.mlx_put_image_to_window(self.mlx_ptr,
                                             self.win_ptr, self.img, 0, 0)
            draw_player_overlay(self)
            return 0

        for i in range(len(self.img_data)):
            self.img_data[i] = 0
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.maze_obj.pattern_cells:
                    self._fill_tile(x, y, self.logo_color)

        self._fill_tile(*self.maze_obj.entry, 0x00FF00)
        self._fill_tile(*self.maze_obj.exit_pt, 0xFF0000)

        if self.show_solution:
            self.draw_path()

        for y in range(self.height):
            for x in range(self.width):
                px, py = x * self.tile_size, y * self.tile_size
                val = self.grid[y][x]
                if val & 1:
                    self._draw_line(px, py, px + self.tile_size, py,
                                    self.wall_color, self.wall_thickness)
                if val & 2:
                    self._draw_line(px + self.tile_size, py, px +
                                    self.tile_size, py + self.tile_size,
                                    self.wall_color, self.wall_thickness)
                if val & 4:
                    self._draw_line(px, py + self.tile_size, px +
                                    self.tile_size, py + self.tile_size,
                                    self.wall_color, self.wall_thickness)
                if val & 8:
                    self._draw_line(px, py, px, py + self.tile_size,
                                    self.wall_color, self.wall_thickness)

        if getattr(self, 'coins', None):
            draw_coins(self)
        draw_player_buffer(self)
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        self.mlx.mlx_put_image_to_window(self.mlx_ptr,
                                         self.win_ptr, self.img, 0, 0)
        draw_player_overlay(self)
        if self.play_start_time:
            draw_timer_overlay(self, int(time.time() - self.play_start_time))
        # Mostrar estadísticas (movimientos y monedas)
        #  en la esquina superior derecha (no se actualizan continuamente)
        stats_text = f"Moves: {
            self.moves_count} | Coins: {self.coins_collected}"
        stats_x = max(10, self.win_w - 240)
        self.mlx.mlx_string_put(
            self.mlx_ptr, self.win_ptr, stats_x, 20, 0xFFFFFF, stats_text)
        self.needs_update = False
        return 0

    def handle_keys(self, keycode, *args):
        # ESC para cerrar
        if keycode in [53, 65307, 0xFF1B]:
            self.exit_program()
        if keycode in [114, 15, 82]:
            print("Regenerating a new random maze...")
            self.maze_obj.regenerate()
            self.maze_obj.generate()
            self.grid = self.maze_obj.grid
            self.solution = self.maze_obj.solve()
            self._reset_game()
            return 0

        if keycode in [119, 87, 65362, 126]:
            self._try_move_player(0, -1)
        elif keycode in [115, 83, 65364, 125]:
            self._try_move_player(0, 1)
        elif keycode in [97, 65, 65361, 123]:
            self._try_move_player(-1, 0)
        elif keycode in [100, 68, 65363, 124]:
            self._try_move_player(1, 0)
        elif keycode in [112, 80]:
            self.show_solution = not self.show_solution
            if self.show_solution:
                print("Solution calculated and visible")
                self.anim_start_time = time.time()
            else:
                print("Solution hidden")
                self.anim_start_time = None
            self.needs_update = True
        elif keycode in [8, 99, 67]:
            self.change_wall_color()
        return 0

    def _try_move_player(self, dx, dy):
        px, py = self.player_pos
        bit = {(0, -1): 1, (1, 0): 2, (0, 1): 4, (-1, 0): 8}.get((dx, dy))
        if not (self.grid[py][px] & bit):
            self.player_pos = (px + dx, py + dy)
            self.moves_count += 1
            if collect_coin(self, self.player_pos):
                self.coins_collected += 1
            if self.player_pos == self.maze_obj.exit_pt:
                print("🏆 Goal reached! Maze completed.")
                self.end_time = time.time()
                self.game_over = True
            self.needs_update = True

    def _reset_game(self):
        self.player_pos = self.maze_obj.entry
        self.game_over = False
        self.coins_collected = 0
        self.moves_count = 0
        self.play_start_time = time.time()
        self.anim_start_time = None
        self.show_solution = False
        place_coins(self)
        self.needs_update = True

    def run(self):
        """Inicia el bucle principal del juego y
          configura los hooks de eventos."""
        self.play_start_time = time.time()
        # Configurar hook para eventos de teclado
        self.mlx.mlx_key_hook(self.win_ptr, self.handle_keys, None)
        # Configurar hook para el botón X de cerrar ventana (Evento 33
        #  con máscara 0 = ClientMessage)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self.exit_program, None)
        # Configurar hook para renderizar en cada frame
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.render, None)
        # Iniciar el bucle principal
        self.mlx.mlx_loop(self.mlx_ptr)
