#!/bin/bash
# This script is used to install the requirements for the project on a mac

#cd into the directory of the script
cd "$(dirname "$0")"

# Install homebrew if not already installed
if ! hash brew 2>/dev/null; then
    echo "Installing homebrew"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# find python or python3 executable
if hash python3 2>/dev/null; then
    PIP_EXECUTABLE=pip3
elif hash python 2>/dev/null; then
    # Confirm that python version is 3 or greater
    PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
    if [[ $PYTHON_VERSION == 2* ]]; then
        echo "Python version 3 or greater required"
        brew install python3
        PIP_EXECUTABLE=pip3
    fi
    PIP_EXECUTABLE=pip
else
    echo "Python not found"
    exit 1
fi

# Install system dependencies
echo "Installing system dependencies"
brew install portaudio python-tk

# Install python dependencies
echo "Installing python dependencies"
$PIP_EXECUTABLE install -r requirements.txt