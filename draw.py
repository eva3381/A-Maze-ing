import os
import random  # Necesario para la selección de colores
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
        # Grosor de los muros en píxeles (1 = 1px)
        self.wall_thickness = 3

        self.anim_duration = 5.0
        self.anim_start_time = None
        # Juego: tiempos de partida/fin para el temporizador
        self.play_start_time = None
        self.end_time = None
        # Estado para evitar redibujar el mismo segundo repetidamente
        self._last_timer_sec = None

        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        if not self.mlx_ptr:
            os._exit(1)

        self.win_w = self.width * self.tile_size
        self.win_h = self.height * self.tile_size
        self.win_ptr = self.mlx.mlx_new_window(
                                            self.mlx_ptr, self.win_w,
                                            self.win_h, "A-Maze-ing 42 "
                                            "- Premium Visualizer")

        self.img = self.mlx.mlx_new_image(self.mlx_ptr, self.win_w, self.win_h)
        addr = self.mlx.mlx_get_data_addr(self.img)
        self.img_data, self.bpp, self.line_len, self.endian = addr

        # Color inicial
        self.wall_color = 0xFF1493
        self.solu_color = 0x00FFFF
        self.bg_color = 0x000000
        self.logo_color = 0xFFFFFF

        # Animador del cuadrito que recorre la solución
        self.animator = Animator()
        # Posición del jugador (siempre existe) y estado del juego
        self.player_pos = self.maze_obj.entry
        # Color del jugador cambiado a blanco
        self.player_color = 0xFFFFFF
        self.game_over = False
        # Monedas y puntuación
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
        """Dibuja una línea horizontal o vertical con un grosor dado.

        thickness: número de píxeles en la dirección perpendicular a la línea.
        """
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        th = max(1, int(thickness))
        if x1 == x2:
            # Vertical: expandir en X
            half = th // 2
            for off in range(th):
                dx = off - half
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    self._put_pixel(x1 + dx, y, color)
        elif y1 == y2:
            # Horizontal: expandir en Y
            half = th // 2
            for off in range(th):
                dy = off - half
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    self._put_pixel(x, y1 + dy, color)

    # crear bordes
    def _draw_border(self, color, thickness=3):
        # Borde superior
        for t in range(thickness):
            self._draw_line(0, t, self.win_w - 1, t, color)

        # Borde inferior
        for t in range(thickness):
            self._draw_line(0, self.win_h - 1 - t,
                            self.win_w - 1, self.win_h - 1 - t, color)

        # Borde izquierdo
        for t in range(thickness):
            self._draw_line(t, 0, t, self.win_h - 1, color)

        # Borde derecho
        for t in range(thickness):
            self._draw_line(self.win_w - 1 - t, 0,
                            self.win_w - 1 - t, self.win_h - 1, color)

    def draw_path(self):
        if not self.solution:
            self.solution = self.maze_obj.solve()

        # Si aún no se ha iniciado la animación, no dibujamos nada
        if self.anim_start_time is None:
            return

        # Tiempo transcurrido desde que empezó la animación
        elapsed = time.time() - self.anim_start_time

        # Progreso entre 0 y 1
        t = min(1.0, elapsed / self.anim_duration)

        # Número de pasos a mostrar
        steps_to_draw = int(len(self.solution) * t)

        curr_x, curr_y = self.maze_obj.entry
        half = self.tile_size // 2

        for i in range(steps_to_draw):
            move = self.solution[i]
            sx, sy = (
                curr_x * self.tile_size + half,
                curr_y * self.tile_size + half
            )

            if move == 'N':
                curr_y -= 1
            elif move == 'S':
                curr_y += 1
            elif move == 'E':
                curr_x += 1
            elif move == 'W':
                curr_x -= 1

            ex, ey = (
                curr_x * self.tile_size + half,
                curr_y * self.tile_size + half
            )

            self._draw_line(sx, sy, ex, ey, self.solu_color)

        # Mientras la animación no termine, seguir actualizando frames
        if t < 1.0:
            self.needs_update = True

    def _fill_tile(self, x, y, color):
        """pintar por completo una celda del laberinto, rellenándola
          píxel a píxel con un color sólido"""
        px, py = x * self.tile_size, y * self.tile_size
        for dy in range(self.tile_size):
            for dx in range(self.tile_size):
                self._put_pixel(px + dx, py + dy, color)

    def change_wall_color(self, x=None, y=None, px=None, py=None):
        """Cambia los muros a un color aleatorio y
        también el color del logo 42."""
        wall_colors = [
            0xFF8C00, 0x8A2BE2, 0xFF00FF, 0xFFD700, 0x1E90FF,
            0xFF69B4, 0x32CD32, 0x4B0082, 0x7FFF00, 0x0000FF
        ]

        logo_colors = [
            0xFFFFFF, 0xAAAAAA, 0x00FF7F, 0xFF4500, 0x00CED1,
            0xADFF2F, 0xFF6347, 0x40E0D0
        ]

        # Elegir color de muro distinto al actual
        new_wall = random.choice(wall_colors)
        while new_wall == self.wall_color:
            new_wall = random.choice(wall_colors)
        self.wall_color = new_wall

        # Elegir color del logo distinto al color del muro
        new_logo = random.choice(logo_colors)
        while new_logo == self.wall_color:
            new_logo = random.choice(logo_colors)
        self.logo_color = new_logo

        # Repintar el logo 42 con el nuevo color
        for (cx, cy) in self.maze_obj.pattern_cells:
            px = cx * self.tile_size
            py = cy * self.tile_size
            for ry in range(self.tile_size):
                for rx in range(self.tile_size):
                    self._put_pixel(px + rx, py + ry, self.logo_color)

        self.needs_update = True

    def render(self, *args):
        # Si no hay cambios, simplemente volvemos a poner la imagen
        #  actual en la ventana
        if not self.needs_update:
            self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
                                             self.img, 0, 0)
            # Dibujar jugador en buffer y overlay para asegurar visibilidad
            if not self.game_over:
                draw_player_buffer(self)
                draw_player_overlay(self)
            # Mostrar temporizador en esquina superior derecha.
            if self.play_start_time is not None and not self.game_over:
                if self.width > 5 and self.height > 5:
                    elapsed = int(time.time() - self.play_start_time)
                    draw_timer_overlay(self, elapsed)
                # HUD: monedas y movimientos
                if self.width > 8 and self.height > 8:
                    hud = (
                        f"Coins: {self.coins_collected}"
                        f" Moves: {self.moves_count}")
                    char_w = 10
                    tx = max(10, self.win_w - (len(hud) * char_w) - 10)
                    ty = 10
                    self.mlx.mlx_string_put(
                        self.mlx_ptr, self.win_ptr,
                        tx, ty, 0xFFFFFF, hud)
            return 0

        # 1. LIMPIEZA DEL BUFFER (Fondo negro)
        for i in range(len(self.img_data)):
            self.img_data[i] = 0

        entry_color = 0x00FF00
        exit_color = 0xFF0000
        # Pintar entrada
        ex, ey = self.maze_obj.entry
        self._fill_tile(ex, ey, entry_color)

        # Pintar salida
        sx, sy = self.maze_obj.exit_pt
        self._fill_tile(sx, sy, exit_color)

        # 2. DIBUJO DE CELDAS Y MUROS
        for y in range(self.height):
            for x in range(self.width):
                px, py = x * self.tile_size, y * self.tile_size

                # --- RELLENO BLANCO PARA EL LOGO 42 ---
                # Usamos el set 'pattern_cells' definido en el MazeGenerator

                if (x, y) in self.maze_obj.pattern_cells:
                    # Rellenamos el cuadrado de la celda de color blanco
                    for ry in range(self.tile_size):
                        for rx in range(self.tile_size):
                            self._put_pixel(px + rx, py + ry, self.logo_color)

                # --- DIBUJO DE MUROS ---
                # Se dibujan después del relleno para que queden por encima
                val = self.grid[y][x]
                # Norte
                if val & 1:
                    self._draw_line(px, py, px + self.tile_size,
                                    py, self.wall_color, self.wall_thickness)
                # Este
                if val & 2:
                    self._draw_line(px + self.tile_size, py,
                                    px + self.tile_size, py + self.tile_size,
                                    self.wall_color, self.wall_thickness)
                # Sur
                if val & 4:
                    self._draw_line(px, py + self.tile_size,
                                    px + self.tile_size, py + self.tile_size,
                                    self.wall_color, self.wall_thickness)
                # Oeste
                if val & 8:
                    self._draw_line(px, py, px, py + self.tile_size,
                                    self.wall_color, self.wall_thickness)

                # Añadir un borde
        self._draw_border(0xFFFFFF, thickness=4)

        # 4. SOLUCIÓN
        if self.show_solution:
            self.draw_path()
            # Iniciar animador si hay una solución y aún no está activo
            if self.solution and not self.animator.active:
                # Convertir la solución ('N','E',...) a lista de celdas
                curr_x, curr_y = self.maze_obj.entry
                cells = [(curr_x, curr_y)]
                for move in self.solution:
                    if move == 'N':
                        curr_y -= 1
                    elif move == 'S':
                        curr_y += 1
                    elif move == 'E':
                        curr_x += 1
                    elif move == 'W':
                        curr_x -= 1
                    cells.append((curr_x, curr_y))
                self.animator.start(cells, duration=self.anim_duration)

        # 5. VOLCADO FINAL DE LA IMAGEN
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        # Dibujar monedas en el buffer antes de volcar la imagen
        if getattr(self, 'coins', None):
            draw_coins(self)

        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img, 0, 0
        )

        # Dibujar el cuadrito animado encima de la imagen si está activo
        if self.animator and self.animator.active:
            self.animator.draw(self)

        # Dibujar el jugador únicamente si el juego NO ha terminado.
        if not self.game_over:
            draw_player_buffer(self)
            draw_player_overlay(self)
            # Mostrar temporizador en esquina superior derecha
            if self.play_start_time is not None:
                if self.width > 5 and self.height > 5:
                    elapsed = int(time.time() - self.play_start_time)
                    draw_timer_overlay(self, elapsed)

        # Si el jugador llegó a la salida, marcar fin del juego y mostrar
        # pantalla final (negra + mensaje). El único modo de terminar es llegar
        # a la salida; no salimos con ESC.
        # Si el jugador llegó a la salida
        if self.game_over:
            self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
            for i in range(len(self.img_data)):
                self.img_data[i] = 0
            self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
            self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
                                             self.img, 0, 0)

            # Selección del mensaje según tamaño del laberinto
            if self.width <= 3 and self.height <= 3:
                msg = ""
            elif self.width <= 7 and self.height <= 7:
                msg = "You win!"
            elif self.width < 14 and self.height < 14:
                msg = "You have solved!"
            else:
                msg = "You have solved the A-Maze-Ing!"

            # Dibujar mensaje principal
            char_w = 10
            msg_w = len(msg) * char_w
            msg_x = max(0, (self.win_w - msg_w) // 2)
            msg_y = self.win_h // 2
            self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr,
                                    msg_x, msg_y, 0xFFFFFF, msg)

            # Mostrar score SOLO si el laberinto es mayor a 14x14
            if self.width >= 14 and self.height >= 14:
                hint = "Press (R) Play again | (Esc) Exit"
                hint_w = len(hint) * char_w
                hint_x = max(20, (self.win_w - hint_w) // 2)
                hint_y = msg_y + 24
                self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr,
                                        hint_x, hint_y, 0xFFFFFF, hint)

                # Tiempo final
                if self.play_start_time is not None:
                    end_t = self.end_time or time.time()
                    total = int(end_t - self.play_start_time)
                    mins = total // 60
                    secs = total % 60
                    final_text = f"Total time: {mins}:{secs:02d}"
                    final_w = len(final_text) * char_w
                    final_x = max(10, (self.win_w - final_w) // 2)
                    final_y = hint_y + 24
                    self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr,
                                            final_x, final_y, 0xFFFFFF,
                                            final_text)

                    # Monedas y movimientos
                    stats = (
                            f"Coins: {self.coins_collected} "
                            f"Moves: {self.moves_count}")
                    stats_w = len(stats) * char_w
                    stats_x = max(10, (self.win_w - stats_w) // 2)
                    stats_y = final_y + 20
                    self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr,
                                            stats_x, stats_y, 0xFFFFFF, stats)

            self.needs_update = False
            return 0

        # Mantener animación activa
        if self.show_solution and self.anim_start_time is not None:
            self.needs_update = True
        else:
            self.needs_update = False
        return 0

    def handle_keys(self, keycode, *args):
        # --- ESC (Cerrar) ---
        if keycode in [53, 65307, 0xFF1B]:
            os._exit(0)

        # Movimiento con WASD o flechas (siempre disponible)
        if keycode in [119, 87, 65362, 126]:
            # Arriba W / Up
            if not self.game_over:
                self._try_move_player(0, -1)
            return 0
        if keycode in [115, 83, 65364, 125]:
            # Abajo S / Down
            if not self.game_over:
                self._try_move_player(0, 1)
            return 0
        if keycode in [97, 65, 65361, 123]:
            # Izquierda A / Left
            if not self.game_over:
                self._try_move_player(-1, 0)
            return 0
        if keycode in [100, 68, 65363, 124]:
            # Derecha D / Right
            if not self.game_over:
                self._try_move_player(1, 0)
            return 0

        # --- P (Solución) ---
        if keycode in [112, 80]:
            self.show_solution = not self.show_solution
            if self.show_solution:
                print("Showing the solution")
                self.anim_start_time = time.time()   # empieza animación
                # garantizar que el animator no esté marcado como terminado
                if self.animator:
                    # animator no longer uses `finished`
                    pass
            else:
                print("Hiding the solution")
                self.anim_start_time = None  # la paramos / reseteamos
            self.needs_update = True

        # --- R (Regenerar Laberinto PERFECTO) ---
        elif keycode in [15, 114, 82, 40]:
            print("Regenerating the maze")

            import random
            from maze_generator import MazeGenerator

            new_seed = random.randint(0, 999999)

            new_maze = MazeGenerator(
                width=self.width,
                height=self.height,
                entry=self.maze_obj.entry,
                exit_pt=self.maze_obj.exit_pt,
                output_file=self.maze_obj.output_file,
                perfect=True,
                seed=new_seed
            )

            algo = self.config.algorithm
            if algo == 'PRIM':
                new_maze.generate_prim()
            else:
                new_maze.generate()

            self.maze_obj = new_maze
            self.grid = new_maze.grid
            self.solution = self.maze_obj.solve()

            # Colocar nuevas monedas y resetear contadores
            place_coins(self)
            self.coins_collected = 0
            self.moves_count = 0

            # resetear estado de solución y animación
            self.show_solution = False
            self.anim_start_time = None

            # resetear jugador y estado del juego
            self.player_pos = self.maze_obj.entry
            self.game_over = False
            # resetear temporizador
            self.play_start_time = time.time()
            self.end_time = None
            self._last_timer_sec = None
            self._debug_player_calls = False
            if self.animator:
                self.animator.active = False
                pass

            self.needs_update = True

        # --- C (Cambiar Color) ---
        elif keycode in [8, 99, 67, 14]:
            print("Changing colors")
            self.change_wall_color()

        return 0

    def run(self):
        # Iniciar temporizador de juego justo antes del bucle
        self.play_start_time = time.time()
        self.end_time = None
        self._last_timer_sec = None
        self.mlx.mlx_key_hook(self.win_ptr, self.handle_keys, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.render, None)
        self.mlx.mlx_loop(self.mlx_ptr)

    def _can_move_from(self, x: int, y: int, direction_bit: int) -> bool:
        """Devuelve True si desde (x,y) se puede mover en la dirección
        indicada.

        direction_bit debe ser 1=N, 2=E, 4=S, 8=W (mismos bits que en grid).
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        # Si la pared correspondiente está puesta (bit == 1), NO se puede mover
        return not (self.grid[y][x] & direction_bit)

    def _try_move_player(self, dx: int, dy: int) -> None:
        """Intenta mover al jugador en dx,dy si no hay muro.
        Actualiza `player_pos`, marca `needs_update` y comprueba llegada
        a la salida.
        """
        px, py = self.player_pos
        # Determinar bit según dx,dy
        if dx == 0 and dy == -1:
            bit = 1
        elif dx == 1 and dy == 0:
            bit = 2
        elif dx == 0 and dy == 1:
            bit = 4
        elif dx == -1 and dy == 0:
            bit = 8
        else:
            return

        if self._can_move_from(px, py, bit):
            nx, ny = px + dx, py + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                self.player_pos = (nx, ny)
                self.needs_update = True
                # Contar movimiento válido
                self.moves_count += 1
                # Recoger moneda si existe en la nueva posición
                if collect_coin(self, (nx, ny)):
                    self.coins_collected += 1
                    self.needs_update = True
                # Si llegó a la salida, marcar terminado (game over)
                if (nx, ny) == self.maze_obj.exit_pt:
                    self.game_over = True
                    # registrar tiempo de finalización
                    self.end_time = time.time()
                    # enable debug flag so player draw helpers
                    #  log if still called
                    self._debug_player_calls = True
                    # detener animator si existiera
                    if self.animator:
                        self.animator.active = False
                    self.needs_update = True
