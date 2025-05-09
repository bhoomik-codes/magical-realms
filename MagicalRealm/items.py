import random

class Item:
    """Base class for all items in the game"""
    
    def __init__(self, name, description, value):
        self.name = name
        self.description = description
        self.value = value  # Gold value if sold
        self.emoji = "📦"
        
    def __str__(self):
        return f"{self.emoji} {self.name}: {self.description}"
        
    def use(self, character) -> bool:
        """Base use method - to be overridden by subclasses"""
        print(f"{character.emoji} {character.name} cannot use {self.name}.")
        return False  # Must return False to indicate item was not used


class Consumable(Item):
    """Items that can be consumed for an effect"""
    
    def __init__(self, name, description, value, uses=1):
        super().__init__(name, description, value)
        self.uses = uses  # Number of uses before item is depleted
        
    def use(self, character) -> bool:
        """Use the consumable item - to be defined by subclasses"""
        if self.uses <= 0:
            print(f"{self.emoji} {self.name} is depleted and cannot be used.")
            return False
        
        # Reduce uses
        self.uses -= 1
        return True


class HealthPotion(Consumable):
    """Restores HP when consumed"""
    
    def __init__(self, size="small"):
        self.size = size
        if size == "small":
            name = "Small Health Potion"
            description = "Restores 25 HP"
            value = 15
            self.heal_amount = 25
            self.emoji = "🧪"
        elif size == "medium":
            name = "Medium Health Potion"
            description = "Restores 50 HP"
            value = 30
            self.heal_amount = 50
            self.emoji = "🧪"
        else:  # large
            name = "Large Health Potion"
            description = "Restores 100 HP"
            value = 60
            self.heal_amount = 100
            self.emoji = "🧪"
            
        super().__init__(name, description, value)
        
    def use(self, character) -> bool:
        """Restore character's HP"""
        if not super().use(character):
            return False
            
        old_hp = character.hp
        character.hp = min(character.max_hp, character.hp + self.heal_amount)
        actual_heal = character.hp - old_hp
        
        print(f"{self.emoji} {character.name} drinks {self.name} and recovers {actual_heal} HP! ❤️")
        return True


class ManaPotion(Consumable):
    """Restores Mana when consumed"""
    
    def __init__(self, size="small"):
        self.size = size
        if size == "small":
            name = "Small Mana Potion"
            description = "Restores 15 Mana"
            value = 15
            self.mana_amount = 15
            self.emoji = "🧪"
        elif size == "medium":
            name = "Medium Mana Potion"
            description = "Restores 30 Mana"
            value = 30
            self.mana_amount = 30
            self.emoji = "🧪"
        else:  # large
            name = "Large Mana Potion"
            description = "Restores 60 Mana"
            value = 60
            self.mana_amount = 60
            self.emoji = "🧪"
            
        super().__init__(name, description, value)
        
    def use(self, character) -> bool:
        """Restore character's Mana"""
        if not super().use(character):
            return False
            
        old_mana = character.mana
        character.mana = min(character.max_mana, character.mana + self.mana_amount)
        actual_mana = character.mana - old_mana
        
        print(f"{self.emoji} {character.name} drinks {self.name} and recovers {actual_mana} Mana! 🔮")
        return True


class StrengthElixir(Consumable):
    """Temporarily boosts attack"""
    
    def __init__(self):
        name = "Strength Elixir"
        description = "Increases attack by 10 for 3 turns"
        value = 50
        self.boost_amount = 10
        self.duration = 3
        self.emoji = "⚡"
        
        super().__init__(name, description, value)
        
    def use(self, character) -> bool:
        """Boost character's attack"""
        if not super().use(character):
            return False
            
        if not hasattr(character, 'attack_boost'):
            character.attack_boost = 0
        if not hasattr(character, 'attack_boost_duration'):
            character.attack_boost_duration = 0
            
        character.attack_boost = self.boost_amount
        character.attack_boost_duration = self.duration
        character.base_attack += self.boost_amount
        
        print(f"{self.emoji} {character.name} drinks {self.name} and gains +{self.boost_amount} attack for {self.duration} turns! ⚔️")
        return True


