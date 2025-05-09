# RPG Game - Windows User Guide

## Game Overview

Welcome to the RPG Adventure Game! This is a text-based role-playing game where you can:

- Create characters from different classes (Barbarian, Archer, Mage)
- Battle monsters and villains
- Collect items and gold
- Level up and evolve your character class
- Save multiple characters and track their progress

## System Requirements

- Windows 10 or 11
- Python 3.10 or newer
- PostgreSQL database
- Required Python packages:
  - tkinter (for GUI mode)
  - ttkbootstrap (for enhanced GUI mode)
  - psycopg2-binary
  - sqlalchemy

## Installation Guide

1. **Install Python**:
   - Download from [python.org](https://python.org)
   - Make sure to check "Add Python to PATH" during installation
   - Ensure you select the "tcl/tk and IDLE" option for GUI support

2. **Install PostgreSQL**:
   - Download from [postgresql.org](https://www.postgresql.org/download/windows/)
   - Remember your username, password, and port settings
   - Create a new database named "rpg_game" (or choose your own name)

3. **Install Required Python Packages**:
   ```
   pip install psycopg2-binary sqlalchemy ttkbootstrap
   ```

## Starting the Game

There are multiple ways to run the game:

### Text Mode
Run `start_game.bat` to play the game in text-only console mode.

### Basic GUI Mode
Run `start_improved_gui.bat` to play with the basic graphical interface.

### Enhanced GUI Mode (Recommended)
Run `start_ttkbootstrap_gui.bat` to play with the enhanced graphical interface using ttkbootstrap.

Each of these scripts will:
1. Check if your system has the required dependencies
2. Prompt you for PostgreSQL database connection details
3. Launch the game in the selected mode

## Gameplay Guide

### Character Creation
1. Choose your character class:
   - **Barbarian**: High HP and attack, but low mana and defense
   - **Archer**: Balanced stats with high accuracy
   - **Mage**: High mana and spell power, but low HP and defense
2. Enter a name for your character

### Main Menu
From the main menu, you can:
1. **Hunt Monsters**: Fight random monsters to gain XP and items
2. **Inventory**: Manage your items and equipment
3. **Shop**: Buy and sell items
4. **Character Status**: View detailed information about your character
5. **Face Boss**: Challenge a powerful boss monster
6. **Save Character**: Save your progress
7. **Exit**: Quit the game

### Combat
During combat, you can:
1. **Attack**: Basic attack that deals damage based on your attack value
2. **Special Attack**: More powerful attack that consumes mana
3. **Block**: Reduce incoming damage for the next turn
4. **Dodge**: Chance to completely avoid the next attack
5. **Use Item**: Consume a potion or other usable item
6. **Run**: Try to escape from the battle

### Character Evolution
As you level up, your character will evolve through different class tiers:
- Tier 1 (Level 5): First evolution
- Tier 2 (Level 10): Second evolution
- And so on...

Each evolution grants improved stats and may unlock new abilities!

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Verify your username, password, host, port, and database name
- Check that you have privileges to create tables in the database

### GUI Display Problems
- Make sure you have tkinter installed with your Python installation
- For enhanced GUI, ensure ttkbootstrap is installed
- If text or emojis display as boxes or question marks, the script should automatically set UTF-8 encoding

### Game Crashes
- Check the console output for error messages
- Ensure all required Python packages are installed
- Try running in text mode if GUI mode has issues

## Feedback and Support

This is a standalone game for Windows. For help or to report issues, please contact the developer.

Enjoy your adventure!