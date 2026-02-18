NAME        = a_maze_ing
VENV        = venv
PYTHON      = $(VENV)/bin/python3
PIP         = $(VENV)/bin/pip
MAIN        = a_maze_ing.py
RESET       = \033[0m
CYAN        = \033[36m

all: banner $(VENV) run

banner:
	@echo "$(CYAN)A-MAZE-ING PROJECT (MLX VERSION)$(RESET)"

$(VENV):
	@echo "$(CYAN)Creating virtual environment and installing flake8...$(RESET)"
	@python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@$(PIP) install flake8

run:
	@$(PYTHON) $(MAIN) config.txt

lint:
	@echo "$(CYAN)Running flake8 check...$(RESET)"
	@$(VENV)/bin/flake8 --exclude=$(VENV) .

clean:
	@echo "$(CYAN)Cleaning environment...$(RESET)"
	@rm -rf __pycache__ $(VENV)

re: clean all

.PHONY: all run clean re banner lint