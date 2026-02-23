import random
import sys
from typing import List, Tuple, Optional
from collections import deque

class MazeGenerator:
    """
    Generador de laberintos con soporte para logo '42' central.
    Si perfect=False, rompe muros adicionales para crear múltiples soluciones.
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
        
        # Gestión de semilla y RNG
        self.seed = seed if seed is not None else random.randint(0, 1000000)
        self._rng = random.Random(self.seed)

        # Usamos pattern_cells para compatibilidad con draw.py
        self.pattern_cells = self._setup_logo_42()

    def _setup_logo_42(self) -> set:
        """Dibuja el logo '42' centrado matemáticamente."""
        cells = set()
        logo_w, logo_h = 7, 5
        off_x = (self.width - logo_w) // 2
        off_y = (self.height - logo_h) // 2
        
        pattern = [
            (0,0), (0,1), (0,2), (1,2), (2,0), (2,1), (2,2), (2,3), (2,4), # 4
            (4,0), (5,0), (6,0), (6,1), (6,2), (5,2), (4,2), (4,3), (4,4), (5,4), (6,4) # 2
        ]
        
        for dx, dy in pattern:
            nx, ny = off_x + dx, off_y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                cells.add((nx, ny))
                self.grid[ny][nx] = 0
        
        # Conectar las celdas internas del logo
        for cx, cy in cells:
            for b, dx, dy in [(2,1,0), (4,0,1)]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) in cells:
                    self.grid[cy][cx] &= ~b
                    self.grid[ny][nx] &= ~self.OPPOSITE_WALLS[b]
        return cells

    def generate(self) -> None:
        """Genera el laberinto usando DFS."""
        stack = [self.entry]
        visited = {self.entry} | self.pattern_cells

        while stack:
            cx, cy = stack[-1]
            neighbors = []
            for b, dx, dy in [(1,0,-1), (2,1,0), (4,0,1), (8,-1,0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) not in visited:
                    neighbors.append((b, nx, ny))

            if neighbors:
                b, nx, ny = self._rng.choice(neighbors)
                self.grid[cy][cx] &= ~b
                self.grid[ny][nx] &= ~self.OPPOSITE_WALLS[b]
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

        # Si PERFECT es False, creamos las soluciones múltiples
        if not self.perfect:
            self.add_paths()

    def add_paths(self) -> None:
        """Rompe muros adicionales para crear ciclos y múltiples rutas."""
        # Aumentamos la cantidad de muros a romper para que se note el efecto
        muros_a_romper = (self.width * self.height) // 10 

        for _ in range(muros_a_romper):
            # Elegimos celdas evitando los bordes exteriores
            x = self._rng.randint(1, self.width - 2)
            y = self._rng.randint(1, self.height - 2)
            
            # Intentamos romper un muro aleatorio (N, E, S, o W)
            muro = self._rng.choice([1, 2, 4, 8])
            dx, dy = {1:(0,-1), 2:(1,0), 4:(0,1), 8:(-1,0)}[muro]
            
            nx, ny = x + dx, y + dy
            
            # Reglas: No romper muros del logo y mantenerse en límites
            if (x, y) not in self.pattern_cells and (nx, ny) not in self.pattern_cells:
                if self.grid[y][x] & muro: # Si hay un muro
                    self.grid[y][x] &= ~muro
                    self.grid[ny][nx] &= ~self.OPPOSITE_WALLS[muro]

    def solve(self) -> str:
        """BFS para encontrar siempre el camino MÁS CORTO (ideal para laberintos con ciclos)."""
        queue = deque([(self.entry, "")])
        visited = {self.entry}
        moves = [(1, 0, -1, 'N'), (2, 1, 0, 'E'), (4, 0, 1, 'S'), (8, -1, 0, 'W')]

        while queue:
            (cx, cy), path = queue.popleft()
            if (cx, cy) == self.exit_pt:
                return path

            for bit, dx, dy, char in moves:
                if not (self.grid[cy][cx] & bit):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append(((nx, ny), path + char))
        return ""

    def save(self) -> None:
        """Guarda el laberinto y la solución."""
        solution = self.solve()
        with open(self.output_file, 'w') as f:
            for row in self.grid:
                line = "".join(hex(cell)[2:].upper() for cell in row)
                f.write(line + "\n")
            f.write(f"\n{self.entry[0]},{self.entry[1]}\n")
            f.write(f"{self.exit_pt[0]},{self.exit_pt[1]}\n")
            f.write(f"{solution}\n")
