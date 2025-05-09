#!/bin/bash

echo "========================================"
echo "RPG Game Setup (macOS/Linux)"
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

echo
echo "========================================"
echo "Database Configuration"
echo "========================================"
echo
echo "You'll need PostgreSQL installed and running."
echo "You'll need to install required packages using:"
echo "pip3 install sqlalchemy psycopg2-binary"
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
echo "Starting RPG Game..."
echo "========================================"
echo

python3 rpg_game.py

echo
read -p "Press Enter to continue..."
