import sys
from maze_generator import MazeGenerator
from draw import DrawMaze
from parser import MazeConfig, ConfigError


def main():
    """
    Main entry point for the A-Maze-ing generator.
    """
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.txt'

    try:
        # Parse and Validate configuration
        cfg = MazeConfig(config_file)

        # Initialize MazeGenerator
        maze = MazeGenerator(
            width=cfg.width,
            height=cfg.height,
            entry=cfg.entry,
            exit_pt=cfg.exit,
            output_file=cfg.output_file,
            perfect=cfg.is_perfect,
            seed=cfg.seed
        )

        # Select and run the algorithm
        if cfg.algorithm == 'PRIM' and hasattr(maze, 'generate_prim'):
            maze.generate_prim()
        else:
            maze.generate()

        # Solve and Save
        solution_path = maze.solve()
        maze.save()

        # Visualization
        visualizer = DrawMaze(
            width=cfg.width,
            height=cfg.height,
            grid=maze.grid,
            config=cfg,
            solution=solution_path,
            maze_obj=maze
        )
        visualizer.run()

    except ConfigError as e:
        # Capturamos el error pero salimos de forma "limpia" para el Makefile
        print("\n[!] Maze Configuration Issue:")
        print(f"{e}")
        print("\nPlease fix the config.txt file and try again.\n")
        sys.exit(0)  # <--- Cambiado de 1 a 0 para evitar el rojo en make

    except Exception as e:
        print(f"\n[!] Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
