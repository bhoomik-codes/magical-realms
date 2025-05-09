import random

class Character:
    """Base class for all characters in the game"""
    
    def __init__(self, name, hp=100, mana=50, attack=20, defense=10):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.max_mana = mana
        self.mana = mana
        self.base_attack = attack
        self.defense = defense
        self.is_blocking = False
        self.emoji = "👤"
        # Added for progression system
        self.level = 1
        self.xp = 0
        self.xp_to_level = 100  # Base XP needed for level 2
        self.equipment = {}  # For equipped items
        # Class evolution system
        self.class_tier = 0  # 0 is base class, 6 is max tier
        self.class_title = ""  # Title based on class tier
        self.skills = []  # List of unlocked skills
        self.luck = 0  # Hidden luck stat for shop items
        # Status effects
        self.attack_boost = 0
        self.attack_boost_duration = 0
        self.is_dodging = False
        # Inventory system
        from items import Inventory  # Import here to avoid circular import
        self.inventory = Inventory(max_size=10)
        
    def attack(self, target):
        """Basic attack that deals damage based on attack value with some randomness"""
        # If blocking, cancel block status and return without attacking
        if self.is_blocking:
            print(f"{self.emoji} {self.name} lowers their guard and prepares to attack.")
            self.is_blocking = False
            return 0
            
        # Calculate attack with randomness (-10 to +10)
        attack_value = self.base_attack + random.randint(-10, 10)
        if attack_value < 0:
            attack_value = 0
        
        # Check if target is dodging
        if target.is_dodging:
            # 40% chance to completely avoid attack
            if random.random() < 0.4:
                print(f"{target.emoji} {target.name} dodged the attack completely! 🌪️")
                target.is_dodging = False  # Reset dodge after attempt
                return 0
            else:
                print(f"{target.emoji} {target.name} attempted to dodge but failed! 🌪️")
                target.is_dodging = False  # Reset dodge after attempt
            
        # Apply damage reduction from target's defense
        effective_defense = target.defense
        if target.is_blocking:
            effective_defense *= 2
            print(f"{target.emoji} {target.name} blocked and reduced damage! 🛡️")
            
        damage = max(0, attack_value - effective_defense)
        
        # Apply damage to target
        target.hp = max(0, target.hp - damage)
        
        # Return damage for message display
        return damage
    
    def special_attack(self, target):
        """Special attack that consumes mana but deals more damage"""
        if self.is_blocking:
            print(f"{self.emoji} {self.name} lowers their guard and prepares to attack.")
            self.is_blocking = False
            
        # Default special attack costs 15 mana
        mana_cost = 15
        
        if self.mana < mana_cost:
            print(f"{self.emoji} {self.name} doesn't have enough mana! ❌")
            return 0
            
        # Consume mana
        self.mana -= mana_cost
        
        # Calculate attack with increased damage and randomness
        attack_value = int(self.base_attack * 1.5) + random.randint(-5, 15)
        if attack_value < 0:
            attack_value = 0
            
        # Check if target is dodging - harder to dodge special attacks (30% chance)
        if target.is_dodging:
            if random.random() < 0.3:
                print(f"{target.emoji} {target.name} dodged the special attack! 🌪️")
                target.is_dodging = False  # Reset dodge after attempt
                return 0
            else:
                print(f"{target.emoji} {target.name} attempted to dodge the special attack but failed! 🌪️")
                target.is_dodging = False  # Reset dodge after attempt
            
        # Apply damage reduction from target's defense
        effective_defense = target.defense
        if target.is_blocking:
            effective_defense *= 2
            print(f"{target.emoji} {target.name} blocked and reduced damage! 🛡️")
            
        damage = max(0, attack_value - effective_defense)
        
        # Apply damage to target
        target.hp = max(0, target.hp - damage)
        
        # Return damage for message display
        return damage
    
    def block(self):
        """Enter blocking stance to reduce incoming damage"""
        self.is_blocking = True
        
    def dodge(self):
        """Enter dodging stance to have a chance to avoid attacks"""
        self.is_dodging = True
        
    def is_alive(self):
        """Check if character is still alive"""
        return self.hp > 0
        
    def gain_xp(self, amount):
        """Gain experience points and level up if enough XP is accumulated"""
        self.xp += amount
        print(f"{self.emoji} {self.name} gained {amount} XP!")
        
        # Check for level up
        if self.xp >= self.xp_to_level:
            self.level_up()
            return True
        return False
        
    def level_up(self):
        """Level up the character, increasing stats"""
        self.level += 1
        
        # Increase stats based on character type
        if isinstance(self, Barbarian):
            hp_increase = 15
            mana_increase = 5
            attack_increase = 3
            defense_increase = 1
        elif isinstance(self, Archer):
            hp_increase = 10
            mana_increase = 8
            attack_increase = 2
            defense_increase = 2
        elif isinstance(self, Mage):
            hp_increase = 8
            mana_increase = 12
            attack_increase = 2
            defense_increase = 1
        else:
            hp_increase = 10
            mana_increase = 5
            attack_increase = 2
            defense_increase = 1
            
        # Apply increases
        self.max_hp += hp_increase
        self.hp = self.max_hp  # Full heal on level up
        self.max_mana += mana_increase
        self.mana = self.max_mana  # Full mana restore on level up
        self.base_attack += attack_increase
        self.defense += defense_increase
        
        # Set new XP threshold (increasing with each level)
        self.xp_to_level = int(self.xp_to_level * 1.5)
        
        print(f"🌟 {self.emoji} {self.name} leveled up to level {self.level}! 🌟")
        print(f"HP +{hp_increase}, Mana +{mana_increase}, Attack +{attack_increase}, Defense +{defense_increase}")
        
        # Check for class evolution at certain level thresholds
        # Evolution tiers: 0=Base, 1=Apprentice, 2=Adept, 3=Master, 4=Grand, 5=Elder, 6=Celestial
        evolution_levels = {5: 1, 10: 2, 15: 3, 20: 4, 25: 5, 30: 6}
        
        if self.level in evolution_levels and self.class_tier < evolution_levels[self.level]:
            self.evolve_class(evolution_levels[self.level])
            
    def evolve_class(self, new_tier):
        """Evolve the character's class to a higher tier"""
        old_tier = self.class_tier
        self.class_tier = new_tier
        
        # Base stat boosts for evolution (all classes)
        hp_boost = int(self.max_hp * 0.2)  # 20% HP increase
        mana_boost = int(self.max_mana * 0.2)  # 20% Mana increase
        attack_boost = int(self.base_attack * 0.15)  # 15% Attack increase
        defense_boost = int(self.defense * 0.15)  # 15% Defense increase
        
        # Apply stat boosts
        self.max_hp += hp_boost
        self.hp = self.max_hp
        self.max_mana += mana_boost
        self.mana = self.max_mana
        self.base_attack += attack_boost
        self.defense += defense_boost
        
        # Define titles for all classes
        barbarian_titles = ["Barbarian", "Berserker", "Warlord", "Champion", "Warchief", "Legendary Warrior", "Celestial Conqueror"]
        archer_titles = ["Archer", "Scout", "Ranger", "Sharpshooter", "Marksman", "Legendary Hunter", "Celestial Deadeye"]
        mage_titles = ["Mage", "Apprentice Mage", "Adept Mage", "Master Mage", "Grand Mage", "Elder Sage", "Celestial Magus"]
        
        # Set class title and add special abilities based on class and tier
        if isinstance(self, Barbarian):
            titles = barbarian_titles
            self.class_title = titles[new_tier]
            
            # Add new abilities based on tier
            if new_tier == 1:  # Berserker
                self.skills.append("Battle Cry")  # Intimidates enemies, reducing their attack
            elif new_tier == 2:  # Warlord
                self.skills.append("Cleave")  # Attacks multiple targets
            elif new_tier == 3:  # Champion
                self.skills.append("Endurance")  # Passive health regeneration
            elif new_tier == 4:  # Warchief
                self.skills.append("Rallying Shout")  # Temporarily boosts all stats
            elif new_tier == 5:  # Legendary Warrior
                self.skills.append("Unstoppable Force")  # Ignore damage for one turn
            elif new_tier == 6:  # Celestial Conqueror
                self.skills.append("Divine Fury")  # Ultimate attack with guaranteed critical hit
                
        elif isinstance(self, Archer):
            titles = archer_titles
            self.class_title = titles[new_tier]
            
            # Add new abilities based on tier
            if new_tier == 1:  # Scout
                self.skills.append("Quick Shot")  # Fast attack with lower mana cost
            elif new_tier == 2:  # Ranger
                self.skills.append("Trap")  # Sets a trap that damages enemies
            elif new_tier == 3:  # Sharpshooter
                self.skills.append("Aimed Shot")  # Higher critical hit chance
            elif new_tier == 4:  # Marksman
                self.skills.append("Volley")  # Multiple arrows at once
            elif new_tier == 5:  # Legendary Hunter
                self.skills.append("Shadow Step")  # Increases dodge chance significantly
            elif new_tier == 6:  # Celestial Deadeye
                self.skills.append("Rain of Arrows")  # Ultimate attack hitting multiple times
                
        elif isinstance(self, Mage):
            titles = mage_titles
            self.class_title = titles[new_tier]
            
            # Add new abilities based on tier
            if new_tier == 1:  # Apprentice Mage
                self.skills.append("Frost Nova")  # Slows enemy attacks
            elif new_tier == 2:  # Adept Mage
                self.skills.append("Arcane Missile")  # Multiple small hits
            elif new_tier == 3:  # Master Mage
                self.skills.append("Teleport")  # Increased dodge chance
            elif new_tier == 4:  # Grand Mage
                self.skills.append("Mirror Image")  # Creates a decoy to absorb damage
            elif new_tier == 5:  # Elder Sage
                self.skills.append("Mana Shield")  # Converts damage to mana cost
            elif new_tier == 6:  # Celestial Magus
                self.skills.append("Meteor Storm")  # Ultimate destructive spell
        else:
            # Fallback for any other classes
            titles = ["Novice", "Initiate", "Adept", "Expert", "Master", "Grandmaster", "Celestial"]
            self.class_title = titles[new_tier]
        
        # Get old title for display
        old_title = titles[old_tier] if old_tier < len(titles) else "Unknown"
        
        # Display evolution message with fancy formatting
        print("\n" + "="*60)
        print(f"✨✨✨  CLASS EVOLUTION  ✨✨✨")
        print("="*60)
        print(f"{self.emoji} {self.name} has evolved from {old_title} to {self.class_title}!")
        print(f"This evolution has granted significant power boosts:")
        print(f"❤️ HP +{hp_boost} | 🔮 Mana +{mana_boost} | ⚔️ Attack +{attack_boost} | 🛡️ Defense +{defense_boost}")
        print(f"New Skill Unlocked: {self.skills[-1]}!")
        print("="*60 + "\n")
            
    def status(self):
        """Display character status"""
        block_status = "🛡️ Blocking" if self.is_blocking else ""
        
        # Add level info
        level_info = f"LVL {self.level}"
        if hasattr(self, 'xp') and hasattr(self, 'xp_to_level') and not isinstance(self, Villain):
            level_info += f" | XP {self.xp}/{self.xp_to_level}"
        
        # Add class title if evolved
        title_display = ""
        if hasattr(self, 'class_title') and self.class_title:
            title_display = f" [{self.class_title}]"
            
        luck_display = ""
        if hasattr(self, 'luck') and not isinstance(self, Villain):
            luck_display = f" | Luck {self.luck} ⭐"
            
        return (f"{self.emoji} {self.name}{title_display} [{level_info}]: HP {self.hp}/{self.max_hp} ❤️ | "
                f"Mana {self.mana}/{self.max_mana} 🔮 | ATK {self.base_attack} ⚔️ | "
                f"DEF {self.defense} 🛡️{luck_display} {block_status}")


