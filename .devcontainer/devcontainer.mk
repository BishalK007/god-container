VENV_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))/.venv
CMD_FILE := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))/cmd/main.py
REQ_FILE := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))/requirements.txt
PYTHON    := $(VENV_DIR)/bin/python3
PIP       := $(VENV_DIR)/bin/pip

.PHONY: conf-container

conf-container:
	@if [ ! -d "$(VENV_DIR)" ]; then \
	  python3 -m venv $(VENV_DIR); \
	  echo "Created virtual env in $(VENV_DIR)"; \
	else \
	  echo "Using existing venv at $(VENV_DIR)"; \
	fi
	@echo "Activating venv and installing pip/setup-tools if needed..."
	@$(PYTHON) -m pip install --upgrade pip setuptools >/dev/null
	@echo "Installing requirements..."
	@$(PIP) install -r $(REQ_FILE) 
	@echo "Running configuration..."
	@$(PYTHON) $(CMD_FILE) --conf


.PHONY: conn 

conn:
	@if [ ! -d "$(VENV_DIR)" ]; then \
	  echo "Virtual environment not found. Please run 'make conf-container' first."; \
	  exit 1; \
	fi
	@echo "Connecting to devcontainer..."
	@$(PYTHON) $(CMD_FILE) --conn
