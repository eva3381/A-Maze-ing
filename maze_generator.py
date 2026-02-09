import random
from typing import List, Tuple, Optional

class MazeGenerator:
    """
    Core logic for maze generation.
    This class is reusable and independent of the configuration source.
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
        self.perfect = perfect
        self.grid = [[15 for _ in range(width)] for _ in range(height)]
        
        # Seed management
        self.seed = seed if seed is not None else random.randint(0, 1000000)
        random.seed(self.seed)

    def _get_unvisited_neighbors(self, x: int, y: int, visited: List[List[bool]]):
        results = []
        directions = [(0, -1, 1), (1, 0, 2), (0, 1, 4), (-1, 0, 8)]
        for dx, dy, bit in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height and not visited[ny][nx]:
                results.append((nx, ny, bit))
        return results

    def generate(self) -> None:
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        stack = [self.entry]
        visited[self.entry[1]][self.entry[0]] = True

        while stack:
            cx, cy = stack[-1]
            neighbors = self._get_unvisited_neighbors(cx, cy, visited)
            if neighbors:
                nx, ny, b_curr = random.choice(neighbors)
                b_next = self.OPPOSITE_WALLS[b_curr]
                self.grid[cy][cx] &= ~b_curr
                self.grid[ny][nx] &= ~b_next
                visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()
        
        self._add_pattern_42()
        self._force_entry_exit()

    def _add_pattern_42(self) -> None:
        pattern = [
            [0, 1, 0, 1, 0, 0, 0, 0],
            [0, 1, 0, 1, 1, 1, 1, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [1, 1, 0, 1, 0, 1, 1, 1],
            [1, 1, 0, 1, 0, 0, 0, 0],
        ]
        ph, pw = 5, 8
        if self.width < pw or self.height < ph:
            print("Error: Maze too small for '42' pattern.")
            return
            
        sx, sy = (self.width - pw) // 2, (self.height - ph) // 2
        for y in range(ph):
            for x in range(pw):
                if pattern[y][x] == 0:
                    cx, cy = sx + x, sy + y
                    self.grid[cy][cx] = 0
                    if cy > 0: self.grid[cy-1][cx] &= ~4
                    if cy < self.height-1: self.grid[cy+1][cx] &= ~1
                    if cx < self.width-1: self.grid[cy][cx+1] &= ~8
                    if cx > 0: self.grid[cy][cx-1] &= ~2

    def _force_entry_exit(self) -> None:
        for (x, y) in [self.entry, self.exit_pt]:
            if y == 0: self.grid[y][x] &= ~1
            if y == self.height - 1: self.grid[y][x] &= ~4
            if x == 0: self.grid[y][x] &= ~8
            if x == self.width - 1: self.grid[y][x] &= ~2

    def solve(self) -> str:
        queue = [(self.entry, "")]
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        visited[self.entry[1]][self.entry[0]] = True
        idx = 0
        while idx < len(queue):
            (cx, cy), path = queue[idx]
            idx += 1
            if (cx, cy) == self.exit_pt: return path
            for dx, dy, bit, char in [(0,-1,1,"N"), (1,0,2,"E"), (0,1,4,"S"), (-1,0,8,"W")]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not (self.grid[cy][cx] & bit) and not visited[ny][nx]:
                        visited[ny][nx] = True
                        queue.append(((nx, ny), path + char))
        return ""

    def generate_prim(self) -> None:
        """
        Bonus: Generates a maze using Prim's Algorithm.
        Uses the same bitmask logic (1, 2, 4, 8) as your DFS.
        """
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        # Empezamos por la entrada
        start_x, start_y = self.entry
        visited[start_y][start_x] = True
        
        # Lista de paredes candidatas: (x1, y1, x2, y2, bit)
        # x1,y1 es la celda visitada; x2,y2 es la vecina no visitada
        walls = []
        
        def add_neighbor_walls(x: int, y: int):
            for dx, dy, bit in [(0, -1, 1), (1, 0, 2), (0, 1, 4), (-1, 0, 8)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and not visited[ny][nx]:
                    walls.append((x, y, nx, ny, bit))

        add_neighbor_walls(start_x, start_y)

        while walls:
            # Seleccionar una pared al azar (característica de Prim)
            idx = random.randint(0, len(walls) - 1)
            x1, y1, x2, y2, bit = walls.pop(idx)

            if not visited[y2][x2]:
                visited[y2][x2] = True
                # Romper paredes en ambas celdas usando tus constantes
                self.grid[y1][x1] &= ~bit
                self.grid[y2][x2] &= ~self.OPPOSITE_WALLS[bit]
                
                # Añadir las nuevas paredes de la celda recién visitada
                add_neighbor_walls(x2, y2)
        
        # Aplicar tus funciones finales
        self._add_pattern_42()
        self._force_entry_exit()

    def save(self) -> None:
        path = self.solve()
        with open(self.output_file, 'w') as f:
            for row in self.grid:
                f.write("".join(f"{cell:X}" for cell in row) + "\n")
            f.write(f"\n({self.entry[0]},{self.entry[1]})\n")
            f.write(f"({self.exit_pt[0]},{self.exit_pt[1]})\n")
            f.write(path + "\n")