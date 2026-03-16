import random
from typing import Tuple, Optional
from collections import deque
import sys


class MazeGenerator:
    """
    Generador de laberintos con soporte para logo '42' central.
    """
    OPPOSITE_WALLS = {1: 4, 2: 8, 4: 1, 8: 2}

    def __init__(self, width: int, height: int, entry: Tuple[int, int],
                 exit_pt: Tuple[int, int], output_file: str,
                 perfect: bool = True, seed: Optional[int] = None):
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_pt = exit_pt
        self.output_file = output_file
        self.perfect = perfect
        self.grid = [[15 for _ in range(width)] for _ in range(height)]
        self.generation_failed = False

        if seed is not None:
            self.seed = seed
        else:
            self.seed = random.randint(0, 1000000)
        self._rng = random.Random(self.seed)

        if width > 10 and height > 10:  # Ajustado para asegurar espacio
            self.pattern_cells = self._setup_logo_42()
        else:
            self.pattern_cells = set()

    def _setup_logo_42(self) -> set:
        """Dibuja el logo '42' marcando las celdas como muros íntegros.
        NO se abren paredes entre las celdas del logo: el logo debe permanecer
        como bloque sólido y no participar en el tallado del laberinto.
        """
        logo_w, logo_h = 7, 5
        pattern = [
            # "4"
            (0, 0), (0, 1), (0, 2), (1, 2), (2, 0),
            (2, 1), (2, 2), (2, 3), (2, 4),
            # "2"
            (4, 0), (5, 0), (6, 0), (6, 1), (6, 2), (5, 2),
            (4, 2), (4, 3), (4, 4), (5, 4), (6, 4)
        ]

        off_x = (self.width - logo_w) // 2
        off_y = (self.height - logo_h) // 2

        actual_cells = set()
        for dx, dy in pattern:
            nx, ny = off_x + dx, off_y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                actual_cells.add((nx, ny))
                # Mantenerlo como bloque sólido (todas las paredes)
                self.grid[ny][nx] = 15

        # No abrir puertas entre celdas del logo;
        # el logo se considera espacio no transitable por el generador.
        return actual_cells

    # ...existing code...
    def generate(self) -> bool:
        """Genera el laberinto usando DFS.

        Si la salida (exit_pt) se encuentra dentro del logo se aborta la
        generación, se informa por stderr y NO se modifica el grid existente.
        Retorna True si se generó correctamente, False en caso de error.
        """
        # Reset de flag
        self.generation_failed = False

        # Comprobación: la salida no puede estar dentro del logo
        if self.pattern_cells and (self.exit_pt in self.pattern_cells):

            print(f"Error: exit point {self.exit_pt}"
                  f"está dentro del logo '42'. No se genera el laberinto.",
                  file=sys.stderr)
            # Marcar fallo y no modificar self.grid para que el frontend/GUI
            # no tenga un laberinto "parcial" que mostrar.
            self.generation_failed = True
            return False
        # Comprobación: la entrada tampoco puede estar dentro del logo
        if self.pattern_cells and (self.entry in self.pattern_cells):
            print(f"Error: entry point {self.entry}"
                  f"está dentro del logo '42'. No se genera el laberinto.",
                  file=sys.stderr)
            self.generation_failed = True
            return False

        # --- Tallado del laberinto usando DFS iterativo ---
        # Empezamos por la entrada (ya comprobada que no esté en el logo).
        start = self.entry
        visited = {start}
        stack = [start]
        # Formato: (bit_wall, dx, dy)
        dirs = [(1, 0, -1), (2, 1, 0), (4, 0, 1), (8, -1, 0)]

        while stack:
            cx, cy = stack[-1]
            neighbors = []
            for bit, dx, dy in dirs:
                nx, ny = cx + dx, cy + dy
                if (0 <= nx < self.width and 0 <= ny < self.height
                        and (nx, ny) not in visited
                        and (nx, ny) not in self.pattern_cells):
                    neighbors.append((bit, nx, ny))
            if neighbors:
                bit, nx, ny = self._rng.choice(neighbors)
                # Romper muro entre (cx,cy) y (nx,ny)
                if self.grid[cy][cx] & bit:
                    self.grid[cy][cx] &= ~bit
                    self.grid[ny][nx] &= ~self.OPPOSITE_WALLS[bit]
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

        # Si no se quiere un laberinto "perfect", abrir caminos adicionales
        if not self.perfect:
            self.add_paths()

        return True

    def regenerate(self):
        """Reinicia el estado del generador con una nueva semilla aleatoria."""
        self.seed = random.randint(0, 1000000)
        self._rng = random.Random(self.seed)
        # Limpiar el grid a su estado inicial (todas las paredes levantadas)
        self.grid = [
            [15 for _ in range(self.width)] for _ in range(self.height)]
        self.generation_failed = False

        # Re-inicializar el logo si corresponde
        if self.width > 10 and self.height > 10:
            self.pattern_cells = self._setup_logo_42()
        else:
            self.pattern_cells = set()

    def add_paths(self) -> None:
        muros_a_romper = (self.width * self.height) // 10
        attempts = 0
        made = 0
        while made < muros_a_romper and attempts < muros_a_romper * 5:
            attempts += 1
            x = self._rng.randint(1, self.width - 2)
            y = self._rng.randint(1, self.height - 2)
            # Evitar cualquier celda del logo
            if (x, y) in self.pattern_cells:
                continue
            muro = self._rng.choice([1, 2, 4, 8])
            dx, dy = {1: (0, -1), 2: (1, 0), 4: (0, 1), 8: (-1, 0)}[muro]
            nx, ny = x + dx, y + dy
            # Evitar romper muro que afecte al logo o conecte con él
            if (nx, ny) in self.pattern_cells or (x, y) in self.pattern_cells:
                continue
            if (0 <= nx < self.width and 0 <= ny < self.height
               and (self.grid[y][x] & muro)):
                self.grid[y][x] &= ~muro
                self.grid[ny][nx] &= ~self.OPPOSITE_WALLS[muro]
                made += 1

    def solve(self) -> str:
        queue = deque([(self.entry, "")])
        visited = {self.entry}
        moves = [(1, 0, -1, 'N'), (2, 1, 0, 'E'),
                 (4, 0, 1, 'S'), (8, -1, 0, 'W')]
        while queue:
            (cx, cy), path = queue.popleft()
            if (cx, cy) == self.exit_pt:
                return path
            for bit, dx, dy, char in moves:
                if not (self.grid[cy][cx] & bit):
                    nx, ny = cx + dx, cy + dy
                    if (0 <= nx < self.width and 0 <= ny < self.height
                       and (nx, ny) not in visited):
                        visited.add((nx, ny))
                        queue.append(((nx, ny), path + char))
        return ""

    def save(self) -> None:
        # Evitar guardar si no se generó correctamente
        if getattr(self, "generation_failed", False):
            print(
                "Warning: generación fallida. No se guarda nada.",
                file=sys.stderr)
            return
        solution = self.solve()
        with open(self.output_file, 'w') as f:
            for row in self.grid:
                f.write("".join(hex(cell)[2:].upper() for cell in row) + "\n")
            f.write("\n")
            f.write(f"{self.entry[0]},{self.entry[1]}\n")
            f.write(f"{self.exit_pt[0]},{self.exit_pt[1]}\n")
            f.write(f"{solution}\n")
