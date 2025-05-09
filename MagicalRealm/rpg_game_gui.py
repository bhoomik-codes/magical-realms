import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json
import os
import sys
import threading
import queue
import time
import subprocess
import io
import locale
import re

# Set UTF-8 as default encoding
if sys.platform == "win32":
    # Force UTF-8 encoding on Windows
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    # Set locale to user's default
    locale.setlocale(locale.LC_ALL, '')

# Force the environment to use UTF-8
os.environ["PYTHONIOENCODING"] = "utf-8"

class GameState:
    """Tracks the current state of the game to update the UI accordingly"""
    TITLE_SCREEN = "title"
    CHARACTER_MANAGEMENT = "character_management"
    MAIN_MENU = "main_menu"
    COMBAT = "combat"
    HUNTING = "hunting"
    INVENTORY = "inventory"
    SHOP = "shop"
    BOSS_FIGHT = "boss_fight"
    
    def __init__(self):
        self.current_state = self.TITLE_SCREEN
        self.player_stats = {}
        self.enemy_stats = {}
        self.combat_log = []
        self.shop_items = []
        self.inventory_items = []
        self.available_characters = []
        self.current_prompt = ""
        self.expected_choices = []
        self.last_output = ""

class RPGGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Magical Realms")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Use ttkbootstrap as the style engine with dark theme
        self.style = ttk.Style(theme="darkly")
        
        # Track game state
        self.game_state = GameState()
        
        # Create message queue for handling game outputs
        self.msg_queue = queue.Queue()
        self.input_queue = queue.Queue()
        
        # Create the main frame with 3 sections
        self.create_layout()
        
        # Game process variables
        self.game_process = None
        self.stdout_thread = None
        self.stderr_thread = None
        
        # Prompt patterns for detecting expected inputs
        self.prompt_patterns = {
            r"Enter your choice \((\d+)-(\d+)\)": self.create_number_buttons,
            r"Choose (?:a |an |your |)(?:option|choice|action)(?: \((\d+)-(\d+)\))?": self.create_number_buttons,
            r"(?:Do you want to |Would you like to |)(?:continue|try again|play again)\? \(y/n\)": self.create_yes_no_buttons,
            r"(?:Choose |Select |)(?:your |)(?:character|class)(?: type| class)?(?: \((\d+)-(\d+)\))?": self.create_character_buttons,
            r"Enter (?:character |player |)name:": None,  # No buttons for name input
            r"Enter a number(?: between (\d+)(?:.*)and (\d+))?:": self.create_number_range_buttons,
            r"Press enter to continue": self.create_continue_button
        }
        
        # Common action buttons for different game states
        self.common_actions = {
            GameState.MAIN_MENU: [
                ("Hunt Monsters", "1"),
                ("Inventory", "2"),
                ("Shop", "3"),
                ("Character Status", "4"),
                ("Face Boss", "5"),
                ("Save Character", "6"),
                ("Exit", "7")
            ],
            GameState.CHARACTER_MANAGEMENT: [
                ("Create Character", "1"),
                ("Load Character", "2"),
                ("Save Character", "3"),
                ("Delete Character", "4"),
                ("Return", "5")
            ],
            GameState.HUNTING: [
                ("Continue Hunting", "1"),
                ("Return to Menu", "2")
            ],
            GameState.COMBAT: [
                ("Attack", "1"),
                ("Special Attack", "2"),
                ("Block", "3"),
                ("Dodge", "4"),
                ("Use Item", "5"),
                ("Run", "6")
            ]
        }
        
        # Start the game
        self.start_game()
        
        # Set up periodic handlers
        self.check_msg_queue()
        self.update_status_area()
    
    def create_layout(self):
        """Create the three main sections of the GUI"""
        # Main container with padding
        self.main_container = ttk.Frame(self.root, padding=15)
        self.main_container.pack(fill=BOTH, expand=True)
        
        # Top section: Title area
        self.title_frame = ttk.Frame(self.main_container)
        self.title_frame.pack(fill=X)
        
        self.title_label = ttk.Label(
            self.title_frame,
            text="🎮 MAGICAL REALMS 🎮",
            font=("Segoe UI", 20, "bold"),
            bootstyle="light"
        )
        self.title_label.pack(pady=(0, 10))
        
        # Create a frame for the two main sections (game area and status panel)
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(fill=BOTH, expand=True)
        
        # Configure grid weights
        self.content_frame.grid_columnconfigure(0, weight=7)  # Game area gets 70% width
        self.content_frame.grid_columnconfigure(1, weight=3)  # Status panel gets 30% width
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # 1. Game Area (Left side - 70%)
        self.game_area = ttk.Frame(self.content_frame, padding=10, bootstyle="dark")
        self.game_area.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Game area title
        self.game_area_title = ttk.Label(
            self.game_area,
            text="Welcome to your Adventure",
            font=("Segoe UI", 14, "bold"),
            bootstyle="light",
            anchor="w"
        )
        self.game_area_title.pack(fill=X, pady=(0, 10))
        
        # Game text display area with scrollbar
        self.game_text_frame = ttk.Frame(self.game_area)
        self.game_text_frame.pack(fill=BOTH, expand=True)
        
        self.game_text = tk.Text(
            self.game_text_frame,
            wrap=WORD,
            font=("Segoe UI", 11),
            bg="#1e1e1e",
            fg="#ffffff",
            padx=10,
            pady=10,
            state=DISABLED,
            height=20
        )
        self.game_text.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.game_text_scrollbar = ttk.Scrollbar(self.game_text_frame, command=self.game_text.yview)
        self.game_text_scrollbar.pack(side=RIGHT, fill=Y)
        self.game_text.config(yscrollcommand=self.game_text_scrollbar.set)
        
        # Action buttons area (replaces plain input for common actions)
        self.action_buttons_frame = ttk.Frame(self.game_area, padding=(0, 10, 0, 0))
        self.action_buttons_frame.pack(fill=X)
        
        # This frame will hold dynamically created action buttons
        self.dynamic_buttons_frame = ttk.Frame(self.action_buttons_frame)
        self.dynamic_buttons_frame.pack(fill=X, pady=(0, 10))
        
        # 2. Status Panel (Right side - 30%)
        self.status_panel = ttk.Frame(self.content_frame, padding=10, bootstyle="secondary")
        self.status_panel.grid(row=0, column=1, sticky="nsew")
        
        # Status panel title
        self.status_panel_title = ttk.Label(
            self.status_panel,
            text="Character Status",
            font=("Segoe UI", 14, "bold"),
            bootstyle="light",
            anchor="w"
        )
        self.status_panel_title.pack(fill=X, pady=(0, 10))
        
        # Character status section
        self.char_status_frame = ttk.Frame(self.status_panel, padding=(0, 5))
        self.char_status_frame.pack(fill=X)
        
        # Character information will be populated here
        self.player_info = ttk.Label(
            self.char_status_frame,
            text="No character loaded",
            font=("Segoe UI", 11),
            bootstyle="light",
            justify=LEFT,
            anchor="w"
        )
        self.player_info.pack(fill=X, pady=5)
        
        # Stats display
        self.stats_frame = ttk.Frame(self.status_panel)
        self.stats_frame.pack(fill=X, pady=10)
        
        # Create progress bars for HP, Mana, XP
        self.create_stat_bars()
        
        # Enemy section (hidden by default, shown during combat)
        self.enemy_frame = ttk.Frame(self.status_panel, padding=(0, 10))
        self.enemy_frame.pack(fill=X)
        
        self.enemy_header = ttk.Label(
            self.enemy_frame,
            text="Enemy",
            font=("Segoe UI", 14, "bold"),
            bootstyle="danger",
            anchor="w"
        )
        self.enemy_header.pack(fill=X)
        
        self.enemy_info = ttk.Label(
            self.enemy_frame,
            text="No enemy present",
            font=("Segoe UI", 11),
            bootstyle="light",
            justify=LEFT,
            anchor="w"
        )
        self.enemy_info.pack(fill=X, pady=5)
        
        self.enemy_hp_frame = ttk.Frame(self.enemy_frame)
        self.enemy_hp_frame.pack(fill=X, pady=2)
        
        self.enemy_hp_label = ttk.Label(
            self.enemy_hp_frame,
            text="HP:",
            font=("Segoe UI", 10),
            width=8,
            bootstyle="light",
            anchor="w"
        )
        self.enemy_hp_label.pack(side=LEFT)
        
        self.enemy_hp_bar = ttk.Progressbar(
            self.enemy_hp_frame,
            orient=HORIZONTAL,
            length=100,
            mode='determinate',
            bootstyle="danger"
        )
        self.enemy_hp_bar.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        
        self.enemy_hp_text = ttk.Label(
            self.enemy_hp_frame,
            text="0/0",
            font=("Segoe UI", 10),
            width=7,
            bootstyle="light",
            anchor="e"
        )
        self.enemy_hp_text.pack(side=RIGHT)
        
        # Initially hide enemy frame
        self.enemy_frame.pack_forget()
        
        # 3. Input Section (Bottom)
        self.input_frame = ttk.Frame(self.main_container, padding=(0, 10, 0, 0))
        self.input_frame.pack(fill=X)
        
        # Input prompt label
        self.prompt_label = ttk.Label(
            self.input_frame,
            text="Command:",
            font=("Segoe UI", 11),
            bootstyle="light"
        )
        self.prompt_label.pack(side=LEFT, padx=(0, 5))
        
        # Text input
        self.input_entry = ttk.Entry(
            self.input_frame,
            font=("Segoe UI", 11),
            bootstyle="default"
        )
        self.input_entry.pack(side=LEFT, fill=X, expand=True)
        self.input_entry.bind("<Return>", self.on_enter)
        self.input_entry.focus_set()
        
        # Submit button
        self.submit_button = ttk.Button(
            self.input_frame,
            text="Submit",
            command=self.on_submit,
            bootstyle="primary"
        )
        self.submit_button.pack(side=LEFT, padx=(5, 0))
        
        # Status bar
        self.status_bar = ttk.Label(
            self.root,
            text="Ready",
            bootstyle="light",
            anchor=W,
            padding=(5, 2)
        )
        self.status_bar.pack(side=BOTTOM, fill=X)
    
    def create_stat_bars(self):
        """Create the character stat bars"""
        # HP Bar
        self.hp_frame = ttk.Frame(self.stats_frame)
        self.hp_frame.pack(fill=X, pady=2)
        
        self.hp_label = ttk.Label(
            self.hp_frame,
            text="HP:",
            font=("Segoe UI", 10),
            width=8,
            bootstyle="light",
            anchor="w"
        )
        self.hp_label.pack(side=LEFT)
        
        self.hp_bar = ttk.Progressbar(
            self.hp_frame,
            orient=HORIZONTAL,
            length=100,
            mode='determinate',
            bootstyle="danger"
        )
        self.hp_bar.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        
        self.hp_text = ttk.Label(
            self.hp_frame,
            text="0/0",
            font=("Segoe UI", 10),
            width=7,
            bootstyle="light",
            anchor="e"
        )
        self.hp_text.pack(side=RIGHT)
        
        # Mana Bar
        self.mana_frame = ttk.Frame(self.stats_frame)
        self.mana_frame.pack(fill=X, pady=2)
        
        self.mana_label = ttk.Label(
            self.mana_frame,
            text="Mana:",
            font=("Segoe UI", 10),
            width=8,
            bootstyle="light",
            anchor="w"
        )
        self.mana_label.pack(side=LEFT)
        
        self.mana_bar = ttk.Progressbar(
            self.mana_frame,
            orient=HORIZONTAL,
            length=100,
            mode='determinate',
            bootstyle="info"
        )
        self.mana_bar.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        
        self.mana_text = ttk.Label(
            self.mana_frame,
            text="0/0",
            font=("Segoe UI", 10),
            width=7,
            bootstyle="light",
            anchor="e"
        )
        self.mana_text.pack(side=RIGHT)
        
        # XP Bar
        self.xp_frame = ttk.Frame(self.stats_frame)
        self.xp_frame.pack(fill=X, pady=2)
        
        self.xp_label = ttk.Label(
            self.xp_frame,
            text="XP:",
            font=("Segoe UI", 10),
            width=8,
            bootstyle="light",
            anchor="w"
        )
        self.xp_label.pack(side=LEFT)
        
        self.xp_bar = ttk.Progressbar(
            self.xp_frame,
            orient=HORIZONTAL,
            length=100,
            mode='determinate',
            bootstyle="success"
        )
        self.xp_bar.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        
        self.xp_text = ttk.Label(
            self.xp_frame,
            text="0/0",
            font=("Segoe UI", 10),
            width=7,
            bootstyle="light",
            anchor="e"
        )
        self.xp_text.pack(side=RIGHT)
        
        # Additional player stats
        self.extra_stats_frame = ttk.Frame(self.stats_frame, padding=(0, 5))
        self.extra_stats_frame.pack(fill=X)
        
        self.extra_stats = ttk.Label(
            self.extra_stats_frame,
            text="Level: 1\nAttack: 0\nDefense: 0\nGold: 0",
            font=("Segoe UI", 10),
            bootstyle="light",
            justify=LEFT,
            anchor="w"
        )
        self.extra_stats.pack(fill=X)
    
    def start_game(self):
        """Start the RPG game as a subprocess"""
        self.update_status("Starting game...")
        
        # Set environment variables to force UTF-8 encoding
        env_copy = os.environ.copy()
        env_copy["PYTHONIOENCODING"] = "utf-8"
        
        # On Windows, try to set the console mode to handle UTF-8
        if sys.platform == "win32":
            self.append_text("Running on Windows - Using UTF-8 mode\n", "info")
            os.system("chcp 65001 > NUL")  # Set Windows console to UTF-8
        
        try:
            # Use sys.executable to ensure we use the same Python interpreter
            # Start the game in a new process with UTF-8 encoding
            self.game_process = subprocess.Popen(
                [sys.executable, "rpg_game.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace',  # Replace any characters that can't be decoded
                env=env_copy
            )
            
            # Set up threads to read stdout and stderr
            self.stdout_thread = threading.Thread(
                target=self.read_output,
                args=(self.game_process.stdout, "normal")
            )
            self.stderr_thread = threading.Thread(
                target=self.read_output,
                args=(self.game_process.stderr, "error")
            )
            
            # Set up input writer thread
            self.input_thread = threading.Thread(
                target=self.write_input
            )
            
            # Start threads
            self.stdout_thread.daemon = True
            self.stderr_thread.daemon = True
            self.input_thread.daemon = True
            
            self.stdout_thread.start()
            self.stderr_thread.start()
            self.input_thread.start()
            
            # Monitor process state
            self.monitor_process()
            
            self.update_status("Game running")
        except Exception as e:
            self.append_text(f"Error starting game: {str(e)}\n", "error")
            self.update_status("Error starting game")
    
    def read_output(self, pipe, tag):
        """Thread to read output from the game process with encoding error handling"""
        for line in iter(pipe.readline, ''):
            try:
                # Try to clean the line of any problematic characters
                clean_line = line.encode('utf-8', errors='replace').decode('utf-8')
                
                # Process game output for UI updates
                self.process_game_output(clean_line, tag)
                
                # Add to message queue for display
                self.msg_queue.put((tag, clean_line))
                
                # Save last line for detecting prompts
                self.game_state.last_output = clean_line
            except Exception as e:
                # If there's an encoding error, report it but continue
                self.msg_queue.put(("error", f"[Output encoding error: {str(e)}]\n"))
        
        pipe.close()
    
    def process_game_output(self, text, tag):
        """Process game output to update UI state and detect prompts for dynamic buttons"""
        # Detect game state changes
        if "WELCOME TO THE ENHANCED RPG ADVENTURE" in text:
            self.game_state.current_state = GameState.TITLE_SCREEN
            self.update_game_area_title("Welcome to Magical Realms")
        
        elif "CHARACTER MANAGEMENT" in text:
            self.game_state.current_state = GameState.CHARACTER_MANAGEMENT
            self.update_game_area_title("Character Management")
            self.update_action_buttons_for_state(GameState.CHARACTER_MANAGEMENT)
        
        elif "MAIN MENU" in text:
            self.game_state.current_state = GameState.MAIN_MENU
            self.update_game_area_title("Main Menu")
            self.update_action_buttons_for_state(GameState.MAIN_MENU)
        
        elif "COMBAT INITIATED" in text or "BOSS FIGHT" in text:
            if "BOSS FIGHT" in text:
                self.game_state.current_state = GameState.BOSS_FIGHT
                self.update_game_area_title("Boss Fight")
            else:
                self.game_state.current_state = GameState.COMBAT
                self.update_game_area_title("Combat")
            
            # Show enemy frame during combat
            self.enemy_frame.pack(fill=X, pady=10, after=self.stats_frame)
            self.update_action_buttons_for_state(GameState.COMBAT)
        
        elif "HUNTING GROUNDS" in text:
            self.game_state.current_state = GameState.HUNTING
            self.update_game_area_title("Hunting Grounds")
            self.update_action_buttons_for_state(GameState.HUNTING)
        
        elif "INVENTORY MANAGEMENT" in text:
            self.game_state.current_state = GameState.INVENTORY
            self.update_game_area_title("Inventory Management")
        
        elif "WELCOME TO THE SHOP" in text:
            self.game_state.current_state = GameState.SHOP
            self.update_game_area_title("Shop")
        
        # Check for prompts that might need action buttons
        for pattern, button_creator in self.prompt_patterns.items():
            match = re.search(pattern, text)
            if match:
                self.game_state.current_prompt = text.strip()
                if button_creator:
                    # Extract any groups from the regex match (like min/max numbers)
                    groups = match.groups()
                    # Update expected input options
                    if len(groups) >= 2 and groups[0] and groups[1]:
                        min_val = int(groups[0])
                        max_val = int(groups[1])
                        self.game_state.expected_choices = list(range(min_val, max_val + 1))
                    # Create appropriate buttons
                    button_creator(*groups if groups else ())
                break
        
        # Extract character info from character creation output
        if "Character created:" in text:
            lines = text.split('\n')
            character_info = {}
            for i, line in enumerate(lines):
                if "Character created:" in line:
                    name_line = line.split("Character created:")[1].strip()
                    if "the" in name_line:
                        parts = name_line.split("the")
                        character_info["name"] = parts[0].strip()
                        character_info["class"] = parts[1].strip()
                    
                    # Look for stats in the next few lines
                    for j in range(i+1, min(i+10, len(lines))):
                        stat_line = lines[j]
                        if "HP:" in stat_line:
                            hp_parts = stat_line.split("HP:")[1].split()[0]
                            if "/" in hp_parts:
                                current_hp, max_hp = hp_parts.split("/")
                                character_info["hp"] = int(current_hp)
                                character_info["max_hp"] = int(max_hp)
                        
                        if "Mana:" in stat_line:
                            mana_parts = stat_line.split("Mana:")[1].split()[0]
                            if "/" in mana_parts:
                                current_mana, max_mana = mana_parts.split("/")
                                character_info["mana"] = int(current_mana)
                                character_info["max_mana"] = int(max_mana)
                        
                        if "Level:" in stat_line:
                            level_parts = stat_line.split("Level:")[1].split()[0]
                            character_info["level"] = int(level_parts)
                        
                        if "Attack:" in stat_line:
                            attack_parts = stat_line.split("Attack:")[1].split()[0]
                            character_info["attack"] = int(attack_parts)
                        
                        if "Defense:" in stat_line:
                            defense_parts = stat_line.split("Defense:")[1].split()[0]
                            character_info["defense"] = int(defense_parts)
                        
                        if "XP:" in stat_line:
                            xp_parts = stat_line.split("XP:")[1].split()[0]
                            if "/" in xp_parts:
                                current_xp, max_xp = xp_parts.split("/")
                                character_info["xp"] = int(current_xp)
                                character_info["xp_to_level"] = int(max_xp)
                        
                        if "Gold:" in stat_line:
                            gold_parts = stat_line.split("Gold:")[1].split()[0]
                            character_info["gold"] = int(gold_parts)
            
            # If we found character info, update the game state
            if character_info and "name" in character_info:
                self.game_state.player_stats.update(character_info)
                self.update_player_stats()
        
        # Extract character info from regular status display
        if "Level:" in text and "HP:" in text and "Mana:" in text:
            self.parse_character_status(text)
        
        # Extract enemy info during combat
        if "Enemy:" in text and "HP:" in text:
            self.parse_enemy_status(text)
        
        # Handle combat end
        if "Combat has ended" in text or "You defeated" in text:
            # Hide enemy frame after combat
            self.enemy_frame.pack_forget()
        
        # Check for rewards or items
        if "You found" in text or "You received" in text or "You gained" in text:
            # Highlight rewards
            tag = "reward"
    
    def update_action_buttons_for_state(self, state):
        """Update action buttons based on the current game state"""
        if state in self.common_actions:
            self.clear_dynamic_buttons()
            actions = self.common_actions[state]
            self.create_custom_buttons(actions)
    
    def clear_dynamic_buttons(self):
        """Clear all dynamically created buttons"""
        for widget in self.dynamic_buttons_frame.winfo_children():
            widget.destroy()
    
    def create_number_buttons(self, min_val=None, max_val=None):
        """Create numbered buttons based on prompt"""
        self.clear_dynamic_buttons()
        
        # Get number range if provided, otherwise use 1-9 as default
        try:
            start = int(min_val) if min_val is not None else 1
            end = int(max_val) if max_val is not None else 9
        except (ValueError, TypeError):
            start, end = 1, 9
        
        # Create a frame for the buttons with grid layout
        button_grid = ttk.Frame(self.dynamic_buttons_frame)
        button_grid.pack(fill=X)
        
        # Add buttons in a grid (up to 5 per row)
        row, col = 0, 0
        max_cols = 5
        
        for i in range(start, end + 1):
            button = ttk.Button(
                button_grid,
                text=str(i),
                command=lambda num=i: self.send_input(str(num)),
                width=5,
                bootstyle="primary"
            )
            button.grid(row=row, column=col, padx=2, pady=2)
            
            # Update row and column for next button
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def create_yes_no_buttons(self, *args):
        """Create Yes/No buttons for yes/no prompts"""
        self.clear_dynamic_buttons()
        
        button_frame = ttk.Frame(self.dynamic_buttons_frame)
        button_frame.pack(fill=X)
        
        yes_button = ttk.Button(
            button_frame,
            text="Yes (y)",
            command=lambda: self.send_input("y"),
            bootstyle="success",
            width=10
        )
        yes_button.pack(side=LEFT, padx=5)
        
        no_button = ttk.Button(
            button_frame,
            text="No (n)",
            command=lambda: self.send_input("n"),
            bootstyle="danger",
            width=10
        )
        no_button.pack(side=LEFT, padx=5)
    
    def create_character_buttons(self, *args):
        """Create buttons for character class selection"""
        self.clear_dynamic_buttons()
        
        button_frame = ttk.Frame(self.dynamic_buttons_frame)
        button_frame.pack(fill=X)
        
        # Add buttons for the three main character classes
        barbarian_button = ttk.Button(
            button_frame,
            text="Barbarian (1)",
            command=lambda: self.send_input("1"),
            bootstyle="danger",
            width=12
        )
        barbarian_button.pack(side=LEFT, padx=5)
        
        archer_button = ttk.Button(
            button_frame,
            text="Archer (2)",
            command=lambda: self.send_input("2"),
            bootstyle="success",
            width=12
        )
        archer_button.pack(side=LEFT, padx=5)
        
        mage_button = ttk.Button(
            button_frame,
            text="Mage (3)",
            command=lambda: self.send_input("3"),
            bootstyle="info",
            width=12
        )
        mage_button.pack(side=LEFT, padx=5)
    
    def create_number_range_buttons(self, min_val=None, max_val=None):
        """Create buttons for a range of numbers"""
        self.clear_dynamic_buttons()
        
        try:
            start = int(min_val) if min_val is not None else 1
            end = int(max_val) if max_val is not None else 10
        except (ValueError, TypeError):
            start, end = 1, 10
        
        # If range is too large, just show min, mid, and max
        if end - start > 10:
            button_frame = ttk.Frame(self.dynamic_buttons_frame)
            button_frame.pack(fill=X)
            
            min_button = ttk.Button(
                button_frame,
                text=f"Min ({start})",
                command=lambda: self.send_input(str(start)),
                bootstyle="secondary",
                width=10
            )
            min_button.pack(side=LEFT, padx=5)
            
            mid = (start + end) // 2
            mid_button = ttk.Button(
                button_frame,
                text=f"Mid ({mid})",
                command=lambda: self.send_input(str(mid)),
                bootstyle="secondary",
                width=10
            )
            mid_button.pack(side=LEFT, padx=5)
            
            max_button = ttk.Button(
                button_frame,
                text=f"Max ({end})",
                command=lambda: self.send_input(str(end)),
                bootstyle="secondary",
                width=10
            )
            max_button.pack(side=LEFT, padx=5)
        else:
            # Create a grid of number buttons
            self.create_number_buttons(min_val, max_val)
    
    def create_continue_button(self, *args):
        """Create a continue button"""
        self.clear_dynamic_buttons()
        
        button_frame = ttk.Frame(self.dynamic_buttons_frame)
        button_frame.pack(fill=X)
        
        continue_button = ttk.Button(
            button_frame,
            text="Continue",
            command=lambda: self.send_input(""),
            bootstyle="primary",
            width=15
        )
        continue_button.pack(side=TOP, pady=5)
    
    def create_custom_buttons(self, actions):
        """Create custom action buttons from a list of (label, command) tuples"""
        self.clear_dynamic_buttons()
        
        # Create a frame for the buttons with grid layout
        button_grid = ttk.Frame(self.dynamic_buttons_frame)
        button_grid.pack(fill=X)
        
        # Add buttons in a grid (up to 4 per row)
        row, col = 0, 0
        max_cols = 4
        
        for label, command in actions:
            button = ttk.Button(
                button_grid,
                text=f"{label} ({command})",
                command=lambda cmd=command: self.send_input(cmd),
                bootstyle="primary"
            )
            button.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
            
            # Update row and column for next button
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Configure grid to expand buttons
        for i in range(min(max_cols, len(actions))):
            button_grid.grid_columnconfigure(i, weight=1)
    
    def send_input(self, text):
        """Send input to the game process via the input queue"""
        if text:
            # Add user input to the display
            self.append_text(f"> {text}\n", "input")
            
            # Send to the game process
            self.input_queue.put(text)
            
            # Clear the input entry
            self.input_entry.delete(0, tk.END)
    
    def parse_character_status(self, text):
        """Parse character status information from game output"""
        try:
            # More robust approach using line-by-line parsing
            lines = text.split('\n')
            character_info = {}
            
            # First check if this is a character status display
            status_found = False
            character_name = None
            character_class = None
            
            for line in lines:
                # Check for character name and class
                if "Status of" in line:
                    status_found = True
                    name_parts = line.split("Status of")[1].strip()
                    if "the" in name_parts:
                        name_class = name_parts.split("the")
                        character_info["name"] = name_class[0].strip()
                        character_info["class"] = name_class[1].strip()
                    elif ":" in name_parts:
                        name_class = name_parts.split(":")
                        character_info["name"] = name_class[0].strip()
                        if len(name_class) > 1 and "(" in name_class[1]:
                            class_part = name_class[1].strip()
                            class_name = class_part.split("(")[0].strip()
                            character_info["class"] = class_name
                
                # Check for each stat line
                if "HP:" in line:
                    hp_part = line.split("HP:")[1].split()[0].strip()
                    if "/" in hp_part:
                        current_hp, max_hp = hp_part.split("/")
                        try:
                            character_info["hp"] = int(current_hp)
                            character_info["max_hp"] = int(max_hp)
                        except ValueError:
                            # Handle case where values might have special characters
                            current_hp = ''.join(c for c in current_hp if c.isdigit())
                            max_hp = ''.join(c for c in max_hp if c.isdigit())
                            character_info["hp"] = int(current_hp or 0)
                            character_info["max_hp"] = int(max_hp or 100)
                
                if "Mana:" in line:
                    mana_part = line.split("Mana:")[1].split()[0].strip()
                    if "/" in mana_part:
                        current_mana, max_mana = mana_part.split("/")
                        try:
                            character_info["mana"] = int(current_mana)
                            character_info["max_mana"] = int(max_mana)
                        except ValueError:
                            current_mana = ''.join(c for c in current_mana if c.isdigit())
                            max_mana = ''.join(c for c in max_mana if c.isdigit())
                            character_info["mana"] = int(current_mana or 0)
                            character_info["max_mana"] = int(max_mana or 50)
                
                if "Level:" in line:
                    try:
                        level = line.split("Level:")[1].split()[0].strip()
                        character_info["level"] = int(level)
                    except (ValueError, IndexError):
                        # Extract just the digits
                        level_part = line.split("Level:")[1].strip()
                        level = ''.join(c for c in level_part if c.isdigit())
                        character_info["level"] = int(level or 1)
                
                if "XP:" in line:
                    xp_part = line.split("XP:")[1].split()[0].strip()
                    if "/" in xp_part:
                        current_xp, max_xp = xp_part.split("/")
                        try:
                            character_info["xp"] = int(current_xp)
                            character_info["xp_to_level"] = int(max_xp)
                        except ValueError:
                            current_xp = ''.join(c for c in current_xp if c.isdigit())
                            max_xp = ''.join(c for c in max_xp if c.isdigit())
                            character_info["xp"] = int(current_xp or 0)
                            character_info["xp_to_level"] = int(max_xp or 100)
                
                if "Attack:" in line:
                    try:
                        attack = line.split("Attack:")[1].split()[0].strip()
                        character_info["attack"] = int(attack)
                    except (ValueError, IndexError):
                        attack_part = line.split("Attack:")[1].strip()
                        attack = ''.join(c for c in attack_part if c.isdigit())
                        character_info["attack"] = int(attack or 20)
                
                if "Defense:" in line:
                    try:
                        defense = line.split("Defense:")[1].split()[0].strip()
                        character_info["defense"] = int(defense)
                    except (ValueError, IndexError):
                        defense_part = line.split("Defense:")[1].strip()
                        defense = ''.join(c for c in defense_part if c.isdigit())
                        character_info["defense"] = int(defense or 10)
                
                if "Gold:" in line:
                    try:
                        gold = line.split("Gold:")[1].split()[0].strip()
                        character_info["gold"] = int(gold)
                    except (ValueError, IndexError):
                        gold_part = line.split("Gold:")[1].strip()
                        gold = ''.join(c for c in gold_part if c.isdigit())
                        character_info["gold"] = int(gold or 0)
            
            # If we found any data, update the game state
            if character_info and len(character_info) > 2:  # At least a few stats
                self.game_state.player_stats.update(character_info)
                self.update_player_stats()
        except Exception as e:
            print(f"Error parsing character status: {str(e)}")
    
    def parse_enemy_status(self, text):
        """Parse enemy status information from game output"""
        try:
            # More robust line-by-line parsing
            lines = text.split('\n')
            enemy_info = {}
            
            for line in lines:
                # Look for enemy name
                if "Enemy:" in line or "Monster:" in line or "Boss:" in line:
                    name_line = line
                    if "Enemy:" in line:
                        name_part = line.split("Enemy:")[1].strip()
                    elif "Monster:" in line:
                        name_part = line.split("Monster:")[1].strip()
                    elif "Boss:" in line:
                        name_part = line.split("Boss:")[1].strip()
                    else:
                        continue
                        
                    # Handle potential formatting with HP on same line
                    if "HP:" in name_part:
                        enemy_name = name_part.split("HP:")[0].strip()
                    else:
                        enemy_name = name_part.strip()
                    
                    enemy_info["name"] = enemy_name
                
                # Extract HP values
                if "HP:" in line:
                    # Only process HP if this line contains enemy HP (not player HP)
                    if "Enemy:" in line or "Monster:" in line or "Boss:" in line or (
                            "name" in enemy_info and enemy_info["name"] in line):
                        
                        hp_part = line.split("HP:")[1].split()[0].strip()
                        if "/" in hp_part:
                            try:
                                current_hp, max_hp = hp_part.split("/")
                                enemy_info["hp"] = int(current_hp)
                                enemy_info["max_hp"] = int(max_hp)
                            except ValueError:
                                # Handle non-numeric values
                                current_hp = ''.join(c for c in current_hp if c.isdigit())
                                max_hp = ''.join(c for c in max_hp if c.isdigit())
                                if current_hp and max_hp:
                                    enemy_info["hp"] = int(current_hp)
                                    enemy_info["max_hp"] = int(max_hp)
            
            # If we got valid enemy info, update the game state
            if enemy_info and "name" in enemy_info and "hp" in enemy_info:
                self.game_state.enemy_stats.update(enemy_info)
                self.update_enemy_stats()
                
                # Show enemy frame during combat if it's not already visible
                if self.enemy_frame.winfo_ismapped() == 0:
                    self.enemy_frame.pack(fill=X, pady=10, after=self.stats_frame)
        except Exception as e:
            print(f"Error parsing enemy status: {str(e)}")
    
    def update_player_stats(self):
        """Update the player stats display with current values"""
        stats = self.game_state.player_stats
        if not stats:
            return
        
        # Update player info
        player_info = f"{stats.get('name', 'Unknown')} - Level {stats.get('level', 1)}"
        if 'class' in stats:
            player_info += f" {stats.get('class', '')}"
        self.player_info.config(text=player_info)
        
        # Update HP bar
        current_hp = stats.get('hp', 0)
        max_hp = stats.get('max_hp', 100)
        if max_hp > 0:
            hp_percent = (current_hp / max_hp) * 100
            self.hp_bar['value'] = hp_percent
        self.hp_text.config(text=f"{current_hp}/{max_hp}")
        
        # Update Mana bar
        current_mana = stats.get('mana', 0)
        max_mana = stats.get('max_mana', 50)
        if max_mana > 0:
            mana_percent = (current_mana / max_mana) * 100
            self.mana_bar['value'] = mana_percent
        self.mana_text.config(text=f"{current_mana}/{max_mana}")
        
        # Update XP bar
        current_xp = stats.get('xp', 0)
        xp_to_level = stats.get('xp_to_level', 100)
        if xp_to_level > 0:
            xp_percent = (current_xp / xp_to_level) * 100
            self.xp_bar['value'] = xp_percent
        self.xp_text.config(text=f"{current_xp}/{xp_to_level}")
        
        # Update extra stats
        extra_stats_text = f"Level: {stats.get('level', 1)}\n"
        extra_stats_text += f"Attack: {stats.get('attack', 0)}\n"
        extra_stats_text += f"Defense: {stats.get('defense', 0)}\n"
        extra_stats_text += f"Gold: {stats.get('gold', 0)}"
        self.extra_stats.config(text=extra_stats_text)
    
    def update_enemy_stats(self):
        """Update the enemy stats display with current values"""
        stats = self.game_state.enemy_stats
        if not stats:
            return
        
        # Update enemy info
        enemy_name = stats.get('name', 'Unknown Enemy')
        self.enemy_info.config(text=enemy_name)
        
        # Update enemy HP bar
        current_hp = stats.get('hp', 0)
        max_hp = stats.get('max_hp', 100)
        if max_hp > 0:
            hp_percent = (current_hp / max_hp) * 100
            self.enemy_hp_bar['value'] = hp_percent
        self.enemy_hp_text.config(text=f"{current_hp}/{max_hp}")
    
    def write_input(self):
        """Thread to write input to the game process"""
        while True:
            try:
                # Get input from the queue
                input_text = self.input_queue.get()
                
                # Check if process is still running and stdin is available
                if (self.game_process and self.game_process.poll() is None 
                    and self.game_process.stdin is not None):
                    try:
                        # Try to encode the text as UTF-8 and handle errors
                        safe_text = input_text.encode('utf-8', errors='replace').decode('utf-8')
                        
                        # Write to stdin and flush
                        self.game_process.stdin.write(safe_text + "\n")
                        self.game_process.stdin.flush()
                    except Exception as e:
                        self.msg_queue.put(("error", f"Input encoding error: {str(e)}\n"))
                        
                # Mark as done
                self.input_queue.task_done()
            except Exception as e:
                print(f"Input error: {str(e)}")
                time.sleep(0.1)
    
    def monitor_process(self):
        """Check if the game process is still running"""
        if self.game_process:
            returncode = self.game_process.poll()
            if returncode is not None:
                # Process has ended
                if returncode != 0:
                    self.msg_queue.put(("error", f"\nGame exited with error code {returncode}\n"))
                else:
                    self.msg_queue.put(("info", "\nGame has ended. You can close this window.\n"))
                self.update_status("Game ended")
                return
        
        # Check again after 500ms
        self.root.after(500, self.monitor_process)
    
    def check_msg_queue(self):
        """Check for messages in the queue and update the text widget"""
        try:
            while True:
                tag, text = self.msg_queue.get_nowait()
                self.append_text(text, tag)
                self.msg_queue.task_done()
        except queue.Empty:
            pass
        
        # Schedule to check again after 100ms
        self.root.after(100, self.check_msg_queue)
    
    def append_text(self, text, tag=None):
        """Append text to the output widget with error handling"""
        try:
            # Determine appropriate tag based on content
            if not tag or tag == "normal":
                # Try to determine the appropriate tag based on content
                if "ERROR" in text or "Error" in text:
                    tag = "error"
                elif "WARNING" in text or "Warning" in text:
                    tag = "warning"
                elif "Welcome" in text or "======" in text or text.isupper():
                    tag = "header"
                elif "You found" in text or "received" in text or "gained" in text:
                    tag = "reward"
                elif "attacking" in text or "damage" in text or "hit" in text:
                    tag = "combat"
            
            # Clean text
            if text.startswith(">"):
                tag = "input"
            
            # Enable editing
            self.game_text.config(state=NORMAL)
            
            # If text is getting too long, remove oldest lines
            if float(self.game_text.index('end-1c').split('.')[0]) > 1000:
                self.game_text.delete('1.0', '500.0')
            
            # Configure text tags
            self.game_text.tag_configure("header", foreground="#ffcc00", font=("Segoe UI", 12, "bold"))
            self.game_text.tag_configure("error", foreground="#ff6b6b")
            self.game_text.tag_configure("warning", foreground="#ffff6b")
            self.game_text.tag_configure("info", foreground="#6bff6b")
            self.game_text.tag_configure("input", foreground="#6b9fff")
            self.game_text.tag_configure("combat", foreground="#ff9966")
            self.game_text.tag_configure("reward", foreground="#cc99ff")
            
            # Insert the text with the appropriate tag
            self.game_text.insert(tk.END, text, tag if tag else "")
            self.game_text.see(tk.END)
            
            # Disable editing
            self.game_text.config(state=DISABLED)
        except Exception as e:
            print(f"Error appending text: {str(e)}")
    
    def update_status_area(self):
        """Update the status area periodically"""
        # Update game area title based on game state
        current_state = self.game_state.current_state
        
        if current_state == GameState.TITLE_SCREEN:
            self.game_area_title.config(text="Welcome to Magical Realms")
        elif current_state == GameState.CHARACTER_MANAGEMENT:
            self.game_area_title.config(text="Character Management")
        elif current_state == GameState.MAIN_MENU:
            self.game_area_title.config(text="Main Menu")
        elif current_state == GameState.COMBAT:
            self.game_area_title.config(text="Combat")
        elif current_state == GameState.HUNTING:
            self.game_area_title.config(text="Hunting Grounds")
        elif current_state == GameState.INVENTORY:
            self.game_area_title.config(text="Inventory Management")
        elif current_state == GameState.SHOP:
            self.game_area_title.config(text="Shop")
        elif current_state == GameState.BOSS_FIGHT:
            self.game_area_title.config(text="Boss Fight")
        
        # Update stats
        self.update_player_stats()
        
        # Check if in combat
        if current_state in [GameState.COMBAT, GameState.BOSS_FIGHT]:
            if self.enemy_frame.winfo_ismapped() == 0:
                self.enemy_frame.pack(fill=X, pady=10, after=self.stats_frame)
            self.update_enemy_stats()
        else:
            if self.enemy_frame.winfo_ismapped() == 1:
                self.enemy_frame.pack_forget()
        
        # Scan last output for common prompts
        for pattern, button_creator in self.prompt_patterns.items():
            if re.search(pattern, self.game_state.last_output):
                match = re.search(pattern, self.game_state.last_output)
                if button_creator and match:
                    groups = match.groups()
                    button_creator(*groups if groups else ())
                break
        
        # Check again after 1000ms
        self.root.after(1000, self.update_status_area)
    
    def update_game_area_title(self, title):
        """Update the game area title"""
        self.game_area_title.config(text=title)
    
    def on_enter(self, event):
        """Handle Enter key in the input field"""
        self.on_submit()
    
    def on_submit(self):
        """Process user input"""
        text = self.input_entry.get().strip()
        if text:
            self.send_input(text)
    
    def update_status(self, message):
        """Update the status bar"""
        self.status_bar.config(text=message)
    
    def on_closing(self):
        """Handle window closing"""
        if self.game_process and self.game_process.poll() is None:
            try:
                self.game_process.terminate()
            except:
                pass
        self.root.destroy()

def main():
    root = ttk.Window("RPG Adventure Game", themename="darkly")
    app = RPGGameGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()