class Equipment(Item):
    """Base class for equippable items"""
    
    def __init__(self, name, description, value, slot, stat_boost):
        super().__init__(name, description, value)
        self.slot = slot  # Where it's equipped (weapon, head, body, etc)
        self.stat_boost = stat_boost  # Dict of stats to boost
        
    def equip(self, character) -> bool:
        """Equip the item and apply stat boosts"""
        # Unequip any existing item in that slot
        if hasattr(character, 'equipment') and character.equipment.get(self.slot):
            old_equipment = character.equipment[self.slot]
            # Remove old equipment stat boosts
            for stat, value in old_equipment.stat_boost.items():
                if stat == 'attack':
                    character.base_attack -= value
                elif stat == 'defense':
                    character.defense -= value
                elif stat == 'max_hp':
                    character.max_hp -= value
                    character.hp = min(character.hp, character.max_hp)
                elif stat == 'max_mana':
                    character.max_mana -= value
                    character.mana = min(character.mana, character.max_mana)
        
        # Ensure character has equipment dict
        if not hasattr(character, 'equipment'):
            character.equipment = {}
            
        # Apply new equipment stat boosts
        for stat, value in self.stat_boost.items():
            if stat == 'attack':
                character.base_attack += value
            elif stat == 'defense':
                character.defense += value
            elif stat == 'max_hp':
                character.max_hp += value
            elif stat == 'max_mana':
                character.max_mana += value
                
        # Equip the item
        character.equipment[self.slot] = self
        
        print(f"{self.emoji} {character.name} equipped {self.name}!")
        return True
        
    def unequip(self, character) -> bool:
        """Unequip the item and remove stat boosts"""
        if not hasattr(character, 'equipment') or self.slot not in character.equipment:
            print(f"{character.emoji} {character.name} doesn't have {self.name} equipped.")
            return False
            
        # Remove stat boosts
        for stat, value in self.stat_boost.items():
            if stat == 'attack':
                character.base_attack -= value
            elif stat == 'defense':
                character.defense -= value
            elif stat == 'max_hp':
                character.max_hp -= value
                character.hp = min(character.hp, character.max_hp)
            elif stat == 'max_mana':
                character.max_mana -= value
                character.mana = min(character.mana, character.max_mana)
                
        # Remove from equipment
        del character.equipment[self.slot]
        
        print(f"{self.emoji} {character.name} unequipped {self.name}.")
        return True


class Weapon(Equipment):
    """Weapons that boost attack"""
    
    def __init__(self, name, description, value, attack_boost):
        stat_boost = {'attack': attack_boost}
        super().__init__(name, description, value, 'weapon', stat_boost)
        self.emoji = "⚔️"


class Armor(Equipment):
    """Armor that boosts defense"""
    
    def __init__(self, name, description, value, defense_boost):
        stat_boost = {'defense': defense_boost}
        super().__init__(name, description, value, 'armor', stat_boost)
        self.emoji = "🛡️"


class Accessory(Equipment):
    """Accessories with various stat boosts"""
    
    def __init__(self, name, description, value, stat_boosts):
        super().__init__(name, description, value, 'accessory', stat_boosts)
        self.emoji = "💍"


class Inventory:
    """Manages a character's inventory"""
    
    def __init__(self, max_size=100):
        self.items = []
        self.max_size = max_size
        self.gold = 0
        
    def add_item(self, item) -> bool:
        """Add an item to inventory if space available"""
        if len(self.items) >= self.max_size:
            return False
        self.items.append(item)
        return True
        
    def remove_item(self, item) -> bool:
        """Remove an item from inventory"""
        if item in self.items:
            self.items.remove(item)
            return True
        return False
        
    def get_consumables(self) -> list:
        """Get all consumable items in inventory"""
        return [item for item in self.items if isinstance(item, Consumable)]
        
    def get_equipment(self) -> list:
        """Get all equipment items in inventory"""
        return [item for item in self.items if isinstance(item, Equipment)]
        
    def display(self) -> None:
        """Display inventory contents"""
        if not self.items:
            print("Your inventory is empty.")
            return
            
        print(f"💰 Gold: {self.gold}")
        print(f"Inventory ({len(self.items)}/{self.max_size}):")
        
        for i, item in enumerate(self.items, 1):
            print(f"{i}. {item}")


