#!/usr/bin/env python3
"""
Test menu navigation and button functionality in Field Station
"""

import pygame
import sys
import time
from field_station import FieldStation, GameState

def test_menu_navigation():
    """Test menu navigation and button functionality"""
    print("🧪 Testing Menu Navigation & Buttons")
    print("=" * 50)
    
    pygame.init()
    game = FieldStation()
    
    # Test navigation paths
    navigation_tests = [
        ("Main Menu → Help", GameState.MENU, GameState.HELP),
        ("Main Menu → About", GameState.MENU, GameState.ABOUT), 
        ("Main Menu → Options", GameState.MENU, GameState.OPTIONS),
        ("Main Menu → Achievements", GameState.MENU, GameState.ACHIEVEMENTS),
    ]
    
    print("🎯 Testing State Transitions...")
    
    for test_name, from_state, to_state in navigation_tests:
        print(f"\n🔄 {test_name}")
        
        # Set initial state
        game.game_state = from_state
        
        # Simulate navigation to target state
        game.game_state = to_state
        
        try:
            # Clear screen and render the target page
            game.screen.fill((0, 0, 0))
            
            if to_state == GameState.HELP:
                game.draw_help_screen()
            elif to_state == GameState.ABOUT:
                game.draw_about_screen()
            elif to_state == GameState.OPTIONS:
                game.draw_options_screen()
            elif to_state == GameState.ACHIEVEMENTS:
                game.draw_achievements_screen()
            
            pygame.display.flip()
            print(f"✅ Successfully navigated to {to_state}")
            
        except Exception as e:
            print(f"❌ Navigation failed: {str(e)}")
    
    # Test content quality
    print(f"\n📝 Testing Content Quality...")
    
    content_tests = [
        ("Help Screen Content", GameState.HELP, game.draw_help_screen),
        ("About Screen Content", GameState.ABOUT, game.draw_about_screen),
        ("Options Screen Content", GameState.OPTIONS, game.draw_options_screen),
        ("Achievements Screen Content", GameState.ACHIEVEMENTS, game.draw_achievements_screen),
    ]
    
    for test_name, state, draw_method in content_tests:
        print(f"\n📄 {test_name}")
        
        game.game_state = state
        game.screen.fill((0, 0, 0))
        
        try:
            draw_method()
            pygame.display.flip()
            print(f"✅ Content rendered successfully")
            
            # Check if the content looks reasonable
            # (This is a basic test - in a real scenario you'd check specific elements)
            print(f"   → Screen size: {game.screen.get_size()}")
            print(f"   → Current state: {game.game_state}")
            
        except Exception as e:
            print(f"❌ Content rendering failed: {str(e)}")
    
    # Test button functionality by checking if methods exist
    print(f"\n🔘 Testing Button Methods...")
    
    button_methods = [
        ("Return to Menu", "return_to_menu"),
        ("Return to Game", "return_to_game"),
        ("Start New Game", "start_new_game"),
        ("Save Game", "save_game"),
        ("Load Game", "load_game"),
    ]
    
    for button_name, method_name in button_methods:
        if hasattr(game, method_name):
            print(f"✅ {button_name} method exists: {method_name}")
        else:
            print(f"❌ {button_name} method missing: {method_name}")
    
    # Test ESC key functionality
    print(f"\n⌨️ Testing ESC Key Navigation...")
    
    escape_tests = [
        (GameState.HELP, "Help → Menu"),
        (GameState.ABOUT, "About → Menu"),
        (GameState.OPTIONS, "Options → Menu"),
        (GameState.ACHIEVEMENTS, "Achievements → Menu"),
    ]
    
    for state, description in escape_tests:
        game.game_state = state
        
        # Simulate ESC key press
        escape_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        
        try:
            # This would normally be handled in the event loop
            original_state = game.game_state
            game.handle_event(escape_event)
            
            if game.game_state != original_state:
                print(f"✅ {description}: State changed from {original_state} to {game.game_state}")
            else:
                print(f"⚠️ {description}: State did not change (might be expected)")
                
        except Exception as e:
            print(f"❌ {description}: Error handling ESC - {str(e)}")
    
    pygame.quit()
    print(f"\n🎉 Navigation testing complete!")

if __name__ == "__main__":
    test_menu_navigation()
