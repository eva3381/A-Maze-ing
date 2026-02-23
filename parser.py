import sys
from typing import Dict, Tuple

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
        allowed_keys = {
            'WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 
            'OUTPUT_FILE', 'PERFECT', 'SEED', 'ALGORITHM'
        }

        try:
            with open(self.file_name, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        raise ConfigError(f"Invalid line format: '{line}'")
                    
                    key, value = line.split("=", 1)
                    key_upper = key.strip().upper()
                    
                    if key_upper not in allowed_keys:
                        raise ConfigError(f"Unallowed parameter: '{key_upper}'")
                        
                    config[key_upper] = value.strip()
        except FileNotFoundError:
            raise ConfigError(f"The file '{self.file_name}' does not exist.")
        
        return config

    def _process_and_validate(self, config: Dict[str, str]) -> None:
        # Check mandatory fields
        mandatory = ["WIDTH", "HEIGHT", "PERFECT", "OUTPUT_FILE", "ENTRY", "EXIT"]
        for field in mandatory:
            if field not in config:
                raise ConfigError(f"Missing mandatory field: '{field}'")

        try:
            self.width = int(config["WIDTH"])
            self.height = int(config["HEIGHT"])
            
            # Strict PERFECT check
            perf_val = config["PERFECT"]
            if perf_val not in ["True", "False"]:
                raise ConfigError(f"PERFECT must be 'True' or 'False' (Got: '{perf_val}')")
            self.is_perfect = (perf_val == "True")

            self.output_file = config["OUTPUT_FILE"]
            self.seed = int(config.get("SEED", 0))
            self.algorithm = config.get("ALGORITHM", "DFS").upper()

            # Coordinates validation
            self.entry = self._parse_coords(config["ENTRY"], "ENTRY")
            self.exit = self._parse_coords(config["EXIT"], "EXIT")

        except ValueError:
            raise ConfigError("Invalid data format: expected an integer.")

        self._validate_logic()

    def _parse_coords(self, text: str, label: str) -> Tuple[int, int]:
        parts = text.split(",")
        if len(parts) != 2:
            raise ConfigError(f"{label} must be in 'x,y' format.")
        return (int(parts[0].strip()), int(parts[1].strip()))

    def _validate_logic(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ConfigError("Dimensions must be greater than 0.")

        # Logic check for boundaries
        ex, ey = self.entry
        sx, sy = self.exit

        if not (0 <= ex < self.width and 0 <= ey < self.height):
            raise ConfigError(f"ENTRY {self.entry} is outside {self.width}x{self.height} grid.")
        
        if not (0 <= sx < self.width and 0 <= sy < self.height):
            raise ConfigError(f"EXIT {self.exit} is outside {self.width}x{self.height} grid.")

        if self.entry == self.exit:
            raise ConfigError("ENTRY and EXIT must be different locations.")
