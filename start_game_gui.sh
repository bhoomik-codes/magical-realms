#!/bin/bash

echo "========================================"
echo "RPG Game GUI Setup (macOS/Linux)"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH."
    echo "Please install Python from https://python.org"
    echo "Or use your package manager (apt, brew, etc.)"
    exit 1
fi

# Check Python version
python3 --version

# Check if tkinter is available
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: Tkinter is not available."
    echo "Please ensure the tkinter package for Python is available."
    echo "This is often included with Python but sometimes needs to be added separately."
    exit 1
fi

echo
echo "========================================"
echo "Database Configuration"
echo "========================================"
echo
echo "You'll need PostgreSQL installed and running."
echo

read -p "Enter database username (default: postgres): " PGUSER
PGUSER=${PGUSER:-postgres}

read -sp "Enter database password: " PGPASSWORD
echo

read -p "Enter database host (default: localhost): " PGHOST
PGHOST=${PGHOST:-localhost}

read -p "Enter database port (default: 5432): " PGPORT
PGPORT=${PGPORT:-5432}

read -p "Enter database name (default: rpg_game): " PGDATABASE
PGDATABASE=${PGDATABASE:-rpg_game}

# Export environment variables
export PGUSER
export PGPASSWORD
export PGHOST
export PGPORT
export PGDATABASE
export DATABASE_URL="postgresql://$PGUSER:$PGPASSWORD@$PGHOST:$PGPORT/$PGDATABASE"

echo
echo "Database connection string set to: postgresql://$PGUSER:******@$PGHOST:$PGPORT/$PGDATABASE"
echo

echo "========================================"
echo "Starting RPG Game with GUI..."
echo "========================================"
echo

# Set UTF-8 encoding for better handling of emojis and special characters
export PYTHONIOENCODING=utf-8
export LC_ALL=en_US.UTF-8 2>/dev/null || export LC_ALL=C.UTF-8 2>/dev/null || echo "Warning: Could not set UTF-8 locale"

python3 -X utf8 rpg_game_gui.py

echo
read -p "Press Enter to continue..."
