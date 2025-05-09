#!/bin/bash

echo "========================================"
echo "RPG Game Improved GUI Setup (Unix/Linux)"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH."
    echo "Please install Python using your distribution's package manager."
    echo "For example: sudo apt install python3 python3-tk"
    read -p "Press Enter to exit..."
    exit 1
fi

# Check Python version
python3 --version

# Check if tkinter is available
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "ERROR: Tkinter is not available."
    echo "Please install the Python Tkinter package."
    echo "For example: sudo apt install python3-tk"
    read -p "Press Enter to exit..."
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

# Set the full DATABASE_URL environment variable
export DATABASE_URL="postgresql://$PGUSER:$PGPASSWORD@$PGHOST:$PGPORT/$PGDATABASE"

echo
echo "Database connection string set to: postgresql://$PGUSER:******@$PGHOST:$PGPORT/$PGDATABASE"
echo

echo "========================================"
echo "Starting RPG Game with Improved GUI..."
echo "========================================"
echo

# Set UTF-8 encoding for better display of special characters
export PYTHONIOENCODING=utf-8
python3 rpg_game_improved_gui.py

echo
read -p "Press Enter to exit..."