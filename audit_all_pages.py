#!/usr/bin/env python3
"""Comprehensive audit of all menu pages"""

import pygame
import sys
import time
import os
from field_station import FieldStation, GameState

def take_screenshot(screen, filename, description):
    """Take a screenshot and save it"""
    pygame.image.save(screen, filename)
    print(f"✓ Screenshot saved: {filename} - {description}")

def audit_all_pages():
    """Audit each menu page systematically"""
    print("=" * 60)
    print("COMPREHENSIVE FIELD STATION PAGE AUDIT")
    print("=" * 60)
    
    # Initialize the game
    game = FieldStation()
    clock = pygame.time.Clock()
    
    # Test each page
    pages_to_test = [
        ("MENU", GameState.MENU, "Main Menu"),
        ("FARM_SETUP", GameState.FARM_SETUP, "New Game / Farm Setup"),
        ("ACHIEVEMENTS", GameState.ACHIEVEMENTS, "Achievements"),
        ("HELP", GameState.HELP, "Help"),
        ("OPTIONS", GameState.OPTIONS, "Settings"),
        ("ABOUT", GameState.ABOUT, "About"),
    ]
    
    for state_name, state, description in pages_to_test:
        print(f"\n🔍 TESTING: {description}")
        print("-" * 40)
        
        # Set the game state
        game.game_state = state
        if state == GameState.MENU:
            game.update_menu_options()
        elif state == GameState.OPTIONS:
            game.update_options_items()
        
        # Render the page
        try:
            # Clear screen
            game.screen.fill((0, 0, 0))
            
            # Draw the appropriate screen
            if state == GameState.MENU:
                game.draw_menu()
            elif state == GameState.FARM_SETUP:
                game.draw_farm_setup()
            elif state == GameState.ACHIEVEMENTS:
                game.draw_achievements_screen()
            elif state == GameState.HELP:
                game.draw_help_screen()
            elif state == GameState.OPTIONS:
                game.draw_options_screen()
            elif state == GameState.ABOUT:
                game.draw_about_screen()
            
            pygame.display.flip()
            
            # Take screenshot
            screenshot_path = f"/tmp/audit_{state_name.lower()}.png"
            take_screenshot(game.screen, screenshot_path, description)
            
            # Test basic functionality
            print(f"   State: {state}")
            print(f"   Screen size: {game.screen.get_size()}")
            
            # Check for any obvious issues
            issues = []
            
            # Check if screen is mostly black (might indicate rendering issue)
            screen_array = pygame.surfarray.array3d(game.screen)
            if screen_array.mean() < 10:  # Very dark screen
                issues.append("Screen appears mostly black - possible rendering issue")
            
            if issues:
                print(f"   ⚠️  ISSUES FOUND:")
                for issue in issues:
                    print(f"      - {issue}")
            else:
                print(f"   ✅ Basic rendering OK")
            
            # Small delay for visual feedback
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            continue
    
    print(f"\n{'=' * 60}")
    print("AUDIT COMPLETE - Check screenshots in /tmp/")
    print("Files created:")
    for state_name, _, description in pages_to_test:
        filename = f"audit_{state_name.lower()}.png"
        print(f"  - {filename} ({description})")
    print("=" * 60)
    
    # Keep window open briefly
    time.sleep(1)
    pygame.quit()

if __name__ == "__main__":
    audit_all_pages()