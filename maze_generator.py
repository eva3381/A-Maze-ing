import random
from typing import Tuple, Optional
from collections import deque

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

        if seed is not None:
            self.seed = seed
        else:
            self.seed = random.randint(0, 1000000)
        self._rng = random.Random(self.seed)

        if width > 15 and height > 15: # Ajustado para asegurar espacio
            self.pattern_cells = self._setup_logo_42()
        else:
            self.pattern_cells = set()

    def _setup_logo_42(self) -> set:
        """Dibuja el logo '42' y asegura que las paredes vecinas sean consistentes."""
        cells = set()
        logo_w, logo_h = 7, 5
        pattern = [
            # "4"
            (0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
            # "2"
            (4, 0), (5, 0), (6, 0), (6, 1), (6, 2), (5, 2), (4, 2), (4, 3), (4, 4), (5, 4), (6, 4)
        ]

        off_x = (self.width - logo_w) // 2
        off_y = (self.height - logo_h) // 2
        
        actual_cells = set()
        for dx, dy in pattern:
            nx, ny = off_x + dx, off_y + dy
            actual_cells.add((nx, ny))
            self.grid[ny][nx] = 15 # Inicializar como bloque sólido antes de tallar

        # Tallar el logo y conectar con vecinos para mantener consistencia
        for cx, cy in actual_cells:
            for b, dx, dy in [(1, 0, -1), (2, 1, 0), (4, 0, 1), (8, -1, 0)]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) in actual_cells:
                    # Si el vecino es parte del logo, abrimos camino entre ambos
                    self.grid[cy][cx] &= ~b
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        self.grid[ny][nx] &= ~self.OPPOSITE_WALLS[b]
        
        return actual_cells

    def generate(self) -> None:
        """Genera el laberinto usando DFS."""
        stack = [self.entry]
        visited = {self.entry} | self.pattern_cells

        while stack:
            cx, cy = stack[-1]
            neighbors = []
            for b, dx, dy in [(1, 0, -1), (2, 1, 0), (4, 0, 1), (8, -1, 0)]:
                nx, ny = cx + dx, cy + dy
                if (0 <= nx < self.width and 0 <= ny < self.height and
                        (nx, ny) not in visited):
                    neighbors.append((b, nx, ny))

            if neighbors:
                b, nx, ny = self._rng.choice(neighbors)
                self.grid[cy][cx] &= ~b
                self.grid[ny][nx] &= ~self.OPPOSITE_WALLS[b]
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()
        
        # Conectar el logo al resto del laberinto (al menos un punto)
        if self.pattern_cells:
            lc_x, lc_y = list(self.pattern_cells)[0]
            # Abrir una salida del logo hacia el laberinto
            for b, dx, dy in [(1,0,-1), (2,1,0), (4,0,1), (8,-1,0)]:
                nx, ny = lc_x + dx, lc_y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) not in self.pattern_cells:
                    self.grid[lc_y][lc_x] &= ~b
                    self.grid[ny][nx] &= ~self.OPPOSITE_WALLS[b]
                    break

        if not self.perfect:
            self.add_paths()

    def regenerate(self):
        """Reinicia el estado del generador con una nueva semilla aleatoria."""
        self.seed = random.randint(0, 1000000)
        self._rng = random.Random(self.seed)
        # Limpiar el grid a su estado inicial (todas las paredes levantadas)
        self.grid = [[15 for _ in range(self.width)] for _ in range(self.height)]
        # Re-inicializar el logo si corresponde
        if self.width > 15 and self.height > 15:
            self.pattern_cells = self._setup_logo_42()
        else:
            self.pattern_cells = set()

    def add_paths(self) -> None:
        muros_a_romper = (self.width * self.height) // 10
        for _ in range(muros_a_romper):
            x = self._rng.randint(1, self.width - 2)
            y = self._rng.randint(1, self.height - 2)
            muro = self._rng.choice([1, 2, 4, 8])
            dx, dy = {1: (0, -1), 2: (1, 0), 4: (0, 1), 8: (-1, 0)}[muro]
            nx, ny = x + dx, y + dy
            if self.grid[y][x] & muro:
                self.grid[y][x] &= ~muro
                self.grid[ny][nx] &= ~self.OPPOSITE_WALLS[muro]

    def solve(self) -> str:
        queue = deque([(self.entry, "")])
        visited = {self.entry}
        moves = [(1, 0, -1, 'N'), (2, 1, 0, 'E'), (4, 0, 1, 'S'), (8, -1, 0, 'W')]
        while queue:
            (cx, cy), path = queue.popleft()
            if (cx, cy) == self.exit_pt: return path
            for bit, dx, dy, char in moves:
                if not (self.grid[cy][cx] & bit):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append(((nx, ny), path + char))
        return ""

    def save(self) -> None:
        solution = self.solve()
        with open(self.output_file, 'w') as f:
            for row in self.grid:
                f.write("".join(hex(cell)[2:].upper() for cell in row) + "\n")
            f.write("\n")
            f.write(f"{self.entry[0]},{self.entry[1]}\n")
            f.write(f"{self.exit_pt[0]},{self.exit_pt[1]}\n")
            f.write(f"{solution}\n")
            