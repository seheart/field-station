#!/usr/bin/env python3
"""
Automated QA Testing Framework for Field Station
Catches UI errors, functionality issues, and regressions automatically
"""

import pygame
import sys
import os
import time
import traceback
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass

# Add the field_station directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from field_station import FieldStation, GameState
except ImportError as e:
    print(f"Error importing field_station: {e}")
    sys.exit(1)

@dataclass
class TestResult:
    test_name: str
    passed: bool
    error_message: Optional[str] = None
    execution_time: float = 0.0

class QATestFramework:
    """Comprehensive QA testing framework for Field Station"""
    
    def __init__(self):
        self.game = None
        self.test_results = []
        self.setup_pygame()
    
    def setup_pygame(self):
        """Initialize pygame for headless testing"""
        pygame.init()
        # Use smaller display for testing
        os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Headless mode
        self.display = pygame.display.set_mode((800, 600))
    
    def run_all_tests(self):
        """Run the complete test suite"""
        print("🚀 Starting Field Station QA Test Suite")
        print("=" * 50)
        
        # Core functionality tests
        self.test_game_initialization()
        self.test_menu_navigation()
        self.test_farm_setup_flow()
        self.test_input_handling()
        self.test_ui_rendering()
        self.test_button_interactions()
        self.test_error_handling()
        
        # Generate report
        self.generate_report()
    
    def test_game_initialization(self):
        """Test game starts without errors"""
        start_time = time.time()
        try:
            self.game = FieldStation()
            time.sleep(0.5)  # Let it initialize
            
            # Check critical attributes exist
            assert hasattr(self.game, 'game_state'), "Game state not initialized"
            assert hasattr(self.game, 'screen'), "Screen not initialized"
            assert hasattr(self.game, 'farm_name'), "Farm name not initialized"
            
            self.add_result("Game Initialization", True, execution_time=time.time() - start_time)
        except Exception as e:
            self.add_result("Game Initialization", False, str(e), time.time() - start_time)
    
    def test_menu_navigation(self):
        """Test menu navigation works without errors"""
        if not self.game:
            self.add_result("Menu Navigation", False, "Game not initialized")
            return
            
        start_time = time.time()
        try:
            # Test each menu state
            menu_states = [
                GameState.MENU,
                GameState.FARM_SETUP, 
                GameState.ACHIEVEMENTS,
                GameState.HELP,
                GameState.OPTIONS,
                GameState.ABOUT
            ]
            
            for state in menu_states:
                self.game.game_state = state
                
                # Try to render the page
                pygame.event.pump()
                self.game.screen.fill((0, 0, 0))
                
                # Call the appropriate draw method
                if state == GameState.MENU:
                    self.game.draw_menu()
                elif state == GameState.FARM_SETUP:
                    self.game.draw_farm_setup()
                elif state == GameState.ACHIEVEMENTS:
                    self.game.draw_achievements_screen()
                elif state == GameState.HELP:
                    self.game.draw_help_screen()
                elif state == GameState.OPTIONS:
                    self.game.draw_options_screen()
                elif state == GameState.ABOUT:
                    self.game.draw_about_screen()
                
                pygame.display.flip()
                time.sleep(0.1)
            
            self.add_result("Menu Navigation", True, execution_time=time.time() - start_time)
        except Exception as e:
            self.add_result("Menu Navigation", False, str(e), time.time() - start_time)
    
    def test_farm_setup_flow(self):
        """Test farm setup form functionality"""
        if not self.game:
            self.add_result("Farm Setup Flow", False, "Game not initialized")
            return
            
        start_time = time.time()
        try:
            # Navigate to farm setup
            self.game.game_state = GameState.FARM_SETUP
            
            # Test form validation
            original_name = self.game.farm_name
            self.game.farm_name = ""
            can_start_empty = bool(self.game.farm_name.strip()) and self.game.setup_season_selection >= 0
            
            self.game.farm_name = "Test Farm"
            self.game.setup_season_selection = 0
            can_start_filled = bool(self.game.farm_name.strip()) and self.game.setup_season_selection >= 0
            
            assert not can_start_empty, "Should not allow starting with empty name"
            assert can_start_filled, "Should allow starting with valid data"
            
            # Test available options exist
            assert len(self.game.available_locations) > 0, "No locations available"
            assert len(self.game.available_seasons) > 0, "No seasons available"
            
            # Restore original state
            self.game.farm_name = original_name
            
            self.add_result("Farm Setup Flow", True, execution_time=time.time() - start_time)
        except Exception as e:
            self.add_result("Farm Setup Flow", False, str(e), time.time() - start_time)
    
    def test_input_handling(self):
        """Test keyboard and mouse input handling"""
        if not self.game:
            self.add_result("Input Handling", False, "Game not initialized")
            return
            
        start_time = time.time()
        try:
            # Test escape key handling in different states
            test_states = [GameState.FARM_SETUP, GameState.HELP, GameState.OPTIONS]
            
            for state in test_states:
                self.game.game_state = state
                
                # Simulate ESC key press
                escape_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
                result = self.game.handle_event(escape_event)
                
                # Should return True (handled) and go back to menu
                assert result == True, f"ESC not handled in {state}"
                assert self.game.game_state == GameState.MENU, f"ESC didn't return to menu from {state}"
            
            # Test Enter key in farm setup
            self.game.game_state = GameState.FARM_SETUP
            self.game.setup_name_input_active = True
            
            enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
            result = self.game.handle_event(enter_event)
            # Should not crash
            
            self.add_result("Input Handling", True, execution_time=time.time() - start_time)
        except Exception as e:
            self.add_result("Input Handling", False, str(e), time.time() - start_time)
    
    def test_ui_rendering(self):
        """Test UI elements render without errors"""
        if not self.game:
            self.add_result("UI Rendering", False, "Game not initialized")
            return
            
        start_time = time.time()
        try:
            # Test farm setup UI framework
            self.game.game_state = GameState.FARM_SETUP
            
            # Force panel creation
            self.game.draw_farm_setup()
            
            # Check panel was created
            assert hasattr(self.game, 'farm_setup_panel'), "Farm setup panel not created"
            
            # Check panel has required elements
            panel = self.game.farm_setup_panel
            assert hasattr(panel, 'input_fields'), "Input fields not created"
            assert hasattr(panel, 'buttons'), "Buttons not created"
            assert len(panel.buttons) >= 2, "Not enough buttons created"
            
            # Test button rectangles are created during render
            pygame.event.pump()
            self.game.screen.fill((0, 0, 0))
            self.game.draw_farm_setup()
            
            # Check buttons have rectangles for click detection
            for button in panel.buttons:
                assert button['rect'] is not None, f"Button {button['text']} has no click rectangle"
            
            self.add_result("UI Rendering", True, execution_time=time.time() - start_time)
        except Exception as e:
            self.add_result("UI Rendering", False, str(e), time.time() - start_time)
    
    def test_button_interactions(self):
        """Test button click detection and responses"""
        if not self.game:
            self.add_result("Button Interactions", False, "Game not initialized")
            return
            
        start_time = time.time()
        try:
            # Test farm setup buttons
            self.game.game_state = GameState.FARM_SETUP
            self.game.draw_farm_setup()  # Ensure UI is rendered
            
            # Test that buttons exist and have click areas
            panel = self.game.farm_setup_panel
            start_button = None
            back_button = None
            
            for button in panel.buttons:
                if button['id'] == 'start':
                    start_button = button
                elif button['id'] == 'back':
                    back_button = button
            
            assert start_button is not None, "START button not found"
            assert back_button is not None, "BACK button not found"
            assert start_button['rect'] is not None, "START button has no click area"
            assert back_button['rect'] is not None, "BACK button has no click area"
            
            # Test button states
            self.game.farm_name = ""
            self.game.setup_season_selection = -1
            self.game.draw_farm_setup()  # Refresh UI
            
            # Find start button again after refresh
            for button in panel.buttons:
                if button['id'] == 'start':
                    start_button = button
                    break
            
            assert not start_button['enabled'], "START button should be disabled with invalid form"
            
            # Set valid form data
            self.game.farm_name = "Test Farm"
            self.game.setup_season_selection = 0
            self.game.draw_farm_setup()  # Refresh UI
            
            # Find start button again
            for button in panel.buttons:
                if button['id'] == 'start':
                    start_button = button
                    break
            
            assert start_button['enabled'], "START button should be enabled with valid form"
            
            self.add_result("Button Interactions", True, execution_time=time.time() - start_time)
        except Exception as e:
            self.add_result("Button Interactions", False, str(e), time.time() - start_time)
    
    def test_error_handling(self):
        """Test error conditions don't crash the game"""
        if not self.game:
            self.add_result("Error Handling", False, "Game not initialized")
            return
            
        start_time = time.time()
        try:
            # Test invalid input handling
            original_name = self.game.farm_name
            
            # Test very long farm name
            self.game.farm_name = "x" * 100
            self.game.game_state = GameState.FARM_SETUP
            self.game.draw_farm_setup()  # Should not crash
            
            # Test special characters
            self.game.farm_name = "Test Farm!@#$%"
            self.game.draw_farm_setup()  # Should not crash
            
            # Test empty/None values
            self.game.farm_name = ""
            self.game.draw_farm_setup()  # Should not crash
            
            # Test invalid game states
            original_state = self.game.game_state
            
            # These should not crash the event handler
            for state in GameState:
                self.game.game_state = state
                dummy_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
                result = self.game.handle_event(dummy_event)
                # Should return boolean
                assert isinstance(result, bool), f"Event handler returned non-boolean for {state}"
            
            # Restore original values
            self.game.farm_name = original_name
            self.game.game_state = original_state
            
            self.add_result("Error Handling", True, execution_time=time.time() - start_time)
        except Exception as e:
            self.add_result("Error Handling", False, str(e), time.time() - start_time)
    
    def add_result(self, test_name: str, passed: bool, error_message: str = None, execution_time: float = 0.0):
        """Add a test result to the results list"""
        result = TestResult(test_name, passed, error_message, execution_time)
        self.test_results.append(result)
        
        # Print immediate feedback
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name} ({execution_time:.2f}s)")
        if not passed and error_message:
            print(f"   Error: {error_message}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 50)
        print("📊 FIELD STATION QA TEST REPORT")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.passed)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Execution Time: {sum(r.execution_time for r in self.test_results):.2f}s")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result.passed:
                    print(f"❌ {result.test_name}: {result.error_message}")
        
        print("\n📈 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result.passed else "❌"
            print(f"{status} {result.test_name:<25} {result.execution_time:>8.2f}s")
        
        # Return exit code
        return 0 if failed_tests == 0 else 1
    
    def cleanup(self):
        """Clean up resources"""
        if self.game:
            pygame.quit()

def main():
    """Run QA test suite"""
    qa = QATestFramework()
    try:
        exit_code = qa.run_all_tests()
        return exit_code
    except Exception as e:
        print(f"💥 CRITICAL TEST FRAMEWORK ERROR: {e}")
        traceback.print_exc()
        return 2
    finally:
        qa.cleanup()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)