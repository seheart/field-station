"""
Example of how to use the UI Framework

This shows how to convert an existing menu page to use the new framework
instead of manual pygame rendering.
"""

import pygame
from ui_framework import UIManager, MenuPanel

def create_help_page_with_framework(screen, fonts):
    """
    Example: Create the help page using the new UI framework
    
    OLD WAY (lots of repetitive code):
    - Manual panel creation
    - Manual text wrapping
    - Manual emoji handling
    - Lots of hardcoded positions
    
    NEW WAY (clean and simple):
    - Just define content
    - Framework handles everything else
    """
    
    # Extract fonts (assume these are passed from the main game)
    title_font = fonts['title']
    emoji_font = fonts['emoji'] 
    content_font = fonts['content']
    ui_font = fonts['ui']
    
    # Create UI manager
    ui = UIManager(screen)
    
    # Draw background
    ui.draw_warm_gradient_background()
    
    # Create menu panel with title and emoji
    help_panel = MenuPanel("HELP & TUTORIALS", "📖", width=700, height=500)
    help_panel.set_fonts(title_font, emoji_font, content_font, ui_font)
    
    # Add content using the simple API
    help_panel.content_area.add_header("Welcome to Field Station!", ui_font) \
        .add_spacer() \
        .add_text("Field Station is an agricultural simulation game where you can:", content_font) \
        .add_spacer() \
        .add_text("• Plant and grow various crops", content_font) \
        .add_text("• Monitor soil quality and conditions", content_font) \
        .add_text("• Track detailed growth data", content_font) \
        .add_text("• Harvest and sell your produce", content_font) \
        .add_spacer() \
        .add_header("Getting Started:", ui_font) \
        .add_text("1. Click on empty tiles to plant crops", content_font) \
        .add_text("2. Wait for crops to grow (time advances automatically)", content_font) \
        .add_text("3. Click on ready crops to harvest them", content_font) \
        .add_text("4. Use the market panel to sell your harvest", content_font) \
        .add_spacer() \
        .add_header("Advanced Features:", ui_font) \
        .add_text("• Right-click tiles to see detailed information", content_font) \
        .add_text("• Use the data panels to track farm statistics", content_font) \
        .add_text("• Experiment with different crop combinations", content_font)
    
    # Add panel to UI manager
    ui.add_element(help_panel)
    
    # Render everything
    ui.render()
    
    return ui  # Return so caller can handle events

# Example of how to integrate this into your existing game:
"""
def draw_help_screen_NEW_WAY(self):
    # OLD CODE: 50+ lines of manual rendering
    
    # NEW CODE: 3 lines!
    fonts = {
        'title': self.title_font,
        'emoji': self.emoji_font, 
        'content': self.font,
        'ui': self.ui_font
    }
    self.current_ui = create_help_page_with_framework(self.screen, fonts)

def handle_help_screen_events_NEW_WAY(self, event):
    # Let framework handle events
    return self.current_ui.handle_event(event)
"""

def create_about_page_with_framework(screen, fonts):
    """Another example - About page with framework"""
    
    ui = UIManager(screen)
    ui.draw_warm_gradient_background()
    
    about_panel = MenuPanel("FIELD STATION", "ℹ️", width=700, height=500)
    about_panel.set_fonts(fonts['title'], fonts['emoji'], fonts['content'], fonts['ui'])
    
    about_panel.content_area.add_text("Version 0.1", fonts['ui']) \
        .add_spacer() \
        .add_header("Grow, Learn, Discover - A Playful Plant Growing Experience", fonts['ui']) \
        .add_spacer() \
        .add_text("A sandbox farming game where you can watch plants grow and enjoy the rich data behind every harvest.", fonts['content']) \
        .add_spacer() \
        .add_text("Plant crops, monitor soil quality, track growth patterns, and harvest your success. It's fun but has real data for those who love details and learning.", fonts['content']) \
        .add_spacer() \
        .add_text("Built with passion for plants and discovery.", fonts['content'])
    
    ui.add_element(about_panel)
    ui.render()
    return ui

def create_controls_page_with_framework(screen, fonts):
    """Controls page example - super clean!"""
    
    ui = UIManager(screen)
    ui.draw_warm_gradient_background()
    
    controls_panel = MenuPanel("CONTROLS", "⌨️", width=700, height=500)
    controls_panel.set_fonts(fonts['title'], fonts['emoji'], fonts['content'], fonts['ui'])
    
    controls_panel.content_area.add_header("Mouse Controls:", fonts['ui']) \
        .add_text("• Left Click - Plant crops, harvest, interact with tiles", fonts['content']) \
        .add_text("• Right Click - Get information about tiles", fonts['content']) \
        .add_text("• Mouse Wheel - Zoom in and out", fonts['content']) \
        .add_text("• Drag - Pan the camera view", fonts['content']) \
        .add_spacer() \
        .add_header("Keyboard Controls:", fonts['ui']) \
        .add_text("• Space - Pause/unpause the game", fonts['content']) \
        .add_text("• ESC - Return to main menu", fonts['content']) \
        .add_text("• F1 - Toggle debug information display", fonts['content']) \
        .add_text("• Ctrl+S - Quick save game", fonts['content']) \
        .add_text("• Ctrl+L - Quick load game", fonts['content']) \
        .add_spacer() \
        .add_header("Game Tips:", fonts['ui']) \
        .add_text("• Time automatically advances when not paused", fonts['content']) \
        .add_text("• Click empty tiles to plant crops", fonts['content']) \
        .add_text("• Click ready crops to harvest them", fonts['content']) \
        .add_text("• Use the UI panels for market and farm info", fonts['content']) \
        .add_text("• Monitor soil quality and crop progress", fonts['content'])
    
    ui.add_element(controls_panel)
    ui.render()
    return ui