class Barbarian(Character):
    """Barbarian class with high HP and attack, but low mana and defense"""
    
    def __init__(self, name):
        super().__init__(name, hp=150, mana=30, attack=25, defense=8)
        self.emoji = "🪓"
        
    def special_attack(self, target):
        """Barbarian's rage attack deals heavy damage but costs more mana"""
        if self.is_blocking:
            print(f"{self.emoji} {self.name} lowers their guard and prepares to attack.")
            self.is_blocking = False
            
        mana_cost = 20
        
        if self.mana < mana_cost:
            print(f"{self.emoji} {self.name} doesn't have enough mana for Rage Attack! ❌")
            return 0
            
        print(f"{self.emoji} {self.name} unleashes a powerful Rage Attack! 🔥")
        self.mana -= mana_cost
        
        # Stronger attack with wider random range
        attack_value = int(self.base_attack * 2) + random.randint(-10, 20)
        if attack_value < 0:
            attack_value = 0
            
        effective_defense = target.defense
        if target.is_blocking:
            effective_defense *= 2
            print(f"{target.emoji} {target.name} blocked and reduced damage! 🛡️")
            
        damage = max(0, attack_value - effective_defense)
        target.hp = max(0, target.hp - damage)
        
        return damage


class Archer(Character):
    """Archer class with balanced stats and high accuracy"""
    
    def __init__(self, name):
        super().__init__(name, hp=90, mana=60, attack=22, defense=12)
        self.emoji = "🏹"
        
    def attack(self, target):
        """Archer's attacks have less randomness"""
        if self.is_blocking:
            print(f"{self.emoji} {self.name} lowers their guard and prepares to attack.")
            self.is_blocking = False
            return 0
            
        # More consistent damage (-5 to +5 instead of -10 to +10)
        attack_value = self.base_attack + random.randint(-5, 5)
        if attack_value < 0:
            attack_value = 0
            
        effective_defense = target.defense
        if target.is_blocking:
            effective_defense *= 2
            print(f"{target.emoji} {target.name} blocked and reduced damage! 🛡️")
            
        damage = max(0, attack_value - effective_defense)
        target.hp = max(0, target.hp - damage)
        
        return damage
        
    def special_attack(self, target):
        """Archer's precision shot has a chance to ignore defense"""
        if self.is_blocking:
            print(f"{self.emoji} {self.name} lowers their guard and prepares to attack.")
            self.is_blocking = False
            
        mana_cost = 15
        
        if self.mana < mana_cost:
            print(f"{self.emoji} {self.name} doesn't have enough mana for Precision Shot! ❌")
            return 0
            
        print(f"{self.emoji} {self.name} takes aim for a Precision Shot! 🎯")
        self.mana -= mana_cost
        
        # 30% chance to ignore defense
        ignore_defense = random.random() < 0.3
        
        attack_value = int(self.base_attack * 1.3) + random.randint(-5, 10)
        if attack_value < 0:
            attack_value = 0
            
        effective_defense = 0 if ignore_defense else target.defense
        if target.is_blocking and not ignore_defense:
            effective_defense *= 2
            print(f"{target.emoji} {target.name} blocked and reduced damage! 🛡️")
            
        if ignore_defense:
            print(f"Critical hit! {self.emoji} The arrow finds a gap in the armor! ⚡")
            
        damage = max(0, attack_value - effective_defense)
        target.hp = max(0, target.hp - damage)
        
        return damage


