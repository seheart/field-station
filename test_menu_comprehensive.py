#!/usr/bin/env python3
"""Comprehensive test of menu functionality with emojis"""

import pygame
import sys
import time
from field_station import FieldStation

def test_menu_clicks():
    """Test clicking each menu item"""
    print("Starting comprehensive menu test...")
    print("=" * 60)
    
    # Initialize the game
    game = FieldStation()
    
    # Ensure we're in menu state
    from field_station import GameState
    game.game_state = GameState.MENU
    game.update_menu_options()
    
    print(f"Menu options: {game.menu_options}")
    print(f"Number of options: {len(game.menu_options)}")
    
    # Draw the menu once to populate button rects
    game.draw_menu()
    pygame.display.flip()
    
    # Check if button rects are populated
    if hasattr(game, 'main_menu_button_rects'):
        print(f"\nButton rectangles created: {len(game.main_menu_button_rects)}")
        for i, rect in game.main_menu_button_rects.items():
            option = game.menu_options[i] if i < len(game.menu_options) else "Unknown"
            print(f"  [{i}] {option}: {rect}")
    else:
        print("\nERROR: main_menu_button_rects not created!")
        return False
    
    # Test each button click
    print("\nSimulating clicks on each button:")
    print("-" * 40)
    
    for i, option in enumerate(game.menu_options):
        if i in game.main_menu_button_rects:
            rect = game.main_menu_button_rects[i]
            center = rect.center
            
            # Create a mouse click event at the button center
            click_event = pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {'pos': center, 'button': 1}
            )
            
            # Store initial state
            initial_state = game.game_state
            
            # Handle the click
            result = game.handle_menu_event(click_event)
            
            # Check if state changed or action was taken
            new_state = game.game_state
            
            print(f"  {option}:")
            print(f"    Click pos: {center}")
            print(f"    Rect: {rect}")
            print(f"    State change: {initial_state} -> {new_state}")
            print(f"    Handler returned: {result}")
            
            # Reset to menu for next test
            game.game_state = GameState.MENU
            
            # Small delay to see visual feedback
            game.draw_menu()
            pygame.display.flip()
            time.sleep(0.1)
        else:
            print(f"  {option}: NO BUTTON RECT FOUND!")
    
    print("\n" + "=" * 60)
    print("Menu test completed!")
    
    # Keep window open briefly
    time.sleep(1)
    
    pygame.quit()
    return True

if __name__ == "__main__":
    success = test_menu_clicks()
    sys.exit(0 if success else 1)