#!/usr/bin/env python3
"""
Visual inspection of all menu pages
This script will display each menu page for manual inspection
"""

import pygame
import sys
import time
from field_station import FieldStation, GameState

def show_page(game, page_name, state, draw_method, duration=3):
    """Show a page for visual inspection"""
    print(f"\n🖼️ Showing {page_name}...")
    
    # Set state and draw
    game.game_state = state
    game.screen.fill((0, 0, 0))
    
    try:
        draw_method()
        pygame.display.flip()
        
        print(f"   ✅ {page_name} displayed")
        print(f"   ⏱️ Showing for {duration} seconds...")
        
        # Wait for the specified duration
        start_time = time.time()
        while time.time() - start_time < duration:
            # Handle events to keep window responsive
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        print("   ⏭️ Skipping to next page...")
                        return True
                    elif event.key == pygame.K_ESCAPE:
                        print("   🛑 Stopping inspection...")
                        return False
            
            time.sleep(0.1)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error displaying {page_name}: {str(e)}")
        return True

def main():
    """Visual inspection of all menu pages"""
    print("👀 Field Station Visual Menu Inspection")
    print("=" * 50)
    print("Instructions:")
    print("  • Each page will show for 3 seconds")
    print("  • Press SPACE to skip to next page")
    print("  • Press ESC to stop inspection")
    print("  • Close window to exit")
    print("=" * 50)
    
    pygame.init()
    game = FieldStation()
    
    # Set a reasonable window size for inspection
    screen_info = pygame.display.Info()
    print(f"Screen resolution: {screen_info.current_w}x{screen_info.current_h}")
    
    # Pages to inspect
    pages = [
        ("Main Menu", GameState.MENU, game.draw_menu),
        ("Help Screen", GameState.HELP, game.draw_help_screen),
        ("About Screen", GameState.ABOUT, game.draw_about_screen), 
        ("Options Screen", GameState.OPTIONS, game.draw_options_screen),
        ("Achievements Screen", GameState.ACHIEVEMENTS, game.draw_achievements_screen),
    ]
    
    print("\n🎬 Starting visual inspection...")
    
    for page_name, state, draw_method in pages:
        if not show_page(game, page_name, state, draw_method):
            break
    
    # Show summary
    print("\n" + "=" * 50)
    print("📋 VISUAL INSPECTION CHECKLIST")
    print("=" * 50)
    print("For each page, verify:")
    print("  ✓ Title is visible and properly positioned")
    print("  ✓ Content is readable and well-formatted")
    print("  ✓ Buttons are visible and properly styled")
    print("  ✓ Colors and fonts look consistent")
    print("  ✓ Text doesn't overflow or get cut off")
    print("  ✓ Layout looks professional and organized")
    print("  ✓ Background gradient is visible")
    print("  ✓ UI elements are properly aligned")
    print("\n🎯 Issues to look for:")
    print("  ❌ Missing or corrupted text")
    print("  ❌ Overlapping UI elements")
    print("  ❌ Inconsistent fonts or colors")
    print("  ❌ Buttons that look broken or misaligned")
    print("  ❌ Poor contrast or readability")
    
    pygame.quit()
    print(f"\n✨ Visual inspection complete!")

if __name__ == "__main__":
    main()
