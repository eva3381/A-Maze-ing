# Colores para la terminal
PINK        = \033[38;5;205m
RESET       = \033[0m

# Nombres y Rutas
NAME        = a_maze_ing
VENV        = venv
PYTHON      = $(VENV)/bin/python3
PIP         = $(VENV)/bin/pip
MAIN        = a_maze_ing.py

all: banner install run

banner:
	@echo "$(PINK)"
	@echo "  🌸  A-MAZE-ING PROJECT  🌸  "
	@echo "=============================="
	@echo "$(RESET)"

$(VENV):
	@echo "$(PINK)Creating virtual environment...$(RESET)"
	@python3 -m venv $(VENV)

install: $(VENV)
	@echo "$(PINK)Installing dependencies...$(RESET)"
	@$(PIP) install --upgrade pip
	@$(PIP) install python-mini-libx
	@# Si usas más librerías, añádelas aquí

run:
	@echo "$(PINK)Running maze generator...$(RESET)"
	@$(PYTHON) $(MAIN)

clean:
	@echo "$(PINK)Cleaning up...$(RESET)"
	@rm -rf __pycache__
	@rm -rf $(VENV)

re: clean all

.PHONY: all install run clean re banner