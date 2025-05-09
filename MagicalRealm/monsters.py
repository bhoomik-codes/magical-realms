import random
from characters import Character, Villain

class Monster(Character):
    """Base class for monsters that can be encountered during hunting"""
    
    def __init__(self, name, level=1, is_boss=False):
        # Base stats are affected by monster level
        hp = 50 + (level * 10)
        mana = 30 + (level * 5)
        attack = 15 + (level * 2)
        defense = 8 + level
        
        # Boss monsters are stronger
        if is_boss:
            hp = int(hp * 1.5)
            mana = int(mana * 1.5)
            attack = int(attack * 1.3)
            defense = int(defense * 1.3)
            
        super().__init__(name, hp, mana, attack, defense)
        self.level = level
        self.is_boss = is_boss
        self.emoji = "👾"
        self.gold_reward = level * 10 + random.randint(5, 20)
        
        # Boss monsters drop more gold
        if is_boss:
            self.gold_reward = int(self.gold_reward * 2.5)
            
    def special_attack(self, target):
        """Generic special attack for monsters"""
        if self.is_blocking:
            self.is_blocking = False
            
        mana_cost = 10 + self.level
        
        if self.mana < mana_cost:
            return super().attack(target)  # Fallback to regular attack
            
        print(f"{self.emoji} {self.name} uses a special attack!")
        self.mana -= mana_cost
        
        # Special attack has higher base damage
        attack_value = int(self.base_attack * 1.4) + random.randint(-5, 10)
        if attack_value < 0:
            attack_value = 0
            
        effective_defense = target.defense
        if target.is_blocking:
            effective_defense *= 2
            print(f"{target.emoji} {target.name} blocked and reduced damage! 🛡️")
            
        damage = max(0, attack_value - effective_defense)
        target.hp = max(0, target.hp - damage)
        
        return damage


class Slime(Monster):
    """A basic weak monster"""
    
    def __init__(self, level=1, is_boss=False):
        name = "King Slime" if is_boss else "Slime"
        super().__init__(name, level, is_boss)
        self.emoji = "🟢"
        
        # Slimes have more HP but less attack
        self.max_hp += 10
        self.hp = self.max_hp
        self.base_attack -= 2
        
    def special_attack(self, target):
        """Slime splits to attack multiple times but for less damage"""
        if self.is_blocking:
            self.is_blocking = False
            
        mana_cost = 8 + self.level
        
        if self.mana < mana_cost:
            return super().attack(target)
            
        print(f"{self.emoji} {self.name} splits and attacks multiple times!")
        self.mana -= mana_cost
        
        # Multiple small attacks
        num_attacks = 3
        total_damage = 0
        
        for i in range(num_attacks):
            attack_value = int(self.base_attack * 0.6) + random.randint(-2, 5)
            if attack_value < 0:
                attack_value = 0
                
            effective_defense = target.defense
            if target.is_blocking:
                effective_defense *= 2
                
            damage = max(0, attack_value - effective_defense)
            target.hp = max(0, target.hp - damage)
            total_damage += damage
            
            print(f"{self.emoji} Hit {i+1} deals {damage} damage!")
            
        return total_damage


class Goblin(Monster):
    """Fast monster with higher attack but lower defense"""
    
    def __init__(self, level=1, is_boss=False):
        name = "Goblin Chieftain" if is_boss else "Goblin"
        super().__init__(name, level, is_boss)
        self.emoji = "👺"
        
        # Goblins have more attack but less defense and HP
        self.base_attack += 4
        self.defense -= 2
        self.max_hp -= 10
        self.hp = self.max_hp
        
    def special_attack(self, target):
        """Goblins use sneaky strike that can ignore some defense"""
        if self.is_blocking:
            self.is_blocking = False
            
        mana_cost = 10 + self.level
        
        if self.mana < mana_cost:
            return super().attack(target)
            
        print(f"{self.emoji} {self.name} performs a sneaky strike!")
        self.mana -= mana_cost
        
        # Defense reduction
        attack_value = int(self.base_attack * 1.3) + random.randint(-3, 8)
        if attack_value < 0:
            attack_value = 0
            
        # Reduce effective defense by 50%
        effective_defense = int(target.defense * 0.5)
        if target.is_blocking:
            effective_defense = target.defense  # Still reduced even when blocking
            
        damage = max(0, attack_value - effective_defense)
        target.hp = max(0, target.hp - damage)
        
        return damage


