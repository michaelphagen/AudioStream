#!/bin/bash
# This script is used to install the requirements for the project on a mac

#cd into the directory of the script
cd "$(dirname "$0")" || exit

# Install homebrew if not already installed
if ! hash brew 2>/dev/null; then
    echo "Installing homebrew"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# If portaudio and python-tk@3.11 are not installed, install them
if ! brew list | grep -q portaudio || ! brew list | grep -q python-tk@3.11; then
    echo "Installing system dependencies"
    echo "Installing portaudio and python-tk@3.11"
    brew install portaudio python-tk@3.11
fi

# Get the python 3.11 executable and pip executable installed via homebrew
PYTHON_EXECUTABLE=$(brew --prefix python@3.11)/bin/python3.11
PIP_EXECUTABLE=$(brew --prefix python@3.11)/bin/pip3.11

# If python dependencies are not installed (requirements.txt), install them
# Check for a pyvenv.cfg file to determine if the environment is managed externally
if [ -f pyvenv.cfg ]; then
    source ./bin/activate
    if ! python -m pip freeze | grep -q -f requirements.txt; then
        echo "Installing python dependencies"
        $PIP_EXECUTABLE install -r requirements.txt
    fi
else
    if ! python -m pip freeze | grep -q -f requirements.txt; then
        echo "Installing python dependencies"
        $PIP_EXECUTABLE install -r requirements.txt || {
            if [[ $? -eq 1 && $($PIP_EXECUTABLE install -r requirements.txt 2>&1) == *"externally-managed-environment"* ]]; then
                echo "Handling externally managed environment error"
                $PYTHON_EXECUTABLE -m venv ./
                source ./bin/activate
                $PIP_EXECUTABLE install -r requirements.txt
            else
                exit 1
            fi
        }
    fi
fi

# Run the app
$PYTHON_EXECUTABLE app.py