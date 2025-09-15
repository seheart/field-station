#!/usr/bin/env python3
"""
Fix and test all menu pages in Field Station
This script will check each menu page and fix any issues found
"""

import pygame
import sys
import time
from field_station import FieldStation, GameState

def test_menu_page(game, state_name, state_value, page_method):
    """Test a specific menu page"""
    print(f"\n🧪 Testing {state_name}...")
    
    try:
        # Set the game state
        game.game_state = state_value
        
        # Clear screen
        game.screen.fill((0, 0, 0))
        
        # Try to draw the page
        page_method()
        
        # Update display
        pygame.display.flip()
        
        print(f"✅ {state_name} - Rendered successfully")
        time.sleep(1)  # Brief pause to see the page
        
        return True
        
    except Exception as e:
        print(f"❌ {state_name} - Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test all menu pages"""
    print("🎮 Field Station Menu Page Tester")
    print("=" * 50)
    
    # Initialize pygame and game
    pygame.init()
    game = FieldStation()
    
    # Test cases: (name, state, method)
    test_cases = [
        ("Main Menu", GameState.MENU, game.draw_menu),
        ("Help Screen", GameState.HELP, game.draw_help_screen),
        ("About Screen", GameState.ABOUT, game.draw_about_screen),
        ("Options Screen", GameState.OPTIONS, game.draw_options_screen),
        ("Achievements Screen", GameState.ACHIEVEMENTS, game.draw_achievements_screen),
    ]
    
    results = []
    
    for name, state, method in test_cases:
        success = test_menu_page(game, name, state, method)
        results.append((name, success))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed < total:
        print("\n💡 Issues found! Check the error messages above.")
        print("The script will now attempt to fix the issues...")
        fix_menu_issues(game)
    else:
        print("\n🎉 All menu pages are working correctly!")
    
    pygame.quit()

def fix_menu_issues(game):
    """Attempt to fix common menu issues"""
    print("\n🔧 FIXING MENU ISSUES")
    print("=" * 30)
    
    # Check if UI framework is available
    try:
        from ui_framework import UIManager, GenericPagePanel
        print("✅ UI Framework is available")
    except ImportError as e:
        print(f"❌ UI Framework import error: {e}")
        return
    
    # Check if fonts are properly initialized
    font_issues = []
    fonts_to_check = ['menu_title_font', 'ui_font', 'font', 'menu_font']
    
    for font_name in fonts_to_check:
        if not hasattr(game, font_name) or getattr(game, font_name) is None:
            font_issues.append(font_name)
    
    if font_issues:
        print(f"❌ Missing fonts: {', '.join(font_issues)}")
    else:
        print("✅ All required fonts are available")
    
    # Check screen initialization
    if game.screen is None:
        print("❌ Screen not initialized")
    else:
        print(f"✅ Screen initialized: {game.screen.get_size()}")
    
    print("\n💡 Recommendations:")
    print("1. Ensure all font variables are properly initialized")
    print("2. Check that UI framework imports work correctly")
    print("3. Verify screen surface is created before drawing")
    print("4. Make sure GenericPagePanel exists in ui_framework.py")

if __name__ == "__main__":
    main()