# Item generation functions
def generate_random_item(level=1, is_boss=False) -> Item:
    """Generate a random item based on player level and if from a boss"""
    item_type = random.choices(
        ['weapon', 'armor', 'accessory', 'health_potion', 'mana_potion', 'strength_elixir'],
        weights=[20, 20, 10, 25, 20, 5]
    )[0]
    
    # Increase chance of better items from bosses
    quality_boost = 2 if is_boss else 0
    
    # Quality tiers based on level + boss bonus
    if random.random() < 0.2 + (0.05 * quality_boost):  # 10-20% chance for rare
        quality = "rare"
    elif random.random() < 0.3 + (0.1 * quality_boost):  # 30-50% chance for uncommon
        quality = "uncommon"
    elif random.random() < 0.5 + (0.15 * quality_boost):  # 60-75% chance for common
        quality = "common"
    else:  # 50-40% chance for common
        quality = "legendary"
        
    # Generate based on type
    if item_type == 'weapon':
        return generate_weapon(level, quality)
    elif item_type == 'armor':
        return generate_armor(level, quality)
    elif item_type == 'accessory':
        return generate_accessory(level, quality)
    elif item_type == 'health_potion':
        size = "small"
        if level > 5 or quality == "uncommon":
            size = "medium"
        if level > 10 or quality == "rare":
            size = "large"
        return HealthPotion(size)
    elif item_type == 'mana_potion':
        size = "small"
        if level > 5 or quality == "uncommon":
            size = "medium"
        if level > 10 or quality == "rare":
            size = "large"
        return ManaPotion(size)
    else:  # strength_elixir
        return StrengthElixir()


def generate_weapon(level: int, quality: str) -> Weapon:
    """Generate a weapon based on level and quality"""
    weapon_types = {
        'Barbarian': ['Axe', 'War Hammer', 'Greatsword', 'Battle Axe'],
        'Archer': ['Bow', 'Crossbow', 'Longbow', 'Hunting Bow'],
        'Mage': ['Staff', 'Wand', 'Orb', 'Grimoire']
    }
    
    # Choose random class and weapon type
    character_class = random.choice(list(weapon_types.keys()))
    weapon_type = random.choice(weapon_types[character_class])
    
    # Set base stats based on quality
    if quality == "common":
        prefix = ""
        attack_boost = level + random.randint(1, 3)
        value = level * 10 + random.randint(5, 15)
    elif quality == "uncommon":
        prefix = random.choice(["Fine ", "Strong ", "Crafted "])
        attack_boost = level + random.randint(3, 6)
        value = level * 20 + random.randint(10, 30)
    elif quality == "rare": # rare
        prefix = random.choice(["Masterwork ", "Enchanted ", "Superior "])
        attack_boost = level + random.randint(5, 10)
        value = level * 50 + random.randint(25, 75)
    else:  # legendary
        prefix = random.choice(["From the depths of hell ", "The one with gods ", "Forged from Elixir "])
        attack_boost = level + random.randint(10, 20)
        value = level * 100 + random.randint(50, 150)
        
    name = f"{prefix}{weapon_type}"
    description = f"Increases attack by {attack_boost}"
    
    return Weapon(name, description, value, attack_boost)


