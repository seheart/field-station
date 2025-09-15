#!/usr/bin/env python3
"""Test script to verify menu button click detection with emojis"""

import pygame
import sys
from menu_icons import get_menu_icon

pygame.init()

# Test font rendering with emojis
font = pygame.font.Font(None, 36)

menu_options = ["New Game", "Load Game", "Settings", "Exit"]

print("Testing menu text rendering with emojis:")
print("-" * 50)

for option in menu_options:
    # Original text
    text_surface = font.render(option, True, (255, 255, 255))
    original_width = text_surface.get_width()
    
    # Text with emoji
    emoji = get_menu_icon(option)
    menu_text = f"{emoji}  {option}"
    emoji_surface = font.render(menu_text, True, (255, 255, 255))
    emoji_width = emoji_surface.get_width()
    
    print(f"Option: {option}")
    print(f"  Emoji: {emoji}")
    print(f"  Original width: {original_width}px")
    print(f"  With emoji width: {emoji_width}px")
    print(f"  Width increase: {emoji_width - original_width}px")
    print()

# Test button rect calculations
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

print("\nButton Rectangle Calculations:")
print("-" * 50)

# From draw_main_menu_buttons_overlay
button_x = SCREEN_WIDTH // 2 + 50
button_width = 250
button_height = 45
button_spacing = 55
total_menu_items = len(menu_options)
buttons_start_y = SCREEN_HEIGHT // 2 - (total_menu_items * button_spacing // 2) + 20

print(f"draw_main_menu_buttons_overlay rectangles:")
for i, option in enumerate(menu_options):
    button_y = buttons_start_y + i * button_spacing
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    print(f"  {option}: {button_rect}")

print()

# From get_menu_item_rect (old incorrect version)
print(f"get_menu_item_rect rectangles (old):")
for i, option in enumerate(menu_options):
    button_y = SCREEN_HEIGHT // 2 + i * 50
    button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, button_y, 400, 45)
    print(f"  {option}: {button_rect}")

print("\nMismatch Analysis:")
print("- X position mismatch: draw uses 650, get_menu_item_rect uses 400")
print("- Width mismatch: draw uses 250, get_menu_item_rect uses 400")
print("- Y calculation mismatch: different spacing and start positions")