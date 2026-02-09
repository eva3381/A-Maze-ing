import sys
import random
from maze_generator import MazeGenerator
from draw import DrawMaze

def load_config(file_path: str):
    """
    Lee el archivo config.txt y lo mete en un diccionario.
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
        # 2. Extraer datos (Validación estricta)
        if 'WIDTH' not in cfg or 'HEIGHT' not in cfg:
            print("Error: WIDTH and HEIGHT are mandatory in config.", file=sys.stderr)
            sys.exit(1)

        w, h = int(cfg['WIDTH']), int(cfg['HEIGHT'])
        
        # Procesar coordenadas de entrada y salida
        e_str = cfg.get('ENTRY', '0,0').split(',')
        e_coord = (int(e_str[0]), int(e_str[1]))

        s_str = cfg.get('EXIT', f'{w-1},{h-1}').split(',')
        s_coord = (int(s_str[0]), int(s_str[1]))
        
        out_file = cfg.get('OUTPUT_FILE', 'maze.txt')
        is_perfect = cfg.get('PERFECT', 'True').lower() == 'true'
        
        seed_raw = cfg.get('SEED')
        seed_val = int(seed_raw) if seed_raw else None

        # 3. Inicializar tu MazeGenerator
        maze = MazeGenerator(w, h, e_coord, s_coord, out_file, is_perfect, seed_val)

        # 4. BONUS: Selección de algoritmo
        algo = cfg.get('ALGORITHM', 'DFS').upper()
        print(f"Algorithm selected: {algo}")
        
        if algo == 'PRIM':
            maze.generate_prim() 
        else:
            maze.generate()

        # 5. Resolver y Guardar
        solution_path = maze.solve()
            
        maze.save()
        print(f"Success: Maze saved to {out_file}")

        # 6. BONUS: Parte Gráfica (MLX)
        # CORRECCIÓN: Se añade 'maze' como sexto argumento para permitir regenerar/resolver
        vis = DrawMaze(w, h, maze.grid, cfg, solution_path, maze)
        
        # Ejecutar el dibujo y el bucle de eventos de la MLX
        vis.draw_all_tiles()
        if hasattr(vis, 'mlx'):
            vis.mlx.mlx_loop(vis.ptr)

    except Exception as error:
        print(f"Error during execution: {error}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
