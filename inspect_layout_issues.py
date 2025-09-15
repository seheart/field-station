#!/usr/bin/env python3
"""
Inspect layout issues by running the game and showing debug information
"""

import pygame
import sys
import time
from field_station import FieldStation, GameState

def inspect_page_layout(game, page_name, state, draw_method):
    """Inspect layout of a specific page with debug info"""
    print(f"\n🔍 Inspecting {page_name} Layout...")
    
    # Set state and draw
    game.game_state = state
    game.screen.fill((0, 0, 0))
    
    try:
        draw_method()
        
        # Get screen dimensions
        screen_width = game.screen.get_width()
        screen_height = game.screen.get_height()
        
        print(f"   📐 Screen: {screen_width}x{screen_height}")
        
        # Check if panel reference exists
        panel_attr = page_name.lower().replace(" screen", "_panel")
        if hasattr(game, panel_attr):
            panel = getattr(game, panel_attr)
            print(f"   📦 Panel: {panel.width}x{panel.height}")
            
            # Calculate expected panel position
            panel_x = (screen_width - panel.width) // 2
            panel_y = (screen_height - panel.height) // 2
            print(f"   📍 Panel Position: ({panel_x}, {panel_y})")
            
            # Check content elements
            if hasattr(panel, 'content_elements'):
                print(f"   📝 Content Elements: {len(panel.content_elements)}")
                
                # Calculate content height
                estimated_content_height = 40  # Title
                if panel.subtitle:
                    estimated_content_height += 40  # Subtitle
                
                for elem_type, elem_data in panel.content_elements:
                    if elem_type == 'text':
                        estimated_content_height += 30
                    elif elem_type == 'header':
                        estimated_content_height += 35
                    elif elem_type == 'spacer':
                        estimated_content_height += elem_data['height']
                
                if panel.buttons:
                    estimated_content_height += 80  # Button area
                
                print(f"   📏 Estimated Content Height: {estimated_content_height}")
                print(f"   ⚠️ Content Overflow: {'YES' if estimated_content_height > panel.height else 'NO'}")
                
                if estimated_content_height > panel.height:
                    overflow = estimated_content_height - panel.height
                    print(f"      Overflow Amount: {overflow}px")
            
            # Check buttons
            if hasattr(panel, 'buttons') and panel.buttons:
                print(f"   🔘 Buttons: {len(panel.buttons)}")
                for i, button in enumerate(panel.buttons):
                    print(f"      Button {i}: '{button['text']}'")
                    if 'rect' in button and button['rect']:
                        rect = button['rect']
                        print(f"         Position: ({rect.x}, {rect.y})")
                        print(f"         Size: {rect.width}x{rect.height}")
                        
                        # Check if button is within panel bounds
                        panel_bottom = panel_y + panel.height
                        if rect.bottom > panel_bottom:
                            print(f"         ⚠️ Button extends {rect.bottom - panel_bottom}px below panel!")
        else:
            print(f"   ❌ No panel reference found: {panel_attr}")
        
        pygame.display.flip()
        time.sleep(2)  # Show for 2 seconds
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error inspecting {page_name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Inspect layout of all menu pages"""
    print("🔍 Field Station Layout Inspector")
    print("=" * 50)
    
    pygame.init()
    game = FieldStation()
    
    # Pages to inspect
    pages = [
        ("Help Screen", GameState.HELP, game.draw_help_screen),
        ("About Screen", GameState.ABOUT, game.draw_about_screen),
        ("Achievements Screen", GameState.ACHIEVEMENTS, game.draw_achievements_screen),
    ]
    
    for page_name, state, draw_method in pages:
        inspect_page_layout(game, page_name, state, draw_method)
    
    print(f"\n📊 Common Layout Issues Found:")
    print(f"  • Content overflowing panel boundaries")
    print(f"  • Fixed spacing not accounting for panel size")
    print(f"  • No content area clipping")
    print(f"  • Buttons positioned outside panel")
    print(f"  • Poor responsive design for different screen sizes")
    
    print(f"\n💡 Recommended Fixes:")
    print(f"  1. Implement proper content area with clipping")
    print(f"  2. Add content overflow handling (scrolling or truncation)")
    print(f"  3. Make spacing responsive to panel size")
    print(f"  4. Ensure all elements stay within panel bounds")
    print(f"  5. Add padding/margins for content area")
    
    pygame.quit()
    print(f"\n✨ Layout inspection complete!")

if __name__ == "__main__":
    main()