class Skeleton(Monster):
    """Undead monster with resistance to damage"""
    
    def __init__(self, level=1, is_boss=False):
        name = "Skeleton Lord" if is_boss else "Skeleton"
        super().__init__(name, level, is_boss)
        self.emoji = "💀"
        
        # Skeletons have less HP but more defense
        self.max_hp -= 15
        self.hp = self.max_hp
        self.defense += 3
        
    def take_damage(self, amount):
        """Skeletons take reduced damage from attacks"""
        # 25% damage reduction
        reduced_amount = int(amount * 0.75)
        self.hp = max(0, self.hp - reduced_amount)
        if reduced_amount < amount:
            print(f"{self.emoji} {self.name}'s bones absorb some of the damage!")
        return reduced_amount
        
    def special_attack(self, target):
        """Bone throw attack"""
        if self.is_blocking:
            self.is_blocking = False
            
        mana_cost = 12 + self.level
        
        if self.mana < mana_cost:
            return super().attack(target)
            
        print(f"{self.emoji} {self.name} throws a volley of bones!")
        self.mana -= mana_cost
        
        attack_value = int(self.base_attack * 1.5) + random.randint(-2, 12)
        if attack_value < 0:
            attack_value = 0
            
        effective_defense = target.defense
        if target.is_blocking:
            effective_defense *= 2
            print(f"{target.emoji} {target.name} blocked and reduced damage! 🛡️")
            
        damage = max(0, attack_value - effective_defense)
        target.hp = max(0, target.hp - damage)
        
        return damage


class Dragon(Monster):
    """Powerful boss monster"""
    
    def __init__(self, level=5):
        name = f"Dragon"
        super().__init__(name, level, True)  # Always a boss
        self.emoji = "🐉"
        
        # Dragons have much better stats
        self.max_hp = int(self.max_hp * 1.2)
        self.hp = self.max_hp
        self.base_attack += 8
        self.defense += 5
        
    def special_attack(self, target):
        """Dragon breath attack that ignores defense"""
        if self.is_blocking:
            self.is_blocking = False
            
        mana_cost = 20 + self.level
        
        if self.mana < mana_cost:
            return super().attack(target)
            
        print(f"{self.emoji} {self.name} unleashes a devastating fire breath! 🔥")
        self.mana -= mana_cost
        
        # High damage attack that ignores defense
        attack_value = int(self.base_attack * 2) + random.randint(0, 15)
        
        # Dragon breath ignores half of defense even when blocking
        effective_defense = int(target.defense * 0.5)
        if target.is_blocking:
            effective_defense = target.defense  # Only normal defense when blocking
            print(f"{target.emoji} {target.name}'s block is partially effective against the flames! 🛡️🔥")
            
        damage = max(0, attack_value - effective_defense)
        target.hp = max(0, target.hp - damage)
        
        return damage


class Vampire(Monster):
    """Undead monster with lifesteal abilities"""
    
    def __init__(self, level=3, is_boss=False):
        name = "Vampire Lord" if is_boss else "Vampire"
        super().__init__(name, level, is_boss)
        self.emoji = "🧛"
        
    def attack(self, target):
        """Vampires steal life with their attacks"""
        damage = super().attack(target)
        
        # Lifesteal 20% of damage dealt
        lifesteal = int(damage * 0.2)
        if lifesteal > 0:
            self.hp = min(self.max_hp, self.hp + lifesteal)
            print(f"{self.emoji} {self.name} drains {lifesteal} health! 💉")
            
        return damage
        
    def special_attack(self, target):
        """Powerful blood drain attack"""
        if self.is_blocking:
            self.is_blocking = False
            
        mana_cost = 15 + self.level
        
        if self.mana < mana_cost:
            return super().attack(target)
            
        print(f"{self.emoji} {self.name} performs a powerful blood drain! 💉")
        self.mana -= mana_cost
        
        attack_value = int(self.base_attack * 1.6) + random.randint(-3, 10)
        if attack_value < 0:
            attack_value = 0
            
        effective_defense = target.defense
        if target.is_blocking:
            effective_defense *= 2
            print(f"{target.emoji} {target.name} blocked and reduced damage! 🛡️")
            
        damage = max(0, attack_value - effective_defense)
        target.hp = max(0, target.hp - damage)
        
        # Enhanced lifesteal (40%)
        lifesteal = int(damage * 0.4)
        if lifesteal > 0:
            self.hp = min(self.max_hp, self.hp + lifesteal)
            print(f"{self.emoji} {self.name} drains {lifesteal} health! 💉")
            
        return damage


# Monster generation functions
def get_monster_by_level(level: int, force_boss=False) -> Monster:
    """Generate an appropriate monster based on player level"""
    # Determine if this is a boss encounter
    is_boss = force_boss or random.random() < 0.1  # 10% chance for boss normally
    
    # Available monster types based on level
    available_types = []
    
    # Basic monsters always available
    available_types.append(Slime)
    available_types.append(Goblin)
    
    # Add more monster types as level increases
    if level >= 2:
        available_types.append(Skeleton)
    if level >= 3:
        available_types.append(Vampire)
    
    # Dragon is only available as a special boss encounter at higher levels
    if level >= 5 and is_boss and random.random() < 0.3:
        return Dragon(level)
        
    # Select a random monster type from available ones
    monster_class = random.choice(available_types)
    return monster_class(level, is_boss)