# Makefile for Python Project on Debian-based systems
SHELL = /bin/bash

# Variables
VENV = venv
PYTHON = python3.11
PIP = pip
REQ_FILE = requirements.txt
PYINSTALLER = pyinstaller
PIPREQS = pipreqs

DEB_PACKAGE = Alice-Client
DEB_VERSION = 1.0.0
DEB_ARCH = armhf

all: run
# Default target
install: install_deps
dist: compile build_deb
update: update_packages generate_reqs

# Check if the system is Debian-based
check_debian:
	@echo "Checking if system is Debian-based..."
	@cat /etc/*-release | grep -q 'ID=raspbian' || (echo "This system is not Debian-based. Exiting..."; false)

# Check for Pyth on and version, install if not present
check_python: check_debian
	@echo "Checking for Python 3.11..."
	@(command -v $(PYTHON) > /dev/null && $(PYTHON) --version | grep -q 'Python 3.11') || \
	(echo "Python 3.11 is not installed. Installing..."; sudo apt-get update; sudo apt-get install -y $(PYTHON) $(PYTHON)-dev)

# Check for pip and install if not installed
check_pip: check_python
	@echo "Checking for pip..."
	@(command -v $(PIP) > /dev/null) || \
	(echo "pip is not installed. Installing pip..."; sudo apt-get install -y $(PYTHON)-pip)

# Check for venv and install if not installed
check_venv:
	@echo "Checking for venv..."
	@(command -v $(PYTHON) -m venv > /dev/null) || \
	(echo "venv is not installed. Installing venv..."; sudo apt-get install -y $(PYTHON)-venv)

# Create virtual environment
venv: check_pip check_venv
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV); \
	else \
		echo "Virtual environment already exists."; \
	fi

# Install dependencies
install_deps: venv
	@echo "Installing dependencies..."
	@(source $(VENV)/bin/activate; $(PIP) install -r $(REQ_FILE); $(PIP) install -U $(PYINSTALLER) $(PIPREQS))

# Compile with pyinstaller
compile: install_deps
	@echo "Compiling with pyinstaller..."
	@(source $(VENV)/bin/activate; $(PYINSTALLER) app.py)

# Update pip packages
update_packages: venv
	@echo "Updating pip packages..."
	@(source $(VENV)/bin/activate; $(PIP) list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 $(PIP) install -U)

# Generate new requirements file
generate_reqs: venv
	@echo "Generating new requirements.txt file..."
	@(source $(VENV)/bin/activate; $(PIPREQS) --force ./)

.PHONY: run clean
run: venv
	@echo "Running script..."
	@(source $(VENV)/bin/activate; $(PYTHON) app.py)
# Convenience targets
clean:
	@echo "Cleaning up..."
	@rm -rf $(VENV) build dist __pycache__

build_deb:
	@echo "Building Debian package..."
	@mkdir -p $(DEB_PACKAGE)/lib/systemd/system
	@cp $(DEB_PACKAGE)/alice-client.service $(DEB_PACKAGE)/lib/systemd/system/alice-client.service
	@cp dist/app/app $(DEB_PACKAGE)/usr/local/bin/alice-client
	@dpkg-deb --build $(DEB_PACKAGE)
