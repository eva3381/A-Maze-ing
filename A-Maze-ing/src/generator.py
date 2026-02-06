import random
import sys
from typing import List, Tuple, Optional

class MazeGenerator:
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
        if seed is not None:
            random.seed(seed)

    def _get_opposite_wall(self, wall: int) -> int:
        opposite_walls = {1: 4, 2: 8, 4: 1, 8: 2}
        return opposite_walls.get(wall, 0)

    def _get_unvisited_neighbors(self, x: int, y: int, visited: List[List[bool]]):
        results = []
        directions = [(0, -1, 1), (1, 0, 2), (0, 1, 4), (-1, 0, 8)]
        for dx, dy, bit in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height and not visited[ny][nx]:
                results.append((nx, ny, bit))
        return results

    def generate(self):
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        stack = [self.entry]
        visited[self.entry[1]][self.entry[0]] = True

        while stack:
            cx, cy = stack[-1]
            neighbors = self._get_unvisited_neighbors(cx, cy, visited)
            if neighbors:
                nx, ny, b_curr = random.choice(neighbors)
                b_next = self._get_opposite_wall(b_curr)
                self.grid[cy][cx] &= ~b_curr
                self.grid[ny][nx] &= ~b_next
                visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()
        self._add_pattern_42()
        self._force_entry_exit()

    def _add_pattern_42(self):
        pattern = [
            [0, 1, 0, 1, 0, 0, 0, 0],
            [0, 1, 0, 1, 1, 1, 1, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [1, 1, 0, 1, 0, 1, 1, 1],
            [1, 1, 0, 1, 0, 0, 0, 0],
        ]
        ph, pw = 5, 8
        if self.width < pw or self.height < ph: return
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

    def _force_entry_exit(self):
        for (x, y) in [self.entry, self.exit_pt]:
            if y == 0: self.grid[y][x] &= ~1
            if y == self.height - 1: self.grid[y][x] &= ~4
            if x == 0: self.grid[y][x] &= ~8
            if x == self.width - 1: self.grid[y][x] &= ~2

    def find_shortest_path(self) -> str:
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

    def save(self):
        path = self.find_shortest_path()
        with open(self.output_file, 'w') as f:
            for row in self.grid:
                f.write("".join(f"{cell:X}" for cell in row) + "\n")
            f.write(f"\n({self.entry[0]},{self.entry[1]})\n")
            f.write(f"({self.exit_pt[0]},{self.exit_pt[1]})\n")
            f.write(path + "\n")

if __name__ == "__main__":
    # 1. Separar argumentos con '=' de los argumentos numericos directos
    named_args = {}
    positional_args = []
    
    for a in sys.argv[1:]:
        if '=' in a:
            k, v = a.split('=')
            named_args[k.upper()] = v
        else:
            positional_args.append(a)

    try:
        # 2. Obtener WIDTH: Primero de WIDTH=X, luego del primer numero directo, luego por defecto
        if 'WIDTH' in named_args:
            w = int(named_args['WIDTH'])
        elif len(positional_args) >= 1:
            w = int(positional_args[0])
        else:
            w = 20

        # 3. Obtener HEIGHT: Primero de HEIGHT=Y, luego del segundo numero directo, luego por defecto
        if 'HEIGHT' in named_args:
            h = int(named_args['HEIGHT'])
        elif len(positional_args) >= 2:
            h = int(positional_args[1])
        else:
            h = 15
        
        # 4. Procesar ENTRY y EXIT (ahora que tenemos el w y h reales)
        e_str = named_args.get('ENTRY')
        e_coord = tuple(map(int, e_str.split(','))) if e_str else (0, 0)

        s_str = named_args.get('EXIT')
        s_coord = tuple(map(int, s_str.split(','))) if s_str else (w - 1, h - 1)
        
        out = named_args.get('OUTPUT_FILE', 'maze.txt')
        perf = named_args.get('PERFECT', 'True') == 'True'

        gen = MazeGenerator(w, h, e_coord, s_coord, out, perf)
        gen.generate()
        gen.save()
        
        print(f"Laberinto {out} generado con dimensiones {w}x{h}")
        print(f"Entrada: {e_coord}")
        print(f"Salida: {s_coord}")
        
    except Exception as ex:
        print(f"Error al procesar parametros: {ex}")