"""Database models for RPG game"""
import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Get database URL from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Create declarative base
Base = declarative_base()

class SavedCharacter(Base):
    """Model for saved character data"""
    __tablename__ = 'saved_characters'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    character_class = Column(String(20), nullable=False)  # Barbarian, Archer, Mage
    class_tier = Column(Integer, default=0)  # Class evolution tier (0-6)
    class_title = Column(String(50), default='')  # Title based on evolution
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    xp_to_level = Column(Integer, default=100)
    hp = Column(Integer, nullable=False)
    max_hp = Column(Integer, nullable=False)
    mana = Column(Integer, nullable=False)
    max_mana = Column(Integer, nullable=False)
    base_attack = Column(Integer, nullable=False)
    defense = Column(Integer, nullable=False)
    gold = Column(Integer, default=0)
    luck = Column(Integer, default=0)  # Hidden luck stat for shop items
    created_at = Column(DateTime, default=datetime.utcnow)
    last_saved = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # JSON fields for more complex data
    inventory_items = Column(Text, default='[]')  # JSON string of items
    equipment = Column(Text, default='{}')  # JSON string of equipped items
    skills = Column(Text, default='[]')  # JSON string of unlocked skills
    
    # Relationships
    items = relationship("SavedItem", back_populates="character", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'character_class': self.character_class,
            'class_tier': self.class_tier,
            'class_title': self.class_title,
            'level': self.level,
            'xp': self.xp,
            'xp_to_level': self.xp_to_level,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'mana': self.mana,
            'max_mana': self.max_mana,
            'base_attack': self.base_attack,
            'defense': self.defense,
            'gold': self.gold,
            'luck': self.luck,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_saved': self.last_saved.isoformat() if self.last_saved else None,
            'inventory_items': json.loads(self.inventory_items),
            'equipment': json.loads(self.equipment),
            'skills': json.loads(self.skills),
        }

class SavedItem(Base):
    """Model for saved items"""
    __tablename__ = 'saved_items'
    
    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('saved_characters.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    item_type = Column(String(20))  # weapon, armor, accessory, consumable, etc.
    value = Column(Integer, default=0)
    
    # JSON field for item-specific attributes
    attributes = Column(Text, default='{}')  # JSON string for attributes like damage, defense, etc.
    
    # Relationship
    character = relationship("SavedCharacter", back_populates="items")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'item_type': self.item_type,
            'value': self.value,
            'attributes': json.loads(self.attributes),
        }

# Create all tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    # Initialize database
    init_db()