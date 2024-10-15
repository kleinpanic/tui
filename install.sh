#!/bin/bash

set -e

# Function to determine the package manager
detect_package_manager() {
    if command -v apt-get &> /dev/null; then
        echo "apt-get"
    elif command -v yum &> /dev/null; then
        echo "yum"
    elif command -v pacman &> /dev/null; then
        echo "pacman"
    elif command -v zypper &> /dev/null; then
        echo "zypper"
    elif command -v brew &> /dev/null; then
        echo "brew"
    else
        echo "unsupported"
    fi
}

# Function to check for Python and install if missing
install_python() {
    if ! command -v python3 &> /dev/null; then
        echo "Python3 is not installed. Installing..."
        local manager=$(detect_package_manager)
        case $manager in
            apt-get)
                sudo apt-get update && sudo apt-get install -y python3 python3-venv
                ;;
            yum)
                sudo yum install -y python3 python3-venv
                ;;
            pacman)
                sudo pacman -Sy python python-virtualenv
                ;;
            zypper)
                sudo zypper install -y python3 python3-venv
                ;;
            brew)
                brew install python3
                ;;
            *)
                echo "Unsupported package manager. Please install Python3 manually."
                exit 1
                ;;
        esac
    else
        echo "Python3 is already installed."
    fi
}

# Function to check and install virtualenv
install_venv() {
    if ! python3 -m venv --help &> /dev/null; then
        echo "Python venv is not installed. Installing..."
        local manager=$(detect_package_manager)
        case $manager in
            apt-get)
                sudo apt-get install -y python3-venv
                ;;
            yum)
                sudo yum install -y python3-venv
                ;;
            pacman)
                sudo pacman -Sy python-virtualenv
                ;;
            zypper)
                sudo zypper install -y python3-venv
                ;;
            brew)
                brew install python3
                ;;
            *)
                echo "Unsupported package manager. Please install python3-venv manually."
                exit 1
                ;;
        esac
    else
        echo "Python venv is already installed."
    fi
}

# Function to create virtual environment and install requirements
setup_virtualenv() {
    echo "Setting up Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    if [[ -f "requirements.txt" ]]; then
        echo "Installing requirements..."
        pip install -r requirements.txt
    else
        echo "No requirements.txt found. Skipping package installation."
    fi
}

# Function to install fonts and utilities for ASCII graphics
install_ascii_fonts() {
    echo "Installing utilities and fonts for ASCII graphics..."
    local manager=$(detect_package_manager)
    case $manager in
        apt-get)
            sudo apt-get install -y figlet toilet
            ;;
        yum)
            sudo yum install -y figlet toilet
            ;;
        pacman)
            sudo pacman -Sy figlet toilet
            ;;
        zypper)
            sudo zypper install -y figlet toilet
            ;;
        brew)
            brew install figlet toilet
            ;;
        *)
            echo "Unsupported package manager. Please install figlet and toilet manually."
            exit 1
            ;;
    esac
}

# Function to check the shell/terminal being used
detect_terminal() {
    echo "Detecting terminal environment..."
    echo "Current shell: $SHELL"
    echo "Current terminal: $TERM"

    case "$TERM" in
        xterm*|rxvt*|screen*|tmux*|vt100*|linux*|cygwin*|ansi)
            echo "Compatible terminal detected: $TERM"
            ;;
        *)
            echo "Warning: Unusual or unknown terminal type ($TERM). ASCII graphics might not display correctly."
            ;;
    esac

    case "$SHELL" in
        */bash)
            echo "You are using bash."
            ;;
        */zsh)
            echo "You are using zsh."
            ;;
        */fish)
            echo "You are using fish."
            ;;
        *)
            echo "Unknown shell. Please ensure compatibility."
            ;;
    esac
}

# Main installer function
main() {
    echo "Starting installation process..."
    install_python
    install_venv
    setup_virtualenv
    install_ascii_fonts
    detect_terminal
    echo "Installation complete."
}

main
