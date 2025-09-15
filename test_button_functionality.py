#!/usr/bin/env python3
"""
Test button functionality in all menu pages
"""

import pygame
import sys
import time
from field_station import FieldStation, GameState

def test_button_clicks():
    """Test button click functionality on all pages"""
    print("🔘 Testing Button Functionality")
    print("=" * 50)
    
    pygame.init()
    game = FieldStation()
    
    # Test cases: (page_name, state, draw_method, expected_buttons)
    test_cases = [
        ("Help Screen", GameState.HELP, game.draw_help_screen, ["back"]),
        ("About Screen", GameState.ABOUT, game.draw_about_screen, ["back"]),
        ("Achievements Screen", GameState.ACHIEVEMENTS, game.draw_achievements_screen, ["back"]),
    ]
    
    for page_name, state, draw_method, expected_buttons in test_cases:
        print(f"\n🧪 Testing {page_name}...")
        
        # Set state and draw the page
        game.game_state = state
        game.screen.fill((0, 0, 0))
        
        try:
            draw_method()
            pygame.display.flip()
            print(f"   ✅ Page rendered successfully")
            
            # Check if panel reference is stored
            panel_attr = page_name.lower().replace(" screen", "_panel")
            if hasattr(game, panel_attr):
                panel = getattr(game, panel_attr)
                print(f"   ✅ Panel reference stored: {panel_attr}")
                
                # Check if buttons exist
                if hasattr(panel, 'buttons') and panel.buttons:
                    print(f"   ✅ Buttons found: {[btn['id'] for btn in panel.buttons]}")
                    
                    # Test button click simulation
                    for expected_button in expected_buttons:
                        button_found = any(btn['id'] == expected_button for btn in panel.buttons)
                        if button_found:
                            print(f"   ✅ Expected button '{expected_button}' exists")
                            
                            # Test event handling
                            test_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 100))
                            
                            try:
                                result = panel.handle_event(test_event)
                                print(f"   ✅ Event handling works: {result}")
                            except Exception as e:
                                print(f"   ❌ Event handling failed: {e}")
                        else:
                            print(f"   ❌ Expected button '{expected_button}' not found")
                else:
                    print(f"   ⚠️ No buttons found in panel")
            else:
                print(f"   ❌ Panel reference not stored: {panel_attr}")
                
        except Exception as e:
            print(f"   ❌ Error testing {page_name}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Test ESC key handling
    print(f"\n⌨️ Testing ESC Key Navigation...")
    
    escape_tests = [
        (GameState.HELP, "handle_help_event"),
        (GameState.ABOUT, "handle_about_event"),
        (GameState.ACHIEVEMENTS, "handle_achievements_event"),
    ]
    
    for state, handler_name in escape_tests:
        game.game_state = state
        
        # Create ESC key event
        escape_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        
        try:
            if hasattr(game, handler_name):
                handler = getattr(game, handler_name)
                original_state = game.game_state
                handler(escape_event)
                
                if game.game_state == GameState.MENU:
                    print(f"   ✅ ESC from {original_state} → MENU")
                else:
                    print(f"   ⚠️ ESC from {original_state} → {game.game_state} (unexpected)")
            else:
                print(f"   ❌ Handler {handler_name} not found")
                
        except Exception as e:
            print(f"   ❌ ESC handling failed for {state}: {e}")
    
    # Test button click navigation
    print(f"\n🖱️ Testing Button Click Navigation...")
    
    for page_name, state, draw_method, expected_buttons in test_cases:
        game.game_state = state
        game.screen.fill((0, 0, 0))
        draw_method()
        
        panel_attr = page_name.lower().replace(" screen", "_panel")
        if hasattr(game, panel_attr):
            panel = getattr(game, panel_attr)
            
            # Simulate clicking the BACK button
            if panel.buttons:
                back_button = next((btn for btn in panel.buttons if btn['id'] == 'back'), None)
                if back_button:
                    # Create a mock click event at button position
                    if 'rect' in back_button and back_button['rect']:
                        click_pos = back_button['rect'].center
                        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=click_pos)
                        
                        try:
                            original_state = game.game_state
                            result = panel.handle_event(click_event)
                            
                            # Handle the button click result
                            handler_name = f"handle_{page_name.lower().split()[0]}_event"
                            if hasattr(game, handler_name):
                                handler = getattr(game, handler_name)
                                handler(click_event)
                            
                            if game.game_state == GameState.MENU:
                                print(f"   ✅ BACK button from {original_state} → MENU")
                            else:
                                print(f"   ⚠️ BACK button from {original_state} → {game.game_state}")
                                
                        except Exception as e:
                            print(f"   ❌ Button click failed: {e}")
                    else:
                        print(f"   ⚠️ Button rect not set for {page_name}")
    
    pygame.quit()
    print(f"\n🎉 Button functionality testing complete!")

if __name__ == "__main__":
    test_button_clicks()
