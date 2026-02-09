import sys
import random
from maze_generator import MazeGenerator
from draw import DrawMaze

def load_config(file_path: str):
    """
    Lee el archivo config.txt y lo mete en un diccionario.
    Sustituye a la clase MazeConfig si no quieres usar el archivo externo.
    """
    config = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip().upper()] = value.strip()
    except FileNotFoundError:
        print(f"Error: {file_path} not found.", file=sys.stderr)
        sys.exit(1)
    return config

def main():
    # 1. Cargar configuración
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.txt'
    cfg = load_config(config_file)

    try:
        # 2. Extraer datos (con valores por defecto)
        w = int(cfg.get('WIDTH', 20))
        h = int(cfg.get('HEIGHT', 15))
        e = tuple(map(int, cfg.get('ENTRY', '0,0').split(',')))
        s = tuple(map(int, cfg.get('EXIT', f'{h-1},{w-1}').split(',')))
        out = cfg.get('OUTPUT_FILE', 'maze.txt')
        perf = cfg.get('PERFECT', 'True') == 'True'
        seed = int(cfg['SEED']) if 'SEED' in cfg else random.randint(0, 999)

        # 3. Inicializar tu MazeGenerator
        maze = MazeGenerator(h, w, e, s, out, perf, seed)

        # 4. BONUS: Selección de algoritmo
        algo = cfg.get('ALGORITHM', 'DFS').upper()
        print(f"Algorithm selected: {algo}")
        
        if algo == 'PRIM':
            maze.generate_prim() # Asegúrate de tener este método en mazegen.py
        else:
            maze.get_maze()      # Tu DFS original

        # 5. Resolver y Guardar
        maze.solve_maze()
        if not maze.perfect:
            maze.open_maze()
        maze.write_maze()
        print(f"Maze saved to {out}")

        # 6. BONUS: Parte Gráfica
        # Ajustamos los parámetros según lo que espera tu clase DrawMaze en draw.py
        vis = DrawMaze(w, h, maze.cells, cfg, maze.solution)
        vis.draw_all_tiles()
        vis.mlx.mlx_loop(vis.ptr)

    except Exception as error:
        print(f"Error during execution: {error}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()