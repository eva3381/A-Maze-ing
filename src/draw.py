from mlx import Mlx 
import sys

class DrawMaze:
    def __init__(self, width, height, cells, config, solution):
        self.mlx = Mlx()
        self.ptr = self.mlx.mlx_init()
        # Creamos ventana (50 píxeles por celda por ejemplo)
        self.win = self.mlx.mlx_new_window(self.ptr, width * 50, height * 50, "A-Maze-ing Bonus")
        self.cells = cells
        
    def draw_all_tiles(self):
        """
        Aquí recorres self.cells y usas mlx_pixel_put o mlx_put_image_to_window
        para dibujar las paredes según los bits (1, 2, 4, 8).
        """
        pass

    def handle_keys(self, keycode):
        # ESC para cerrar (53 en Mac, 65307 en Linux)
        if keycode == 53: 
            sys.exit(0)
