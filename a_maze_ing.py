import sys
from parser import MazeConfig, ConfigError
from maze_generator import MazeGenerator
from draw import DrawMaze

def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.txt'

    try:
        # Cargar configuración
        cfg = MazeConfig(config_file)

        # Generar laberinto
        maze = MazeGenerator(
            width=cfg.width,
            height=cfg.height,
            entry=cfg.entry,
            exit_pt=cfg.exit,
            output_file=cfg.output_file,
            perfect=cfg.is_perfect,
            seed=cfg.seed
        )

        maze.generate()
        solution_path = maze.solve()
        maze.save()

        # Iniciar visualización
        visualizer = DrawMaze(cfg.width, cfg.height, maze.grid, cfg, solution_path, maze)
        visualizer.run()

    except ConfigError as e:
        # Mensaje limpio sin Traceback
        print("\n" + "!"*50)
        print(f"WARNING: {e}")
        print("!"*50 + "\n")
        sys.exit(0) # Cerramos el programa normalmente

    except Exception as e:
        # Para cualquier otro error no esperado, sí mostramos algo de info
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()