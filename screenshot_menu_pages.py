#!/usr/bin/env python3
"""
Take screenshots of all menu pages to visually inspect layout issues
"""

import pygame
import sys
import time
from field_station import FieldStation, GameState

def take_screenshot(game, page_name, state, draw_method, filename):
    """Take a screenshot of a specific page"""
    print(f"📸 Taking screenshot of {page_name}...")
    
    # Set state and draw
    game.game_state = state
    game.screen.fill((0, 0, 0))
    
    try:
        draw_method()
        pygame.display.flip()
        
        # Save screenshot
        pygame.image.save(game.screen, filename)
        print(f"   ✅ Screenshot saved: {filename}")
        
        # Brief pause to see the page
        time.sleep(1)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error taking screenshot of {page_name}: {str(e)}")
        return False

def main():
    """Take screenshots of all menu pages"""
    print("📷 Field Station Menu Screenshot Tool")
    print("=" * 50)
    print("Taking screenshots to visually inspect layout and spacing...")
    print("=" * 50)
    
    pygame.init()
    game = FieldStation()
    
    # Pages to screenshot
    pages = [
        ("Main Menu", GameState.MENU, game.draw_menu, "screenshot_main_menu.png"),
        ("Help Screen", GameState.HELP, game.draw_help_screen, "screenshot_help.png"),
        ("About Screen", GameState.ABOUT, game.draw_about_screen, "screenshot_about.png"), 
        ("Options Screen", GameState.OPTIONS, game.draw_options_screen, "screenshot_options.png"),
        ("Achievements Screen", GameState.ACHIEVEMENTS, game.draw_achievements_screen, "screenshot_achievements.png"),
    ]
    
    successful = 0
    total = len(pages)
    
    for page_name, state, draw_method, filename in pages:
        if take_screenshot(game, page_name, state, draw_method, filename):
            successful += 1
    
    print(f"\n📊 Screenshot Results: {successful}/{total} successful")
    print(f"\nScreenshots saved in current directory:")
    for _, _, _, filename in pages:
        print(f"  • {filename}")
    
    print(f"\n🔍 Now manually inspect each screenshot for:")
    print(f"  ❌ Text overlapping or cut off")
    print(f"  ❌ Poor alignment or centering")
    print(f"  ❌ Inconsistent spacing")
    print(f"  ❌ UI elements extending beyond panel boundaries")
    print(f"  ❌ Buttons positioned incorrectly")
    print(f"  ❌ Title or content positioning issues")
    
    pygame.quit()
    print(f"\n✨ Screenshot capture complete!")

if __name__ == "__main__":
    main()
