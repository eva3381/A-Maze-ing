import sys
from typing import Dict, Tuple, Set

class ConfigError(Exception):
    """Excepción personalizada para errores de configuración."""
    pass

class MazeConfig:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.width: int = 0
        self.height: int = 0
        self.seed: int = 0
        self.output_file: str = ""
        self.entry: Tuple[int, int] = (0, 0)
        self.exit: Tuple[int, int] = (0, 0)
        self.is_perfect: bool = False
        self.algorithm: str = "DFS"

        raw_data = self._read_file()
        self._process_and_validate(raw_data)

    def _read_file(self) -> Dict[str, str]:
        config: Dict[str, str] = {}
        try:
            with open(self.file_name, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith("#"): continue
                    if "=" not in line: continue
                    key, value = line.split("=", 1)
                    config[key.strip().upper()] = value.strip()
            return config
        except FileNotFoundError:
            raise ConfigError(f"The file could not be found: {self.file_name}")

    def _process_and_validate(self, config: Dict[str, str]) -> None:
        try:
            self.width = int(config.get("WIDTH", 0))
            self.height = int(config.get("HEIGHT", 0))
            self.is_perfect = (config.get("PERFECT", "True") == "True")
            self.output_file = config.get("OUTPUT_FILE", "maze.txt")
            self.seed = int(config.get("SEED", 0))
            self.algorithm = config.get("ALGORITHM", "DFS")
            
            self.entry = self._parse_coords(config.get("ENTRY", "0,0"))
            self.exit = self._parse_coords(config.get("EXIT", "0,0"))
        except ValueError:
            raise ConfigError("One of the numeric values ​​in config.txt is invalid.")

        # VALIDACIÓN DE RANGOS
        self._validate_boundaries()

    def _parse_coords(self, text: str) -> Tuple[int, int]:
        try:
            parts = text.split(",")
            return (int(parts[0].strip()), int(parts[1].strip()))
        except:
            raise ConfigError("Invalid coordinate format. Must be 'x,y'.")

    def _validate_boundaries(self) -> None:
        """Verifica que ENTRY y EXIT estén dentro del laberinto."""
        # Validar Entrada
        if not (0 <= self.entry[0] < self.width) or not (0 <= self.entry[1] < self.height):
            raise ConfigError(
                f"The ENTRY ({self.entry[0]},{self.entry[1]}) It's out of bounds.\n"
                f"For a labyrinth of {self.width}x{self.height}, the allowed range is from 0.0 to {self.width-1},{self.height-1}.\n"
                f"Please adjust the parameters in config.txt."
            )
        
        # Validar Salida
        if not (0 <= self.exit[0] < self.width) or not (0 <= self.exit[1] < self.height):
            raise ConfigError(
                f"The EXIT ({self.exit[0]},{self.exit[1]}) It's out of bounds.\n"
                f"For a labyrinth of {self.width}x{self.height}, the allowed range is from 0.0 to {self.width-1},{self.height-1}.\n"
                f"Please adjust the parameters in config.txt."
            )
