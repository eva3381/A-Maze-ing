import random
from typing import List, Tuple, Optional

class MazeGenerator:
    """
    Generador de laberintos que garantiza perfección (sin ciclos) y solución única.
    Utiliza un algoritmo de búsqueda en profundidad (DFS) con retroceso.
    """
    OPPOSITE_WALLS = {1: 4, 2: 8, 4: 1, 8: 2}

    def __init__(self, width: int, height: int, entry: Tuple[int, int], 
                 exit_pt: Tuple[int, int], output_file: str, perfect: bool = True, 
                 seed: Optional[int] = None):
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_pt = exit_pt
        self.output_file = output_file
        self.perfect = perfect  # Si es True, no habrá ciclos
        self.grid = [[15 for _ in range(width)] for _ in range(height)]
        self.pattern_cells = set()
        
        # Gestión de semilla
        self.seed = seed if seed is not None else random.randint(0, 1000000)
        random.seed(self.seed)

    def _setup_pattern_42(self) -> List[Tuple[int, int]]:
        """Calcula las celdas que forman el logo '42'."""
        cells = []
        # Definición relativa del número 4
        n_four = [
            (0,0), (0,1), (0,2), (1,2), (2,2), 
            (2,0), (2,1), (2,3), (2,4)
        ]
        # Definición relativa del número 2
        n_two = [
            (0,0), (1,0), (2,0), (2,1), (2,2), 
            (1,2), (0,2), (0,3), (0,4), (1,4), (2,4)
        ]
        
        # Centrar el logo
        start_x = (self.width - 8) // 2
        start_y = (self.height - 5) // 2
        
        for x, y in n_four:
            cells.append((start_x + x, start_y + y))
        for x, y in n_two:
            cells.append((start_x + x + 5, start_y + y))
            
        return cells

    def _get_unvisited_neighbors(self, x: int, y: int, visited: List[List[bool]]):
        results = []
        directions = [(0, -1, 1), (1, 0, 2), (0, 1, 4), (-1, 0, 8)]
        for dx, dy, bit in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height and not visited[ny][nx]:
                results.append((nx, ny, bit))
        return results

    def generate(self) -> None:
        """Genera un laberinto perfecto rodeando el logo '42'."""
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        # 1. Preparar el patrón '42' como zona prohibida
        pattern_coords = self._setup_pattern_42()
        for px, py in pattern_coords:
            if 0 <= px < self.width and 0 <= py < self.height:
                visited[py][px] = True
                self.grid[py][px] = 15 # Bloque sólido
                self.pattern_cells.add((px, py))

        # 2. Algoritmo DFS para garantizar un laberinto perfecto
        stack = [self.entry]
        visited[self.entry[1]][self.entry[0]] = True

        while stack:
            cx, cy = stack[-1]
            neighbors = self._get_unvisited_neighbors(cx, cy, visited)
            
            if neighbors:
                nx, ny, bit = random.choice(neighbors)
                # Romper muros entre celda actual y vecina
                self.grid[cy][cx] &= ~bit
                self.grid[ny][nx] &= ~self.OPPOSITE_WALLS[bit]
                
                visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()

        # 3. Asegurar que la entrada y salida sean accesibles
        self._force_entry_exit()

    def _force_entry_exit(self) -> None:
        """Asegura que las celdas de entrada y salida no tengan muros exteriores."""
        # Entrada (ej. arriba a la izquierda)
        # Si la entrada está en el borde superior, abrimos el norte
        ex, ey = self.entry
        if ey == 0: self.grid[ey][ex] &= ~1
        elif ey == self.height - 1: self.grid[ey][ex] &= ~4

        # Salida
        sx, sy = self.exit_pt
        if sy == 0: self.grid[sy][sx] &= ~1
        elif sy == self.height - 1: self.grid[sy][sx] &= ~4
        elif sx == 0: self.grid[sy][sx] &= ~8
        elif sx == self.width - 1: self.grid[sy][sx] &= ~2

    def solve(self) -> str:
        """Resuelve el laberinto usando BFS para encontrar el camino único."""
        from collections import deque
        queue = deque([(self.entry, "")])
        visited = {self.entry}
        
        # Direcciones: bit de muro, cambio x, cambio y, letra comando
        moves = [(1, 0, -1, 'N'), (2, 1, 0, 'E'), (4, 0, 1, 'S'), (8, -1, 0, 'W')]

        while queue:
            (cx, cy), path = queue.popleft()
            if (cx, cy) == self.exit_pt:
                return path

            for bit, dx, dy, char in moves:
                # Si no hay muro en esa dirección
                if not (self.grid[cy][cx] & bit):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append(((nx, ny), path + char))
        return ""

    def save(self) -> None:
        """Guarda el laberinto y su solución en el archivo de salida."""
        solution = self.solve()
        with open(self.output_file, 'w') as f:
            for row in self.grid:
                line = "".join(hex(cell)[2:].upper() for cell in row)
                f.write(line + "\n")
            f.write(f"\n{self.entry[0]},{self.entry[1]}\n")
            f.write(f"{self.exit_pt[0]},{self.exit_pt[1]}\n")
            f.write(f"{solution}\n")
