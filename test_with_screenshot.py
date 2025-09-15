#!/usr/bin/env python3
"""Test the menu display and take a screenshot"""

import pygame
import sys
import time
import os

# Import the game
from field_station import FieldStation, GameState

def test_menu_with_screenshot():
    """Run the game and take a screenshot of the menu"""
    print("Starting Field Station with screenshot test...")
    
    # Initialize the game
    game = FieldStation()
    
    # Ensure we're in menu state
    game.game_state = GameState.MENU
    game.update_menu_options()
    
    print(f"Menu options: {game.menu_options}")
    
    # Main game loop for a few seconds
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    screenshot_taken = False
    
    while pygame.time.get_ticks() - start_time < 5000:  # Run for 5 seconds
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        # Draw the menu
        game.draw_menu()
        pygame.display.flip()
        
        # Take screenshot after 1 second
        if not screenshot_taken and pygame.time.get_ticks() - start_time > 1000:
            print("Taking screenshot...")
            pygame.image.save(game.screen, "/tmp/field_station_menu_test.png")
            print("Screenshot saved to /tmp/field_station_menu_test.png")
            screenshot_taken = True
        
        clock.tick(60)
    
    print("Test completed!")
    pygame.quit()

if __name__ == "__main__":
    test_menu_with_screenshot()