def generate_armor(level: int, quality: str) -> Armor:
    """Generate armor based on level and quality"""
    armor_types = {
        'Barbarian': ['Hide Armor', 'Fur Armor', 'Plate Mail', 'Chain Mail'],
        'Archer': ['Leather Armor', 'Scout Armor', 'Rangers Cloak', 'Hunters Garb'],
        'Mage': ['Robe', 'Enchanted Garb', 'Mystic Vestments', 'Arcane Cloak']
    }
    
    # Choose random class and armor type
    character_class = random.choice(list(armor_types.keys()))
    armor_type = random.choice(armor_types[character_class])
    
    # Set base stats based on quality
    if quality == "common":
        prefix = ""
        defense_boost = level + random.randint(1, 2)
        value = level * 10 + random.randint(5, 15)
    elif quality == "uncommon":
        prefix = random.choice(["Sturdy ", "Reinforced ", "Hardy "])
        defense_boost = level + random.randint(2, 4)
        value = level * 20 + random.randint(10, 30)
    elif quality == "rare":  # rare
        prefix = random.choice(["Impenetrable ", "Enchanted ", "Superior "])
        defense_boost = level + random.randint(3, 7)
        value = level * 50 + random.randint(25, 75)
    else:  # legendary
        prefix = random.choice(["From the depths of hell ", "The one with gods ", "Forged from Elixir "])
        defense_boost = level + random.randint(5, 15)
        value = level * 100 + random.randint(50, 150)
        
    name = f"{prefix}{armor_type}"
    description = f"Increases defense by {defense_boost}"
    
    return Armor(name, description, value, defense_boost)


def generate_accessory(level: int, quality: str) -> Accessory:
    """Generate an accessory based on level and quality"""
    accessory_types = ['Amulet', 'Ring', 'Bracers', 'Belt', 'Cloak']
    accessory_type = random.choice(accessory_types)
    
    # Different stat boosts
    possible_stats = ['attack', 'defense', 'max_hp', 'max_mana']
    
    # Determine number of stat boosts based on quality
    if quality == "common":
        prefix = ""
        num_stats = 1
        stat_range = (1, 2)
        value = level * 15 + random.randint(5, 25)
    elif quality == "uncommon":
        prefix = random.choice(["Enchanted ", "Mystic ", "Empowered "])
        num_stats = random.randint(1, 2)
        stat_range = (2, 4)
        value = level * 30 + random.randint(15, 45)
    elif quality == "rare":  # rare
        prefix = random.choice(["Nelson's ", "Odin's ", "King's "])
        num_stats = random.randint(2, 3)
        stat_range = (3, 6)
        value = level * 70 + random.randint(30, 90)
    else:  # legendary
        prefix = random.choice(["Mythical ", "Ancient ", "Epic "])
        num_stats = random.randint(3, 4)
        stat_range = (5, 10)
        value = level * 150 + random.randint(50, 200)
    
    # Select stats to boost
    selected_stats = random.sample(possible_stats, num_stats)
    stat_boosts = {}
    
    # Generate boost values
    for stat in selected_stats:
        if stat in ['attack', 'defense']:
            stat_boosts[stat] = level // 2 + random.randint(stat_range[0], stat_range[1])
        else:  # max_hp, max_mana
            stat_boosts[stat] = level * 2 + random.randint(stat_range[0] * 5, stat_range[1] * 5)
    
    name = f"{prefix}{accessory_type}"
    
    # Create description from stat boosts
    stat_descriptions = []
    for stat, boost in stat_boosts.items():
        if stat == 'attack':
            stat_descriptions.append(f"+{boost} Attack")
        elif stat == 'defense':
            stat_descriptions.append(f"+{boost} Defense")
        elif stat == 'max_hp':
            stat_descriptions.append(f"+{boost} Max HP")
        elif stat == 'max_mana':
            stat_descriptions.append(f"+{boost} Max Mana")
            
    description = ", ".join(stat_descriptions)
    
    return Accessory(name, description, value, stat_boosts)