class Mage(Character):
    """Mage class with high mana, strong spells but low HP and defense"""
    
    def __init__(self, name):
        super().__init__(name, hp=80, mana=120, attack=15, defense=5)
        self.emoji = "🧙"
        
    def special_attack(self, target):
        """Mage's fireball spell deals high damage"""
        if self.is_blocking:
            print(f"{self.emoji} {self.name} lowers their guard and prepares to cast.")
            self.is_blocking = False
            
        mana_cost = 25
        
        if self.mana < mana_cost:
            print(f"{self.emoji} {self.name} doesn't have enough mana for Fireball! ❌")
            return 0
            
        print(f"{self.emoji} {self.name} casts a powerful Fireball! 🔥")
        self.mana -= mana_cost
        
        # High damage with significant randomness
        attack_value = int(self.base_attack * 2.5) + random.randint(-10, 30)
        if attack_value < 0:
            attack_value = 0
            
        effective_defense = target.defense
        if target.is_blocking:
            effective_defense *= 1.5  # Magic partially bypasses blocking
            print(f"{target.emoji} {target.name} blocked but the spell partially penetrated! 🛡️🔮")
            
        damage = max(0, attack_value - effective_defense)
        target.hp = max(0, target.hp - damage)
        
        return damage
        
    def heal(self):
        """Mages can heal themselves"""
        if self.is_blocking:
            print(f"{self.emoji} {self.name} lowers their guard to cast a spell.")
            self.is_blocking = False
            
        mana_cost = 30
        
        if self.mana < mana_cost:
            print(f"{self.emoji} {self.name} doesn't have enough mana to Heal! ❌")
            return 0
            
        heal_amount = 25 + random.randint(0, 15)
        self.mana -= mana_cost
        
        # Apply healing but don't exceed max HP
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + heal_amount)
        actual_heal = self.hp - old_hp
        
        print(f"{self.emoji} {self.name} casts Heal and recovers {actual_heal} HP! ✨")
        return actual_heal


