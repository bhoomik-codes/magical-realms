import random
import time
import os
from characters import Barbarian, Archer, Mage, DarkKnight, DarkArcher, DarkMage
from combat import Combat
from monsters import get_monster_by_level
from items import Inventory, generate_random_item, HealthPotion, ManaPotion, Shop
from db_utils import save_character, load_character, get_all_characters, delete_character

class Game:
    """Main game class that manages the Magical Realms game flow with enhanced features"""
    
    def __init__(self):
        self.player = None
        self.villain = None
        
    def display_intro(self):
        """Display game introduction"""
        print("\n" + "="*60)
        print("🎮  WELCOME TO MAGICAL REALMS  🎮")
        print("="*60)
        print("Embark on an epic journey as a brave adventurer!")
        print("Face dangerous monsters, collect items, and become stronger.")
        print("-"*60)
        print("• Hunt monsters to gain XP and items")
        print("• Use your inventory to equip gear and use potions")
        print("• Level up to become more powerful")
        print("• Face boss monsters for rare rewards")
        print("="*60 + "\n")
        
    def create_player(self):
        """Let the player choose their character class"""
        print("Choose your character class:")
        print("1. Barbarian 🪓 - High HP and attack, but low defense and mana")
        print("   Special: Rage Attack - Powerful but costly attack")
        print()
        print("2. Archer 🏹 - Balanced stats with consistent damage")
        print("   Special: Precision Shot - Can sometimes ignore target's defense")
        print()
        print("3. Mage 🧙 - High mana and special attack, but low HP and defense")
        print("   Special: Fireball - High damage spell")
        print("   Unique: Healing spell to restore HP")
        
        while True:
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == "1":
                name = input("Enter your Barbarian's name: ")
                self.player = Barbarian(name)
                break
            elif choice == "2":
                name = input("Enter your Archer's name: ")
                self.player = Archer(name)
                break
            elif choice == "3":
                name = input("Enter your Mage's name: ")
                self.player = Mage(name)
                break
            else:
                print("Invalid choice. Please try again.")
                
        # Character already has inventory initialized in the Character class
        # Just add starter items
        self.player.inventory.add_item(HealthPotion("small"))
        self.player.inventory.add_item(ManaPotion("small"))
        self.player.inventory.gold = 50
        
        print(f"\nWelcome, {self.player.emoji} {self.player.name} the {self.player.__class__.__name__}!")
        print(self.player.status())
        print("You've received some starter items and 50 gold coins.")
        
    def create_villain(self):
        """Create a random villain for the player to face"""
        villain_classes = [DarkKnight, DarkArcher, DarkMage]
        villain_names = [
            "Grimshade", "Doomfang", "Nightblade", "Shadowreaper", "Vileblood", 
            "Bonecrush", "Deathwhisper", "Stormbane", "Dreadlord", "Netherclaw"
        ]
        
        villain_class = random.choice(villain_classes)
        villain_name = random.choice(villain_names)
        
        self.villain = villain_class(villain_name)
        
        # Match villain level to player level
        for _ in range(1, self.player.level):
            # Scale villain stats with player level
            self.villain.max_hp += random.randint(10, 15)
            self.villain.hp = self.villain.max_hp
            self.villain.max_mana += random.randint(5, 10)
            self.villain.mana = self.villain.max_mana
            self.villain.base_attack += random.randint(2, 3)
            self.villain.defense += random.randint(1, 2)
        
        # Map villain class to player class for more interesting combat
        if villain_class == DarkKnight and isinstance(self.player, Barbarian):
            print(f"\nA dark warrior approaches, drawn to your battle prowess...")
        elif villain_class == DarkArcher and isinstance(self.player, Archer):
            print(f"\nA shadowy figure with a bow steps out, challenging your archery...")
        elif villain_class == DarkMage and isinstance(self.player, Mage):
            print(f"\nA corrupted spellcaster seeks to test their dark magic against yours...")
        else:
            print(f"\nA fearsome enemy appears before you...")
            
        time.sleep(1)
        print(f"You face {self.villain.emoji} {self.villain.name} the {self.villain.__class__.__name__}!")
        print(self.villain.status())
        
    def start_combat(self, monster=None):
        """Begin combat between player and opponent (villain or monster)"""
        opponent = monster if monster else self.villain
        combat = Combat(self.player, opponent)
        combat.start_combat()
        
        combat_ended = False
        while not combat_ended:
            combat_ended = combat.execute_turn()
            
        victory = self.player.is_alive()
        
        if victory and monster:
            # Calculate rewards based on monster level and if it's a boss
            xp_reward = monster.level * 25
            if monster.is_boss:
                xp_reward *= 2
                
            # Grant experience
            level_up = self.player.gain_xp(xp_reward)
            
            # Add gold
            self.player.inventory.gold += monster.gold_reward
            print(f"💰 You received {monster.gold_reward} gold!")
            
            # Chance to get item drops
            if random.random() < 0.6 or monster.is_boss:  # 60% chance, always for bosses
                item = generate_random_item(self.player.level, monster.is_boss)
                if self.player.inventory.add_item(item):
                    print(f"🎁 You found {item.emoji} {item.name}!")
                else:
                    print("🎒 Your inventory is full! You couldn't pick up the item.")
        
        return victory
        
    def hunt_monsters(self):
        """Hunt for monsters to gain XP and items"""
        print("\n" + "="*50)
        print("🏕️  HUNTING GROUNDS  🏕️")
        print("="*50)
        
        # Offer different hunting areas based on player level
        print("Choose a hunting area:")
        
        hunting_areas = []
        
        # Always available
        hunting_areas.append(("Forest Outskirts", "Easy monsters for beginners", 1))
        
        # Unlock at level 3
        if self.player.level >= 3:
            hunting_areas.append(("Deep Woods", "Moderate challenge with better rewards", 3))
            
        # Unlock at level 5
        if self.player.level >= 5:
            hunting_areas.append(("Ancient Ruins", "Difficult monsters with good rewards", 5))
            
        # Unlock at level 8
        if self.player.level >= 8:
            hunting_areas.append(("Dark Caverns", "Very challenging with excellent rewards", 8))
            
        # Special boss area
        if self.player.level >= 5:
            hunting_areas.append(("Dragon's Lair", "⚠️ BOSS FIGHT - Extremely Difficult ⚠️", 10))
        
        for i, (area, desc, _) in enumerate(hunting_areas, 1):
            print(f"{i}. {area} - {desc}")
            
        print(f"0. Return to Main Menu")
        
        while True:
            choice = input("\nEnter your choice: ")
            
            try:
                choice_idx = int(choice)
                if choice_idx == 0:
                    return
                    
                if 1 <= choice_idx <= len(hunting_areas):
                    area_name, _, difficulty = hunting_areas[choice_idx - 1]
                    break
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Please enter a number.")
        
        # Now enter a continuous hunting loop until player decides to return home
        continue_hunting = True
        
        while continue_hunting and self.player.is_alive():
            print(f"\nYou venture deeper into the {area_name}...")
            time.sleep(1)
            
            # Force boss for Dragon's Lair
            force_boss = (area_name == "Dragon's Lair")
            
            # Generate appropriate monster
            monster = get_monster_by_level(difficulty, force_boss)
            
            print(f"You encounter {monster.emoji} {monster.name}!")
            
            # Ask if player wants to fight or run
            while True:
                action = input("\nDo you want to (f)ight, (r)un, or return (g)o home? (f/r/g): ").lower()
                if action == 'f':
                    victory = self.start_combat(monster)
                    
                    # If player died in combat, exit the hunting loop
                    if not victory:
                        continue_hunting = False
                    
                    break
                elif action == 'r':
                    escape_chance = 0.7  # 70% chance to escape
                    if random.random() < escape_chance:
                        print("You managed to escape!")
                    else:
                        print("You couldn't escape! The monster attacks!")
                        victory = self.start_combat(monster)
                        
                        # If player died in combat, exit the hunting loop
                        if not victory:
                            continue_hunting = False
                    
                    break
                elif action == 'g':
                    print("You decide to head back to safety.")
                    continue_hunting = False
                    break
                else:
                    print("Invalid choice. Enter 'f' to fight, 'r' to run, or 'g' to go home.")
            
            # Show post-combat options if player is still hunting
            if continue_hunting and self.player.is_alive():
                input("\nPress Enter to continue hunting...")
        
        # Final return to main menu
        if self.player.is_alive():
            input("\nPress Enter to return to main menu...")
                
    def manage_inventory(self):
        """Manage player's inventory, equipment, and items"""
        while True:
            print("\n" + "="*50)
            print("🎒  INVENTORY MANAGEMENT  🎒")
            print("="*50)
            
            # Display gold
            print(f"💰 Gold: {self.player.inventory.gold}")
            
            # Display current equipment if any
            print("\nEquipped Items:")
            if hasattr(self.player, 'equipment') and self.player.equipment:
                for slot, item in self.player.equipment.items():
                    print(f"{slot.capitalize()}: {item.emoji} {item.name} ({item.description})")
            else:
                print("No items equipped.")
                
            # Inventory menu options
            print("\nInventory Options:")
            print("1. View All Items")
            print("2. Use Item")
            print("3. Equip Item")
            print("4. Unequip Item")
            print("5. Return to Main Menu")
            
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == "1":  # View items
                if not self.player.inventory.items:
                    print("Your inventory is empty.")
                else:
                    print("\nInventory Items:")
                    self.player.inventory.display()
                    
            elif choice == "2":  # Use item
                consumables = self.player.inventory.get_consumables()
                if not consumables:
                    print("You don't have any usable items.")
                    continue
                    
                print("\nChoose an item to use:")
                for i, item in enumerate(consumables, 1):
                    print(f"{i}. {item}")
                    
                try:
                    item_choice = input(f"Enter your choice (1-{len(consumables)}, or 0 to cancel): ")
                    if item_choice == "0":
                        continue
                        
                    item_idx = int(item_choice) - 1
                    if 0 <= item_idx < len(consumables):
                        item = consumables[item_idx]
                        if item.use(self.player):
                            self.player.inventory.remove_item(item)
                    else:
                        print("Invalid choice.")
                except ValueError:
                    print("Please enter a number.")
                    
            elif choice == "3":  # Equip item
                equipment = self.player.inventory.get_equipment()
                if not equipment:
                    print("You don't have any equipment to equip.")
                    continue
                    
                print("\nChoose an item to equip:")
                for i, item in enumerate(equipment, 1):
                    print(f"{i}. {item}")
                    
                try:
                    equip_choice = input(f"Enter your choice (1-{len(equipment)}, or 0 to cancel): ")
                    if equip_choice == "0":
                        continue
                        
                    equip_idx = int(equip_choice) - 1
                    if 0 <= equip_idx < len(equipment):
                        item = equipment[equip_idx]
                        item.equip(self.player)
                    else:
                        print("Invalid choice.")
                except ValueError:
                    print("Please enter a number.")
                    
            elif choice == "4":  # Unequip item
                if not hasattr(self.player, 'equipment') or not self.player.equipment:
                    print("You don't have any equipment to unequip.")
                    continue
                    
                print("\nChoose an item to unequip:")
                equipment_list = list(self.player.equipment.values())
                for i, item in enumerate(equipment_list, 1):
                    print(f"{i}. {item.emoji} {item.name} ({item.slot})")
                    
                try:
                    unequip_choice = input(f"Enter your choice (1-{len(equipment_list)}, or 0 to cancel): ")
                    if unequip_choice == "0":
                        continue
                        
                    unequip_idx = int(unequip_choice) - 1
                    if 0 <= unequip_idx < len(equipment_list):
                        item = equipment_list[unequip_idx]
                        item.unequip(self.player)
                        self.player.inventory.add_item(item)
                    else:
                        print("Invalid choice.")
                except ValueError:
                    print("Please enter a number.")
                    
            elif choice == "5":  # Return to main menu
                break
                
    def show_character_status(self):
        """Display detailed character status"""
        print("\n" + "="*50)
        print(f"👤  CHARACTER PROFILE: {self.player.emoji} {self.player.name}  👤")
        print("="*50)
        
        # Basic stats
        print(f"Class: {self.player.__class__.__name__}")
        print(f"Level: {self.player.level}")
        print(f"XP: {self.player.xp}/{self.player.xp_to_level}")
        print(f"HP: {self.player.hp}/{self.player.max_hp} ❤️")
        print(f"Mana: {self.player.mana}/{self.player.max_mana} 🔮")
        print(f"Attack: {self.player.base_attack} ⚔️")
        print(f"Defense: {self.player.defense} 🛡️")
        print(f"Luck: {self.player.luck} ⭐")
        
        # Equipment
        print("\nEquipment:")
        if hasattr(self.player, 'equipment') and self.player.equipment:
            for slot, item in self.player.equipment.items():
                print(f"  {slot.capitalize()}: {item.emoji} {item.name}")
        else:
            print("  No equipment")
            
        # Inventory summary
        print("\nInventory:")
        print(f"  Gold: {self.player.inventory.gold} 💰")
        print(f"  Items: {len(self.player.inventory.items)}/{self.player.inventory.max_size}")
        
        input("\nPress Enter to continue...")
        
    def face_boss(self):
        """Face a challenging boss appropriate for player's level"""
        print("\n" + "="*50)
        print("⚠️  BOSS CHALLENGE  ⚠️")
        print("="*50)
        
        print("You've decided to face a powerful boss!")
        print("These challenging enemies drop better rewards but are much stronger.")
        print("Make sure you're prepared before continuing.")
        
        proceed = input("\nDo you want to proceed? (y/n): ").lower()
        if proceed != 'y':
            return
            
        # Create a boss based on player level
        boss = get_monster_by_level(self.player.level, True)
        
        print(f"\nYou approach {boss.emoji} {boss.name}...")
        time.sleep(1)
        print(f"The powerful {boss.emoji} {boss.name} stands before you!")
        print(boss.status())
        
        proceed = input("\nDo you still want to fight? (y/n): ").lower()
        if proceed != 'y':
            print("You decide to retreat and prepare more...")
            return
            
        # Start boss combat
        victory = self.start_combat(boss)
        
        if victory:
            # Extra rewards for boss victory
            extra_gold = random.randint(50, 100) * self.player.level
            self.player.inventory.gold += extra_gold
            print(f"💰 You found an additional {extra_gold} gold!")
            
            # Guaranteed rare item
            rare_item = generate_random_item(self.player.level + 2, True)
            if self.player.inventory.add_item(rare_item):
                print(f"🎁 You found a rare item: {rare_item.emoji} {rare_item.name}!")
            else:
                print("🎒 Your inventory is full! You couldn't pick up the rare item.")
                
            # Increase player's luck after defeating a boss
            luck_gain = random.randint(2, 5)
            self.player.luck += luck_gain
            print(f"⭐ Your fortune increases! (+{luck_gain} Luck)")
                
        input("\nPress Enter to continue...")
        
    def visit_shop(self):
        """Visit the shop to buy and sell items"""
        # Initialize shop with player's level and luck
        luck = 0
        if hasattr(self.player, 'luck'):
            luck = self.player.luck
        
        shop = Shop(level=self.player.level, luck=luck)
        
        print("\n" + "="*60)
        print("🛒  MERCHANT'S SHOP  🛒")
        print("="*60)
        print(f"Welcome, {self.player.emoji} {self.player.name}! What would you like to do?")
        print(f"You have {self.player.inventory.gold} gold coins. 💰")
        
        while True:
            print("\nShop Options:")
            print("1. Browse Items")
            print("2. Sell Items")
            print("3. Refresh Shop Inventory (costs 20 gold)")
            print("4. Return to Main Menu")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == "1":  # Browse/buy items
                shop.display()
                
                if not shop.inventory:
                    continue
                    
                buy_choice = input(f"Enter item number to buy (1-{len(shop.inventory)}, or 0 to cancel): ")
                try:
                    buy_idx = int(buy_choice) - 1
                    if buy_idx == -1:  # Cancel
                        continue
                        
                    if 0 <= buy_idx < len(shop.inventory):
                        shop.buy_item(self.player, buy_idx)
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Please enter a number.")
                    
            elif choice == "2":  # Sell items
                if not self.player.inventory.items:
                    print("You don't have any items to sell!")
                    continue
                    
                print("\nYour Inventory:")
                for i, item in enumerate(self.player.inventory.items, 1):
                    sell_value = max(1, item.value // 2)
                    print(f"{i}. {item.emoji if hasattr(item, 'emoji') else '📦'} {item.name} - Sell value: {sell_value} gold")
                    
                sell_choice = input(f"Enter item number to sell (1-{len(self.player.inventory.items)}, or 0 to cancel): ")
                try:
                    sell_idx = int(sell_choice) - 1
                    if sell_idx == -1:  # Cancel
                        continue
                        
                    if 0 <= sell_idx < len(self.player.inventory.items):
                        shop.sell_item(self.player, sell_idx)
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Please enter a number.")
                    
            elif choice == "3":  # Refresh inventory
                refresh_cost = 20
                if self.player.inventory.gold < refresh_cost:
                    print(f"You don't have enough gold! Need {refresh_cost} gold.")
                    continue
                    
                confirm = input(f"Refresh the shop inventory for {refresh_cost} gold? (y/n): ").lower()
                if confirm == 'y':
                    self.player.inventory.gold -= refresh_cost
                    shop.refresh()
                    print("The merchant brings out new items!")
                    
            elif choice == "4":  # Return to main menu
                break
                
            else:
                print("Invalid choice. Please try again.")
        
    def manage_saved_characters(self):
        """Load, save, or delete saved characters"""
        while True:
            print("\n" + "="*50)
            print("💾  CHARACTER MANAGEMENT  💾")
            print("="*50)
            
            print("Choose an option:")
            print("1. Create New Character")
            print("2. Load Saved Character")
            print("3. Save Current Character")
            print("4. Delete Saved Character")
            print("5. Return to Title Screen")
            
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == "1":  # Create new
                self.create_player()
                return True
                
            elif choice == "2":  # Load character
                saved_characters = get_all_characters()
                
                if not saved_characters:
                    print("No saved characters found.")
                    continue
                    
                print("\nChoose a character to load:")
                for i, char in enumerate(saved_characters, 1):
                    class_name = char.character_class
                    print(f"{i}. {char.name} (Level {char.level} {class_name})")
                    
                try:
                    load_choice = input(f"Enter your choice (1-{len(saved_characters)}, or 0 to cancel): ")
                    if load_choice == "0":
                        continue
                        
                    load_idx = int(load_choice) - 1
                    if 0 <= load_idx < len(saved_characters):
                        character_id = saved_characters[load_idx].id
                        loaded_character = load_character(character_id)
                        
                        if loaded_character:
                            self.player = loaded_character
                            print(f"\nWelcome back, {self.player.name}!")
                            print(self.player.status())
                            return True
                        else:
                            print("Failed to load character.")
                    else:
                        print("Invalid choice.")
                except ValueError:
                    print("Please enter a number.")
                    
            elif choice == "3":  # Save character
                if not self.player:
                    print("No active character to save.")
                    continue
                    
                # Ask for confirmation if overwriting
                saved_characters = get_all_characters()
                character_exists = False
                
                for char in saved_characters:
                    if char.name == self.player.name and char.character_class == self.player.__class__.__name__:
                        character_exists = True
                        break
                        
                if character_exists:
                    confirm = input("A character with this name already exists. Overwrite? (y/n): ").lower()
                    if confirm != 'y':
                        continue
                        
                    overwrite = True
                else:
                    overwrite = False
                    
                saved = save_character(self.player, overwrite)
                if saved:
                    print(f"Character {self.player.name} saved successfully!")
                else:
                    print("Failed to save character.")
                    
            elif choice == "4":  # Delete character
                saved_characters = get_all_characters()
                
                if not saved_characters:
                    print("No saved characters found.")
                    continue
                    
                print("\nChoose a character to delete:")
                for i, char in enumerate(saved_characters, 1):
                    class_name = char.character_class
                    print(f"{i}. {char.name} (Level {char.level} {class_name})")
                    
                try:
                    delete_choice = input(f"Enter your choice (1-{len(saved_characters)}, or 0 to cancel): ")
                    if delete_choice == "0":
                        continue
                        
                    delete_idx = int(delete_choice) - 1
                    if 0 <= delete_idx < len(saved_characters):
                        character_id = saved_characters[delete_idx].id
                        character_name = saved_characters[delete_idx].name
                        
                        # Confirm deletion
                        confirm = input(f"Are you sure you want to delete {character_name}? (y/n): ").lower()
                        if confirm != 'y':
                            continue
                            
                        deleted = delete_character(character_id)
                        if deleted:
                            print(f"Character {character_name} deleted successfully.")
                        else:
                            print("Failed to delete character.")
                    else:
                        print("Invalid choice.")
                except ValueError:
                    print("Please enter a number.")
                    
            elif choice == "5":  # Return to title
                return False
                
    def run(self):
        """Main game loop with enhanced menu"""
        self.display_intro()
        
        # Character selection screen
        has_character = self.manage_saved_characters()
        if not has_character:
            self.create_player()
        
        running = True
        while running:
            # Main menu
            print("\n" + "="*50)
            print("🎮  MAIN MENU  🎮")
            print("="*50)
            
            print(f"Character: {self.player.emoji} {self.player.name} (Level {self.player.level})")
            print(f"HP: {self.player.hp}/{self.player.max_hp} | Mana: {self.player.mana}/{self.player.max_mana}")
            
            print("\nChoose an action:")
            print("1. Hunt Monsters 🏕️")
            print("2. Face a Villain 👺")
            print("3. Challenge Boss ⚠️")
            print("4. Manage Inventory 🎒")
            print("5. Visit Shop 🛒")
            print("6. Character Status 👤")
            print("7. Rest and Recover 🏠")
            print("8. Save Character 💾")
            print("9. Change Character 👥")
            print("10. Exit Game 🚪")
            
            choice = input("\nEnter your choice (1-10): ")
            
            if choice == "1":  # Hunt
                self.hunt_monsters()
                
            elif choice == "2":  # Face villain
                self.create_villain()
                victory = self.start_combat()
                
                if victory:
                    print("\n🎉 Congratulations on your victory! 🎉")
                    # Rewards for defeating a villain
                    xp_reward = 50 * self.villain.level
                    self.player.gain_xp(xp_reward)
                    
                    gold_reward = random.randint(20, 40) * self.villain.level
                    self.player.inventory.gold += gold_reward
                    print(f"💰 You received {gold_reward} gold!")
                    
                    # Chance for item
                    if random.random() < 0.7:  # 70% chance
                        item = generate_random_item(self.player.level, False)
                        if self.player.inventory.add_item(item):
                            print(f"🎁 You found {item.emoji} {item.name}!")
                        else:
                            print("🎒 Your inventory is full! You couldn't pick up the item.")
                            
                    # Small chance to gain luck from defeating a villain
                    if random.random() < 0.3:  # 30% chance
                        luck_gain = random.randint(1, 2)
                        self.player.luck += luck_gain
                        print(f"⭐ Your fortune increases slightly! (+{luck_gain} Luck)")
                else:
                    print("\n😢 You were defeated! You've been revived but lost some gold.")
                    # Lose some gold when defeated
                    gold_loss = min(int(self.player.inventory.gold * 0.2), 50)  # 20% or max 50
                    self.player.inventory.gold = max(0, self.player.inventory.gold - gold_loss)
                    if gold_loss > 0:
                        print(f"💸 You lost {gold_loss} gold!")
                    
                    # Restore some HP and mana
                    self.player.hp = max(1, int(self.player.max_hp * 0.5))  # 50% HP
                    self.player.mana = max(1, int(self.player.max_mana * 0.5))  # 50% mana
                
                input("\nPress Enter to continue...")
                
            elif choice == "3":  # Boss challenge
                self.face_boss()
                
            elif choice == "4":  # Inventory
                self.manage_inventory()
                
            elif choice == "5":  # Visit Shop
                self.visit_shop()
                
            elif choice == "6":  # Character status
                self.show_character_status()
                
            elif choice == "7":  # Rest
                # Restore HP and mana
                old_hp = self.player.hp
                old_mana = self.player.mana
                
                self.player.hp = self.player.max_hp
                self.player.mana = self.player.max_mana
                
                hp_restored = self.player.hp - old_hp
                mana_restored = self.player.mana - old_mana
                
                print("\n" + "="*50)
                print("🏠  RESTING  🏠")
                print("="*50)
                print(f"You take some time to rest and recover...")
                time.sleep(1)
                print(f"HP restored: +{hp_restored} ❤️")
                print(f"Mana restored: +{mana_restored} 🔮")
                print("You feel refreshed and ready for adventure!")
                
                input("\nPress Enter to continue...")
                
            elif choice == "8":  # Save character
                # Use the save character function from the manage_saved_characters method
                if not self.player:
                    print("No active character to save.")
                    continue
                    
                # Ask for confirmation if overwriting
                saved_characters = get_all_characters()
                character_exists = False
                
                for char in saved_characters:
                    if char.name == self.player.name and char.character_class == self.player.__class__.__name__:
                        character_exists = True
                        break
                        
                if character_exists:
                    confirm = input("A character with this name already exists. Overwrite? (y/n): ").lower()
                    if confirm != 'y':
                        continue
                        
                    overwrite = True
                else:
                    overwrite = False
                    
                saved = save_character(self.player, overwrite)
                if saved:
                    print(f"Character {self.player.name} saved successfully!")
                else:
                    print("Failed to save character.")
                
                input("\nPress Enter to continue...")
                
            elif choice == "9":  # Change character
                # Confirm with the player if they want to switch characters
                confirm = input("Are you sure you want to switch characters? Unsaved progress will be lost. (y/n): ").lower()
                if confirm != 'y':
                    continue
                    
                # Use the existing character management screen
                has_character = self.manage_saved_characters()
                if not has_character:
                    self.create_player()
                
            elif choice == "10":  # Exit
                # Ask to save before exiting
                save_prompt = input("Would you like to save your character before exiting? (y/n): ").lower()
                if save_prompt == 'y':
                    # Use the same save logic as option 7
                    saved_characters = get_all_characters()
                    character_exists = False
                    
                    for char in saved_characters:
                        if char.name == self.player.name and char.character_class == self.player.__class__.__name__:
                            character_exists = True
                            break
                            
                    if character_exists:
                        confirm = input("A character with this name already exists. Overwrite? (y/n): ").lower()
                        if confirm != 'y':
                            continue
                            
                        overwrite = True
                    else:
                        overwrite = False
                        
                    saved = save_character(self.player, overwrite)
                    if saved:
                        print(f"Character {self.player.name} saved successfully!")
                    else:
                        print("Failed to save character.")
                
                print("\nThank you for playing Magical Realms! 👋")
                running = False
                
            else:
                print("Invalid choice. Please try again.")
                
def main():
    """Entry point for the Magical Realms game"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()