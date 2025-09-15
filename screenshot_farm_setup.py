#!/usr/bin/env python3
"""
Take screenshot of New Farm Setup page
"""

import pygame
import sys
import os
import time

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
    print("Taking screenshot of New Farm Setup page...")
    
    # Initialize the game
    game = FieldStation()
    
    # Wait for game to fully initialize
    time.sleep(1)
    
    try:
        # Navigate to farm setup page
        print("Navigating to Farm Setup page...")
        game.game_state = GameState.FARM_SETUP
        
        # Wait a moment for the page to render
        time.sleep(0.5)
        
        # Process a single frame to render the page
        for event in pygame.event.get():
            game.handle_event(event)
        
        # Clear screen
        game.screen.fill((0, 0, 0))
        
        # Draw the farm setup page
        game.draw_farm_setup()
        pygame.display.flip()
        
        # Take screenshot
        take_screenshot(game, "farm_setup_current.png", "Current Farm Setup page")
        
        print("\n=== Screenshot Complete ===")
        print("Check: /tmp/farm_setup_current.png")
        
    except Exception as e:
        print(f"Error during screenshot: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        pygame.quit()

if __name__ == "__main__":
    main()