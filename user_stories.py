#!/usr/bin/env python3
"""
Field Station - User Stories Definition
Defines expected user behaviors and flows for QA testing
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

class UserAction(Enum):
    CLICK = "click"
    TYPE = "type" 
    PRESS_KEY = "press_key"
    HOVER = "hover"
    WAIT = "wait"
    VERIFY = "verify"
    SCREENSHOT = "screenshot"

@dataclass
class TestStep:
    action: UserAction
    target: str  # Element to interact with
    value: Optional[str] = None  # Value to type or key to press
    expected_result: Optional[str] = None  # What should happen
    screenshot_name: Optional[str] = None

@dataclass
class UserStory:
    story_id: str
    title: str
    description: str
    user_type: str  # "New User", "Returning User", etc.
    acceptance_criteria: List[str]
    test_steps: List[TestStep]
    page: str  # Which page this story tests

# Define all user stories for Field Station
USER_STORIES = {
    
    # MAIN MENU STORIES
    "US001": UserStory(
        story_id="US001",
        title="Navigate Main Menu with Mouse",
        description="As a user, I want to navigate the main menu using mouse clicks so I can access different game features",
        user_type="Any User",
        acceptance_criteria=[
            "All menu items should be clickable",
            "Menu items should show hover effects", 
            "Icons should appear on hover",
            "Clicking should navigate to correct page"
        ],
        test_steps=[
            TestStep(UserAction.SCREENSHOT, "main_menu", screenshot_name="menu_initial"),
            TestStep(UserAction.HOVER, "New Game", expected_result="Icon appears next to text"),
            TestStep(UserAction.CLICK, "New Game", expected_result="Navigate to Farm Setup"),
            TestStep(UserAction.PRESS_KEY, "K_ESCAPE", expected_result="Return to Main Menu"),
            TestStep(UserAction.CLICK, "Achievements", expected_result="Navigate to Achievements"),
            TestStep(UserAction.PRESS_KEY, "K_ESCAPE", expected_result="Return to Main Menu"),
            TestStep(UserAction.CLICK, "Help", expected_result="Navigate to Help"),
            TestStep(UserAction.PRESS_KEY, "K_ESCAPE", expected_result="Return to Main Menu"),
            TestStep(UserAction.CLICK, "Settings", expected_result="Navigate to Settings"),
            TestStep(UserAction.PRESS_KEY, "K_ESCAPE", expected_result="Return to Main Menu"),
            TestStep(UserAction.CLICK, "About", expected_result="Navigate to About"),
        ],
        page="Main Menu"
    ),

    "US002": UserStory(
        story_id="US002", 
        title="Navigate Main Menu with Keyboard",
        description="As a keyboard user, I want to navigate the menu using arrow keys and Enter so I can play without a mouse",
        user_type="Keyboard User",
        acceptance_criteria=[
            "Arrow keys should move selection",
            "Enter should activate selected item",
            "Visual feedback for selected item"
        ],
        test_steps=[
            TestStep(UserAction.PRESS_KEY, "K_DOWN", expected_result="Selection moves down"),
            TestStep(UserAction.PRESS_KEY, "K_UP", expected_result="Selection moves up"),
            TestStep(UserAction.PRESS_KEY, "K_RETURN", expected_result="Activate selected menu item"),
        ],
        page="Main Menu"
    ),

    # FARM SETUP STORIES
    "US003": UserStory(
        story_id="US003",
        title="Create New Farm - Happy Path",
        description="As a new player, I want to create a farm with a custom name and settings so I can start playing",
        user_type="New User",
        acceptance_criteria=[
            "Can enter farm name in text field",
            "Can select location from dropdown", 
            "Can select starting season",
            "START FARM button enables when form is valid",
            "Form submits successfully"
        ],
        test_steps=[
            TestStep(UserAction.SCREENSHOT, "farm_setup", screenshot_name="setup_initial"),
            TestStep(UserAction.CLICK, "farm_name_input", expected_result="Input field becomes active"),
            TestStep(UserAction.TYPE, "farm_name_input", value="Test Farm", expected_result="Text appears in field"),
            TestStep(UserAction.PRESS_KEY, "K_RETURN", expected_result="Field deactivates with visual feedback"),
            TestStep(UserAction.CLICK, "location_dropdown", expected_result="Location selection available"),
            TestStep(UserAction.CLICK, "season_spring", expected_result="Spring season selected"),
            TestStep(UserAction.VERIFY, "start_button", expected_result="Button is enabled"),
            TestStep(UserAction.SCREENSHOT, "farm_setup", screenshot_name="setup_filled"),
            TestStep(UserAction.CLICK, "start_button", expected_result="Game starts"),
        ],
        page="Farm Setup"
    ),

    "US004": UserStory(
        story_id="US004",
        title="Farm Setup Validation", 
        description="As a user, I want clear feedback when my farm setup is invalid so I know what to fix",
        user_type="Any User", 
        acceptance_criteria=[
            "Empty farm name should disable START button",
            "No season selected should disable START button", 
            "Invalid characters should be handled gracefully",
            "Clear visual feedback for validation state"
        ],
        test_steps=[
            TestStep(UserAction.VERIFY, "start_button", expected_result="Button is disabled initially"),
            TestStep(UserAction.TYPE, "farm_name_input", value="", expected_result="START button remains disabled"),
            TestStep(UserAction.TYPE, "farm_name_input", value="A", expected_result="START button still disabled (no season)"),
            TestStep(UserAction.CLICK, "season_spring", expected_result="START button becomes enabled"),
            TestStep(UserAction.TYPE, "farm_name_input", value="", expected_result="START button becomes disabled again"),
        ],
        page="Farm Setup"
    ),

    "US005": UserStory(
        story_id="US005",
        title="Farm Setup Navigation",
        description="As a user, I want to easily navigate back from farm setup so I can return to the main menu",
        user_type="Any User",
        acceptance_criteria=[
            "BACK button should be visible and clickable",
            "BACK button should return to main menu",
            "ESC key should also return to main menu"
        ],
        test_steps=[
            TestStep(UserAction.VERIFY, "back_button", expected_result="BACK button is visible"),
            TestStep(UserAction.CLICK, "back_button", expected_result="Return to Main Menu"),
            TestStep(UserAction.CLICK, "New Game", expected_result="Back to Farm Setup"),
            TestStep(UserAction.PRESS_KEY, "K_ESCAPE", expected_result="Return to Main Menu"),
        ],
        page="Farm Setup"
    ),

    # ACHIEVEMENTS STORIES  
    "US006": UserStory(
        story_id="US006",
        title="View Achievements Page",
        description="As a player, I want to see my achievements so I can track my progress",
        user_type="Any User",
        acceptance_criteria=[
            "Page loads without errors",
            "Page title displays with icon", 
            "Achievement content is readable",
            "Navigation back to menu works"
        ],
        test_steps=[
            TestStep(UserAction.SCREENSHOT, "achievements", screenshot_name="achievements_page"),
            TestStep(UserAction.VERIFY, "page_title", expected_result="Shows '* ACHIEVEMENTS'"),
            TestStep(UserAction.VERIFY, "achievements_content", expected_result="Content is visible and readable"),
            TestStep(UserAction.PRESS_KEY, "K_ESCAPE", expected_result="Return to Main Menu"),
        ],
        page="Achievements"
    ),

    # HELP STORIES
    "US007": UserStory(
        story_id="US007", 
        title="Access Help Information",
        description="As a user, I want to access help information so I can learn how to play",
        user_type="New User",
        acceptance_criteria=[
            "Help page loads successfully",
            "Help content is readable and informative",
            "Page title shows help icon",
            "Easy navigation back to menu"
        ],
        test_steps=[
            TestStep(UserAction.SCREENSHOT, "help", screenshot_name="help_page"),
            TestStep(UserAction.VERIFY, "page_title", expected_result="Shows '? HELP & TUTORIALS'"),
            TestStep(UserAction.VERIFY, "help_content", expected_result="Help text is visible"),
            TestStep(UserAction.PRESS_KEY, "K_ESCAPE", expected_result="Return to Main Menu"),
        ],
        page="Help"
    ),

    # SETTINGS STORIES
    "US008": UserStory(
        story_id="US008",
        title="Access Settings Page", 
        description="As a user, I want to access game settings so I can customize my experience",
        user_type="Any User",
        acceptance_criteria=[
            "Settings page loads without errors",
            "Settings content is visible",
            "Page navigation works correctly"
        ],
        test_steps=[
            TestStep(UserAction.SCREENSHOT, "settings", screenshot_name="settings_page"), 
            TestStep(UserAction.VERIFY, "page_title", expected_result="Shows '@ SETTINGS'"),
            TestStep(UserAction.VERIFY, "settings_content", expected_result="Settings options visible"),
            TestStep(UserAction.PRESS_KEY, "K_ESCAPE", expected_result="Return to Main Menu"),
        ],
        page="Settings" 
    ),

    # ABOUT STORIES
    "US009": UserStory(
        story_id="US009",
        title="View About Information",
        description="As a user, I want to see information about the game so I understand what I'm playing",
        user_type="Any User", 
        acceptance_criteria=[
            "About page displays game information",
            "Content is readable and informative", 
            "Page title shows info icon"
        ],
        test_steps=[
            TestStep(UserAction.SCREENSHOT, "about", screenshot_name="about_page"),
            TestStep(UserAction.VERIFY, "page_title", expected_result="Shows 'i ABOUT'"),
            TestStep(UserAction.VERIFY, "about_content", expected_result="About text is visible"),
            TestStep(UserAction.PRESS_KEY, "K_ESCAPE", expected_result="Return to Main Menu"),
        ],
        page="About"
    ),
    
    # CROSS-PAGE STORIES
    "US010": UserStory(
        story_id="US010",
        title="Complete New User Flow",
        description="As a new user, I want to complete the full flow from menu to starting a game",
        user_type="New User",
        acceptance_criteria=[
            "Can navigate from menu to farm setup",
            "Can complete farm setup form",
            "Can start new game successfully",
            "No errors or crashes during flow"
        ],
        test_steps=[
            TestStep(UserAction.CLICK, "New Game", expected_result="Navigate to Farm Setup"),
            TestStep(UserAction.TYPE, "farm_name_input", value="My First Farm", expected_result="Name entered"),
            TestStep(UserAction.CLICK, "season_spring", expected_result="Season selected"),
            TestStep(UserAction.CLICK, "start_button", expected_result="Game starts successfully"),
        ],
        page="Full Flow"
    ),
}

def get_stories_for_page(page_name: str) -> List[UserStory]:
    """Get all user stories for a specific page"""
    return [story for story in USER_STORIES.values() if story.page == page_name]

def get_all_pages() -> List[str]:
    """Get list of all pages that have user stories"""
    return list(set(story.page for story in USER_STORIES.values()))

def get_story_by_id(story_id: str) -> Optional[UserStory]:
    """Get a specific user story by ID"""
    return USER_STORIES.get(story_id)

if __name__ == "__main__":
    print("📋 Field Station User Stories Summary")
    print("=" * 50)
    
    for page in get_all_pages():
        stories = get_stories_for_page(page)
        print(f"\n📄 {page}: {len(stories)} stories")
        for story in stories:
            print(f"  {story.story_id}: {story.title}")
    
    print(f"\n📊 Total: {len(USER_STORIES)} user stories across {len(get_all_pages())} pages")