class Villain(Character):
    """Base villain class with slightly adjusted stats"""
    
    def __init__(self, name, hp=120, mana=50, attack=22, defense=12):
        super().__init__(name, hp, mana, attack, defense)
        self.emoji = "👺"


class DarkKnight(Villain):
    """Tank-like villain with high defense"""
    
    def __init__(self, name):
        super().__init__(name, hp=130, mana=40, attack=20, defense=20)
        self.emoji = "🖤"
        
    def special_attack(self, target):
        """Dark slash attack with lifesteal"""
        if self.is_blocking:
            self.is_blocking = False
            
        mana_cost = 20
        
        if self.mana < mana_cost:
            return super().special_attack(target)
            
        print(f"{self.emoji} {self.name} performs a Dark Slash! ⚔️🌑")
        self.mana -= mana_cost
        
        attack_value = int(self.base_attack * 1.7) + random.randint(-5, 15)
        if attack_value < 0:
            attack_value = 0
            
        effective_defense = target.defense
        if target.is_blocking:
            effective_defense *= 2
            
        damage = max(0, attack_value - effective_defense)
        target.hp = max(0, target.hp - damage)
        
        # Lifesteal effect
        heal_amount = int(damage * 0.3)
        self.hp = min(self.max_hp, self.hp + heal_amount)
        if heal_amount > 0:
            print(f"{self.emoji} {self.name} absorbs {heal_amount} HP from the attack! 💉")
        
        return damage


