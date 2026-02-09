# Colores Rositas
PINK        = \033[38;5;205m
RESET       = \033[0m

NAME        = a_maze_ing
VENV        = venv
PYTHON      = $(VENV)/bin/python3
MAIN        = a_maze_ing.py

all: banner $(VENV) run

banner:
	@echo "$(PINK)  🌸  A-MAZE-ING PROJECT (MLX VERSION)  🌸  $(RESET)"

$(VENV):
	@echo "$(PINK)Creating virtual environment... ✨$(RESET)"
	@python3 -m venv $(VENV)
	@# No instalamos nada por pip porque usaremos los archivos locales de MLX

run:
	@echo "$(PINK)Running with MiniLibX... 🚀$(RESET)"
	@$(PYTHON) $(MAIN)

clean:
	@rm -rf __pycache__ $(VENV)

re: clean all

.PHONY: all run clean re banner
