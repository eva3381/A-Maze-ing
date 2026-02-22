import time
from typing import List, Tuple, Optional


class Animator:
    """Anima un pequeño cuadrado que recorre una secuencia de celdas.

    Uso:
      animator = Animator()
      animator.start(path_cells, duration=5.0)
      dentro del bucle de render llamar animator.draw(draw_maze)
    """

    def __init__(self):
        self.path: List[Tuple[int, int]] = []
        self.start_time: Optional[float] = None
        self.duration: float = 5.0
        self.active: bool = False
        # `finished` flag removed: animator no longer signals game end
        self.color = 0xFFFF00

    def start(
            self, cell_path: List[Tuple[int, int]],
            duration: float = 5.0) -> None:
        """Inicia la animación con la lista de celdas (coordenadas x,y).

        `cell_path` debe ser una lista de coordenadas de celdas (x,y), por
        ejemplo generada a partir de la solución del laberinto.
        """
        if not cell_path:
            return
        self.path = list(cell_path)
        self.duration = max(0.001, float(duration))
        self.start_time = time.time()
        self.active = True

    def stop(self) -> None:
        self.active = False
        self.start_time = None
        # nothing else to reset

    def _current_index(self) -> int:
        if not self.active or self.start_time is None or not self.path:
            return 0
        elapsed = time.time() - self.start_time
        t = min(1.0, elapsed / self.duration)
        idx = int(t * (len(self.path) - 1))
        return idx

    def draw(self, draw_maze) -> None:
        """Dibuja el cuadrado en la posición actual sobre el objeto
        `draw_maze`.

        Espera que `draw_maze` tenga métodos `_fill_tile(x,y,color)` y
        atributos `tile_size` y `maze_obj` para extraer coordenadas si es
        necesario.
        """
        if not self.active:
            return

        idx = self._current_index()
        x, y = self.path[idx]

        # El animator NO dibuja un cuadrito que compita con el jugador. Su
        # responsabilidad es controlar el progreso temporal de la animación
        # (por ejemplo para dibujar la traza de la solución en otro sitio).
        # Aquí simplemente actualizamos `active` cuando termina.
        if idx >= len(self.path) - 1:
            self.active = False
