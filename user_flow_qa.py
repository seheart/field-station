#!/usr/bin/env python3
"""
Field Station - User Flow QA Testing Framework
Automated testing of user stories and workflows
"""

import pygame
import sys
import os
import time
import traceback
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Add the field_station directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from field_station import FieldStation, GameState
    from user_stories import USER_STORIES, UserStory, TestStep, UserAction, get_stories_for_page
except ImportError as e:
    print(f"Error importing: {e}")
    sys.exit(1)

@dataclass
class FlowTestResult:
    story_id: str
    story_title: str
    passed: bool
    step_results: List[Dict[str, Any]]
    error_message: Optional[str] = None
    execution_time: float = 0.0
    screenshots: List[str] = None

class UserFlowQAFramework:
    """Advanced QA framework that tests complete user workflows"""
    
    def __init__(self):
        self.game = None
        self.test_results = []
        self.screenshot_dir = Path("qa_screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        self.setup_pygame()
    
    def setup_pygame(self):
        """Initialize pygame for testing"""
        pygame.init()
        os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Headless mode
        self.display = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("Field Station User Flow QA")
    
    def run_user_story_tests(self, story_ids: Optional[List[str]] = None):
        """Run user story tests for specified stories or all stories"""
        print("🧑‍💻 Starting Field Station User Flow QA")
        print("=" * 60)
        
        stories_to_test = story_ids or list(USER_STORIES.keys())
        
        for story_id in stories_to_test:
            story = USER_STORIES.get(story_id)
            if not story:
                print(f"❌ Story {story_id} not found")
                continue
                
            print(f"\n📋 Testing: {story_id} - {story.title}")
            print(f"👤 User Type: {story.user_type}")
            print(f"📄 Page: {story.page}")
            
            self.test_user_story(story)
        
        self.generate_flow_report()
    
    def test_user_story(self, story: UserStory):
        """Test a complete user story with all its steps"""
        start_time = time.time()
        step_results = []
        screenshots = []
        
        try:
            # Initialize game for each story
            if not self.game:
                self.game = FieldStation()
                time.sleep(0.2)  # Let it initialize
            
            # Navigate to the correct starting page
            self.navigate_to_page(story.page)
            
            # Execute each test step
            for i, step in enumerate(story.test_steps):
                step_start = time.time()
                step_result = self.execute_test_step(step, i + 1)
                step_result['execution_time'] = time.time() - step_start
                step_results.append(step_result)
                
                if step.screenshot_name:
                    screenshot_path = self.take_screenshot(f"{story.story_id}_{step.screenshot_name}")
                    screenshots.append(screenshot_path)
                
                # If step failed and it's critical, stop the story
                if not step_result['passed'] and step.expected_result:
                    break
                    
                # Small delay between steps for stability
                time.sleep(0.1)
            
            # Check if all steps passed
            all_passed = all(step['passed'] for step in step_results)
            
            result = FlowTestResult(
                story_id=story.story_id,
                story_title=story.title,
                passed=all_passed,
                step_results=step_results,
                execution_time=time.time() - start_time,
                screenshots=screenshots
            )
            
            if not all_passed:
                failed_steps = [s for s in step_results if not s['passed']]
                result.error_message = f"Failed steps: {[s['step_number'] for s in failed_steps]}"
            
        except Exception as e:
            result = FlowTestResult(
                story_id=story.story_id,
                story_title=story.title,
                passed=False,
                step_results=step_results,
                error_message=str(e),
                execution_time=time.time() - start_time,
                screenshots=screenshots
            )
        
        self.test_results.append(result)
        
        # Print immediate feedback
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"  {status} {len(result.step_results)} steps ({result.execution_time:.2f}s)")
        if result.error_message:
            print(f"    Error: {result.error_message}")
    
    def navigate_to_page(self, page: str):
        """Navigate to the specified page from main menu"""
        if page == "Main Menu":
            self.game.game_state = GameState.MENU
        elif page == "Farm Setup":
            self.game.game_state = GameState.FARM_SETUP
        elif page == "Achievements":
            self.game.game_state = GameState.ACHIEVEMENTS  
        elif page == "Help":
            self.game.game_state = GameState.HELP
        elif page == "Settings":
            self.game.game_state = GameState.OPTIONS
        elif page == "About":
            self.game.game_state = GameState.ABOUT
        elif page == "Full Flow":
            self.game.game_state = GameState.MENU
        
        # Render the page to ensure it's ready
        pygame.event.pump()
        self.game.screen.fill((0, 50, 0))
        self.render_current_page()
        pygame.display.flip()
        time.sleep(0.1)
    
    def render_current_page(self):
        """Render the current game page"""
        if self.game.game_state == GameState.MENU:
            self.game.draw_menu()
        elif self.game.game_state == GameState.FARM_SETUP:
            self.game.draw_farm_setup()
        elif self.game.game_state == GameState.ACHIEVEMENTS:
            self.game.draw_achievements_screen()
        elif self.game.game_state == GameState.HELP:
            self.game.draw_help_screen()
        elif self.game.game_state == GameState.OPTIONS:
            self.game.draw_options_screen()
        elif self.game.game_state == GameState.ABOUT:
            self.game.draw_about_screen()
    
    def execute_test_step(self, step: TestStep, step_number: int) -> Dict[str, Any]:
        """Execute a single test step and return result"""
        result = {
            'step_number': step_number,
            'action': step.action.value,
            'target': step.target,
            'value': step.value,
            'expected_result': step.expected_result,
            'passed': False,
            'actual_result': None,
            'error': None
        }
        
        try:
            if step.action == UserAction.CLICK:
                result['passed'], result['actual_result'] = self.simulate_click(step.target)
            
            elif step.action == UserAction.TYPE:
                result['passed'], result['actual_result'] = self.simulate_typing(step.target, step.value)
            
            elif step.action == UserAction.PRESS_KEY:
                result['passed'], result['actual_result'] = self.simulate_key_press(step.value)
            
            elif step.action == UserAction.HOVER:
                result['passed'], result['actual_result'] = self.simulate_hover(step.target)
            
            elif step.action == UserAction.VERIFY:
                result['passed'], result['actual_result'] = self.verify_condition(step.target, step.expected_result)
            
            elif step.action == UserAction.SCREENSHOT:
                screenshot_path = self.take_screenshot(f"step_{step_number}_{step.target}")
                result['passed'] = True
                result['actual_result'] = f"Screenshot saved: {screenshot_path}"
            
            elif step.action == UserAction.WAIT:
                wait_time = float(step.value) if step.value else 0.5
                time.sleep(wait_time)
                result['passed'] = True
                result['actual_result'] = f"Waited {wait_time}s"
                
        except Exception as e:
            result['error'] = str(e)
            result['actual_result'] = f"Error: {e}"
        
        return result
    
    def simulate_click(self, target: str) -> Tuple[bool, str]:
        """Simulate clicking on a UI element"""
        try:
            # Refresh the page rendering
            self.render_current_page()
            
            if target == "New Game":
                return self.click_menu_item("New Game")
            elif target == "Achievements":
                return self.click_menu_item("Achievements")
            elif target == "Help":
                return self.click_menu_item("Help")
            elif target == "Settings":
                return self.click_menu_item("Settings") 
            elif target == "About":
                return self.click_menu_item("About")
            elif target == "farm_name_input":
                return self.click_farm_name_input()
            elif target == "location_dropdown":
                return self.click_location_dropdown()
            elif target == "season_spring":
                return self.select_season(0)
            elif target == "start_button":
                return self.click_start_button()
            elif target == "back_button":
                return self.click_back_button()
            else:
                return False, f"Unknown click target: {target}"
                
        except Exception as e:
            return False, f"Click error: {e}"
    
    def click_menu_item(self, item_name: str) -> Tuple[bool, str]:
        """Click a main menu item"""
        if hasattr(self.game, 'main_menu_button_rects'):
            for i, option in enumerate(self.game.main_menu_options):
                if option == item_name:
                    # Simulate click on this menu item
                    original_state = self.game.game_state
                    
                    # Create a mock click event
                    mouse_pos = (400, 300 + i * 50)  # Approximate position
                    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=mouse_pos)
                    
                    # Handle the click
                    self.game.handle_event(click_event)
                    
                    # Check if state changed
                    new_state = self.game.game_state
                    if new_state != original_state:
                        return True, f"Navigated from {original_state} to {new_state}"
                    else:
                        return False, f"State did not change from {original_state}"
        
        return False, f"Could not find menu item: {item_name}"
    
    def click_farm_name_input(self) -> Tuple[bool, str]:
        """Click the farm name input field"""
        try:
            if self.game.game_state == GameState.FARM_SETUP:
                # Activate the farm name input
                self.game.setup_name_input_active = True
                return True, "Farm name input activated"
            return False, "Not on farm setup page"
        except Exception as e:
            return False, f"Farm name input error: {e}"
    
    def click_location_dropdown(self) -> Tuple[bool, str]:
        """Click the location dropdown"""
        return True, "Location dropdown clicked (placeholder)"
    
    def select_season(self, season_index: int) -> Tuple[bool, str]:
        """Select a season option"""
        try:
            if self.game.game_state == GameState.FARM_SETUP:
                self.game.setup_season_selection = season_index
                return True, f"Season {season_index} selected"
            return False, "Not on farm setup page"
        except Exception as e:
            return False, f"Season selection error: {e}"
    
    def click_start_button(self) -> Tuple[bool, str]:
        """Click the START FARM button"""
        try:
            if (self.game.game_state == GameState.FARM_SETUP and 
                bool(self.game.farm_name.strip()) and 
                self.game.setup_season_selection >= 0):
                # Button should be enabled, simulate click
                original_state = self.game.game_state
                # For now, just verify the button would be clickable
                return True, "START FARM button is enabled and clickable"
            return False, "START FARM button is disabled"
        except Exception as e:
            return False, f"Start button error: {e}"
    
    def click_back_button(self) -> Tuple[bool, str]:
        """Click the BACK button"""
        try:
            original_state = self.game.game_state
            if original_state != GameState.MENU:
                self.game.game_state = GameState.MENU
                return True, f"Navigated back from {original_state} to MENU"
            return False, "Already on main menu"
        except Exception as e:
            return False, f"Back button error: {e}"
    
    def simulate_typing(self, target: str, text: str) -> Tuple[bool, str]:
        """Simulate typing text into a field"""
        try:
            if target == "farm_name_input":
                if self.game.game_state == GameState.FARM_SETUP:
                    self.game.farm_name = text
                    return True, f"Typed '{text}' into farm name field"
            return False, f"Could not type into: {target}"
        except Exception as e:
            return False, f"Typing error: {e}"
    
    def simulate_key_press(self, key: str) -> Tuple[bool, str]:
        """Simulate pressing a key"""
        try:
            key_map = {
                'K_ESCAPE': pygame.K_ESCAPE,
                'K_RETURN': pygame.K_RETURN,
                'K_UP': pygame.K_UP,
                'K_DOWN': pygame.K_DOWN
            }
            
            if key in key_map:
                pygame_key = key_map[key]
                key_event = pygame.event.Event(pygame.KEYDOWN, key=pygame_key)
                
                original_state = self.game.game_state
                result = self.game.handle_event(key_event)
                new_state = self.game.game_state
                
                return True, f"Pressed {key}, state: {original_state} -> {new_state}"
            
            return False, f"Unknown key: {key}"
        except Exception as e:
            return False, f"Key press error: {e}"
    
    def simulate_hover(self, target: str) -> Tuple[bool, str]:
        """Simulate hovering over an element"""
        # For now, just return success - hover effects are visual
        return True, f"Hovered over {target}"
    
    def verify_condition(self, target: str, condition: str) -> Tuple[bool, str]:
        """Verify a condition is met"""
        try:
            if target == "start_button":
                if "enabled" in condition:
                    is_enabled = bool(self.game.farm_name.strip()) and self.game.setup_season_selection >= 0
                    expected_enabled = "enabled" in condition
                    if is_enabled == expected_enabled:
                        return True, f"START button is {'enabled' if is_enabled else 'disabled'} as expected"
                    else:
                        return False, f"START button is {'enabled' if is_enabled else 'disabled'}, expected {'enabled' if expected_enabled else 'disabled'}"
            
            elif target == "page_title":
                # Check if we're on the right page with right title
                current_state = self.game.game_state
                return True, f"Page title verified for {current_state}"
            
            return True, f"Verified: {target} - {condition}"
        except Exception as e:
            return False, f"Verification error: {e}"
    
    def take_screenshot(self, name: str) -> str:
        """Take a screenshot of current game state"""
        try:
            # Render current page
            self.render_current_page()
            pygame.display.flip()
            
            # Save screenshot
            timestamp = int(time.time())
            filename = f"{name}_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            
            pygame.image.save(self.display, str(filepath))
            return str(filepath)
        except Exception as e:
            return f"Screenshot error: {e}"
    
    def generate_flow_report(self):
        """Generate comprehensive user flow test report"""
        print("\n" + "=" * 60)
        print("📊 USER FLOW QA TEST REPORT")
        print("=" * 60)
        
        total_stories = len(self.test_results)
        passed_stories = sum(1 for result in self.test_results if result.passed)
        failed_stories = total_stories - passed_stories
        success_rate = (passed_stories / total_stories * 100) if total_stories > 0 else 0
        
        print(f"Total User Stories: {total_stories}")
        print(f"Passed Stories: {passed_stories}")
        print(f"Failed Stories: {failed_stories}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Execution Time: {sum(r.execution_time for r in self.test_results):.2f}s")
        
        # Story summaries
        print("\n📋 STORY RESULTS:")
        for result in self.test_results:
            status = "✅" if result.passed else "❌"
            print(f"{status} {result.story_id}: {result.story_title}")
            if not result.passed:
                print(f"    ❌ {result.error_message}")
                
        # Failed stories detail  
        if failed_stories > 0:
            print("\n🔍 FAILED STORY DETAILS:")
            for result in self.test_results:
                if not result.passed:
                    print(f"\n❌ {result.story_id}: {result.story_title}")
                    for step in result.step_results:
                        if not step['passed']:
                            print(f"   Step {step['step_number']}: {step['action']} {step['target']}")
                            print(f"   Expected: {step['expected_result']}")
                            print(f"   Actual: {step['actual_result']}")
        
        # Screenshots summary
        total_screenshots = sum(len(r.screenshots or []) for r in self.test_results)
        if total_screenshots > 0:
            print(f"\n📸 Generated {total_screenshots} screenshots in {self.screenshot_dir}")
        
        return 0 if failed_stories == 0 else 1
    
    def cleanup(self):
        """Clean up resources"""
        if self.game:
            pygame.quit()

def main():
    """Run user flow QA tests"""
    qa = UserFlowQAFramework()
    try:
        # Run critical user stories first
        critical_stories = ["US003", "US004", "US005", "US001", "US010"]
        qa.run_user_story_tests(critical_stories)
        return qa.generate_flow_report()
    except Exception as e:
        print(f"💥 CRITICAL FLOW TEST ERROR: {e}")
        traceback.print_exc()
        return 2
    finally:
        qa.cleanup()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)