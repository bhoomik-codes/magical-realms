import random
import time
from characters import Barbarian, Archer, Mage, DarkKnight, DarkArcher, DarkMage
from combat import Combat

class Game:
    """Main game class that manages the RPG game flow"""
    
    def __init__(self):
        self.player = None
        self.villain = None
        
    def display_intro(self):
        """Display game introduction"""
        print("\n" + "="*60)
        print("🎮  WELCOME TO THE EMOJI RPG ADVENTURE  🎮")
        print("="*60)
        print("Embark on an epic journey as a brave adventurer!")
        print("Face dangerous villains and prove your worth in combat.")
        print("-"*60)
        print("Each character class has unique abilities and attributes.")
        print("• Choose your attacks wisely")
        print("• Use special abilities when needed")
        print("• Block to reduce incoming damage")
        print("• Manage your mana for special attacks")
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
                
        print(f"\nWelcome, {self.player.emoji} {self.player.name} the {self.player.__class__.__name__}!")
        print(self.player.status())
        
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
        
    def start_combat(self):
        """Begin combat between player and villain"""
        combat = Combat(self.player, self.villain)
        combat.start_combat()
        
        combat_ended = False
        while not combat_ended:
            combat_ended = combat.execute_turn()
            
        return self.player.is_alive()
        
    def play_again(self):
        """Ask if the player wants to play another round"""
        while True:
            choice = input("\nDo you want to play again? (y/n): ").lower()
            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            else:
                print("Invalid choice. Please enter 'y' or 'n'.")
                
    def run(self):
        """Main game loop"""
        self.display_intro()
        
        playing = True
        while playing:
            self.create_player()
            self.create_villain()
            
            victory = self.start_combat()
            
            if victory:
                print("\n🎉 Congratulations on your victory! 🎉")
            else:
                print("\n😢 Better luck next time! 😢")
                
            playing = self.play_again()
            
        print("\nThank you for playing Emoji RPG Adventure! 👋")
