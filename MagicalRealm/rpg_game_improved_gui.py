import tkinter as tk
from tkinter import ttk, font as tkfont, messagebox
import json
import os
import sys
import threading
import queue
import time
import subprocess
import io
import locale

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

class RPGGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RPG Adventure Game")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.root.configure(bg="#2e2e2e")
        
        # Track game state
        self.game_state = GameState()
        
        # Create custom fonts
        self.title_font = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        self.header_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.normal_font = tkfont.Font(family="Segoe UI", size=11)
        self.status_font = tkfont.Font(family="Segoe UI", size=10)
        self.button_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        
        # Create message queue for handling game outputs
        self.msg_queue = queue.Queue()
        self.input_queue = queue.Queue()
        
        # Create the main frame with 3 sections
        self.create_layout()
        
        # Set up color scheme
        self.configure_colors()
        
        # Game process variables
        self.game_process = None
        self.stdout_thread = None
        self.stderr_thread = None
        
        # Start the game
        self.start_game()
        
        # Set up periodic handlers
        self.check_msg_queue()
        self.update_status_area()
    
    def create_layout(self):
        """Create the three main sections of the GUI"""
        # Main container with padding
        self.main_container = tk.Frame(self.root, bg="#2e2e2e", padx=15, pady=15)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Top section: Title area
        self.title_frame = tk.Frame(self.main_container, bg="#2e2e2e")
        self.title_frame.pack(fill=tk.X)
        
        self.title_label = tk.Label(
            self.title_frame,
            text="🎮 RPG ADVENTURE GAME 🎮",
            font=self.title_font,
            fg="#ffffff",
            bg="#2e2e2e"
        )
        self.title_label.pack(pady=(0, 10))
        
        # Create a frame for the two main sections (game area and status panel)
        self.content_frame = tk.Frame(self.main_container, bg="#2e2e2e")
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        self.content_frame.grid_columnconfigure(0, weight=7)  # Game area gets 70% width
        self.content_frame.grid_columnconfigure(1, weight=3)  # Status panel gets 30% width
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # 1. Game Area (Left side - 70%)
        self.game_area = tk.Frame(self.content_frame, bg="#1a1a1a", padx=10, pady=10)
        self.game_area.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Game area title
        self.game_area_title = tk.Label(
            self.game_area,
            text="Welcome to your Adventure",
            font=self.header_font,
            fg="#ffffff",
            bg="#1a1a1a",
            anchor="w"
        )
        self.game_area_title.pack(fill=tk.X, pady=(0, 10))
        
        # Game text display area with scrollbar
        self.game_text_frame = tk.Frame(self.game_area, bg="#1a1a1a")
        self.game_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.game_text = tk.Text(
            self.game_text_frame,
            wrap=tk.WORD,
            font=self.normal_font,
            bg="#111111",
            fg="#ffffff",
            padx=10,
            pady=10,
            state=tk.DISABLED,
            height=20
        )
        self.game_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.game_text_scrollbar = tk.Scrollbar(self.game_text_frame, command=self.game_text.yview)
        self.game_text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.game_text.config(yscrollcommand=self.game_text_scrollbar.set)
        
        # Game buttons area
        self.game_buttons_frame = tk.Frame(self.game_area, bg="#1a1a1a", pady=10)
        self.game_buttons_frame.pack(fill=tk.X)
        
        # 2. Status Panel (Right side - 30%)
        self.status_panel = tk.Frame(self.content_frame, bg="#252525", padx=10, pady=10)
        self.status_panel.grid(row=0, column=1, sticky="nsew")
        
        # Status panel title
        self.status_panel_title = tk.Label(
            self.status_panel,
            text="Character Status",
            font=self.header_font,
            fg="#ffffff",
            bg="#252525",
            anchor="w"
        )
        self.status_panel_title.pack(fill=tk.X, pady=(0, 10))
        
        # Character status section
        self.char_status_frame = tk.Frame(self.status_panel, bg="#252525", pady=5)
        self.char_status_frame.pack(fill=tk.X)
        
        # Character information will be populated here
        self.player_info = tk.Label(
            self.char_status_frame,
            text="No character loaded",
            font=self.normal_font,
            fg="#ffffff",
            bg="#252525",
            justify=tk.LEFT,
            anchor="w"
        )
        self.player_info.pack(fill=tk.X, pady=5)
        
        # Stats display
        self.stats_frame = tk.Frame(self.status_panel, bg="#252525")
        self.stats_frame.pack(fill=tk.X, pady=10)
        
        # Create progress bars for HP, Mana, XP
        self.create_stat_bars()
        
        # Enemy section (hidden by default, shown during combat)
        self.enemy_frame = tk.Frame(self.status_panel, bg="#252525", pady=10)
        self.enemy_frame.pack(fill=tk.X)
        
        self.enemy_header = tk.Label(
            self.enemy_frame,
            text="Enemy",
            font=self.header_font,
            fg="#ff6b6b",
            bg="#252525",
            anchor="w"
        )
        self.enemy_header.pack(fill=tk.X)
        
        self.enemy_info = tk.Label(
            self.enemy_frame,
            text="No enemy present",
            font=self.normal_font,
            fg="#ffffff",
            bg="#252525",
            justify=tk.LEFT,
            anchor="w"
        )
        self.enemy_info.pack(fill=tk.X, pady=5)
        
        self.enemy_hp_frame = tk.Frame(self.enemy_frame, bg="#252525")
        self.enemy_hp_frame.pack(fill=tk.X, pady=2)
        
        self.enemy_hp_label = tk.Label(
            self.enemy_hp_frame,
            text="HP:",
            font=self.status_font,
            fg="#ffffff",
            bg="#252525",
            width=8,
            anchor="w"
        )
        self.enemy_hp_label.pack(side=tk.LEFT)
        
        self.enemy_hp_bar = ttk.Progressbar(
            self.enemy_hp_frame,
            orient=tk.HORIZONTAL,
            length=100,
            mode='determinate',
            style="enemy.Horizontal.TProgressbar"
        )
        self.enemy_hp_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.enemy_hp_text = tk.Label(
            self.enemy_hp_frame,
            text="0/0",
            font=self.status_font,
            fg="#ffffff",
            bg="#252525",
            width=7,
            anchor="e"
        )
        self.enemy_hp_text.pack(side=tk.RIGHT)
        
        # Initially hide enemy frame
        self.enemy_frame.pack_forget()
        
        # 3. Input Section (Bottom)
        self.input_frame = tk.Frame(self.main_container, bg="#2e2e2e", pady=10)
        self.input_frame.pack(fill=tk.X)
        
        # Input prompt label
        self.prompt_label = tk.Label(
            self.input_frame,
            text="Command:",
            font=self.normal_font,
            fg="#ffffff",
            bg="#2e2e2e"
        )
        self.prompt_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Text input
        self.input_entry = tk.Entry(
            self.input_frame,
            font=self.normal_font,
            bg="#111111",
            fg="#ffffff",
            insertbackground="#ffffff"
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self.on_enter)
        self.input_entry.focus_set()
        
        # Submit button
        self.submit_button = tk.Button(
            self.input_frame,
            text="Submit",
            command=self.on_submit,
            bg="#4a6cd4",
            fg="#ffffff",
            activebackground="#395ab9",
            activeforeground="#ffffff",
            font=self.button_font
        )
        self.submit_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#333333",
            fg="#cccccc"
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_stat_bars(self):
        """Create the character stat bars"""
        # HP Bar
        self.hp_frame = tk.Frame(self.stats_frame, bg="#252525")
        self.hp_frame.pack(fill=tk.X, pady=2)
        
        self.hp_label = tk.Label(
            self.hp_frame,
            text="HP:",
            font=self.status_font,
            fg="#ffffff",
            bg="#252525",
            width=8,
            anchor="w"
        )
        self.hp_label.pack(side=tk.LEFT)
        
        self.hp_bar = ttk.Progressbar(
            self.hp_frame,
            orient=tk.HORIZONTAL,
            length=100,
            mode='determinate',
            style="hp.Horizontal.TProgressbar"
        )
        self.hp_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.hp_text = tk.Label(
            self.hp_frame,
            text="0/0",
            font=self.status_font,
            fg="#ffffff",
            bg="#252525",
            width=7,
            anchor="e"
        )
        self.hp_text.pack(side=tk.RIGHT)
        
        # Mana Bar
        self.mana_frame = tk.Frame(self.stats_frame, bg="#252525")
        self.mana_frame.pack(fill=tk.X, pady=2)
        
        self.mana_label = tk.Label(
            self.mana_frame,
            text="Mana:",
            font=self.status_font,
            fg="#ffffff",
            bg="#252525",
            width=8,
            anchor="w"
        )
        self.mana_label.pack(side=tk.LEFT)
        
        self.mana_bar = ttk.Progressbar(
            self.mana_frame,
            orient=tk.HORIZONTAL,
            length=100,
            mode='determinate',
            style="mana.Horizontal.TProgressbar"
        )
        self.mana_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.mana_text = tk.Label(
            self.mana_frame,
            text="0/0",
            font=self.status_font,
            fg="#ffffff",
            bg="#252525",
            width=7,
            anchor="e"
        )
        self.mana_text.pack(side=tk.RIGHT)
        
        # XP Bar
        self.xp_frame = tk.Frame(self.stats_frame, bg="#252525")
        self.xp_frame.pack(fill=tk.X, pady=2)
        
        self.xp_label = tk.Label(
            self.xp_frame,
            text="XP:",
            font=self.status_font,
            fg="#ffffff",
            bg="#252525",
            width=8,
            anchor="w"
        )
        self.xp_label.pack(side=tk.LEFT)
        
        self.xp_bar = ttk.Progressbar(
            self.xp_frame,
            orient=tk.HORIZONTAL,
            length=100,
            mode='determinate',
            style="xp.Horizontal.TProgressbar"
        )
        self.xp_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.xp_text = tk.Label(
            self.xp_frame,
            text="0/0",
            font=self.status_font,
            fg="#ffffff",
            bg="#252525",
            width=7,
            anchor="e"
        )
        self.xp_text.pack(side=tk.RIGHT)
        
        # Additional player stats
        self.extra_stats_frame = tk.Frame(self.stats_frame, bg="#252525", pady=5)
        self.extra_stats_frame.pack(fill=tk.X)
        
        self.extra_stats = tk.Label(
            self.extra_stats_frame,
            text="Level: 1\nAttack: 0\nDefense: 0\nGold: 0",
            font=self.status_font,
            fg="#ffffff",
            bg="#252525",
            justify=tk.LEFT,
            anchor="w"
        )
        self.extra_stats.pack(fill=tk.X)
        
    def configure_colors(self):
        """Configure custom colors for widgets"""
        style = ttk.Style()
        
        # HP bar style (red)
        style.configure(
            "hp.Horizontal.TProgressbar",
            troughcolor="#331111",
            background="#cc3333",
            thickness=15
        )
        
        # Mana bar style (blue)
        style.configure(
            "mana.Horizontal.TProgressbar",
            troughcolor="#111133",
            background="#3333cc",
            thickness=15
        )
        
        # XP bar style (green)
        style.configure(
            "xp.Horizontal.TProgressbar",
            troughcolor="#113311",
            background="#33cc33",
            thickness=15
        )
        
        # Enemy HP bar style (dark red)
        style.configure(
            "enemy.Horizontal.TProgressbar",
            troughcolor="#331111",
            background="#990000",
            thickness=15
        )
        
        # Configure text tags
        self.game_text.tag_configure("header", foreground="#ffcc00", font=self.header_font)
        self.game_text.tag_configure("info", foreground="#6bff6b")
        self.game_text.tag_configure("error", foreground="#ff6b6b")
        self.game_text.tag_configure("warning", foreground="#ffff6b")
        self.game_text.tag_configure("input", foreground="#6b9fff")
        self.game_text.tag_configure("combat", foreground="#ff9966")
        self.game_text.tag_configure("reward", foreground="#cc99ff")
    
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
            except Exception as e:
                # If there's an encoding error, report it but continue
                self.msg_queue.put(("error", f"[Output encoding error: {str(e)}]\n"))
        
        pipe.close()
    
    def process_game_output(self, text, tag):
        """Process game output to update UI state"""
        # Detect game state changes
        if "WELCOME TO THE ENHANCED RPG ADVENTURE" in text:
            self.game_state.current_state = GameState.TITLE_SCREEN
            self.update_game_area_title("Welcome to RPG Adventure")
        
        elif "CHARACTER MANAGEMENT" in text:
            self.game_state.current_state = GameState.CHARACTER_MANAGEMENT
            self.update_game_area_title("Character Management")
        
        elif "MAIN MENU" in text:
            self.game_state.current_state = GameState.MAIN_MENU
            self.update_game_area_title("Main Menu")
        
        elif "COMBAT INITIATED" in text or "BOSS FIGHT" in text:
            if "BOSS FIGHT" in text:
                self.game_state.current_state = GameState.BOSS_FIGHT
                self.update_game_area_title("Boss Fight")
            else:
                self.game_state.current_state = GameState.COMBAT
                self.update_game_area_title("Combat")
            
            # Show enemy frame during combat
            self.enemy_frame.pack(fill=tk.X, pady=10, after=self.stats_frame)
        
        elif "HUNTING GROUNDS" in text:
            self.game_state.current_state = GameState.HUNTING
            self.update_game_area_title("Hunting Grounds")
        
        elif "INVENTORY MANAGEMENT" in text:
            self.game_state.current_state = GameState.INVENTORY
            self.update_game_area_title("Inventory Management")
        
        elif "WELCOME TO THE SHOP" in text:
            self.game_state.current_state = GameState.SHOP
            self.update_game_area_title("Shop")
        
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
                    self.enemy_frame.pack(fill=tk.X, pady=10, after=self.stats_frame)
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
            self.game_text.config(state=tk.NORMAL)
            
            # If text is getting too long, remove oldest lines
            if float(self.game_text.index('end-1c').split('.')[0]) > 1000:
                self.game_text.delete('1.0', '500.0')
            
            # Insert the text with the appropriate tag
            self.game_text.insert(tk.END, text, tag if tag else "")
            self.game_text.see(tk.END)
            
            # Disable editing
            self.game_text.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Error appending text: {str(e)}")
    
    def update_status_area(self):
        """Update the status area periodically"""
        # Update game area title based on game state
        current_state = self.game_state.current_state
        
        if current_state == GameState.TITLE_SCREEN:
            self.game_area_title.config(text="Welcome to RPG Adventure")
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
                self.enemy_frame.pack(fill=tk.X, pady=10, after=self.stats_frame)
            self.update_enemy_stats()
        else:
            if self.enemy_frame.winfo_ismapped() == 1:
                self.enemy_frame.pack_forget()
        
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
            # Add user input to the display
            self.append_text(f"> {text}\n", "input")
            
            # Send to the game process
            self.input_queue.put(text)
            
            # Clear the input field
            self.input_entry.delete(0, tk.END)
    
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
    root = tk.Tk()
    app = RPGGameGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()