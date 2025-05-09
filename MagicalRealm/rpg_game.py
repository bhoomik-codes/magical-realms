#!/usr/bin/env python3
import os
from new_game import Game
from db_models import init_db

def main():
    """Entry point for the RPG game"""
    # Initialize database
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Warning: Error initializing database: {e}")
        print("Game will run, but character saving/loading will be disabled.")
    
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