class Shop:
    """Shop system for buying and selling items"""
    
    def __init__(self, level=1, luck=0):
        self.inventory = []  # Available items in the shop
        self.level = level   # Level affects item quality
        self.luck = luck     # Higher luck increases chances for better items
        self.refresh()
        
    def refresh(self):
        """Refresh shop inventory with new random items"""
        self.inventory = []
        
        # Number of items based on player level (3-10)
        num_items = min(10, 3 + self.level // 2)
        
        # Generate random items
        for _ in range(num_items):
            # Determine item type
            item_type = random.choices(
                ["weapon", "armor", "accessory", "health_potion", "mana_potion", "strength_elixir"],
                weights=[20, 20, 15, 20, 20, 5],
                k=1
            )[0]
            
            # Quality chances (affected by luck)
            # Luck increases rare chance by 1% per point, up to +20%
            luck_boost = min(20, self.luck)
            quality_weights = [70 - luck_boost//2, 25, 5 + luck_boost//2]
            
            # After boss fights (higher luck), better chance for rare items
            if self.luck > 10:
                quality_weights = [50 - luck_boost//2, 30, 20 + luck_boost//2]
                
            quality = random.choices(
                ["common", "uncommon", "rare"],
                weights=quality_weights,
                k=1
            )[0]
            
            # Generate the item
            if item_type == "weapon":
                item = generate_weapon(self.level, quality)
            elif item_type == "armor":
                item = generate_armor(self.level, quality)
            elif item_type == "accessory":
                item = generate_accessory(self.level, quality)
            elif item_type == "health_potion":
                size = random.choice(["small", "medium", "large"])
                item = HealthPotion(size)
            elif item_type == "mana_potion":
                size = random.choice(["small", "medium", "large"])
                item = ManaPotion(size)
            else:  # strength_elixir
                item = StrengthElixir()
                
            self.inventory.append(item)
    
    def display(self):
        """Display all items in the shop inventory"""
        print("\n" + "="*60)
        print("🛒  MERCHANT'S SHOP  🛒")
        print("="*60)
        
        if not self.inventory:
            print("The shop is empty! Come back later.")
            return
            
        print(f"Gold is required to purchase these items.")
        print("-"*60)
        
        for i, item in enumerate(self.inventory, 1):
            quality_marker = ""
            if hasattr(item, 'description') and 'rare' in item.description.lower():
                quality_marker = "🌟"
            elif hasattr(item, 'description') and 'uncommon' in item.description.lower():
                quality_marker = "✨"
                
            print(f"{i}. {item.emoji if hasattr(item, 'emoji') else '📦'} {item.name} {quality_marker}- {item.value} gold")
            if hasattr(item, 'description'):
                print(f"   {item.description}")
        
        print("="*60)
        
    def buy_item(self, player, item_index):
        """Let player buy an item from the shop"""
        if item_index < 0 or item_index >= len(self.inventory):
            print("Invalid item selection!")
            return False
            
        item = self.inventory[item_index]
        
        # Check if player has enough gold
        if not hasattr(player, 'inventory') or not hasattr(player.inventory, 'gold') or player.inventory.gold < item.value:
            print(f"{player.emoji if hasattr(player, 'emoji') else '👤'} {player.name} doesn't have enough gold! Need {item.value} gold.")
            return False
            
        # Try to add to player's inventory
        if player.inventory.add_item(item):
            # Deduct gold
            player.inventory.gold -= item.value
            # Remove from shop
            self.inventory.pop(item_index)
            print(f"{player.emoji if hasattr(player, 'emoji') else '👤'} {player.name} purchased {item.emoji if hasattr(item, 'emoji') else '📦'} {item.name} for {item.value} gold!")
            return True
        else:
            print(f"{player.emoji if hasattr(player, 'emoji') else '👤'} {player.name}'s inventory is full!")
            return False
            
    def sell_item(self, player, item_index):
        """Let player sell an item to the shop"""
        if not hasattr(player, 'inventory') or not hasattr(player.inventory, 'items') or item_index < 0 or item_index >= len(player.inventory.items):
            print("Invalid item selection!")
            return False
            
        item = player.inventory.items[item_index]
        
        # Calculate sell value (50% of buy value)
        sell_value = max(1, item.value // 2)
        
        # Add gold to player
        player.inventory.gold += sell_value
        
        # Remove item from inventory
        player.inventory.remove_item(item)
        
        print(f"{player.emoji if hasattr(player, 'emoji') else '👤'} {player.name} sold {item.emoji if hasattr(item, 'emoji') else '📦'} {item.name} for {sell_value} gold!")