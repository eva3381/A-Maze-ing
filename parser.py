import sys
from typing import Dict, Tuple, Set

class ConfigError(Exception):
    """Custom exception for maze configuration errors."""
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
        allowed_keys = {'WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE', 'PERFECT', 'SEED', 'ALGORITHM'}
        try:
            with open(self.file_name, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith("#"): continue
                    if "=" not in line: raise ConfigError(f"Invalid line format: '{line}'")
                    key, value = line.split("=", 1)
                    key_upper = key.strip().upper()
                    if key_upper not in allowed_keys: raise ConfigError(f"Unallowed parameter: '{key_upper}'")
                    config[key_upper] = value.strip()
        except FileNotFoundError:
            raise ConfigError(f"The file '{self.file_name}' does not exist.")
        return config

    def _get_42_cells(self) -> Set[Tuple[int, int]]:
        """Calcula las celdas ocupadas por el logo '42' en el centro."""
        cells = set()
        mid_x, mid_y = self.width // 2, self.height // 2
        # Offset para centrar el bloque de 3x5 que ocupa el '42'
        off_x, off_y = mid_x - 1, mid_y - 2
        
        # Coordenadas relativas del "4" y el "2"
        pattern = [
            (0,0), (0,1), (0,2), (1,2), (2,0), (2,1), (2,2), (2,3), (2,4), # El 4
            (4,0), (5,0), (6,0), (6,1), (6,2), (5,2), (4,2), (4,3), (4,4), (5,4), (6,4) # El 2
        ]
        for dx, dy in pattern:
            cells.add((off_x + dx, off_y + dy))
        return cells

    def _process_and_validate(self, config: Dict[str, str]) -> None:
        try:
            self.width = int(config["WIDTH"])
            self.height = int(config["HEIGHT"])
            self.is_perfect = config["PERFECT"] == "True"
            self.output_file = config["OUTPUT_FILE"]
            self.seed = int(config.get("SEED", 0))
            self.algorithm = config.get("ALGORITHM", "DFS").upper()
            self.entry = self._parse_coords(config["ENTRY"], "ENTRY")
            self.exit = self._parse_coords(config["EXIT"], "EXIT")
        except (ValueError, KeyError):
            raise ConfigError("Invalid or missing data in config (integers expected for dimensions/coords).")

        self._validate_logic()

    def _parse_coords(self, text: str, label: str) -> Tuple[int, int]:
        parts = text.split(",")
        if len(parts) != 2: raise ConfigError(f"{label} must be 'x,y'.")
        return (int(parts[0].strip()), int(parts[1].strip()))

    def _validate_logic(self) -> None:
        # 1. Límites básicos
        if self.width < 10 or self.height < 10:
            raise ConfigError("Maze is too small for a '42' pattern (min 10x10).")

        for label, (x, y) in [("ENTRY", self.entry), ("EXIT", self.exit)]:
            if not (0 <= x < self.width and 0 <= y < self.height):
                raise ConfigError(f"{label} {x,y} is out of bounds.")

        # 2. Validación del LOGO 42
        logo_cells = self._get_42_cells()
        if self.entry in logo_cells:
            raise ConfigError(f"Invalid ENTRY: {self.entry} falls inside the '42' logo area. Please change it.")
        if self.exit in logo_cells:
            raise ConfigError(f"Invalid EXIT: {self.exit} falls inside the '42' logo area. Please change it.")

        if self.entry == self.exit:
            raise ConfigError("ENTRY and EXIT must be different.")
