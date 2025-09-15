#!/usr/bin/env python3
"""
Comprehensive test of ALL menu pages in Field Station
"""

import pygame
import sys
import time
from field_station import FieldStation, GameState

def test_all_pages():
    """Test every single page in the game"""
    print("🔍 COMPREHENSIVE PAGE TESTING - ALL PAGES")
    print("=" * 60)
    
    pygame.init()
    game = FieldStation()
    
    # ALL pages that exist in the game
    all_pages = [
        ("Main Menu", GameState.MENU, game.draw_menu),
        ("Farm Setup", GameState.FARM_SETUP, game.draw_farm_setup),
        ("Help Screen", GameState.HELP, game.draw_help_screen),
        ("About Screen", GameState.ABOUT, game.draw_about_screen),
        ("Options Screen", GameState.OPTIONS, game.draw_options_screen),
        ("Achievements Screen", GameState.ACHIEVEMENTS, game.draw_achievements_screen),
        ("Load Screen", GameState.LOAD, lambda: game.draw_placeholder_screen("LOAD GAME")),
        ("Tutorials/Interface", GameState.TUTORIALS, game.draw_interface_controls),
        ("Pause Menu", GameState.PAUSE_MENU, game.draw_pause_menu),
    ]
    
    results = []
    
    for page_name, state, draw_method in all_pages:
        print(f"\n🧪 Testing {page_name}...")
        
        # Set state
        game.game_state = state
        game.screen.fill((0, 0, 0))
        
        try:
            # Special handling for pause menu (needs game background)
            if state == GameState.PAUSE_MENU:
                game.screen.fill(game.get_seasonal_background_color())
                # Don't draw full game state, just the pause menu
            
            draw_method()
            pygame.display.flip()
            
            print(f"   ✅ {page_name}: Rendered successfully")
            
            # Check for layout issues
            layout_issues = []
            
            # Check if it's using framework
            uses_framework = False
            panel_attr = None
            
            if "Screen" in page_name and page_name not in ["Load Screen"]:
                panel_attr = page_name.lower().replace(" screen", "_panel")
                if hasattr(game, panel_attr):
                    uses_framework = True
                    panel = getattr(game, panel_attr)
                    
                    # Check panel bounds
                    screen_width = game.screen.get_width()
                    screen_height = game.screen.get_height()
                    panel_x = (screen_width - panel.width) // 2
                    panel_y = (screen_height - panel.height) // 2
                    
                    print(f"   📦 Panel: {panel.width}x{panel.height} at ({panel_x}, {panel_y})")
                    
                    # Check buttons
                    if hasattr(panel, 'buttons') and panel.buttons:
                        for button in panel.buttons:
                            if 'rect' in button and button['rect']:
                                btn_rect = button['rect']
                                panel_bottom = panel_y + panel.height
                                if btn_rect.bottom > panel_bottom:
                                    layout_issues.append(f"Button '{button['text']}' extends {btn_rect.bottom - panel_bottom}px below panel")
                                else:
                                    print(f"   🔘 Button '{button['text']}': Properly positioned")
            
            # Check for specific page types
            page_type = "Framework" if uses_framework else "Legacy/Custom"
            print(f"   🎨 Type: {page_type}")
            
            if layout_issues:
                print(f"   ⚠️ Layout Issues: {'; '.join(layout_issues)}")
                results.append((page_name, False, f"Layout issues: {'; '.join(layout_issues)}"))
            else:
                print(f"   ✅ Layout: Good")
                results.append((page_name, True, "All good"))
            
            time.sleep(1)  # Brief pause to see each page
            
        except Exception as e:
            print(f"   ❌ {page_name}: ERROR - {str(e)}")
            results.append((page_name, False, f"Rendering error: {str(e)}"))
            import traceback
            traceback.print_exc()
    
    # Summary
    print(f"\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for page_name, success, message in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {page_name}: {message}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} pages working correctly")
    
    # Framework vs Legacy breakdown
    framework_pages = [name for name, _, _ in all_pages if "Screen" in name and name != "Load Screen"]
    legacy_pages = [name for name, _, _ in all_pages if name not in framework_pages]
    
    print(f"\n📋 Page Types:")
    print(f"   🎨 Framework Pages: {len(framework_pages)} - {', '.join(framework_pages)}")
    print(f"   🛠️ Legacy/Custom Pages: {len(legacy_pages)} - {', '.join(legacy_pages)}")
    
    if passed < total:
        print(f"\n⚠️ Issues found in {total - passed} pages - check output above for details")
    else:
        print(f"\n🎉 All pages working correctly!")
    
    pygame.quit()

if __name__ == "__main__":
    test_all_pages()
