"""
Menu Icons for Field Station
Simple text-based icons that render reliably across all systems
"""

# Menu option icons - using simple ASCII characters for reliable rendering
MENU_ICONS = {
    "Continue Game": ">",
    "New Game": "+", 
    "Load Game": "[=]",
    "Save Game": "[S]",
    "Achievements": "*",
    "Help": "?",
    "Settings": "@",
    "About": "i",
    "Exit": "X",
    # Pause menu icons
    "Resume Game": ">",
    "Main Menu": "^",
    "Exit Game": "X"
}

def get_menu_icon(option_text):
    """Get a simple ASCII icon for the given menu option"""
    return MENU_ICONS.get(option_text, "•")

# Alternative: More descriptive text-based icons
MENU_ICONS_TEXT = {
    "Continue Game": "PLAY",
    "New Game": "NEW", 
    "Load Game": "LOAD",
    "Save Game": "SAVE",
    "Achievements": "STAR",
    "Help": "HELP",
    "Settings": "OPTS",
    "About": "INFO",
    "Exit": "QUIT"
}

def get_menu_icon_text(option_text):
    """Get a text-based icon for the given menu option"""
    return MENU_ICONS_TEXT.get(option_text, "---")
