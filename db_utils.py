"""Utility functions for database operations"""
import json
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from db_models import session, SavedCharacter, SavedItem, init_db
from items import Item, Equipment, Consumable, Weapon, Armor, Accessory, HealthPotion, ManaPotion, StrengthElixir
from characters import Barbarian, Archer, Mage

# Initialize the database
init_db()

def save_character(character, overwrite=False):
    """
    Save character data to database
    
    Args:
        character: Character object to save
        overwrite: Whether to overwrite existing character with same name
    
    Returns:
        SavedCharacter object if successful, None otherwise
    """
    try:
        # Check if character with same name exists
        existing_character = session.query(SavedCharacter).filter_by(
            name=character.name,
            character_class=character.__class__.__name__,
            is_active=True
        ).first()
        
        if existing_character and not overwrite:
            return None  # Don't overwrite
        
        if existing_character:
            # Update existing character
            existing_character.level = character.level
            existing_character.xp = character.xp
            existing_character.xp_to_level = character.xp_to_level
            existing_character.hp = character.hp
            existing_character.max_hp = character.max_hp
            existing_character.mana = character.mana
            existing_character.max_mana = character.max_mana
            existing_character.base_attack = character.base_attack
            existing_character.defense = character.defense
            existing_character.luck = character.luck if hasattr(character, 'luck') else 0
            existing_character.last_saved = datetime.utcnow()
            
            # Save inventory gold
            if hasattr(character, 'inventory') and character.inventory:
                existing_character.gold = character.inventory.gold
                
                # Save inventory items
                inventory_items = []
                for item in character.inventory.items:
                    item_data = {
                        'name': item.name,
                        'description': item.description,
                        'value': item.value,
                    }
                    
                    # Add type-specific data
                    if isinstance(item, Weapon):
                        item_data['type'] = 'weapon'
                        item_data['attack_boost'] = item.stat_boost.get('attack', 0)
                    elif isinstance(item, Armor):
                        item_data['type'] = 'armor'
                        item_data['defense_boost'] = item.stat_boost.get('defense', 0)
                    elif isinstance(item, Accessory):
                        item_data['type'] = 'accessory'
                        item_data['stat_boosts'] = item.stat_boost
                    elif isinstance(item, HealthPotion):
                        item_data['type'] = 'health_potion'
                        item_data['size'] = item.size
                    elif isinstance(item, ManaPotion):
                        item_data['type'] = 'mana_potion'
                        item_data['size'] = item.size
                    elif isinstance(item, StrengthElixir):
                        item_data['type'] = 'strength_elixir'
                    
                    inventory_items.append(item_data)
                
                existing_character.inventory_items = json.dumps(inventory_items)
            
            # Save equipment
            if hasattr(character, 'equipment') and character.equipment:
                equipment_data = {}
                for slot, item in character.equipment.items():
                    item_data = {
                        'name': item.name,
                        'description': item.description,
                        'value': item.value,
                    }
                    
                    # Add type-specific data
                    if isinstance(item, Weapon):
                        item_data['type'] = 'weapon'
                        item_data['attack_boost'] = item.stat_boost.get('attack', 0)
                    elif isinstance(item, Armor):
                        item_data['type'] = 'armor'
                        item_data['defense_boost'] = item.stat_boost.get('defense', 0)
                    elif isinstance(item, Accessory):
                        item_data['type'] = 'accessory'
                        item_data['stat_boosts'] = item.stat_boost
                    
                    equipment_data[slot] = item_data
                
                existing_character.equipment = json.dumps(equipment_data)
            
            saved_character = existing_character
        else:
            # Create new character record
            inventory_items = []
            equipment_data = {}
            gold = 0
            
            # Save inventory if it exists
            if hasattr(character, 'inventory') and character.inventory:
                gold = character.inventory.gold
                
                # Save inventory items
                for item in character.inventory.items:
                    item_data = {
                        'name': item.name,
                        'description': item.description,
                        'value': item.value,
                    }
                    
                    # Add type-specific data
                    if isinstance(item, Weapon):
                        item_data['type'] = 'weapon'
                        item_data['attack_boost'] = item.stat_boost.get('attack', 0)
                    elif isinstance(item, Armor):
                        item_data['type'] = 'armor'
                        item_data['defense_boost'] = item.stat_boost.get('defense', 0)
                    elif isinstance(item, Accessory):
                        item_data['type'] = 'accessory'
                        item_data['stat_boosts'] = item.stat_boost
                    elif isinstance(item, HealthPotion):
                        item_data['type'] = 'health_potion'
                        item_data['size'] = item.size
                    elif isinstance(item, ManaPotion):
                        item_data['type'] = 'mana_potion'
                        item_data['size'] = item.size
                    elif isinstance(item, StrengthElixir):
                        item_data['type'] = 'strength_elixir'
                    
                    inventory_items.append(item_data)
            
            # Save equipment if it exists
            if hasattr(character, 'equipment') and character.equipment:
                for slot, item in character.equipment.items():
                    item_data = {
                        'name': item.name,
                        'description': item.description,
                        'value': item.value,
                    }
                    
                    # Add type-specific data
                    if isinstance(item, Weapon):
                        item_data['type'] = 'weapon'
                        item_data['attack_boost'] = item.stat_boost.get('attack', 0)
                    elif isinstance(item, Armor):
                        item_data['type'] = 'armor'
                        item_data['defense_boost'] = item.stat_boost.get('defense', 0)
                    elif isinstance(item, Accessory):
                        item_data['type'] = 'accessory'
                        item_data['stat_boosts'] = item.stat_boost
                    
                    equipment_data[slot] = item_data
            
            saved_character = SavedCharacter(
                name=character.name,
                character_class=character.__class__.__name__,
                level=character.level,
                xp=character.xp,
                xp_to_level=character.xp_to_level,
                hp=character.hp,
                max_hp=character.max_hp,
                mana=character.mana,
                max_mana=character.max_mana,
                base_attack=character.base_attack,
                defense=character.defense,
                gold=gold,
                luck=character.luck if hasattr(character, 'luck') else 0,
                inventory_items=json.dumps(inventory_items),
                equipment=json.dumps(equipment_data)
            )
            session.add(saved_character)
        
        session.commit()
        return saved_character
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return None
    except Exception as e:
        session.rollback()
        print(f"Error saving character: {e}")
        return None

