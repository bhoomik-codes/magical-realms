# Magical-Realms
A simple text-based adventure RPG game made using applying OOPS paradigm in Python
# RPG GAME USER GUIDE

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Character Classes](#character-classes)
4. [Game Controls](#game-controls)
5. [Combat System](#combat-system)
6. [Items and Equipment](#items-and-equipment)
7. [Monsters and Enemies](#monsters-and-enemies)
8. [Leveling and Progression](#leveling-and-progression)
9. [Saving and Loading](#saving-and-loading)
10. [Tips and Strategies](#tips-and-strategies)

## Introduction

Welcome to the enhanced RPG adventure! This text-based role-playing game allows you to create a character, battle monsters, collect items, level up, and save your progress. The game features multiple character classes, each with unique abilities, an inventory system, and a variety of monsters to defeat.

## Getting Started

When you start the game, you'll see the main title screen with options to create a new character or load an existing one. If this is your first time playing, select "Create New Character" to begin your adventure.

## Character Classes

There are three character classes to choose from, each with different strengths and weaknesses:

### Barbarian 🪓
- **Base Stats**: HP 150, Mana 30, Attack 25, Defense 8
- **Special Ability**: Rage Attack - A powerful attack that deals double damage but costs 20 mana
- **Level-up Gains**: HP +15, Mana +5, Attack +3, Defense +1
- **Play Style**: The Barbarian excels at dealing high damage and has a large health pool, making them ideal for players who prefer an aggressive play style. However, they have limited mana for special abilities.

### Archer 🏹
- **Base Stats**: HP 90, Mana 60, Attack 22, Defense 12
- **Special Ability**: Precision Shot - An accurate attack with a 30% chance to ignore defense, costs 15 mana
- **Regular Attack**: More consistent damage (less randomness)
- **Level-up Gains**: HP +10, Mana +8, Attack +2, Defense +2
- **Play Style**: The Archer offers a balanced play style with consistent damage output and moderate defenses. Their special ability can be devastating against heavily armored foes.

### Mage 🧙
- **Base Stats**: HP 80, Mana 120, Attack 15, Defense 5
- **Special Ability**: Fireball - A high-damage spell that costs 25 mana and partially bypasses blocking
- **Unique Ability**: Heal - Restores 25-40 HP for 30 mana
- **Level-up Gains**: HP +8, Mana +12, Attack +2, Defense +1
- **Play Style**: The Mage is a glass cannon with the highest damage potential but low survivability. They excel at using special abilities and can heal themselves, making them versatile but challenging to play.

## Game Controls

The game uses a text-based interface where you make choices by entering numbers or letters. The main game loop consists of these key menus:

### Main Menu
- Hunt Monsters 🏕️: Find and fight monsters for XP, gold, and items (you can now hunt continuously without returning to the main menu)
- Face a Villain 👺: Battle a random villain appropriate to your level
- Challenge Boss ⚠️: Face a powerful boss monster for better rewards
- Manage Inventory 🎒: View, use, and equip items
- Character Status 👤: View detailed character information
- Rest and Recover 🏠: Restore HP and mana to maximum
- Save Character 💾: Save your progress
- Change Character 👥: Switch to a different character
- Exit Game 🚪: Quit the game

## Combat System

Combat is turn-based and offers several actions:

1. **Attack**: Perform a basic attack
2. **Special Attack**: Use your class's special ability (costs mana)
3. **Block**: Reduce incoming damage by doubling your defense
4. **Dodge**: Attempt to avoid an attack entirely (60% success chance)
5. **Use Item**: Use a consumable item from your inventory
6. **Run**: Attempt to escape from combat (70% success chance)

### Combat Mechanics:
- **Damage Calculation**: Attack value - Defense value = Damage dealt
- **Randomness**: Attack values have some randomness (-10 to +10)
- **Blocking**: Doubles defense but prevents attacking on that turn
- **Dodging**: 60% chance to avoid attacks, but fails 70% against special attacks
- **Death**: If your HP reaches 0, you lose the battle but are revived with 50% HP and mana (losing some gold)

## Items and Equipment

### Consumables
Items that can be used for immediate effects:

1. **Health Potions**
   - Small Health Potion: Restores 25 HP (Value: 15 gold)
   - Medium Health Potion: Restores 50 HP (Value: 30 gold)
   - Large Health Potion: Restores 100 HP (Value: 60 gold)

2. **Mana Potions**
   - Small Mana Potion: Restores 15 Mana (Value: 15 gold)
   - Medium Mana Potion: Restores 30 Mana (Value: 30 gold)
   - Large Mana Potion: Restores 60 Mana (Value: 60 gold)

3. **Strength Elixir**: Increases attack by 10 for 3 turns (Value: 50 gold)

### Equipment
Items that can be equipped to permanently boost stats until unequipped:

#### Weapons (Boost Attack)
1. **Barbarian Weapons**:
   - Axe
   - War Hammer
   - Greatsword
   - Battle Axe

2. **Archer Weapons**:
   - Bow
   - Crossbow
   - Longbow
   - Hunting Bow

3. **Mage Weapons**:
   - Staff
   - Wand
   - Orb
   - Grimoire

#### Armor (Boost Defense)
1. **Barbarian Armor**:
   - Hide Armor
   - Fur Armor
   - Plate Mail
   - Chain Mail

2. **Archer Armor**:
   - Leather Armor
   - Scout Armor
   - Rangers Cloak
   - Hunters Garb

3. **Mage Armor**:
   - Robe
   - Enchanted Garb
   - Mystic Vestments
   - Arcane Cloak

#### Accessories (Multiple Stat Boosts)
Accessories can boost any combination of Attack, Defense, Max HP, or Max Mana:
- Amulet
- Ring
- Bracers
- Belt
- Cloak

### Item Quality
All equipment comes in three quality tiers, affecting their stats and value:

1. **Common**: No prefix, basic stat boosts
2. **Uncommon**: Prefixed with "Fine", "Strong", "Crafted", "Sturdy", "Reinforced", or "Hardy", medium stat boosts
3. **Rare**: Prefixed with "Masterwork", "Enchanted", "Superior", "Impenetrable", "Ancient", "Legendary", or "Mythical", high stat boosts

The stat boosts of items scale with your character level, so higher-level characters will find more powerful equipment.

## Monsters and Enemies

### Regular Monsters

1. **Slime** 🟢
   - **Base Stats**: Higher HP (+10), Lower Attack (-2)
   - **Special Attack**: Split - Multiple weak attacks (3 hits)
   - **Drops**: Small health/mana potions, common equipment
   - **Difficulty**: Easy
   - **Boss Version**: King Slime (50% more HP/Mana, 30% more Attack/Defense)

2. **Goblin** 👺
   - **Base Stats**: Higher Attack (+4), Lower Defense (-2), Lower HP (-10)
   - **Special Attack**: Sneaky Strike - Ignores 50% of target's defense
   - **Drops**: Gold, uncommon weapons, potions
   - **Difficulty**: Medium
   - **Boss Version**: Goblin Chieftain (50% more HP/Mana, 30% more Attack/Defense)

3. **Skeleton** 💀 (Available at player level 2+)
   - **Base Stats**: Lower HP (-15), Higher Defense (+3)
   - **Special Ability**: Damage Reduction - Takes 25% less damage
   - **Special Attack**: Bone Throw - 50% more damage than base attack
   - **Drops**: Weapons, armor, strength elixirs
   - **Difficulty**: Medium
   - **Boss Version**: Skeleton Lord (50% more HP/Mana, 30% more Attack/Defense)

4. **Vampire** 🧛 (Available at player level 3+)
   - **Base Stats**: Standard monster stats
   - **Special Ability**: Lifesteal - Regains 20% of damage dealt as HP
   - **Special Attack**: Blood Drain - Stronger attack with 40% lifesteal
   - **Drops**: Rare accessories, potions, high gold
   - **Difficulty**: Hard
   - **Boss Version**: Vampire Lord (50% more HP/Mana, 30% more Attack/Defense)

5. **Dragon** 🐉 (Boss only, available at player level 5+)
   - **Base Stats**: Much higher HP (+20%), Attack (+8), and Defense (+5)
   - **Special Attack**: Fire Breath - Double damage and ignores 50% of defense
   - **Drops**: Guaranteed rare items, high gold rewards
   - **Difficulty**: Very Hard

### Villain Types

1. **Dark Knight** 🖤
   - **Base Stats**: HP 130, Mana 40, Attack 20, Defense 20
   - **Special Attack**: Dark Slash - 70% more damage and heals 30% of damage dealt

2. **Dark Archer** 🏹
   - **Base Stats**: HP 90, Mana 70, Attack 25, Defense 8
   - **Special Attack**: Poison Arrow - Deals additional poison damage over time

3. **Dark Mage** 🧙‍♂️
   - **Base Stats**: HP 85, Mana 130, Attack 15, Defense 6
   - **Special Attack**: Dark Energy Blast - Triple damage and ignores 30% of defense

## Monster Drops

All monsters drop gold and have a chance to drop items. The quantity and quality of drops depend on:
- Monster level (higher level = better drops)
- Monster type (boss versions drop more valuable items)
- Monster difficulty (harder monsters = better drops)

### Drop Chances
- Regular monsters: 60% chance for an item drop
- Boss monsters: 100% chance for an item drop
- Dragon boss: Guaranteed rare item drop

### General Drop Rates for Items
- Weapons: 20% chance
- Armor: 20% chance
- Accessories: 10% chance
- Health Potions: 25% chance
- Mana Potions: 20% chance
- Strength Elixirs: 5% chance

## Leveling and Progression

### Experience Points
- Defeating monsters grants XP based on their level (25 XP per level)
- Boss monsters grant double XP
- Defeating villains grants 50 XP per villain level

### Level Up System
- Each level requires 50% more XP than the previous level
- Level ups restore full HP and mana
- Each class gains different stat increases when leveling up (see Character Classes section)

### Hunting Areas
As you level up, new hunting areas become available:
1. **Forest Outskirts**: Always available, easy monsters
2. **Deep Woods**: Unlocks at level 3, moderate difficulty
3. **Ancient Ruins**: Unlocks at level 5, difficult monsters
4. **Dark Caverns**: Unlocks at level 8, very challenging
5. **Dragon's Lair**: Unlocks at level 5, boss fight (extremely difficult)

### Luck System ⭐
The game features a hidden luck stat that affects item quality in the shop:

- **Starting Luck**: All characters begin with 0 luck
- **Increasing Luck**:
  - Defeating a boss guarantees +2-5 luck points
  - Defeating a villain has a 30% chance to give +1-2 luck points
- **Effects of Luck**:
  - Higher luck increases the probability of uncommon and rare items appearing in the shop
  - Luck does not affect combat or item drops from monsters
  - The shop inventory refreshes after each boss or villain battle, and can also be manually refreshed for 20 gold

### Shop System 🛒
Visit the shop from the main menu to buy and sell items:

- **Browse Items**: View and purchase available equipment and consumables
- **Sell Items**: Sell unwanted items for half their value
- **Refresh Inventory**: Pay 20 gold to get a new selection of items
- **Item Quality**: Item quality (and stats) is influenced by:
  - Your character's level
  - Your character's luck stat
  - Random chance

## Saving and Loading

### Save System
- You can save your character at any time from the main menu
- The game uses a database to store character information, including:
  - Stats (HP, Mana, Attack, Defense)
  - Level and XP
  - Inventory items and gold
  - Equipped items

### Character Management
The character management screen allows you to:
1. Create new characters
2. Load saved characters
3. Save your current character
4. Delete saved characters

You can have multiple saved characters and switch between them.

## Tips and Strategies

### General Tips
- Rest to restore HP and mana before difficult battles
- Save your character regularly to avoid losing progress
- Use special attacks wisely to conserve mana
- Buy health and mana potions when available

### Class-Specific Tips

#### Barbarian
- Use your high HP to your advantage in difficult fights
- Save mana for Rage Attack against tough enemies
- Invest in defense boosting items to compensate for lower base defense

#### Archer
- Leverage your consistent damage and balanced stats
- Use Precision Shot against heavily armored opponents
- Dodge works well with your balanced defenses

#### Mage
- Keep enemies at bay with powerful spells
- Don't forget to use Heal when your HP gets low
- Block when conserving mana
- Focus on boosting your max HP with accessories

### Combat Tips
- Against powerful enemies, block when your HP is low
- Use dodge against high-damage attacks
- Save your special attacks for when they'll be most effective
- Remember that some special attacks partially bypass blocking

### Item Management
- Sell or discard common items when you find better equipment
- Keep a few healing and mana potions for emergencies
- Equip items that complement your class's strengths
- Strength Elixirs are most effective during boss fights

---

Enjoy your adventure in the Enhanced RPG Game! May your blades stay sharp and your spells powerful!


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



