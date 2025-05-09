# Local Installation Guide for RPG Game

This guide will help you set up and run the RPG game on your local computer.

## Prerequisites

Before you start, you'll need to have the following installed:

1. **Python 3.10 or newer**
2. **PostgreSQL database server**
3. **Required Python packages**: 
   - sqlalchemy
   - psycopg2-binary

## Step-by-Step Installation

### 1. Install Python

#### Windows
1. Download the latest Python installer from [python.org](https://www.python.org/downloads/)
2. Run the installer and **make sure to check "Add Python to PATH"**
3. Verify installation by opening Command Prompt and typing `python --version`

#### macOS
1. Install using Homebrew: `brew install python`
2. Or download from [python.org](https://www.python.org/downloads/)
3. Verify with `python3 --version`

#### Linux
1. Most distributions come with Python pre-installed
2. If not, use your package manager: `sudo apt install python3` (Ubuntu/Debian)
3. Verify with `python3 --version`

### 2. Install PostgreSQL

#### Windows
1. Download the installer from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Run the installer and follow the prompts
3. Remember the password you set for the postgres user
4. The installer includes pgAdmin, which is a helpful GUI tool

#### macOS
1. Install using Homebrew: `brew install postgresql`
2. Or download from [postgresql.org](https://www.postgresql.org/download/macosx/)

#### Linux
1. Use your package manager: `sudo apt install postgresql postgresql-contrib` (Ubuntu/Debian)

### 3. Create a Database

#### Using pgAdmin (Windows/GUI method)
1. Open pgAdmin from your Start menu
2. Connect to your PostgreSQL server
3. Right-click on "Databases" → "Create" → "Database"
4. Name it `rpg_game` (or your preferred name)

#### Using Command Line (All platforms)
1. Open terminal or command prompt
2. Log in to PostgreSQL: `psql -U postgres`
3. Create database: `CREATE DATABASE rpg_game;`
4. Exit with `\q`

### 4. Install Required Python Packages

Open terminal or command prompt and run:

```
pip install sqlalchemy psycopg2-binary
```

On some systems, you might need to use `pip3` instead of `pip`.

### 5. Download the Game Files

1. Download all the game files preserving the folder structure
2. Make sure you have all key files:
   - rpg_game.py
   - new_game.py
   - characters.py
   - items.py
   - db_models.py
   - db_utils.py
   - combat.py
   - monsters.py
   - (and other related files)

### 6. Configure Database Connection

#### Using the Setup Scripts (Easiest Method)
1. Use the provided setup scripts:
   - `start_game.bat` for Windows
   - `start_game.sh` for macOS/Linux
2. These scripts will prompt you for database credentials and set up the necessary environment variables

#### Manual Setup (Alternative Method)

You need to set these environment variables:

##### Windows
Open Command Prompt and run:
```
set PGUSER=postgres
set PGPASSWORD=your_password
set PGHOST=localhost
set PGPORT=5432
set PGDATABASE=rpg_game
set DATABASE_URL=postgresql://postgres:your_password@localhost:5432/rpg_game
```

##### macOS/Linux
Open Terminal and run:
```
export PGUSER=postgres
export PGPASSWORD=your_password
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=rpg_game
export DATABASE_URL=postgresql://postgres:your_password@localhost:5432/rpg_game
```

### 7. Run the Game

#### Using the Setup Scripts
Simply run:
- Windows: Double-click `start_game.bat` or run it from Command Prompt
  - The console will automatically switch to white background with black text for better readability
- macOS/Linux: Run `./start_game.sh` in Terminal

#### GUI Mode (Recommended for Windows)
For better visual experience, especially with emojis:
- Windows: Double-click `start_game_gui.bat`
- macOS/Linux: Run `./start_game_gui.sh` in Terminal

#### Manual Run
Navigate to the game directory in terminal/command prompt and run:
```
python rpg_game.py
```
(Use `python3` instead of `python` on macOS/Linux if needed)

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check if your username and password are correct
- Make sure the database exists
- Try connecting with a different tool to verify credentials

### Missing Packages
If you see import errors, install the missing package:
```
pip install package_name
```

### Permission Issues
- Make sure Python has read/write access to the game directory
- On Unix-based systems, you might need to run: `chmod +x start_game.sh`

### Character Encoding
- The game uses emoji characters. If they don't display correctly, try a different terminal or command prompt

## Enjoy the Game!

Follow the in-game instructions to create your character and begin your adventure. Refer to the USER_GUIDE.md for gameplay instructions.