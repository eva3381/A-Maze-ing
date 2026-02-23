
NAME         = a_maze_ing
VENV         = venv
PYTHON       = $(VENV)/bin/python3

PIP          = $(PYTHON) -m pip
MAIN         = a_maze_ing.py
CONFIG_FILE  = config.txt
REQUIREMENTS = requirements.txt


SRC_FILES    = maze_generator.py draw.py a_maze_ing.py



all: install run

install: $(VENV)/bin/activate

$(VENV)/bin/activate: $(REQUIREMENTS)
	@echo "Status: Creating virtual environment..."
	@python3 -m venv $(VENV)
	@echo "Status: Updating pip and installing dependencies..."
	@$(PIP) install --upgrade pip
	@$(PIP) install -r $(REQUIREMENTS)
	@touch $(VENV)/bin/activate

run: install
	@echo "Status: Executing $(NAME)..."
	@$(PYTHON) $(MAIN) $(CONFIG_FILE)


lint: install
	@echo "--- Static Analysis ---"
	@echo "[flake8] Checking code style..."
	@$(PYTHON) -m flake8 $(SRC_FILES)
	@echo "[mypy] Checking type annotations..."
	@$(PYTHON) -m mypy --ignore-missing-imports $(SRC_FILES)

ar la traza de la solución en otro sitio).
        # Aquí simplemente actuali
clean:
	@echo "Status: Cleaning temporary files..."
	@rm -rf __pythoncache__ .mypy_cache .pytest_cache
	@rm -rf $(VENV)

re: clean all

.PHONY: all install run lint clean re