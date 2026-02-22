import sys
import os
from maze_generator import MazeGenerator
from draw import DrawMaze


def load_config(file_path: str):
    config = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip().upper()] = value.strip()
    except FileNotFoundError:
        print(f"Error: {file_path} no encontrado.", file=sys.stderr)
        sys.exit(1)
    return config


def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.txt'
    cfg = load_config(config_file)

    try:
        # Extraer dimensiones
        w, h = int(cfg['WIDTH']), int(cfg['HEIGHT'])
        e_str = cfg.get('ENTRY', '0,0').split(',')
        e_coord = (int(e_str[0]), int(e_str[1]))
        s_str = cfg.get('EXIT', f'{w-1},{h-1}').split(',')
        s_coord = (int(s_str[0]), int(s_str[1]))
        out_file = cfg.get('OUTPUT_FILE', 'maze.txt')

        # Generación inicial
        # Parsear flag PERFECT (acepta '1', 'true', 'yes', 'y')
        perfect_val = cfg.get('PERFECT', 'False').strip().lower()
        perfect = perfect_val in ('1', 'true', 'yes', 'y')

        # Parsear SEED si existe
        seed_val = cfg.get('SEED')
        seed = None
        if seed_val is not None and seed_val != '':
            try:
                seed = int(seed_val)
            except ValueError:
                print(f"Advertencia: SEED inválida"
                      f"('{seed_val}'), se ignorará.")

        maze = MazeGenerator(
            w, h, e_coord, s_coord, out_file, perfect=perfect, seed=seed
            )

        algo = cfg.get('ALGORITHM', 'DFS').upper()
        if algo == 'PRIM' and hasattr(maze, 'generate_prim'):
            maze.generate_prim()
        else:
            maze.generate()

        solution_path = maze.solve()
        maze.save()
        print(f"Éxito: Laberinto inicial guardado en {out_file}")
        vis = DrawMaze(w, h, maze.grid, cfg, solution_path, maze)

        vis.run()

    except Exception as e:
        print(f"Error inesperado: {e}")
        os._exit(1)


if __name__ == "__main__":
    main()
