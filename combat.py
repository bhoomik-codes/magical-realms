import random
import time
from items import Consumable

class Combat:
    """Handles combat between a player and villain"""
    
    def __init__(self, player, villain):
        self.player = player
        self.villain = villain
        self.turn = 0  # 0 for player's turn, 1 for villain's turn
        self.turn_count = 0  # Track how many turns have passed
        
    def start_combat(self):
        """Initialize combat"""
        print("\n" + "="*50)
        print(f"⚔️  COMBAT BEGINS: {self.player.emoji} {self.player.name} vs {self.villain.emoji} {self.villain.name}  ⚔️")
        print("="*50 + "\n")
        
        print(self.player.status())
        print(self.villain.status())
        print("\n")
        
    def player_turn(self):
        """Handle player's turn"""
        print("\n" + "-"*50)
        print(f"{self.player.emoji} {self.player.name}'s turn!")
        print("-"*50)
        
        action = self.get_player_action()
        self.execute_player_action(action)
        
        # Reset block status if not actively blocking this turn
        if action != "3" and self.player.is_blocking:
            self.player.is_blocking = False
            
        time.sleep(1)
        
    def villain_turn(self):
        """Handle villain's turn"""
        print("\n" + "-"*50)
        print(f"{self.villain.emoji} {self.villain.name}'s turn!")
        print("-"*50)
        
        # Simple AI for villain
        action = self.get_villain_action()
        self.execute_villain_action(action)
        
        # Reset block status if not actively blocking this turn
        if action != 3 and self.villain.is_blocking:
            self.villain.is_blocking = False
            
        time.sleep(1)
        
    def get_player_action(self):
        """Get player's chosen action"""
        print("\nChoose your action:")
        print("1. Attack ⚔️")
        print("2. Special Attack 🔥")
        print("3. Block 🛡️")
        print("4. Dodge 🌪️")
        print("5. Use Item 🎒")
        
        # Special case for Mage class - Add healing option
        if self.player.__class__.__name__ == "Mage":
            print("6. Heal ✨")
            valid_actions = ["1", "2", "3", "4", "5", "6"]
        else:
            valid_actions = ["1", "2", "3", "4", "5"]
            
        while True:
            action = input("Enter your choice (1-{}): ".format(len(valid_actions)))
            if action in valid_actions:
                return action
            print("Invalid choice. Try again.")
            
    def execute_player_action(self, action):
        """Execute the player's chosen action"""
        if action == "1":  # Attack
            damage = self.player.attack(self.villain)
            print(f"{self.player.emoji} {self.player.name} attacks for {damage} damage!")
            
        elif action == "2":  # Special Attack
            # Different message based on class
            class_name = self.player.__class__.__name__
            
            if class_name == "Barbarian":
                special_name = "Rage Attack"
            elif class_name == "Archer":
                special_name = "Precision Shot"
            elif class_name == "Mage":
                special_name = "Fireball"
            else:
                special_name = "Special Attack"
                
            damage = self.player.special_attack(self.villain)
            if damage > 0:
                print(f"{self.player.emoji} {self.player.name}'s {special_name} deals {damage} damage!")
                
        elif action == "3":  # Block
            self.player.block()
            print(f"{self.player.emoji} {self.player.name} takes a defensive stance! 🛡️")
            
        elif action == "4":  # Dodge
            self.player.dodge()
            print(f"{self.player.emoji} {self.player.name} prepares to dodge the next attack! 🌪️")
            
        elif action == "5":  # Use Item
            self.use_item()
            
        elif action == "6" and self.player.__class__.__name__ == "Mage":  # Heal (Mage only)
            self.player.heal()
            
    def use_item(self):
        """Let the player choose and use an item from inventory"""
        if not hasattr(self.player, 'inventory'):
            from items import Inventory
            self.player.inventory = Inventory()
            # Add some starter items for testing
            from items import HealthPotion, ManaPotion, StrengthElixir
            self.player.inventory.add_item(HealthPotion("small"))
            self.player.inventory.add_item(ManaPotion("small"))
            
        consumables = self.player.inventory.get_consumables()
        if not consumables:
            print(f"{self.player.emoji} {self.player.name} has no usable items!")
            return
            
        print("\nChoose an item to use:")
        for i, item in enumerate(consumables, 1):
            print(f"{i}. {item}")
            
        while True:
            try:
                choice = input(f"Enter your choice (1-{len(consumables)}, or 0 to cancel): ")
                if choice == "0":
                    print("Canceled item use.")
                    return
                    
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(consumables):
                    item = consumables[choice_idx]
                    if item.use(self.player):
                        self.player.inventory.remove_item(item)
                    return
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Please enter a number.")
            
    def get_villain_action(self):
        """Determine villain's action based on simple AI"""
        # Villain will try to heal when low on health and block when very low
        if self.villain.hp < self.villain.max_hp * 0.2:
            if random.random() < 0.7:  # 70% chance to block when very low health
                return 3  # Block
                
        if self.villain.hp < self.villain.max_hp * 0.4:
            if self.villain.__class__.__name__ == "DarkMage" and self.villain.mana >= 30 and random.random() < 0.6:
                return 4  # Heal if DarkMage and has enough mana
                
        # Use special attack if enough mana and with higher probability at high health
        mana_threshold = 15
        if self.villain.__class__.__name__ == "DarkMage":
            mana_threshold = 30
        elif self.villain.__class__.__name__ == "DarkArcher":
            mana_threshold = 25
        else:
            mana_threshold = 20
            
        special_attack_chance = 0.4
        if self.villain.hp > self.villain.max_hp * 0.7:
            special_attack_chance = 0.6  # More aggressive when healthy
            
        if self.villain.mana >= mana_threshold and random.random() < special_attack_chance:
            return 2  # Special attack
            
        # Default to basic attack
        return 1
        
    def execute_villain_action(self, action):
        """Execute the villain's chosen action"""
        if action == 1:  # Attack
            damage = self.villain.attack(self.player)
            print(f"{self.villain.emoji} {self.villain.name} attacks for {damage} damage!")
            
        elif action == 2:  # Special Attack
            # Different message based on class
            class_name = self.villain.__class__.__name__
            
            if class_name == "DarkKnight":
                special_name = "Dark Slash"
            elif class_name == "DarkArcher":
                special_name = "Poison Arrow"
            elif class_name == "DarkMage":
                special_name = "Dark Energy Blast"
            else:
                special_name = "Special Attack"
                
            damage = self.villain.special_attack(self.player)
            if damage > 0:
                print(f"{self.villain.emoji} {self.villain.name}'s {special_name} deals {damage} damage!")
                
        elif action == 3:  # Block
            self.villain.block()
            print(f"{self.villain.emoji} {self.villain.name} takes a defensive stance! 🛡️")
            
        elif action == 4 and self.villain.__class__.__name__ == "DarkMage":  # DarkMage heal
            # Simple heal for Dark Mage
            if self.villain.mana >= 30:
                heal_amount = 30 + random.randint(0, 10)
                self.villain.mana -= 30
                old_hp = self.villain.hp
                self.villain.hp = min(self.villain.max_hp, self.villain.hp + heal_amount)
                actual_heal = self.villain.hp - old_hp
                print(f"{self.villain.emoji} {self.villain.name} casts Dark Healing and recovers {actual_heal} HP! 🌑✨")
            else:
                # Fallback to attack if not enough mana
                damage = self.villain.attack(self.player)
                print(f"{self.villain.emoji} {self.villain.name} attacks for {damage} damage!")
                
    def check_combat_end(self):
        """Check if combat has ended"""
        if not self.player.is_alive():
            print("\n" + "="*50)
            print(f"💀 {self.player.emoji} {self.player.name} has been defeated! 💀")
            print(f"{self.villain.emoji} {self.villain.name} wins with {self.villain.hp} HP remaining!")
            print("="*50)
            return True
            
        if not self.villain.is_alive():
            print("\n" + "="*50)
            print(f"🏆 {self.player.emoji} {self.player.name} is victorious! 🏆")
            print(f"{self.villain.emoji} {self.villain.name} has been defeated!")
            print("="*50)
            return True
            
        return False
        
    def display_status(self):
        """Display current status of combatants"""
        print("\n" + "."*50)
        print(self.player.status())
        print(self.villain.status())
        print("."*50 + "\n")
        
    def execute_turn(self):
        """Execute a single turn of combat"""
        if self.turn == 0:
            self.player_turn()
            self.turn = 1
        else:
            self.villain_turn()
            self.turn = 0
            
        self.display_status()
        return self.check_combat_end()
