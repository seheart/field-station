#!/usr/bin/env python3
"""
Verify that all page titles have icons
"""

import pygame
import sys
import os
import time
from enum import Enum
from pathlib import Path

# Add the field_station directory to sys.path so we can import field_station
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from field_station import FieldStation, GameState
except ImportError as e:
    print(f"Error importing field_station: {e}")
    sys.exit(1)

def take_screenshot(game, filename, description):
    """Take a screenshot and save it"""
    print(f"Taking screenshot: {description}")
    
    # Save screenshot
    screenshot_path = f"/tmp/{filename}"
    pygame.image.save(game.screen, screenshot_path)
    print(f"Screenshot saved: {screenshot_path}")

def main():
    print("Starting page icon verification...")
    
    # Initialize the game
    game = FieldStation()
    
    # Wait for game to fully initialize
    time.sleep(1)
    
    # Keep track of pages to test
    pages_to_test = [
        (GameState.FARM_SETUP, "new_game_with_icon.png", "New Game page with + icon"),
        (GameState.ACHIEVEMENTS, "achievements_with_icon.png", "Achievements page with * icon"),  
        (GameState.HELP, "help_with_icon.png", "Help page with ? icon"),
        (GameState.OPTIONS, "settings_with_icon.png", "Settings page with @ icon"),
        (GameState.ABOUT, "about_with_icon.png", "About page with i icon"),
    ]
    
    try:
        for page_state, filename, description in pages_to_test:
            print(f"\n--- Testing {description} ---")
            
            # Go to the page
            game.game_state = page_state
            
            # Wait a moment for the page to render
            time.sleep(0.5)
            
            # Handle the display update
            game.handle_events()
            game.update()
            game.draw()
            pygame.display.flip()
            
            # Take screenshot
            take_screenshot(game, filename, description)
            
            # Return to main menu for next test
            game.game_state = GameState.MENU
            time.sleep(0.5)
        
        print("\n=== Icon Verification Complete ===")
        print("All page screenshots taken. Check:")
        for _, filename, _ in pages_to_test:
            print(f"  /tmp/{filename}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    
    finally:
        # Cleanup
        pygame.quit()

if __name__ == "__main__":
    main()