def load_character(character_id):
    """
    Load character data from database
    
    Args:
        character_id: ID of character to load
    
    Returns:
        Character object if successful, None otherwise
    """
    try:
        saved_character = session.query(SavedCharacter).filter_by(
            id=character_id,
            is_active=True
        ).first()
        
        if not saved_character:
            return None
        
        # Create appropriate character class
        if saved_character.character_class == "Barbarian":
            character = Barbarian(saved_character.name)
        elif saved_character.character_class == "Archer":
            character = Archer(saved_character.name)
        elif saved_character.character_class == "Mage":
            character = Mage(saved_character.name)
        else:
            return None
        
        # Load basic stats
        character.level = saved_character.level
        character.xp = saved_character.xp
        character.xp_to_level = saved_character.xp_to_level
        character.hp = saved_character.hp
        character.max_hp = saved_character.max_hp
        character.mana = saved_character.mana
        character.max_mana = saved_character.max_mana
        character.base_attack = saved_character.base_attack
        character.defense = saved_character.defense
        character.luck = saved_character.luck
        
        # Load gold
        character.inventory.gold = saved_character.gold
        
        # Clear default inventory items
        character.inventory.items = []
        
        # Load inventory items
        inventory_items = json.loads(saved_character.inventory_items)
        for item_data in inventory_items:
            item = None
            
            if item_data.get('type') == 'weapon':
                item = Weapon(
                    item_data['name'],
                    item_data['description'],
                    item_data['value'],
                    item_data.get('attack_boost', 0)
                )
            elif item_data.get('type') == 'armor':
                item = Armor(
                    item_data['name'],
                    item_data['description'],
                    item_data['value'],
                    item_data.get('defense_boost', 0)
                )
            elif item_data.get('type') == 'accessory':
                item = Accessory(
                    item_data['name'],
                    item_data['description'],
                    item_data['value'],
                    item_data.get('stat_boosts', {})
                )
            elif item_data.get('type') == 'health_potion':
                item = HealthPotion(item_data.get('size', 'small'))
            elif item_data.get('type') == 'mana_potion':
                item = ManaPotion(item_data.get('size', 'small'))
            elif item_data.get('type') == 'strength_elixir':
                item = StrengthElixir()
            
            if item:
                character.inventory.add_item(item)
        
        # Load equipment
        equipment_data = json.loads(saved_character.equipment)
        for slot, item_data in equipment_data.items():
            item = None
            
            if item_data.get('type') == 'weapon':
                item = Weapon(
                    item_data['name'],
                    item_data['description'],
                    item_data['value'],
                    item_data.get('attack_boost', 0)
                )
            elif item_data.get('type') == 'armor':
                item = Armor(
                    item_data['name'],
                    item_data['description'],
                    item_data['value'],
                    item_data.get('defense_boost', 0)
                )
            elif item_data.get('type') == 'accessory':
                item = Accessory(
                    item_data['name'],
                    item_data['description'],
                    item_data['value'],
                    item_data.get('stat_boosts', {})
                )
            
            if item:
                # Skip the normal equip method to avoid duplicate stat boosts
                # Just put the item in the equipment dict
                character.equipment[slot] = item
                
        return character
    
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Error loading character: {e}")
        return None

def get_all_characters():
    """
    Get all saved characters
    
    Returns:
        List of SavedCharacter objects
    """
    try:
        return session.query(SavedCharacter).filter_by(is_active=True).all()
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return []

def delete_character(character_id):
    """
    Delete character by ID (soft delete)
    
    Args:
        character_id: ID of character to delete
    
    Returns:
        True if successful, False otherwise
    """
    try:
        saved_character = session.query(SavedCharacter).filter_by(
            id=character_id
        ).first()
        
        if not saved_character:
            return False
        
        # Soft delete
        saved_character.is_active = False
        session.commit()
        return True
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error: {e}")
        return False
    except Exception as e:
        session.rollback()
        print(f"Error deleting character: {e}")
        return False