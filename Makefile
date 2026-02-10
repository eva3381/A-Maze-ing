# Colores Rositas
RESET       = \033[0m

NAME        = a_maze_ing
VENV        = venv
PYTHON      = $(VENV)/bin/python3
MAIN        = a_maze_ing.py

all: banner $(VENV) run

banner:
	@echo "$ A-MAZE-ING PROJECT (MLX VERSION)$(RESET)"

$(VENV):
	@echo "$ Creating virtual environment... ✨$(RESET)"
	@python3 -m venv $(VENV)
	@# No instalamos nada por pip porque usaremos los archivos locales de MLX

run:
	@$(PYTHON) $(MAIN) config.txt

clean:
	@rm -rf __pycache__ $(VENV)

re: clean all

.PHONY: all run clean re banner
