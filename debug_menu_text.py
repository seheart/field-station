#!/usr/bin/env python3
"""Debug what text is actually being rendered"""

import pygame
from menu_icons import get_menu_icon

pygame.init()
font = pygame.font.Font(None, 36)

menu_options = ["New Game", "Load Game", "Settings", "Exit"]

print("Testing menu text rendering:")
print("-" * 40)

for option in menu_options:
    icon = get_menu_icon(option)
    menu_text = f"{icon}  {option}"
    
    print(f"Option: '{option}'")
    print(f"Icon: '{icon}'")
    print(f"Combined text: '{menu_text}'")
    print(f"Length: {len(menu_text)}")
    print()

pygame.quit()