class DarkArcher(Villain):
    """Ranged villain with poison attacks"""
    
    def __init__(self, name):
        super().__init__(name, hp=90, mana=70, attack=25, defense=8)
        self.emoji = "🏹"
        self.target_poisoned = False
        
    def special_attack(self, target):
        """Poison arrow attack that deals damage over time"""
        if self.is_blocking:
            self.is_blocking = False
            
        mana_cost = 25
        
        if self.mana < mana_cost:
            return super().special_attack(target)
            
        print(f"{self.emoji} {self.name} fires a Poison Arrow! 🏹☠️")
        self.mana -= mana_cost
        
        attack_value = int(self.base_attack * 1.2) + random.randint(-5, 10)
        if attack_value < 0:
            attack_value = 0
            
        effective_defense = target.defense
        if target.is_blocking:
            effective_defense *= 2
            
        damage = max(0, attack_value - effective_defense)
        target.hp = max(0, target.hp - damage)
        
        # Apply poison effect
        self.target_poisoned = True
        poison_damage = random.randint(5, 8)
        target.hp = max(0, target.hp - poison_damage)
        print(f"☠️ The poison deals an additional {poison_damage} damage to {target.name}!")
        
        # Return as integer to avoid type mismatch issues
        return int(damage + poison_damage)


class DarkMage(Villain):
    """Magic villain with strong spells"""
    
    def __init__(self, name):
        super().__init__(name, hp=85, mana=130, attack=15, defense=6)
        self.emoji = "🧙‍♂️"
        
    def special_attack(self, target):
        """Dark energy blast"""
        if self.is_blocking:
            self.is_blocking = False
            
        mana_cost = 30
        
        if self.mana < mana_cost:
            return super().special_attack(target)
            
        print(f"{self.emoji} {self.name} unleashes Dark Energy Blast! 🌑✨")
        self.mana -= mana_cost
        
        attack_value = int(self.base_attack * 3) + random.randint(-5, 25)
        if attack_value < 0:
            attack_value = 0
            
        # Dark magic ignores some defense
        effective_defense = int(target.defense * 0.7)
        if target.is_blocking:
            effective_defense *= 1.5  # Still partially bypasses blocking
            
        damage = max(0, attack_value - effective_defense)
        target.hp = max(0, target.hp - damage)
        
        # Return as integer to avoid type mismatch
        return int(damage)
