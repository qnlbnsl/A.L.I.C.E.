# Makefile for Python Project on Debian-based systems

# Variables
VENV := venv
PYTHON := python3
PIP := pip
REQ_FILE := requirements.txt
PYINSTALLER := pyinstaller
PIPREQS := pipreqs

DEB_PACKAGE := Alice-Client
DEB_VERSION := 1.0.0
DEB_ARCH := amd64

# Default target
all: check_debian check_python venv install_deps compile update_packages generate_reqs

# Check if the system is Debian-based
check_debian:
	@echo "Checking if system is Debian-based..."
	@cat /etc/*-release | grep -q 'ID=debian' || (echo "This system is not Debian-based. Exiting..."; false)

# Check for Python and version, install if not present
check_python:
	@echo "Checking for Python 3.11..."
	@(command -v $(PYTHON) > /dev/null && $(PYTHON) --version | grep -q 'Python 3.11') || \
	(echo "Python 3.11 is not installed. Installing..."; sudo apt-get update; sudo apt-get install -y python3.11)

# Check for pip and install if not installed
check_pip:
	@echo "Checking for pip..."
	@(command -v $(PIP) > /dev/null) || \
	(echo "pip is not installed. Installing pip..."; sudo apt-get install -y python3-pip)

# Check for venv and install if not installed
check_venv:
	@echo "Checking for venv..."
	@(command -v $(PYTHON) -m venv > /dev/null) || \
	(echo "venv is not installed. Installing venv..."; sudo apt-get install -y python3-venv)

# Create virtual environment
venv: check_python check_pip check_venv
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV); \
	else \
		echo "Virtual environment already exists."; \
	fi

# Install dependencies
install_deps: venv
	@echo "Installing dependencies..."
	@(source $(VENV)/bin/activate; $(PIP) install -r $(REQ_FILE); $(PIP) install $(PYINSTALLER) $(PIPREQS))

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

.PHONY: run
run: venv
	@echo "Running script..."
	@(source $(VENV)/bin/activate; $(PYTHON) app.py)
# Convenience targets
.PHONY: clean
clean:
	@echo "Cleaning up..."
	@rm -rf $(VENV) build dist __pycache__

prepare_deb:
    @echo "Preparing Debian package structure..."
    @mkdir -p $(DEB_PACKAGE)/DEBIAN
    @mkdir -p $(DEB_PACKAGE)/usr/local/bin
    @mkdir -p $(DEB_PACKAGE)/lib/systemd/system
    @echo "Package: $(DEB_PACKAGE)\nVersion: $(DEB_VERSION)\nSection: base\nPriority: optional\nArchitecture: $(DEB_ARCH)\nDepends: python3\nMaintainer: Your Name <your.email@example.com>\nDescription: My application description" > $(DEB_PACKAGE)/DEBIAN/control
    @cp dist/myapp $(DEB_PACKAGE)/usr/local/bin/alice-client
    @echo "[Unit]\nDescription=Alice-Client Service\nAfter=network.target\n[Service]\nExecStart=/usr/local/bin/alice-client\nRestart=on-failure\nRestartSec=60\n[Install]\nWantedBy=multi-user.target" > $(DEB_PACKAGE)/lib/systemd/system/$(DEB_PACKAGE).service

# Build Debian package
build_deb: prepare_deb
    @echo "Building Debian package..."
    @dpkg-deb --build $(DEB_PACKAGE)