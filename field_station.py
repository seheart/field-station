#!/usr/bin/env python3
"""
Field Station - A Scientifically-Accurate Farming Simulation

Copyright (c) 2024 Seth Roberts. All rights reserved.

This software is proprietary. See LICENSE file for terms and conditions.
Educational use in academic institutions is permitted.
Commercial use requires explicit written permission.

For licensing inquiries: contact@field-station.dev
"""

import pygame
import sys
import math
import random
import os
import json
from datetime import datetime, timedelta

# Import the new UI framework
try:
    from ui_framework import UIManager, MenuPanel
    UI_FRAMEWORK_AVAILABLE = True
except ImportError as e:
    UI_FRAMEWORK_AVAILABLE = False
    print(f"UI Framework not available: {e}, using legacy rendering")
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple, List
from menu_icons import get_menu_icon, get_menu_icon_text

# Set window class BEFORE initializing Pygame
os.environ['SDL_VIDEO_X11_WMCLASS'] = 'field-station'

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
GRID_WIDTH = 3
GRID_HEIGHT = 3
TILE_WIDTH = 64
TILE_HEIGHT = 32

# Game Constants
SEED_COST = 10
HARVEST_SOIL_DAMAGE = 0.05
DAY_LENGTH_MS = 30000
MESSAGE_DURATION = 3000

# Font Sizes
FONT_SIZES = {
    'title': 72,
    'heading': 48,
    'body': 24,
    'small': 16
}

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
BLUE = (100, 149, 237)
YELLOW = (255, 215, 0)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 100, 0)
LIGHT_BROWN = (205, 133, 63)
LIGHT_GREEN = (144, 238, 144)
DARK_GRAY = (50, 50, 50)
RED = (255, 0, 0)

# Seasons
class Season(Enum):
    SPRING = 1
    SUMMER = 2
    FALL = 3
    WINTER = 4

# Crop Types
@dataclass
class CropType:
    name: str
    growth_time: int  # days
    color: Tuple[int, int, int]
    seasons: List[Season]  # Valid planting seasons
    nitrogen_need: float  # 0-1
    water_need: float  # 0-1
    value: int  # Sale price
    
CROP_TYPES = {
    "wheat_soft_red_winter": CropType("Wheat - Triticum aestivum 'Soft Red Winter'", 90, YELLOW, [Season.FALL], 0.4, 0.3, 25),
    "corn_sweet": CropType("Corn - Zea mays var. saccharata", 120, (255, 200, 0), [Season.SPRING], 0.6, 0.5, 35),
    "potato_russet_burbank": CropType("Potato - Solanum tuberosum 'Russet Burbank'", 70, (165, 113, 78), [Season.SPRING], 0.3, 0.4, 20),
    "carrot_imperator": CropType("Carrot - Daucus carota 'Imperator'", 60, (255, 140, 0), [Season.SPRING, Season.SUMMER], 0.2, 0.3, 15),
    "soybean": CropType("Soybean - Glycine max", 95, DARK_GREEN, [Season.SPRING, Season.SUMMER], -0.3, 0.4, 30),  # Negative = adds nitrogen
    "field_corn": CropType("Field Corn - Zea mays var. indentata", 140, (200, 160, 0), [Season.SPRING], 0.7, 0.6, 40),
    "pumpkin_howden": CropType("Pumpkin - Cucurbita pepo 'Howden'", 110, (255, 117, 24), [Season.SPRING], 0.5, 0.7, 28),
    "tomato_better_boy": CropType("Tomato - Solanum lycopersicum 'Better Boy'", 75, (255, 99, 71), [Season.SPRING, Season.SUMMER], 0.6, 0.8, 45),
}

class Weather(Enum):
    SUNNY = 1
    CLOUDY = 2
    RAINY = 3
    SNOWY = 4
    DROUGHT = 5
    FLOOD = 6
    STORM = 7
    HAIL = 8

@dataclass
class Tile:
    x: int
    y: int
    soil_quality: float  # 0-1
    moisture: float  # 0-1
    nitrogen: float  # 0-1
    crop: Optional[str] = None
    growth_progress: float = 0.0
    days_planted: int = 0
    harvested_times: int = 0

class Market:
    """Handles dynamic pricing for crops based on season and supply/demand"""
    
    def __init__(self):
        # Seasonal modifiers for crop prices
        self.seasonal_modifiers = {
            Season.SPRING: {
                "wheat_soft_red_winter": 1.2,  # Higher demand in spring
                "corn_sweet": 0.9,
                "potato_russet_burbank": 1.1,
                "carrot_imperator": 1.0,
                "soybean": 1.0,
                "field_corn": 0.8,
                "pumpkin_howden": 0.7,  # Off season
                "tomato_better_boy": 0.9
            },
            Season.SUMMER: {
                "wheat_soft_red_winter": 0.8,
                "corn_sweet": 1.3,  # Peak season
                "potato_russet_burbank": 0.9,
                "carrot_imperator": 1.1,
                "soybean": 1.0,
                "field_corn": 1.0,
                "pumpkin_howden": 0.8,
                "tomato_better_boy": 1.4  # Peak season
            },
            Season.FALL: {
                "wheat_soft_red_winter": 1.0,
                "corn_sweet": 0.7,
                "potato_russet_burbank": 1.2,  # Harvest season
                "carrot_imperator": 1.3,  # Harvest season
                "soybean": 1.2,  # Harvest season
                "field_corn": 1.3,  # Harvest season
                "pumpkin_howden": 1.5,  # Peak season
                "tomato_better_boy": 0.8
            },
            Season.WINTER: {
                "wheat_soft_red_winter": 1.1,
                "corn_sweet": 1.0,
                "potato_russet_burbank": 1.0,
                "carrot_imperator": 0.9,
                "soybean": 1.1,
                "field_corn": 1.0,
                "pumpkin_howden": 0.6,  # Off season
                "tomato_better_boy": 1.1  # Greenhouse premium
            }
        }
        
        # Random daily fluctuations
        self.daily_variance = 0.15  # ±15% daily price variation
        
    def get_crop_price(self, crop_name: str, season: Season, day: int) -> int:
        """Get current market price for a crop"""
        if crop_name not in CROP_TYPES:
            return 0
            
        base_price = CROP_TYPES[crop_name].value
        seasonal_modifier = self.seasonal_modifiers[season].get(crop_name, 1.0)
        
        # Add some daily randomness based on day (deterministic but varying)
        random.seed(day + hash(crop_name))  # Deterministic randomness
        daily_modifier = 1.0 + random.uniform(-self.daily_variance, self.daily_variance)
        
        final_price = int(base_price * seasonal_modifier * daily_modifier)
        return max(1, final_price)  # Minimum price of 1
    
    def get_price_trend(self, crop_name: str, season: Season) -> str:
        """Get price trend indicator for UI"""
        modifier = self.seasonal_modifiers[season].get(crop_name, 1.0)
        if modifier >= 1.2:
            return "↗ HIGH"
        elif modifier >= 1.1:
            return "↗ Good"
        elif modifier <= 0.8:
            return "↘ Low"
        elif modifier <= 0.9:
            return "↘ Poor"
        else:
            return "→ Fair"
    
class GameState(Enum):
    MENU = 1
    GAME = 2
    LOAD = 3
    TUTORIALS = 4
    ACHIEVEMENTS = 5
    OPTIONS = 6
    HELP = 7
    FARM_SETUP = 8
    PAUSE_MENU = 9
    ABOUT = 10

class FieldStation:
    def __init__(self):
        # Detect available displays and set initial display
        self.current_display = self.get_current_display()
        self.available_displays = self.get_available_displays()
        
        # Start in fullscreen (borderless windowed)
        self.fullscreen = True
        self.create_window()
            
        pygame.display.set_caption("Field Station")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        self.ui_font = pygame.font.Font(None, 24)
        self.menu_font = pygame.font.Font(None, 48)
        self.menu_title_font = pygame.font.Font(None, 72)
        
        # Try to load emoji font - larger base size for better scaling
        try:
            self.emoji_font = pygame.font.Font("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 48)
        except Exception as e:
            # Try alternative emoji font locations
            try:
                self.emoji_font = pygame.font.SysFont("Segoe UI Emoji", 48)
            except:
                self.emoji_font = None  # Will use fallback
        
        # Game states
        self.game_state = GameState.MENU
        self.menu_selection = 0
        
        # Mouse and camera controls
        self.mouse_dragging = False
        self.mouse_down = False  # Track if mouse is down but not yet dragging
        self.drag_start = (0, 0)
        self.drag_threshold = 5  # Pixels to move before starting drag
        self.keys_pressed = set()  # Track continuously held keys
        self.zoom_level = 1.0  # Zoom level for camera
        self.min_zoom = 0.3
        self.max_zoom = 10.0  # Much higher zoom for close crop viewing
        
        # Options menu
        self.options_selection = 0
        self.previous_game_state = None  # Track where we came from
        self.game_in_progress = False  # Track if there's a game to return to
        self.update_menu_options()
        self.update_options_items()
        self.update_pause_menu_options()
        
        # Tile selection
        self.selected_tile_pos = None
        self.auto_harvest = False
        
        # Message system for user feedback
        self.messages = []
        
        # Tooltip system
        self.tooltip_text = ""
        self.tooltip_pos = (0, 0)
        self.tooltip_timer = 0
        
        # Tile popup interface (Banished-style)
        self.tile_popup_active = False
        self.tile_popup_pos = None  # (x, y) grid position
        self.popup_crop_selection = None  # Currently selected crop (None = nothing selected)
        self.popup_dropdown_open = False  # Is dropdown menu open
        self.popup_rect = None  # Screen rect for popup
        self.popup_close_rect = None  # Rect for X close button
        
        # Farm setup
        self.farm_name = ""
        self.farm_location = "Champaign, Illinois, USA (40.1164°N, 88.2434°W)"
        self.setup_name_input_active = True  # Start with name input active
        self.setup_location_selection = 0  # Index in available locations
        self.setup_season_selection = -1  # -1 means location selection, 0+ means season selection
        self.available_locations = [
            "Champaign, Illinois, USA (40.1164°N, 88.2434°W)",
            # More locations will be added later
        ]
        self.available_seasons = [
            ("Spring", "Plant new crops and begin growing season"),
            ("Summer", "Hot weather, ideal for summer crops"),
            ("Fall", "Harvest season with premium crop prices"),
            ("Winter", "Limited planting, plan next year's crops")
        ]
        
        # Interface controls screen
        self.interface_controls = [
            "CAMERA CONTROLS:",
            "  WASD / Arrow Keys - Move camera",
            "  Mouse Drag / Middle Mouse - Pan camera", 
            "  Mouse Wheel - Zoom in/out (0.3x to 10x)",
            "",
            "FARMING CONTROLS:",
            "  Left Click - Open tile popup",
            "  Dropdown - Select crop to plant",
            "  Click Harvest - Harvest crop from popup",
            "  A Key - Toggle auto-harvest",
            "",
            "GAME CONTROLS:",
            "  Space - Pause/unpause game",
            "  + / - Keys - Speed up/slow down time",
            "  ESC - Return to menu",
            "",
            "INTERFACE:",
            "  Mouse hover - Highlight menu items",
            "  Click or Enter - Confirm selection"
        ]
        
        # Help content
        self.help_content = [
            "GETTING STARTED:",
            "  • Start with the 3x3 grid of empty tiles",
            "  • Left-click to select a tile",
            "  • Press P to plant crops on empty tiles",
            "  • Press A to toggle auto-harvest mode",
            "",
            "GAME MECHANICS:",
            "  • Each tile has soil quality, moisture, and nitrogen",
            "  • Weather affects crop growth and soil moisture",
            "  • Seasons determine which crops can be planted",
            "  • Harvesting gradually reduces soil quality",
            "  • Different crops have different requirements",
            "",
            "CROP INFORMATION:",
            "  • Wheat: 90 days, moderate nitrogen need",
            "  • Corn: 120 days, high nitrogen need",
            "  • Potato: 70 days, low nitrogen need",
            "  • Carrot: 60 days, very low nitrogen need",
            "  • Beans: 80 days, adds nitrogen to soil",
            "",
            "TIPS:",
            "  • Use mouse wheel to zoom in and see crops up close",
            "  • Click pause/speed buttons in top left for time control",
            "  • Watch the weather - rain helps crops grow",
            "  • Plant beans to restore soil nitrogen",
            "  • Different seasons allow different crops"
        ]
        
        # Game state
        self.grid = [[Tile(x, y, 
                          random.uniform(0.4, 0.8),  # soil quality
                          random.uniform(0.3, 0.6),  # moisture
                          random.uniform(0.3, 0.7))   # nitrogen
                     for x in range(GRID_WIDTH)] 
                    for y in range(GRID_HEIGHT)]
        
        self.money = 500
        self.day = 1
        self.season = Season.SPRING
        self.weather = Weather.SUNNY
        # Center camera on the grid - more precise calculation
        self.camera_x = SCREEN_WIDTH // 2 - (GRID_WIDTH * TILE_WIDTH) // 2
        self.camera_y = SCREEN_HEIGHT // 2 - (GRID_HEIGHT * TILE_HEIGHT) // 2 - 50  # Offset up slightly for UI
        self.paused = False
        self.speed = 1  # Game speed multiplier
        self.last_day_update = pygame.time.get_ticks()
        
        # Date system - start at March 1st, 2025 (Spring)
        self.start_date = datetime(2025, 3, 1)
        self.current_date = self.start_date
        
        # Market system
        self.market = Market()
        
        # Weather affects
        self.weather_moisture_change = {
            Weather.SUNNY: -0.02,
            Weather.CLOUDY: -0.01,
            Weather.RAINY: 0.05,
            Weather.SNOWY: 0.02,
            Weather.DROUGHT: -0.08,  # Severe moisture loss
            Weather.FLOOD: 0.15,     # Excessive moisture
            Weather.STORM: 0.08,     # Heavy rain
            Weather.HAIL: 0.03       # Some moisture but crop damage
        }
        
        # Extreme weather tracking
        self.extreme_weather_chance = 0.05  # 5% chance per day
        self.last_extreme_weather = 0
        
        # Debug mode (toggle with F1)
        self.debug_mode = False
        
        # UI elements
        self.settings_button_rect = None
        
        # Modular panel system - Banished-style
        self.modular_panels = {}  # Panel ID -> panel data
        self.dragging_panel = None
        self.drag_offset = (0, 0)
        self.icon_size = 32
        self.icon_spacing = 40
        
        # Initialize bottom-right icon positions
        icon_start_x = SCREEN_WIDTH - 50
        icon_y = SCREEN_HEIGHT - 50
        
        self.ui_icons = {
            'field_study': {'pos': (icon_start_x - 4 * self.icon_spacing, icon_y), 'panel': None},
            'resources': {'pos': (icon_start_x - 3 * self.icon_spacing, icon_y), 'panel': None},
            'speed': {'pos': (icon_start_x - 2 * self.icon_spacing, icon_y), 'panel': None},
            'help': {'pos': (icon_start_x - self.icon_spacing, icon_y), 'panel': None},
            'settings': {'pos': (icon_start_x, icon_y), 'panel': None}
        }
    
    # ============================================================================
    # UI FRAMEWORK INTEGRATION
    # ============================================================================
    
    def create_framework_fonts(self) -> dict:
        """Create font dictionary for UI framework"""
        return {
            'title': self.menu_title_font,
            'emoji': self.emoji_font,
            'content': self.font,
            'ui': self.ui_font
        }
    
    def create_framework_page(self, title: str, emoji: str, content_callback) -> 'UIManager':
        """
        Create a page using the UI framework
        
        Args:
            title: Page title
            emoji: Emoji for title
            content_callback: Function that takes content_area and populates it
        
        Returns:
            UIManager instance ready for rendering
        """
        if not UI_FRAMEWORK_AVAILABLE:
            return None
            
        ui = UIManager(self.screen)
        ui.draw_warm_gradient_background()
        
        # Create panel
        panel = MenuPanel(title, emoji, width=700, height=500)
        panel.set_fonts(**self.create_framework_fonts())
        
        # Let callback populate content
        content_callback(panel.content_area)
        
        ui.add_element(panel)
        return ui
    
    def render_help_page_framework(self):
        """Example: Render help page using framework"""
        def populate_content(content_area):
            fonts = self.create_framework_fonts()
            content_area.add_header("Welcome to Field Station!", fonts['ui']) \
                .add_spacer() \
                .add_text("Field Station is an agricultural simulation game where you can:", fonts['content']) \
                .add_spacer() \
                .add_text("• Plant and grow various crops", fonts['content']) \
                .add_text("• Monitor soil quality and conditions", fonts['content']) \
                .add_text("• Track detailed growth data", fonts['content']) \
                .add_text("• Harvest and sell your produce", fonts['content']) \
                .add_spacer() \
                .add_header("Getting Started:", fonts['ui']) \
                .add_text("1. Click on empty tiles to plant crops", fonts['content']) \
                .add_text("2. Wait for crops to grow (time advances automatically)", fonts['content']) \
                .add_text("3. Click on ready crops to harvest them", fonts['content']) \
                .add_text("4. Use the market panel to sell your harvest", fonts['content'])
        
        ui = self.create_framework_page("HELP & TUTORIALS", "📖", populate_content)
        if ui:
            ui.render()
            return ui
        return None
    
    # ============================================================================
    # END UI FRAMEWORK INTEGRATION
    # ============================================================================
    
    def screen_to_grid(self, x, y) -> Optional[Tuple[int, int]]:
        """Convert screen coordinates to grid coordinates - WITH DIAMOND SHAPE CHECK"""
        # Adjust for camera offset
        world_x = x - self.camera_x
        world_y = y - self.camera_y
        
        # Apply zoom to tile size - use same int conversion as grid_to_screen
        tile_w = int(TILE_WIDTH * self.zoom_level)
        tile_h = int(TILE_HEIGHT * self.zoom_level)
        
        # Offset click position to account for tile center vs corner
        # The drawn tile center is at (corner_x + tile_w//2, corner_y + tile_h//2)
        # So to find which corner a center click came from, we offset backward
        world_x -= tile_w // 2
        world_y -= tile_h // 2
        
        # Now apply the inverse formula to the corner coordinates
        grid_x_float = (world_x / tile_w * 2 + world_y / tile_h * 2) / 2
        grid_y_float = (world_y / tile_h * 2 - world_x / tile_w * 2) / 2
        
        # Round to nearest grid position
        grid_x = round(grid_x_float)
        grid_y = round(grid_y_float)
        
        # Check bounds first
        if not (0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT):
            return None
        
        # Now check if the click is actually INSIDE the diamond shape
        # Get the corner position of this tile
        corner_x, corner_y = self.grid_to_screen(grid_x, grid_y)
        
        # Convert back to original click position relative to tile corner
        click_x = x - corner_x
        click_y = y - corner_y
        
        # Check if click is inside diamond using diamond equation
        # Diamond points: (0, tile_h//2), (tile_w//2, 0), (tile_w, tile_h//2), (tile_w//2, tile_h)
        # For a point to be inside, we check if it's within all 4 triangle boundaries
        is_inside = self.point_in_diamond(click_x, click_y, tile_w, tile_h)
        
        if self.debug_mode:
            self.show_message(f"Grid({grid_x},{grid_y}): click_rel({click_x:.1f},{click_y:.1f}) inside={is_inside}", 
                            GREEN if is_inside else RED, 2000)
        
        if is_inside:
            return (grid_x, grid_y)
        
        return None
    
    def point_in_diamond(self, px, py, tile_w, tile_h) -> bool:
        """Check if point (px, py) is inside diamond with given tile dimensions"""
        # Diamond center
        cx, cy = tile_w // 2, tile_h // 2
        
        # Convert to relative coordinates from center
        dx = abs(px - cx)
        dy = abs(py - cy)
        
        # Diamond equation: |x|/half_width + |y|/half_height <= 1
        return dx / (tile_w // 2) + dy / (tile_h // 2) <= 1.0
    
    def find_closest_tile(self, screen_x, screen_y) -> Optional[Tuple[int, int]]:
        """Backup method: find the closest tile to a screen click using brute force"""
        closest_tile = None
        min_distance = float('inf')
        
        for grid_y in range(GRID_HEIGHT):
            for grid_x in range(GRID_WIDTH):
                # Get the center of this tile
                tile_center_x, tile_center_y = self.grid_to_screen(grid_x, grid_y)
                
                # Calculate distance from click to tile center
                dx = screen_x - tile_center_x
                dy = screen_y - tile_center_y
                distance = (dx * dx + dy * dy) ** 0.5
                
                # Check if this is the closest tile and within reasonable range
                max_distance = 100 * self.zoom_level  # Generous click radius
                if distance < min_distance and distance < max_distance:
                    min_distance = distance
                    closest_tile = (grid_x, grid_y)
        
        return closest_tile
    
    def grid_to_screen(self, grid_x, grid_y) -> Tuple[int, int]:
        """Convert grid coordinates to screen coordinates"""
        # Apply zoom to tile size
        tile_w = int(TILE_WIDTH * self.zoom_level)
        tile_h = int(TILE_HEIGHT * self.zoom_level)
        
        x = (grid_x - grid_y) * tile_w // 2 + self.camera_x
        y = (grid_x + grid_y) * tile_h // 2 + self.camera_y
        return (x, y)
    
    def show_message(self, text: str, color: Tuple[int, int, int] = RED, duration: int = MESSAGE_DURATION):
        """Show a message to the user"""
        self.messages.append({
            'text': text,
            'color': color,
            'start_time': pygame.time.get_ticks(),
            'duration': duration
        })
    
    def update_messages(self):
        """Update and remove expired messages"""
        current_time = pygame.time.get_ticks()
        self.messages = [msg for msg in self.messages 
                        if current_time - msg['start_time'] < msg['duration']]
    
    def draw_messages(self):
        """Draw active messages"""
        for i, msg in enumerate(self.messages):
            current_time = pygame.time.get_ticks()
            elapsed = current_time - msg['start_time']
            
            # Fade out effect
            alpha = max(0, 255 - int(255 * elapsed / msg['duration']))
            
            # Create surface with alpha
            text_surface = self.ui_font.render(msg['text'], True, msg['color'])
            text_surface.set_alpha(alpha)
            
            # Position messages at top-center
            x = SCREEN_WIDTH // 2 - text_surface.get_width() // 2
            y = 100 + i * 30
            
            # Background for readability
            bg_rect = pygame.Rect(x - 10, y - 5, text_surface.get_width() + 20, text_surface.get_height() + 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surface.set_alpha(alpha // 2)
            bg_surface.fill(BLACK)
            self.screen.blit(bg_surface, bg_rect)
            
            self.screen.blit(text_surface, (x, y))
    
    def show_tooltip(self, text: str, pos: Tuple[int, int]):
        """Show a tooltip at the specified position"""
        self.tooltip_text = text
        self.tooltip_pos = pos
        self.tooltip_timer = pygame.time.get_ticks()
    
    def draw_tooltip(self):
        """Draw the tooltip if active"""
        if not self.tooltip_text:
            return
            
        # Show tooltip for 2 seconds after being set
        if pygame.time.get_ticks() - self.tooltip_timer > 2000:
            self.tooltip_text = ""
            return
        
        # Create tooltip surface
        tooltip_surface = self.font.render(self.tooltip_text, True, WHITE)
        tooltip_width = tooltip_surface.get_width() + 20
        tooltip_height = tooltip_surface.get_height() + 10
        
        # Position tooltip near mouse, but keep on screen
        x, y = self.tooltip_pos
        x = max(10, min(x + 15, SCREEN_WIDTH - tooltip_width - 10))
        y = max(10, min(y - tooltip_height - 10, SCREEN_HEIGHT - tooltip_height - 10))
        
        # Draw background
        bg_rect = pygame.Rect(x, y, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, (50, 50, 50), bg_rect)
        pygame.draw.rect(self.screen, WHITE, bg_rect, 1)
        
        # Draw text
        self.screen.blit(tooltip_surface, (x + 10, y + 5))
    
    def draw_debug_info(self):
        """Draw debug information overlay"""
        debug_y = 10
        
        # Camera info
        debug_text = f"Camera: ({self.camera_x:.0f}, {self.camera_y:.0f}) Zoom: {self.zoom_level:.2f}"
        debug_surface = self.font.render(debug_text, True, WHITE)
        
        # Background for readability
        bg_rect = pygame.Rect(10, debug_y, debug_surface.get_width() + 10, debug_surface.get_height() + 5)
        pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
        pygame.draw.rect(self.screen, WHITE, bg_rect, 1)
        
        self.screen.blit(debug_surface, (15, debug_y + 2))
        debug_y += 30
        
        # Mouse info
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_pos = self.screen_to_grid(mouse_x, mouse_y)
        mouse_text = f"Mouse: ({mouse_x}, {mouse_y}) Grid: {grid_pos}"
        mouse_surface = self.font.render(mouse_text, True, WHITE)
        
        bg_rect = pygame.Rect(10, debug_y, mouse_surface.get_width() + 10, mouse_surface.get_height() + 5)
        pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
        pygame.draw.rect(self.screen, WHITE, bg_rect, 1)
        
        self.screen.blit(mouse_surface, (15, debug_y + 2))
        debug_y += 30
        
        # Selected tile info
        if self.selected_tile_pos:
            selected_text = f"Selected: {self.selected_tile_pos}"
            selected_surface = self.font.render(selected_text, True, YELLOW)
            
            bg_rect = pygame.Rect(10, debug_y, selected_surface.get_width() + 10, selected_surface.get_height() + 5)
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(self.screen, WHITE, bg_rect, 1)
            
            self.screen.blit(selected_surface, (15, debug_y + 2))
        
        # Draw tile grid outlines
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                tile_screen_x, tile_screen_y = self.grid_to_screen(x, y)
                tile_w = int(TILE_WIDTH * self.zoom_level)
                tile_h = int(TILE_HEIGHT * self.zoom_level)
                
                # Draw tile center
                pygame.draw.circle(self.screen, RED, (tile_screen_x, tile_screen_y), 3)
                
                # Draw tile bounds (diamond) - centered on tile position
                points = [
                    (tile_screen_x, tile_screen_y - tile_h // 2),  # top
                    (tile_screen_x + tile_w // 2, tile_screen_y),  # right
                    (tile_screen_x, tile_screen_y + tile_h // 2),  # bottom  
                    (tile_screen_x - tile_w // 2, tile_screen_y)   # left
                ]
                pygame.draw.polygon(self.screen, RED, points, 1)
    
    def save_game(self, filename: str = "savegame.json"):
        """Save the current game state to a JSON file"""
        try:
            save_data = {
                'version': '0.1',
                'farm_name': self.farm_name,
                'farm_location': self.farm_location,
                'money': self.money,
                'day': self.day,
                'season': self.season.name,
                'weather': self.weather.name,
                'current_date': self.current_date.isoformat(),
                'auto_harvest': self.auto_harvest,
                'grid': []
            }
            
            # Save grid state
            for row in self.grid:
                row_data = []
                for tile in row:
                    tile_data = {
                        'x': tile.x,
                        'y': tile.y,
                        'soil_quality': tile.soil_quality,
                        'moisture': tile.moisture,
                        'nitrogen': tile.nitrogen,
                        'crop': tile.crop,
                        'growth_progress': tile.growth_progress,
                        'days_planted': tile.days_planted,
                        'harvested_times': tile.harvested_times
                    }
                    row_data.append(tile_data)
                save_data['grid'].append(row_data)
            
            # Create saves directory if it doesn't exist
            os.makedirs('saves', exist_ok=True)
            
            with open(f'saves/{filename}', 'w') as f:
                json.dump(save_data, f, indent=2)
            
            self.show_message(f"Game saved as {filename}", GREEN)
            return True
            
        except Exception as e:
            self.show_message(f"Save failed: {str(e)}", RED)
            return False
    
    def load_game(self, filename: str = "savegame.json"):
        """Load a game state from a JSON file"""
        try:
            with open(f'saves/{filename}', 'r') as f:
                save_data = json.load(f)
            
            # Restore game state
            self.farm_name = save_data.get('farm_name', '')
            self.farm_location = save_data.get('farm_location', 'Champaign, Illinois, USA (40.1164°N, 88.2434°W)')
            self.money = save_data.get('money', 500)
            self.day = save_data.get('day', 1)
            self.season = Season[save_data.get('season', 'SPRING')]
            self.weather = Weather[save_data.get('weather', 'SUNNY')]
            self.current_date = datetime.fromisoformat(save_data.get('current_date', '2025-03-01T00:00:00'))
            self.auto_harvest = save_data.get('auto_harvest', False)
            
            # Restore grid
            grid_data = save_data.get('grid', [])
            for y, row_data in enumerate(grid_data):
                for x, tile_data in enumerate(row_data):
                    if y < GRID_HEIGHT and x < GRID_WIDTH:
                        tile = self.grid[y][x]
                        tile.soil_quality = tile_data.get('soil_quality', 0.5)
                        tile.moisture = tile_data.get('moisture', 0.5)
                        tile.nitrogen = tile_data.get('nitrogen', 0.5)
                        tile.crop = tile_data.get('crop')
                        tile.growth_progress = tile_data.get('growth_progress', 0.0)
                        tile.days_planted = tile_data.get('days_planted', 0)
                        tile.harvested_times = tile_data.get('harvested_times', 0)
            
            self.show_message(f"Game loaded from {filename}", GREEN)
            self.game_in_progress = True
            return True
            
        except FileNotFoundError:
            self.show_message("Save file not found", RED)
            return False
        except Exception as e:
            self.show_message(f"Load failed: {str(e)}", RED)
            return False
    
    def get_short_crop_name(self, crop_name: str) -> str:
        """Get shortened crop name for UI display"""
        if not crop_name:
            return ""
        full_name = CROP_TYPES[crop_name].name
        if ' - ' in full_name:
            return full_name.split(' - ')[0]
        return full_name
    
    def get_seasonal_background_color(self) -> Tuple[int, int, int]:
        """Get seasonal background color based on current season"""
        if self.season == Season.WINTER:
            return (180, 200, 220)  # Blue-white
        elif self.season == Season.SPRING:
            return (200, 220, 180)  # Yellow-green
        elif self.season == Season.SUMMER:
            return (220, 210, 170)  # Yellow-orange
        elif self.season == Season.FALL:
            return (210, 180, 160)  # Orange-brown
        else:
            return (190, 190, 190)  # Default gray
    
    def draw_tile(self, tile: Tile):
        """Draw a single isometric tile"""
        x, y = self.grid_to_screen(tile.x, tile.y)
        
        # Apply zoom to tile size
        tile_w = int(TILE_WIDTH * self.zoom_level)
        tile_h = int(TILE_HEIGHT * self.zoom_level)
        
        # Calculate tile color based on state
        if tile.crop and tile.growth_progress < 1.0:
            # Growing crop - blend from brown to crop color
            crop_color = CROP_TYPES[tile.crop].color
            progress = tile.growth_progress
            r = int(BROWN[0] * (1 - progress) + crop_color[0] * progress)
            g = int(BROWN[1] * (1 - progress) + crop_color[1] * progress)
            b = int(BROWN[2] * (1 - progress) + crop_color[2] * progress)
            color = (r, g, b)
        elif tile.crop and tile.growth_progress >= 1.0:
            # Fully grown crop
            color = CROP_TYPES[tile.crop].color
        else:
            # Empty tile - color based on soil quality
            quality = tile.soil_quality
            if quality > 0.7:
                color = DARK_GREEN
            elif quality > 0.5:
                color = GREEN
            else:
                color = LIGHT_BROWN
        
        # Draw the isometric tile with zoom
        points = [
            (x, y + tile_h // 2),
            (x + tile_w // 2, y),
            (x + tile_w, y + tile_h // 2),
            (x + tile_w // 2, y + tile_h)
        ]
        pygame.draw.polygon(self.screen, color, points)
        
        # Draw border with selection highlight
        border_color = YELLOW if (hasattr(self, 'selected_tile_pos') and 
                                 self.selected_tile_pos == (tile.x, tile.y)) else DARK_GRAY
        border_width = 3 if border_color == YELLOW else 2
        pygame.draw.polygon(self.screen, border_color, points, border_width)
        
        # Draw progress bar for crops at high zoom levels
        if tile.crop and self.zoom_level > 2.0:
            self.draw_growth_bar(tile, x, y, tile_w, tile_h)
    
    def draw_growth_bar(self, tile: Tile, tile_x: int, tile_y: int, tile_w: int, tile_h: int):
        """Draw a progress bar above the tile showing crop growth"""
        if not tile.crop or tile.growth_progress >= 1.0:
            return
            
        # Position bar above the tile
        bar_width = max(20, tile_w // 2)
        bar_height = max(4, int(6 * self.zoom_level))
        bar_x = tile_x + tile_w // 2 - bar_width // 2
        bar_y = tile_y - bar_height - 5
        
        # Background bar
        pygame.draw.rect(self.screen, (40, 40, 40), 
                        (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, WHITE, 
                        (bar_x, bar_y, bar_width, bar_height), 1)
        
        # Progress bar
        progress_width = int(bar_width * tile.growth_progress)
        if progress_width > 0:
            progress_color = GREEN if tile.growth_progress >= 0.8 else YELLOW if tile.growth_progress >= 0.5 else RED
            pygame.draw.rect(self.screen, progress_color, 
                           (bar_x, bar_y, progress_width, bar_height))
        
    
    def update_day(self):
        """Progress to next day"""
        self.day += 1
        self.current_date += timedelta(days=1)
        
        # Update season based on calendar date
        month = self.current_date.month
        if month in [3, 4, 5]:
            self.season = Season.SPRING
        elif month in [6, 7, 8]:
            self.season = Season.SUMMER
        elif month in [9, 10, 11]:
            self.season = Season.FALL
        else:  # 12, 1, 2
            self.season = Season.WINTER
        
        # Check for auto-harvest
        self.auto_harvest_check()
        
        # Seasonal and date-based weather patterns
        month = self.current_date.month
        day_of_month = self.current_date.day
        
        # Central Illinois weather patterns - realistic for Champaign area
        if self.season == Season.WINTER:
            # Central Illinois winter: Cold, some snow, many cloudy days
            if month == 12:  # December - early winter, less snow
                weather_options = [Weather.CLOUDY, Weather.CLOUDY, Weather.SNOWY, Weather.SUNNY]
            elif month == 1:  # January - coldest, more snow
                weather_options = [Weather.SNOWY, Weather.CLOUDY, Weather.CLOUDY, Weather.SUNNY]
            else:  # February - late winter, occasional snow
                weather_options = [Weather.CLOUDY, Weather.CLOUDY, Weather.SNOWY, Weather.SUNNY]
        elif self.season == Season.SPRING:
            # Central Illinois spring: Variable, wet, prime planting season
            if month == 3:  # March - cool, wet, unpredictable 
                weather_options = [Weather.CLOUDY, Weather.RAINY, Weather.RAINY, Weather.SUNNY]
            elif month == 4:  # April - wet, mild, good for planting
                weather_options = [Weather.RAINY, Weather.CLOUDY, Weather.SUNNY, Weather.RAINY]
            else:  # May - warming, still rainy, peak planting
                weather_options = [Weather.SUNNY, Weather.RAINY, Weather.CLOUDY, Weather.SUNNY]
        elif self.season == Season.SUMMER:
            # Central Illinois summer: Hot, humid, some thunderstorms
            if month == 6:  # June - warm, frequent rain/storms
                weather_options = [Weather.SUNNY, Weather.RAINY, Weather.CLOUDY, Weather.SUNNY]
            elif month == 7:  # July - hot, less rain, more sun
                weather_options = [Weather.SUNNY, Weather.SUNNY, Weather.CLOUDY, Weather.RAINY]
            else:  # August - hot and dry, occasional storms
                weather_options = [Weather.SUNNY, Weather.SUNNY, Weather.SUNNY, Weather.CLOUDY]
        else:  # FALL
            # Central Illinois fall: Mild, dry, harvest season
            if month == 9:  # September - warm, dry, perfect harvest weather
                weather_options = [Weather.SUNNY, Weather.SUNNY, Weather.CLOUDY, Weather.RAINY]
            elif month == 10:  # October - mild, beautiful fall weather
                weather_options = [Weather.SUNNY, Weather.CLOUDY, Weather.SUNNY, Weather.RAINY]
            else:  # November - cooler, more clouds, preparing for winter
                weather_options = [Weather.CLOUDY, Weather.SUNNY, Weather.RAINY, Weather.CLOUDY]
        
        # Check for extreme weather events first
        if (self.day - self.last_extreme_weather > 7 and 
            random.random() < self.extreme_weather_chance):
            extreme_options = []
            
            if self.season in [Season.SUMMER, Season.FALL]:
                extreme_options.extend([Weather.DROUGHT, Weather.STORM])
            if self.season in [Season.SPRING, Season.SUMMER]:
                extreme_options.extend([Weather.FLOOD, Weather.HAIL])
            
            if extreme_options:
                self.weather = random.choice(extreme_options)
                self.last_extreme_weather = self.day
                
                # Show extreme weather alert
                weather_name = self.weather.name.title()
                self.show_message(f"⚠️ EXTREME WEATHER: {weather_name}!", RED, 5000)
        
        # Normal weather changes (every 3-5 days)
        elif self.day % random.randint(3, 5) == 0:
            self.weather = random.choice(weather_options)
        # Otherwise keep current weather for consistency
        
                # Update all tiles
        for row in self.grid:
            for tile in row:
                # Update moisture based on weather
                tile.moisture += self.weather_moisture_change[self.weather]
                tile.moisture = max(0, min(1, tile.moisture))
                
                # Apply extreme weather effects
                if tile.crop:
                    if self.weather == Weather.HAIL:
                        # Hail can damage crops
                        if random.random() < 0.3:  # 30% chance of damage
                            damage = random.uniform(0.1, 0.3)
                            tile.growth_progress = max(0, tile.growth_progress - damage)
                    
                    elif self.weather == Weather.FLOOD:
                        # Flooding can kill crops
                        if tile.moisture > 0.9 and random.random() < 0.15:  # 15% chance if waterlogged
                            tile.crop = None
                            tile.growth_progress = 0.0
                            tile.days_planted = 0
                    
                    elif self.weather == Weather.DROUGHT:
                        # Drought severely impacts growth
                        if tile.moisture < 0.2:
                            tile.growth_progress = max(0, tile.growth_progress - 0.05)
                
                # Update crops
                if tile.crop:
                    crop_type = CROP_TYPES[tile.crop]
                    tile.days_planted += 1
                    
                    # Growth rate affected by conditions
                    growth_rate = 1.0 / crop_type.growth_time
                    
                    # Moisture affects growth
                    if tile.moisture < crop_type.water_need * 0.5:
                        growth_rate *= 0.5
                    elif tile.moisture > crop_type.water_need * 1.5:
                        growth_rate *= 0.8
                    
                    # Nitrogen affects growth
                    if tile.nitrogen < crop_type.nitrogen_need * 0.5:
                        growth_rate *= 0.6
                    
                    # Season affects growth
                    if self.season == Season.WINTER:
                        growth_rate *= 0.1
                    
                    tile.growth_progress += growth_rate
                    tile.growth_progress = min(1.0, tile.growth_progress)
                    
                    # Update nitrogen (consumption or production)
                    tile.nitrogen -= crop_type.nitrogen_need * 0.001
                    tile.nitrogen = max(0, min(1, tile.nitrogen))
                
                # Natural nitrogen recovery
                if not tile.crop:
                    tile.nitrogen += 0.001
                    tile.nitrogen = min(1, tile.nitrogen)
    
    def plant_crop(self, grid_x, grid_y):
        """Plant a crop at the specified tile"""
        tile = self.grid[grid_y][grid_x]
        
        # Check if we can plant
        if tile.crop:
            self.show_message("Tile already has a crop!", YELLOW)
            return  # Already has a crop
        
        if self.money < SEED_COST:
            self.show_message(f"Need ${SEED_COST} for seeds!", RED)
            return
        
        # Auto-select best crop for current season
        available_crops = [name for name, crop_type in CROP_TYPES.items() 
                          if self.season in crop_type.seasons]
        if not available_crops:
            self.show_message(f"No crops can be planted in {self.season.name.title()}!", RED)
            return  # No crops can be planted this season
            
        # Choose wheat if available, otherwise first available crop
        chosen_crop = "wheat_soft_red_winter" if "wheat_soft_red_winter" in available_crops else available_crops[0]
        crop_type = CROP_TYPES[chosen_crop]
        
        # Plant the crop
        tile.crop = chosen_crop
        tile.growth_progress = 0.0
        tile.days_planted = 0
        self.money -= SEED_COST
        
        crop_name = self.get_short_crop_name(chosen_crop)
        self.show_message(f"Planted {crop_name} for ${SEED_COST}", GREEN)
    
    def harvest_crop(self, grid_x, grid_y):
        """Harvest a crop at the specified tile"""
        tile = self.grid[grid_y][grid_x]
        
        if not tile.crop:
            self.show_message("No crop to harvest!", YELLOW)
            return
            
        if tile.growth_progress < 1.0:
            progress_pct = int(tile.growth_progress * 100)
            self.show_message(f"Crop only {progress_pct}% grown!", YELLOW)
            return
        
        crop_type = CROP_TYPES[tile.crop]
        crop_name = self.get_short_crop_name(tile.crop)
        
        # Calculate yield based on soil quality and market price
        yield_multiplier = tile.soil_quality
        market_price = self.market.get_crop_price(tile.crop, self.season, self.day)
        value = int(market_price * yield_multiplier)
        
        self.money += value
        tile.harvested_times += 1
        
        # Harvesting affects soil quality
        tile.soil_quality -= HARVEST_SOIL_DAMAGE
        tile.soil_quality = max(0.1, tile.soil_quality)
        
        self.show_message(f"Harvested {crop_name} for ${value}!", GREEN)
        
        # Clear the crop
        tile.crop = None
        tile.growth_progress = 0.0
        tile.days_planted = 0
    
    def handle_plant_action(self):
        """Handle plant action on selected tile"""
        if not self.selected_tile_pos:
            return
        
        x, y = self.selected_tile_pos
        self.plant_crop(x, y)
    
    def handle_harvest_action(self):
        """Handle harvest action on selected tile"""
        if not self.selected_tile_pos:
            return
        
        x, y = self.selected_tile_pos
        tile = self.grid[y][x]
        if tile.crop:
            self.harvest_crop(x, y)
    
    def handle_popup_plant_action(self):
        """Handle plant action through popup interface"""
        if not self.tile_popup_active or not self.tile_popup_pos:
            return
        
        x, y = self.tile_popup_pos
        tile = self.grid[y][x]
        
        # Don't plant if tile already has a crop
        if tile.crop:
            return
        
        # Get the selected crop from dropdown
        valid_crops = self.get_valid_crops_for_season()
        if not valid_crops:
            return
            
        selected_crop = valid_crops[self.popup_crop_selection % len(valid_crops)]
        
        # Plant the selected crop
        if self.plant_specific_crop(x, y, selected_crop):
            # Close popup after successful planting
            self.close_tile_popup()
    
    def handle_popup_harvest_action(self):
        """Handle harvest action through popup interface"""
        if not self.tile_popup_active or not self.tile_popup_pos:
            return
        
        x, y = self.tile_popup_pos
        tile = self.grid[y][x]
        
        if tile.crop:
            self.harvest_crop(x, y)
            # Close popup after harvest
            self.close_tile_popup()
    
    def plant_specific_crop(self, x, y, crop_name):
        """Plant a specific crop on a tile (used by popup)"""
        tile = self.grid[y][x]
        
        # Check if tile is empty
        if tile.crop:
            self.show_message("Tile already has a crop!", YELLOW)
            return False
        
        # Check cost
        if self.money < SEED_COST:
            self.show_message(f"Need ${SEED_COST} for seeds!", RED)
            return False
        
        # Check if crop is valid for current season
        crop_type = CROP_TYPES[crop_name]
        if self.season not in crop_type.seasons:
            season_name = self.season.name.title()
            self.show_message(f"Can't plant in {season_name}!", RED)
            return False
        
        # Plant the crop
        self.money -= SEED_COST
        tile.crop = crop_name
        tile.growth_progress = 0.0
        tile.days_planted = 0
        
        crop_display_name = self.get_short_crop_name(crop_name)
        self.show_message(f"Planted {crop_display_name} for ${SEED_COST}", GREEN)
        return True
    
    def auto_harvest_check(self):
        """Check for auto-harvest if enabled"""
        if not self.auto_harvest:
            return
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                tile = self.grid[y][x]
                if tile.crop and tile.growth_progress >= 1.0:
                    self.harvest_crop(x, y)
    
    def draw_weather_icon(self, x, y, weather, size=24):
        """Draw a simple weather icon"""
        center_x, center_y = x + size // 2, y + size // 2
        
        if weather == Weather.SUNNY:
            # Sun
            pygame.draw.circle(self.screen, YELLOW, (center_x, center_y), size // 3)
            # Sun rays (simple lines)
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                start_x = center_x + int(math.cos(rad) * size // 2.2)
                start_y = center_y + int(math.sin(rad) * size // 2.2)
                end_x = center_x + int(math.cos(rad) * size // 1.8)
                end_y = center_y + int(math.sin(rad) * size // 1.8)
                pygame.draw.line(self.screen, YELLOW, (start_x, start_y), (end_x, end_y), 2)
        
        elif weather == Weather.CLOUDY:
            # Clouds
            pygame.draw.circle(self.screen, GRAY, (center_x - 6, center_y), size // 4)
            pygame.draw.circle(self.screen, GRAY, (center_x + 6, center_y), size // 4)
            pygame.draw.circle(self.screen, GRAY, (center_x, center_y - 4), size // 3)
        
        elif weather == Weather.RAINY:
            # Cloud
            pygame.draw.circle(self.screen, GRAY, (center_x, center_y - 4), size // 3)
            # Rain drops
            for i in range(3):
                drop_x = center_x - 6 + i * 6
                pygame.draw.line(self.screen, BLUE, (drop_x, center_y + 4), (drop_x, center_y + 10), 2)
        
        elif weather == Weather.SNOWY:
            # Cloud
            pygame.draw.circle(self.screen, GRAY, (center_x, center_y - 4), size // 3)
            # Snowflakes (simple asterisks)
            for i in range(3):
                flake_x = center_x - 6 + i * 6
                flake_y = center_y + 6
                pygame.draw.line(self.screen, WHITE, (flake_x - 2, flake_y), (flake_x + 2, flake_y), 1)
                pygame.draw.line(self.screen, WHITE, (flake_x, flake_y - 2), (flake_x, flake_y + 2), 1)
        
        elif weather == Weather.DROUGHT:
            # Harsh sun with heat lines
            pygame.draw.circle(self.screen, (255, 200, 0), (center_x, center_y), size // 3)
            # Heat waves (wavy lines)
            for i in range(2):
                y_offset = center_y + 8 + i * 3
                pygame.draw.line(self.screen, (255, 100, 0), 
                               (center_x - 8, y_offset), (center_x + 8, y_offset), 1)
        
        elif weather == Weather.FLOOD:
            # Heavy rain with water level
            pygame.draw.circle(self.screen, GRAY, (center_x, center_y - 6), size // 4)
            # Heavy rain
            for i in range(5):
                drop_x = center_x - 8 + i * 4
                pygame.draw.line(self.screen, BLUE, (drop_x, center_y), (drop_x, center_y + 8), 2)
            # Water level
            pygame.draw.rect(self.screen, BLUE, (center_x - 10, center_y + 8, 20, 3))
        
        elif weather == Weather.STORM:
            # Dark cloud with lightning
            pygame.draw.circle(self.screen, (60, 60, 60), (center_x, center_y - 4), size // 3)
            # Lightning bolt
            points = [(center_x - 2, center_y + 2), (center_x + 1, center_y + 6), 
                     (center_x - 1, center_y + 6), (center_x + 2, center_y + 10)]
            pygame.draw.lines(self.screen, YELLOW, False, points, 2)
        
        elif weather == Weather.HAIL:
            # Cloud with hail
            pygame.draw.circle(self.screen, GRAY, (center_x, center_y - 4), size // 3)
            # Hail stones (small circles)
            for i in range(4):
                hail_x = center_x - 6 + i * 4
                hail_y = center_y + 6
                pygame.draw.circle(self.screen, WHITE, (hail_x, hail_y), 1)
    
    def draw_options_icon(self, x, y, size=24):
        """Draw a simple gear/options icon"""
        center_x, center_y = x + size // 2, y + size // 2
        
        # Outer circle (gear outline)
        outer_radius = size // 2 - 2
        inner_radius = size // 4
        
        # Draw gear teeth (simple approach - 8 small rectangles around circle)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            tooth_x = center_x + int(math.cos(rad) * outer_radius)
            tooth_y = center_y + int(math.sin(rad) * outer_radius)
            pygame.draw.rect(self.screen, GRAY, (tooth_x - 2, tooth_y - 2, 4, 4))
        
        # Inner circle
        pygame.draw.circle(self.screen, GRAY, (center_x, center_y), outer_radius - 2, 2)
    
    def draw_time_indicator(self, x, y):
        """Draw a circular time indicator showing day progress like a sun/globe"""
        if self.paused:
            return
            
        radius = 12
        center = (x, y)
        
        # Calculate day progress (0.0 to 1.0)
        current_time = pygame.time.get_ticks()
        base_day_time = 30000  # milliseconds per day at 1x speed
        day_update_time = base_day_time / self.speed
        
        time_since_last_day = current_time - self.last_day_update
        day_progress = min(time_since_last_day / day_update_time, 1.0)
        
        # Background circle (night)
        pygame.draw.circle(self.screen, (30, 30, 60), center, radius)
        pygame.draw.circle(self.screen, WHITE, center, radius, 1)
        
        # Progress arc (day/sun)
        if day_progress > 0:
            # Calculate arc angle (0 to 2π)
            arc_angle = day_progress * 2 * math.pi
            
            # Draw filled arc for day progress
            points = [center]
            for i in range(int(arc_angle * 20) + 1):  # More points for smoother arc
                angle = -math.pi/2 + (i / 20)  # Start from top
                if angle <= -math.pi/2 + arc_angle:
                    px = center[0] + radius * math.cos(angle)
                    py = center[1] + radius * math.sin(angle)
                    points.append((px, py))
            
            if len(points) > 2:
                pygame.draw.polygon(self.screen, YELLOW, points)
        
        # Speed indicator - small text below circle
        speed_text = f"{self.speed}x"
        speed_surface = self.font.render(speed_text, True, WHITE)
        speed_rect = speed_surface.get_rect(center=(center[0], center[1] + radius + 12))
        self.screen.blit(speed_surface, speed_rect)
    
    def draw_bottom_bar(self):
        """Draw an organized bottom information bar"""
        bar_height = 150
        bar_y = SCREEN_HEIGHT - bar_height
        
        # Resources section - Far left of grey box
        resources_panel = pygame.Rect(10, bar_y + 10, 120, bar_height - 20)
        pygame.draw.rect(self.screen, (40, 40, 40), resources_panel)
        pygame.draw.rect(self.screen, WHITE, resources_panel, 1)
        
        money_title = self.ui_font.render("Resources", True, YELLOW)
        self.screen.blit(money_title, (resources_panel.x + 10, resources_panel.y + 5))
        
        money_color = GREEN if self.money >= 100 else RED if self.money < 50 else YELLOW
        money_text = self.ui_font.render(f"${self.money}", True, money_color)
        self.screen.blit(money_text, (resources_panel.x + 10, resources_panel.y + 30))
        
    
    def draw_main_area_panels(self):
        """Draw main area panels - Left side tile info REMOVED (now uses popup only)"""
        # All tile information now displays through click-to-open popup system
        # No more always-visible side panels cluttering the screen
        
        # Right side - Farm stats panel REMOVED (now available via Field Study icon)
        # All farm statistics now accessible through modular Field Study panel
        
        # Market prices panel (bottom left) - HIDDEN for Phase 1 research focus
        # self.draw_market_panel()
    
    def draw_market_panel(self):
        """Draw market prices for current season"""
        panel_width = 250
        panel_height = 200
        panel_rect = pygame.Rect(20, SCREEN_HEIGHT - panel_height - 170, panel_width, panel_height)
        
        # Draw semi-transparent background
        s = pygame.Surface((panel_width, panel_height))
        s.set_alpha(200)
        s.fill((20, 20, 20))
        self.screen.blit(s, panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 1)
        
        # Title
        title = self.ui_font.render("Market Prices", True, YELLOW)
        self.screen.blit(title, (panel_rect.x + 10, panel_rect.y + 8))
        
        season_text = self.font.render(f"{self.season.name.title()} Season", True, WHITE)
        self.screen.blit(season_text, (panel_rect.x + 10, panel_rect.y + 32))
        
        # Show prices for plantable crops
        y_pos = panel_rect.y + 55
        valid_crops = [name for name, crop_type in CROP_TYPES.items() 
                      if self.season in crop_type.seasons]
        
        for i, crop_name in enumerate(valid_crops[:6]):  # Show max 6 crops
            if y_pos + 20 > panel_rect.y + panel_height - 10:
                break
                
            crop_display = self.get_short_crop_name(crop_name)
            price = self.market.get_crop_price(crop_name, self.season, self.day)
            trend = self.market.get_price_trend(crop_name, self.season)
            
            # Crop name
            crop_text = self.small_font.render(f"{crop_display}:", True, WHITE)
            self.screen.blit(crop_text, (panel_rect.x + 10, y_pos))
            
            # Price
            price_text = self.small_font.render(f"${price}", True, GREEN)
            self.screen.blit(price_text, (panel_rect.x + 120, y_pos))
            
            # Trend
            trend_color = GREEN if "HIGH" in trend or "Good" in trend else RED if "Low" in trend or "Poor" in trend else YELLOW
            trend_text = self.small_font.render(trend, True, trend_color)
            self.screen.blit(trend_text, (panel_rect.x + 160, y_pos))
            
            y_pos += 18
    
    def draw_ui(self):
        """Draw the user interface"""
        # Background panel - REMOVED for clean modular UI system
        # pygame.draw.rect(self.screen, DARK_GRAY, (0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 150))
        
        # Top left - Speed controls REMOVED (now in modular speed panel)
        # All speed controls, pause button, and time indicator moved to modular UI
        
        # Top center - Farm info, date, season, and weather (like Banished layout)
        center_x = SCREEN_WIDTH // 2
        
        # Farm name and location (if set)
        if hasattr(self, 'farm_name') and self.farm_name:
            farm_info = f"{self.farm_name} - {self.farm_location}"
            farm_text = self.ui_font.render(farm_info, True, (160, 130, 100))
            farm_rect = farm_text.get_rect(center=(center_x, 15))
            self.screen.blit(farm_text, farm_rect)
            date_y = 35  # Push date down
        else:
            date_y = 25  # Default position
        
        # Date info
        date_str = self.current_date.strftime("%B %d, %Y")
        date_text = f"{date_str} (Day {self.day})"
        text = self.ui_font.render(date_text, True, WHITE)
        date_rect = text.get_rect(center=(center_x, date_y))
        self.screen.blit(text, date_rect)
        
        # Season and weather on same line (like Banished)
        season_weather_y = date_y + 25  # Position below date
        season_text = f"Season: {self.season.name}"
        season_surface = self.font.render(season_text, True, WHITE)
        
        # Weather icon positioned right next to season text
        weather_text = f" | {self.weather.name}"
        weather_surface = self.font.render(weather_text, True, WHITE)
        
        # Calculate combined width to center properly
        combined_width = season_surface.get_width() + 30 + weather_surface.get_width()  # 30 for icon space
        start_x = center_x - combined_width // 2
        
        # Draw season text
        self.screen.blit(season_surface, (start_x, season_weather_y))
        
        # Draw weather icon right after season text
        icon_x = start_x + season_surface.get_width() + 5
        self.draw_weather_icon(icon_x, season_weather_y - 5, self.weather, size=20)
        
        # Draw weather text right after icon
        weather_x = icon_x + 25
        self.screen.blit(weather_surface, (weather_x, season_weather_y))
        
        # Main area panels (tile info and farm stats)
        self.draw_main_area_panels()
        
        # Bottom bar - REMOVED for new modular icon system
        # self.draw_bottom_bar()
        
        # New modular icon system in bottom right (includes settings)
        self.draw_modular_icons()
        self.draw_modular_panels()
        
        # Remove instructions - moved to Help section
    
    def draw_settings_button(self):
        """Draw settings gear icon in top-right corner"""
        # Settings button position
        settings_size = 32
        settings_x = SCREEN_WIDTH - settings_size - 10
        settings_y = 10
        
        # Store rect for click detection
        self.settings_button_rect = pygame.Rect(settings_x, settings_y, settings_size, settings_size)
        
        # Draw button background
        pygame.draw.rect(self.screen, (60, 60, 60), self.settings_button_rect)
        pygame.draw.rect(self.screen, WHITE, self.settings_button_rect, 2)
        
        # Draw gear icon (⚙ or simplified gear shape)
        center_x = settings_x + settings_size // 2
        center_y = settings_y + settings_size // 2
        
        # Simple gear representation
        gear_text = self.ui_font.render("⚙", True, WHITE)
        gear_rect = gear_text.get_rect(center=(center_x, center_y))
        self.screen.blit(gear_text, gear_rect)
    
    def draw_modular_icons(self):
        """Draw the bottom-right icon bar - Banished style"""
        for icon_id, icon_data in self.ui_icons.items():
            x, y = icon_data['pos']
            
            # Icon background
            icon_rect = pygame.Rect(x - self.icon_size//2, y - self.icon_size//2, self.icon_size, self.icon_size)
            
            # Highlight if panel is open
            is_open = icon_id in self.modular_panels and self.modular_panels[icon_id].get('visible', False)
            bg_color = (80, 80, 80) if is_open else (60, 60, 60)
            border_color = YELLOW if is_open else WHITE
            
            pygame.draw.rect(self.screen, bg_color, icon_rect)
            pygame.draw.rect(self.screen, border_color, icon_rect, 2)
            
            # Icon symbols
            if icon_id == 'field_study':
                icon_text = self.ui_font.render("📊", True, WHITE)
            elif icon_id == 'resources':
                icon_text = self.ui_font.render("💰", True, WHITE)
            elif icon_id == 'speed':
                icon_text = self.ui_font.render("⏱", True, WHITE)
            elif icon_id == 'help':
                icon_text = self.ui_font.render("?", True, WHITE)
            elif icon_id == 'settings':
                icon_text = self.ui_font.render("⚙", True, WHITE)
            
            icon_text_rect = icon_text.get_rect(center=icon_rect.center)
            self.screen.blit(icon_text, icon_text_rect)
    
    def draw_modular_panels(self):
        """Draw the open modular panels"""
        for panel_id, panel_data in self.modular_panels.items():
            if panel_data.get('visible', False):
                self.draw_panel(panel_id, panel_data)
    
    def draw_panel(self, panel_id, panel):
        """Draw a specific modular panel"""
        x, y, w, h = panel['rect']
        
        # Panel background
        s = pygame.Surface((w, h))
        s.set_alpha(220)
        s.fill((30, 30, 30))
        self.screen.blit(s, (x, y))
        pygame.draw.rect(self.screen, WHITE, (x, y, w, h), 2)
        
        # Title bar with close button
        title_height = 25
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, w, title_height))
        
        title_text = self.ui_font.render(panel['title'], True, WHITE)
        self.screen.blit(title_text, (x + 5, y + 3))
        
        # Close button
        close_rect = pygame.Rect(x + w - 22, y + 3, 18, 18)
        pygame.draw.rect(self.screen, (80, 80, 80), close_rect)
        pygame.draw.rect(self.screen, RED, close_rect, 1)
        close_text = self.small_font.render("×", True, WHITE)
        close_text_rect = close_text.get_rect(center=close_rect.center)
        self.screen.blit(close_text, close_text_rect)
        
        # Panel content
        content_y = y + title_height + 5
        if panel_id == 'field_study':
            self.draw_field_study_content(x + 5, content_y, w - 10)
        elif panel_id == 'resources':
            self.draw_resources_content(x + 5, content_y, w - 10)
        elif panel_id == 'speed':
            self.draw_speed_content(x + 5, content_y, w - 10)
        elif panel_id == 'help':
            self.draw_help_content(x + 5, content_y, w - 10, h - title_height - 10)
    
    def draw_field_study_content(self, x, y, width):
        """Draw farm stats content"""
        stats_y = y
        
        # Farm name
        name_text = self.ui_font.render(f"Farm: {self.farm_name or 'Unnamed'}", True, GREEN)
        self.screen.blit(name_text, (x, stats_y))
        stats_y += 25
        
        # Location
        location_text = self.font.render(f"Location: {self.farm_location}", True, WHITE)
        self.screen.blit(location_text, (x, stats_y))
        stats_y += 20
        
        # Date and season
        month = ((self.day - 1) // 30) % 12 + 1
        season_day = ((self.day - 1) % 365) // 30 % 12 + 1
        date_text = self.font.render(f"Day {self.day} - Month {month}", True, WHITE)
        self.screen.blit(date_text, (x, stats_y))
        stats_y += 20
        
        season_text = self.font.render(f"Season: {self.season.name.title()}", True, (160, 130, 100))
        self.screen.blit(season_text, (x, stats_y))
        stats_y += 25
        
        # Crop counts
        planted_count = sum(1 for row in self.grid for tile in row if tile.crop)
        ready_count = sum(1 for row in self.grid for tile in row if tile.crop and tile.growth_progress >= 1.0)
        
        planted_text = self.font.render(f"Planted: {planted_count}/9 tiles", True, WHITE)
        self.screen.blit(planted_text, (x, stats_y))
        stats_y += 20
        
        ready_text = self.font.render(f"Ready: {ready_count} crops", True, GREEN if ready_count > 0 else WHITE)
        self.screen.blit(ready_text, (x, stats_y))
        stats_y += 20
        
        # Auto-harvest
        auto_color = GREEN if self.auto_harvest else GRAY
        auto_text = self.font.render(f"Auto-Harvest: {'ON' if self.auto_harvest else 'OFF'}", True, auto_color)
        self.screen.blit(auto_text, (x, stats_y))
    
    def draw_resources_content(self, x, y, width):
        """Draw resources content"""
        money_color = GREEN if self.money >= 100 else RED if self.money < 50 else YELLOW
        money_text = self.ui_font.render(f"Budget: ${self.money}", True, money_color)
        self.screen.blit(money_text, (x, y))
        
        # Future: Add other resources here
    
    def draw_speed_content(self, x, y, width):
        """Draw speed controls content"""
        # Pause button
        pause_text = "Pause" if not self.paused else "Resume"
        pause_color = RED if not self.paused else GREEN
        pause_rect = pygame.Rect(x, y, 80, 20)
        pygame.draw.rect(self.screen, (40, 40, 40), pause_rect)
        pygame.draw.rect(self.screen, pause_color, pause_rect, 1)
        pause_btn_text = self.font.render(pause_text, True, pause_color)
        pause_text_rect = pause_btn_text.get_rect(center=pause_rect.center)
        self.screen.blit(pause_btn_text, pause_text_rect)
        
        # Store pause button rect for click detection
        if not hasattr(self, 'speed_panel_buttons'):
            self.speed_panel_buttons = {}
        self.speed_panel_buttons['pause'] = pause_rect
        
        # Speed buttons
        speeds = [1, 2, 5, 10]
        button_width = 60
        for i, spd in enumerate(speeds):
            button_x = x + (i * (button_width + 5))
            button_y = y + 30
            speed_rect = pygame.Rect(button_x, button_y, button_width, 20)
            
            # Button styling
            is_current = (self.speed == spd)
            button_color = YELLOW if is_current else (60, 60, 60)
            border_color = YELLOW if is_current else WHITE
            
            pygame.draw.rect(self.screen, button_color if is_current else (40, 40, 40), speed_rect)
            pygame.draw.rect(self.screen, border_color, speed_rect, 1)
            
            speed_text = self.font.render(f"{spd}x", True, WHITE)
            speed_text_rect = speed_text.get_rect(center=speed_rect.center)
            self.screen.blit(speed_text, speed_text_rect)
            
            # Store button rect for click detection
            self.speed_panel_buttons[f'speed_{spd}'] = speed_rect
    
    def draw_help_content(self, x, y, width, height):
        """Draw help content"""
        help_text = self.font.render("Help & Controls", True, YELLOW)
        self.screen.blit(help_text, (x, y))
        
        # Add help text content here
        help_lines = [
            "Mouse: Click tiles to interact",
            "Mouse Wheel: Zoom in/out",  
            "Space: Pause/unpause",
            "F1: Toggle debug mode",
            "Ctrl+S: Save game",
            "Ctrl+L: Load game"
        ]
        
        for i, line in enumerate(help_lines):
            line_y = y + 25 + i * 18
            if line_y < y + height - 20:
                line_text = self.small_font.render(line, True, WHITE)
                self.screen.blit(line_text, (x, line_y))
    
    def get_menu_item_rect(self, index):
        """Get the rectangle for a menu item for mouse detection"""
        spacing = getattr(self, 'menu_button_spacing', 50)
        button_y = getattr(self, 'menu_buttons_start_y', SCREEN_HEIGHT // 2) + index * spacing
        return pygame.Rect(SCREEN_WIDTH // 2 - 200, button_y, 400, 45)
    
    def draw_menu(self):
        """Draw the main menu using the specialized framework component"""
        if not UI_FRAMEWORK_AVAILABLE:
            return self.draw_menu_legacy()
        
        # Import the new component
        from ui_framework import UIManager, MainMenuPanel
        
        # Draw gradient background
        ui = UIManager(self.screen)
        ui.draw_warm_gradient_background()
        
        # Create the specialized main menu panel if not exists or update selection
        if not hasattr(self, 'menu_panel'):
            self.menu_panel = MainMenuPanel(
                "FIELD STATION",
                "Grow, Learn, Discover - A Playful Plant Growing Experience",
                self.menu_options,
                self.menu_selection
            )
            # Set fonts
            self.menu_panel.set_fonts(
                self.menu_title_font,  # title
                self.font,             # subtitle
                self.menu_font         # buttons
            )
        else:
            # Update the selected index to match current selection
            self.menu_panel.selected_index = self.menu_selection
        
        # Add to UI manager and render
        ui.add_element(self.menu_panel)
        ui.render()
        
        return ui
    
    def draw_menu_framework(self):
        """Draw main menu using framework with interactive overlay"""
        # Create content for the information panel
        def populate_content(content_area):
            fonts = self.create_framework_fonts()
            content_area.add_header("Grow, Learn, Discover - Scientific Agriculture Awaits!", fonts['ui']) \
                .add_spacer() \
                .add_text("[S] Create and manage your own farm", fonts['content']) \
                .add_text("[chart] Track detailed growth data and soil quality", fonts['content']) \
                .add_text("[target] Learn real agricultural science through gameplay", fonts['content']) \
                .add_text("[flask] Experiment with different crops and techniques", fonts['content']) \
                .add_spacer() \
                .add_header("Game Features:", fonts['ui']) \
                .add_text("• Realistic crop growth simulation", fonts['content']) \
                .add_text("• Scientific data tracking and analysis", fonts['content']) \
                .add_text("• Weather system affecting crops", fonts['content']) \
                .add_text("• Market dynamics and economics", fonts['content']) \
                .add_spacer() \
                .add_text("Use arrow keys and Enter to navigate menu options", (140, 120, 100), self.small_font)
        
        # Create UI with smaller panel positioned on the left
        ui = UIManager(self.screen)
        ui.draw_warm_gradient_background()
        
        # Create smaller panel positioned on left side for two-column layout
        panel_x = SCREEN_WIDTH // 2 - 350  # Left side positioning
        panel_y = (SCREEN_HEIGHT - 450) // 2  # Centered vertically
        panel = MenuPanel("FIELD STATION", "🌾", width=500, height=450, x=panel_x, y=panel_y)
        panel.set_fonts(**self.create_framework_fonts())
        
        # Populate content
        populate_content(panel.content_area)
        
        ui.add_element(panel)
        ui.render()
        
        # Overlay interactive menu buttons on the right
        self.draw_main_menu_buttons_overlay()
        
        # Version info
        version = self.small_font.render("v0.1", True, (180, 180, 180))
        self.screen.blit(version, (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 30))
    
    def draw_main_menu_buttons_overlay(self):
        """Draw interactive main menu buttons on top of framework panel"""
        # Calculate button positions - positioned on right side of the panel
        total_menu_items = len(self.menu_options)
        button_spacing = 55
        buttons_start_y = SCREEN_HEIGHT // 2 - (total_menu_items * button_spacing // 2) + 20
        button_x = SCREEN_WIDTH // 2 + 50  # Position on right side of panel
        
        mouse_pos = pygame.mouse.get_pos()
        for i, option in enumerate(self.menu_options):
            button_y = buttons_start_y + i * button_spacing
            button_rect = pygame.Rect(button_x, button_y, 280, 45)  # Increased width for emojis
            
            # Store for click handling
            if not hasattr(self, 'main_menu_button_rects'):
                self.main_menu_button_rects = {}
            self.main_menu_button_rects[i] = button_rect
            
            is_hovered = button_rect.collidepoint(mouse_pos)
            if is_hovered:
                self.menu_selection = i
            
            if i == self.menu_selection:
                button_color = (85, 107, 47, 200)  # Selected
                text_color = (255, 255, 255)
                border_color = (144, 238, 144)
                
                # Glow effect
                glow_surface = pygame.Surface((button_rect.width + 10, button_rect.height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (144, 238, 144, 60), (0, 0, button_rect.width + 10, button_rect.height + 10), border_radius=8)
                self.screen.blit(glow_surface, (button_rect.x - 5, button_rect.y - 5))
            else:
                button_color = (40, 50, 35, 150)  # Normal
                text_color = (220, 220, 220)
                border_color = (100, 120, 90)
            
            # Draw button
            button_surface = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
            button_surface.fill(button_color)
            self.screen.blit(button_surface, button_rect)
            pygame.draw.rect(self.screen, border_color, button_rect, 2, border_radius=8)
            
            # Draw text with emoji icon
            emoji = get_menu_icon(option)
            menu_text = f"{emoji}  {option}"
            text = self.menu_font.render(menu_text, True, text_color)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            
            # Selection indicator
            if i == self.menu_selection:
                indicator_color = (218, 165, 32)  # Goldenrod arrow
                pygame.draw.polygon(self.screen, indicator_color, [
                    (button_rect.right - 25, button_rect.centery - 8),
                    (button_rect.right - 15, button_rect.centery),
                    (button_rect.right - 25, button_rect.centery + 8)
                ])
        
        # Store positions for mouse click handling
        self.menu_buttons_start_y = buttons_start_y
        self.menu_button_spacing = button_spacing
    
    def draw_menu_legacy(self):
        """Legacy main menu rendering (fallback)"""
        # Warm gradient background
        self.draw_warm_gradient_background()
        
        # Subtle decorative elements
        self.draw_menu_decorations()
        
        # Calculate vertical centering - total menu height and center it
        total_menu_items = len(self.menu_options)
        button_spacing = max(45, min(50, (SCREEN_HEIGHT - 300) // total_menu_items))  # Adaptive spacing
        menu_height = 80 + 40 + (total_menu_items * button_spacing) + 40  # title + subtitle + buttons + padding
        start_y = max(50, (SCREEN_HEIGHT - menu_height) // 2)  # Don't start too high
        
        # Title with shadow for depth - properly centered
        title_y = start_y + 40
        shadow_title = self.menu_title_font.render("FIELD STATION", True, (20, 25, 15))
        shadow_rect = shadow_title.get_rect(center=(SCREEN_WIDTH // 2 + 2, title_y + 2))
        self.screen.blit(shadow_title, shadow_rect)
        
        title = self.menu_title_font.render("FIELD STATION", True, (144, 238, 144))  # Light green - more pleasant
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, title_y))
        self.screen.blit(title, title_rect)
        
        # Fun and engaging subtitle
        subtitle_y = title_y + 60
        subtitle = self.ui_font.render("Grow, Learn, Discover - Scientific Agriculture Awaits!", True, (218, 165, 32))  # Goldenrod
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, subtitle_y))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Store the calculated start position for buttons and spacing
        self.menu_buttons_start_y = subtitle_y + 50
        self.menu_button_spacing = button_spacing
        
        # Menu options with improved styling
        self.draw_professional_menu_options(self.menu_options)
        
        # Version info in corner
        version = self.small_font.render("v0.1", True, (180, 180, 180))  # Light gray
        self.screen.blit(version, (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 30))
    
    def draw_pause_menu(self):
        """Draw the pause menu with professional styling"""
        # Warm semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((40, 30, 25))  # Warm dark brown
        self.screen.blit(overlay, (0, 0))
        
        # Calculate vertical centering
        total_menu_items = len(self.pause_menu_options)
        menu_height = 80 + (total_menu_items * 50) + 40  # title + buttons + padding
        start_y = (SCREEN_HEIGHT - menu_height) // 2
        
        # Title with warm styling
        title_y = start_y + 40
        title = self.menu_title_font.render("GAME PAUSED", True, (180, 140, 100))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, title_y))
        self.screen.blit(title, title_rect)
        
        # Store button start position
        self.pause_menu_buttons_start_y = title_y + 80
        
        # Menu options with professional styling
        self.draw_professional_pause_menu_options(self.pause_menu_options)
    
    def draw_menu_options(self, options):
        """Draw menu options (shared between main menu and pause menu)"""
        mouse_pos = pygame.mouse.get_pos()
        for i, option in enumerate(options):
            # Check if mouse is hovering over this item
            item_rect = self.get_menu_item_rect(i)
            if item_rect.collidepoint(mouse_pos):
                self.menu_selection = i  # Update selection based on mouse hover
            
            if i == self.menu_selection:
                color = YELLOW
                prefix = "> "
                # Draw hover background
                pygame.draw.rect(self.screen, (40, 40, 40), item_rect)
            else:
                color = WHITE
                prefix = "  "
            
            text = self.menu_font.render(prefix + option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 350 + i * 60))
            self.screen.blit(text, text_rect)
        
        # Instructions
        instructions = self.font.render("Use arrow keys or mouse to select, ENTER or click to confirm", True, GRAY)
        inst_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(instructions, inst_rect)
    
    def draw_warm_gradient_background(self):
        """Draw a pleasant, warm gradient background for the menu"""
        # Get actual screen dimensions
        actual_width = self.screen.get_width()
        actual_height = self.screen.get_height()
        
        for y in range(actual_height):
            ratio = y / actual_height
            # Pleasant earth tones: from warm forest green to soft golden brown
            r = int(60 * (1 - ratio) + 140 * ratio)
            g = int(80 * (1 - ratio) + 120 * ratio)
            b = int(45 * (1 - ratio) + 70 * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (actual_width, y))
    
    def draw_menu_decorations(self):
        """Draw subtle decorative elements"""
        # No decorations - keep it clean
        pass
    
    def get_menu_emoji(self, option):
        """Get icon symbol for menu option from local file"""
        return get_menu_icon(option)
    
    def draw_professional_menu_options(self, options):
        """Draw menu options with professional styling and emoji icons on hover"""
        mouse_pos = pygame.mouse.get_pos()
        
        for i, option in enumerate(options):
            # Check if mouse is hovering over this item
            item_rect = self.get_menu_item_rect(i)
            is_hovered = item_rect.collidepoint(mouse_pos)
            if is_hovered:
                self.menu_selection = i
            
            # Professional button styling - use calculated center position with adaptive spacing
            spacing = getattr(self, 'menu_button_spacing', 50)
            button_y = getattr(self, 'menu_buttons_start_y', SCREEN_HEIGHT // 2) + i * spacing
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, button_y, 400, 45)
            
            if i == self.menu_selection:
                # Selected state - pleasant, readable colors
                button_color = (85, 107, 47, 180)  # Olive green
                text_color = (255, 255, 255)
                border_color = (144, 238, 144)  # Light green
                emoji_color = (218, 165, 32)  # Goldenrod emoji
                
                # Soft glow effect
                glow_surface = pygame.Surface((button_rect.width + 20, button_rect.height + 20), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (144, 238, 144, 40), (0, 0, button_rect.width + 20, button_rect.height + 20), border_radius=8)
                self.screen.blit(glow_surface, (button_rect.x - 10, button_rect.y - 10))
            else:
                # Normal state - subtle background
                button_color = (60, 70, 50, 120)  # Dark olive
                text_color = (220, 220, 220)  # Light gray
                border_color = (120, 140, 100)  # Muted green
                emoji_color = (180, 180, 180)  # Light gray emoji
            
            # Draw button background with rounded corners effect
            button_surface = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
            button_surface.fill(button_color)
            self.screen.blit(button_surface, button_rect)
            
            # Draw elegant border
            pygame.draw.rect(self.screen, border_color, button_rect, 2, border_radius=6)
            
            # Get icon for this option
            icon = self.get_menu_emoji(option)
            
            # Draw emoji icon on the left (only when hovered or selected)
            if i == self.menu_selection:
                # Use emoji font if available, otherwise fallback
                if self.emoji_font:
                    emoji_text = self.emoji_font.render(icon, True, emoji_color)
                    # Scale emoji to be slightly smaller than text height with smooth scaling
                    text_height = self.menu_font.get_height()
                    target_height = int(text_height * 0.8)  # 80% of text height - a bit smaller
                    target_size = (target_height, target_height)  # Square emoji
                    # Use smoothscale for better quality when scaling down
                    emoji_text = pygame.transform.smoothscale(emoji_text, target_size)
                else:
                    emoji_text = self.menu_font.render(icon, True, emoji_color)
                
                # Center the emoji with more space from the text
                emoji_rect = emoji_text.get_rect(center=(button_rect.x + 25, button_rect.centery))
                self.screen.blit(emoji_text, emoji_rect)
                text_x_offset = 50  # More space between icon and text
            else:
                text_x_offset = 0
            
            # Draw option text (centered or offset for emoji)
            text = self.menu_font.render(option, True, text_color)
            if text_x_offset > 0:
                text_rect = text.get_rect(midleft=(button_rect.x + text_x_offset, button_rect.centery))
            else:
                text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            
            # Add subtle selection indicator (arrow on right)
            if i == self.menu_selection:
                indicator_color = (218, 165, 32)  # Goldenrod arrow
                pygame.draw.polygon(self.screen, indicator_color, [
                    (button_rect.right - 25, button_rect.centery - 6),
                    (button_rect.right - 15, button_rect.centery),
                    (button_rect.right - 25, button_rect.centery + 6)
                ])
    
    def draw_professional_pause_menu_options(self, options):
        """Draw pause menu options with professional styling and emoji icons"""
        mouse_pos = pygame.mouse.get_pos()
        
        for i, option in enumerate(options):
            # Check if mouse is hovering over this item
            button_y = getattr(self, 'pause_menu_buttons_start_y', SCREEN_HEIGHT // 2) + i * 50
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, button_y, 400, 45)
            
            is_hovered = button_rect.collidepoint(mouse_pos)
            if is_hovered:
                self.menu_selection = i
            
            if i == self.menu_selection:
                # Selected state - pleasant, readable colors
                button_color = (85, 107, 47, 180)  # Olive green
                text_color = (255, 255, 255)
                border_color = (144, 238, 144)  # Light green
                emoji_color = (218, 165, 32)  # Goldenrod emoji
                
                # Soft glow effect
                glow_surface = pygame.Surface((button_rect.width + 20, button_rect.height + 20), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (144, 238, 144, 40), (0, 0, button_rect.width + 20, button_rect.height + 20), border_radius=8)
                self.screen.blit(glow_surface, (button_rect.x - 10, button_rect.y - 10))
            else:
                # Normal state - subtle background
                button_color = (60, 70, 50, 120)  # Dark olive
                text_color = (220, 220, 220)  # Light gray
                border_color = (120, 140, 100)  # Muted green
                emoji_color = (180, 180, 180)  # Light gray emoji
            
            # Draw button background
            button_surface = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
            button_surface.fill(button_color)
            self.screen.blit(button_surface, button_rect)
            
            # Draw elegant border
            pygame.draw.rect(self.screen, border_color, button_rect, 2, border_radius=6)
            
            # Draw text with emoji icon
            emoji = get_menu_icon(option)
            menu_text = f"{emoji}  {option}"
            text = self.menu_font.render(menu_text, True, text_color)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            
            # Add subtle selection indicator (arrow on right)
            if i == self.menu_selection:
                indicator_color = (218, 165, 32)  # Goldenrod arrow
                pygame.draw.polygon(self.screen, indicator_color, [
                    (button_rect.right - 25, button_rect.centery - 6),
                    (button_rect.right - 15, button_rect.centery),
                    (button_rect.right - 25, button_rect.centery + 6)
                ])
    
    def get_menu_option_icon(self, option):
        """Get simple ASCII icon for menu option that will definitely work"""
        icons = {
            "Continue Game": ">",
            "Save Game": "S", 
            "New Game": "+",
            "Load Game": "L",
            "Tutorials": "?",
            "Achievements": "*",
            "About": "i",
            "Options": "=",
            "Exit": "X"
        }
        return icons.get(option, "•")
    
    def draw_menu_icon(self, surface, icon_text, x, y, size=20, color=(200, 180, 160)):
        """Render icon - with fallback ASCII art for reliability"""
        # Define ASCII fallbacks for common emojis
        ascii_fallbacks = {
            "🏆": "[*]",  # Trophy
            "❓": "[?]",  # Question mark
            "ℹ️": "[i]",  # Info
            "⚙️": "[=]",  # Gear/Settings
            "⚙": "[=]",   # Gear without variation selector
            "🌱": "[+]",  # Seedling/Plant
            "⌨️": "[K]",  # Keyboard
            "⌨": "[K]",   # Keyboard without variation selector
            "★": "*",    # Star
            "☆": "o",    # Empty star
        }
        
        # Strip variation selectors that might cause issues
        icon_text_clean = icon_text.replace('\ufe0f', '').replace('\ufe0e', '')
        
        # Get fallback text if emoji isn't supported
        fallback_text = ascii_fallbacks.get(icon_text, ascii_fallbacks.get(icon_text_clean, icon_text))
        
        try:
            # Try to render as emoji first if we have emoji font
            if self.emoji_font and (icon_text in ascii_fallbacks or icon_text_clean in ascii_fallbacks):
                try:
                    emoji_render = self.emoji_font.render(icon_text, True, color)
                    # Scale to target size
                    target_size = (size, size)
                    emoji_scaled = pygame.transform.smoothscale(emoji_render, target_size)
                    emoji_rect = emoji_scaled.get_rect(center=(x, y))
                    surface.blit(emoji_scaled, emoji_rect)
                    return  # Success!
                except:
                    pass  # Fall through to ASCII fallback
            
            # Use ASCII fallback with nice styling
            fallback_font = pygame.font.Font(None, int(size * 0.8))
            fallback_render = fallback_font.render(fallback_text, True, color)
            fallback_rect = fallback_render.get_rect(center=(x, y))
            surface.blit(fallback_render, fallback_rect)
            
        except Exception as e:
            # Last resort - bullet point
            fallback_font = pygame.font.Font(None, size)
            fallback_render = fallback_font.render("•", True, color)
            fallback_rect = fallback_render.get_rect(center=(x, y))
            surface.blit(fallback_render, fallback_rect)
    
    def draw_text_in_panel(self, panel_rect, content_lines, title_height=120, line_height=22, margin=40):
        """
        Reusable method to draw text content within panel boundaries with proper wrapping and scrolling.
        
        Args:
            panel_rect: pygame.Rect for the panel
            content_lines: List of dictionaries with 'text', 'color', 'font' keys
            title_height: Height from panel top to start content
            line_height: Spacing between lines
            margin: Left/right margin from panel edges
        """
        # Calculate available content area
        content_area = pygame.Rect(
            panel_rect.x + margin, 
            panel_rect.y + title_height,
            panel_rect.width - (margin * 2),
            panel_rect.height - title_height - 60  # Leave space for instructions at bottom
        )
        
        current_y = content_area.y
        visible_lines = []
        
        for line_data in content_lines:
            if isinstance(line_data, str):
                # Convert simple string to dict format for backward compatibility
                line_data = {
                    'text': line_data,
                    'color': (255, 255, 255),
                    'font': self.font
                }
            
            text = line_data.get('text', '')
            color = line_data.get('color', (255, 255, 255))
            font = line_data.get('font', self.font)
            
            # Handle empty lines
            if text.strip() == "":
                current_y += line_height // 2
                continue
            
            # Word wrap long text
            words = text.split(' ')
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                text_width = font.size(test_line)[0]
                
                if text_width <= content_area.width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        # Single word is too long, force it
                        lines.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Add wrapped lines to visible list if they fit in content area
            for wrapped_line in lines:
                if current_y + line_height <= content_area.bottom:
                    visible_lines.append({
                        'text': wrapped_line,
                        'color': color,
                        'font': font,
                        'y': current_y
                    })
                    current_y += line_height
                else:
                    break
        
        # Render visible lines
        for line in visible_lines:
            rendered_text = line['font'].render(line['text'], True, line['color'])
            self.screen.blit(rendered_text, (content_area.x, line['y']))
        
        # Show scroll indicator if content was cut off
        if current_y > content_area.bottom:
            scroll_text = self.small_font.render("(Content continues...)", True, (120, 120, 120))
            self.screen.blit(scroll_text, (content_area.right - scroll_text.get_width(), content_area.bottom - 20))
    
    def wrap_text(self, text, font, max_width):
        """
        Helper method to wrap text to fit within a specified width.
        Returns a list of text lines.
        """
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            text_width = font.size(test_line)[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, force it
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def draw_title_with_emoji(self, emoji, title_text, x, y, title_color=(144, 238, 144), shadow_color=(20, 25, 15)):
        """
        Properly render a title with emoji icon using the correct font systems.
        Separates emoji rendering (using emoji font) from text rendering (using title font).
        """
        # Calculate emoji size based on title font height
        title_height = self.menu_title_font.get_height()
        emoji_size = int(title_height * 0.9)  # 90% of title height for better visibility
        
        # Measure text width to properly position emoji
        title_surface = self.menu_title_font.render(title_text, True, title_color)
        title_width = title_surface.get_width()
        
        # Calculate positions - emoji on left, then text
        total_width = emoji_size + 20 + title_width  # emoji + spacing + text
        start_x = x - total_width // 2
        emoji_x = start_x + emoji_size // 2
        text_x = start_x + emoji_size + 20 + title_width // 2
        
        # Draw shadows first
        if emoji:
            self.draw_menu_icon(self.screen, emoji, emoji_x + 2, y + 2, emoji_size, shadow_color)
        
        shadow_title = self.menu_title_font.render(title_text, True, shadow_color)
        shadow_rect = shadow_title.get_rect(center=(text_x + 2, y + 2))
        self.screen.blit(shadow_title, shadow_rect)
        
        # Draw main emoji and text
        if emoji:
            self.draw_menu_icon(self.screen, emoji, emoji_x, y, emoji_size, (218, 165, 32))  # Goldenrod emoji
        
        title_rect = title_surface.get_rect(center=(text_x, y))
        self.screen.blit(title_surface, title_rect)
    
    def draw_farm_setup(self):
        """Draw the farm setup screen using UI framework with interactive forms"""
        if UI_FRAMEWORK_AVAILABLE:
            return self.draw_farm_setup_framework()
        else:
            return self.draw_farm_setup_legacy()
    
    def draw_farm_setup_framework(self):
        """Draw farm setup using the new generic page framework"""
        from ui_framework import UIManager, GenericPagePanel
        
        # Draw gradient background
        ui = UIManager(self.screen)
        ui.draw_warm_gradient_background()
        
        # Create or update the farm setup panel
        if not hasattr(self, 'farm_setup_panel'):
            self.farm_setup_panel = GenericPagePanel(
                "+ NEW FARM SETUP",
                "Create your personalized plant growing experience",
                width=800,
                height=650
            )
            self.farm_setup_panel.set_fonts(
                self.menu_title_font,
                self.ui_font,
                self.font,
                self.menu_font
            )
        
        # Clear and rebuild content
        self.farm_setup_panel.content_elements = []
        self.farm_setup_panel.input_fields = []
        self.farm_setup_panel.buttons = []
        
        # Update input field states with current game values
        def update_input_field_in_content(field_id, value, active):
            for elem in self.farm_setup_panel.content_elements:
                if elem[0] == 'input_field' and elem[1]['id'] == field_id:
                    elem[1]['value'] = value
                    elem[1]['active'] = active
                    break
        
        # Add farm name input first
        self.farm_setup_panel.add_input_field(
            "Farm Name:",
            "farm_name",
            self.farm_name,
            self.setup_name_input_active,
            "Enter your farm name..."
        )
        self.farm_setup_panel.add_spacer(25)  # Increased spacing
        
        # Add location options
        location_options = []
        for i, loc in enumerate(self.available_locations):
            prefix = "> " if i == self.setup_location_selection else "  "
            location_options.append(prefix + loc)
        
        self.farm_setup_panel.add_option_list(
            "Location:",
            location_options,
            self.setup_location_selection,
            "location"
        )
        self.farm_setup_panel.add_spacer(30)  # Increased spacing
        
        # Add season options
        season_options = []
        for i, (season_name, season_desc) in enumerate(self.available_seasons):
            prefix = "> " if i == self.setup_season_selection else "  "
            season_options.append(f"{prefix}{season_name} - {season_desc}")
        
        self.farm_setup_panel.add_option_list(
            "Starting Season:",
            season_options,
            self.setup_season_selection,
            "season"
        )
        self.farm_setup_panel.add_spacer(50)  # Increased spacing before buttons
        
        # Add buttons
        can_start = bool(self.farm_name.strip()) and self.setup_season_selection >= 0
        self.farm_setup_panel.add_button("START FARM", "start", enabled=can_start)
        self.farm_setup_panel.add_button("BACK", "back", enabled=True)
        
        # Render the panel
        ui.add_element(self.farm_setup_panel)
        ui.render()
    
    def handle_farm_setup_panel_state(self):
        """Handle panel state updates for farm setup"""
        # This will be called to sync the panel state with game state
        pass
    
    
    def draw_farm_setup_legacy(self):
        """Legacy farm setup screen rendering (fallback)"""
        # Warm gradient background
        self.draw_warm_gradient_background()
        
        # Title with proper emoji rendering
        title_y = 100
        self.draw_title_with_emoji("🌱", "NEW FARM SETUP", SCREEN_WIDTH // 2, title_y)
        
        # Subtitle with better colors
        subtitle = self.ui_font.render("Create your personalized plant growing experience", True, (218, 165, 32))  # Goldenrod
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Farm name section
        name_label = self.menu_font.render("Farm Name:", True, WHITE)
        name_label_rect = name_label.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.screen.blit(name_label, name_label_rect)
        
        # Name input field with improved styling
        name_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 300, 400, 40)
        if self.setup_name_input_active:
            pygame.draw.rect(self.screen, (85, 107, 47), name_rect, border_radius=6)  # Olive green
            pygame.draw.rect(self.screen, (144, 238, 144), name_rect, 3, border_radius=6)  # Light green border
        else:
            pygame.draw.rect(self.screen, (60, 70, 50), name_rect, border_radius=6)  # Dark olive
            pygame.draw.rect(self.screen, (120, 140, 100), name_rect, 2, border_radius=6)  # Muted green border
        
        # Farm name text with cursor
        name_display = self.farm_name
        if self.setup_name_input_active and (pygame.time.get_ticks() // 500) % 2:
            name_display += "|"  # Blinking cursor
        
        if name_display:
            name_text = self.font.render(name_display, True, WHITE)
            name_text_rect = name_text.get_rect(left=name_rect.left + 10, centery=name_rect.centery)
            self.screen.blit(name_text, name_text_rect)
        else:
            # Placeholder text
            placeholder = self.font.render("Enter your farm name...", True, (180, 180, 180))  # Light gray
            placeholder_rect = placeholder.get_rect(left=name_rect.left + 10, centery=name_rect.centery)
            self.screen.blit(placeholder, placeholder_rect)
        
        # Location section
        location_label = self.menu_font.render("Location:", True, WHITE)
        location_label_rect = location_label.get_rect(center=(SCREEN_WIDTH // 2, 370))
        self.screen.blit(location_label, location_label_rect)
        
        # Location options
        for i, location in enumerate(self.available_locations):
            y_pos = 400 + i * 40
            location_rect = pygame.Rect(SCREEN_WIDTH // 2 - 300, y_pos, 600, 35)
            
            if i == self.setup_location_selection and not self.setup_name_input_active and self.setup_season_selection == -1:
                pygame.draw.rect(self.screen, (85, 107, 47), location_rect, border_radius=6)  # Olive green
                pygame.draw.rect(self.screen, (144, 238, 144), location_rect, 3, border_radius=6)  # Light green border
                prefix = "📍 "
                color = WHITE
            else:
                pygame.draw.rect(self.screen, (60, 70, 50), location_rect, border_radius=6)  # Dark olive
                pygame.draw.rect(self.screen, (120, 140, 100), location_rect, 1, border_radius=6)  # Muted green border
                prefix = "   "
                color = (220, 220, 220)  # Light gray
            
            location_text = self.font.render(prefix + location, True, color)
            location_text_rect = location_text.get_rect(left=location_rect.left + 10, centery=location_rect.centery)
            self.screen.blit(location_text, location_text_rect)
        
        # Season selection section
        season_label = self.menu_font.render("Starting Season:", True, WHITE)
        season_label_rect = season_label.get_rect(center=(SCREEN_WIDTH // 2, 480))
        self.screen.blit(season_label, season_label_rect)
        
        # Season options
        for i, (season_name, season_desc) in enumerate(self.available_seasons):
            y_pos = 510 + i * 40
            season_rect = pygame.Rect(SCREEN_WIDTH // 2 - 300, y_pos, 600, 35)
            
            if i == self.setup_season_selection and not self.setup_name_input_active and self.setup_season_selection >= 0:
                pygame.draw.rect(self.screen, (85, 107, 47), season_rect, border_radius=6)  # Olive green
                pygame.draw.rect(self.screen, (144, 238, 144), season_rect, 3, border_radius=6)  # Light green border
                # Add season emojis
                season_emojis = ["🌸", "☀️", "🍂", "❄️"]
                prefix = f"{season_emojis[i]} " if i < len(season_emojis) else "🌱 "
                color = WHITE
            else:
                pygame.draw.rect(self.screen, (60, 70, 50), season_rect, border_radius=6)  # Dark olive
                pygame.draw.rect(self.screen, (120, 140, 100), season_rect, 1, border_radius=6)  # Muted green border
                prefix = "   "
                color = (220, 220, 220)  # Light gray
            
            season_text = self.font.render(f"{prefix}{season_name} - {season_desc}", True, color)
            season_text_rect = season_text.get_rect(left=season_rect.left + 10, centery=season_rect.centery)
            self.screen.blit(season_text, season_text_rect)
        
        # Start Game button with improved styling
        start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, 680, 240, 50)
        can_start = bool(self.farm_name.strip()) and self.setup_season_selection >= 0
        
        if can_start:
            # Active button - ready to start
            pygame.draw.rect(self.screen, (85, 107, 47), start_button_rect, border_radius=8)  # Olive green
            pygame.draw.rect(self.screen, (144, 238, 144), start_button_rect, 3, border_radius=8)  # Light green border
            # Add glow effect for active button
            glow_surface = pygame.Surface((start_button_rect.width + 20, start_button_rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (144, 238, 144, 40), (0, 0, start_button_rect.width + 20, start_button_rect.height + 20), border_radius=12)
            self.screen.blit(glow_surface, (start_button_rect.x - 10, start_button_rect.y - 10))
            button_color = WHITE
            button_text = "🌱 START GAME"
        else:
            # Disabled button - missing requirements
            pygame.draw.rect(self.screen, (60, 70, 50), start_button_rect, border_radius=8)  # Dark olive
            pygame.draw.rect(self.screen, (120, 140, 100), start_button_rect, 2, border_radius=8)  # Muted green border
            button_color = (160, 160, 160)  # Light gray text
            button_text = "START GAME"
        
        start_text = self.menu_font.render(button_text, True, button_color)
        start_text_rect = start_text.get_rect(center=start_button_rect.center)
        self.screen.blit(start_text, start_text_rect)
        
        # Instructions with better colors
        if self.setup_name_input_active:
            instructions = self.small_font.render("Type your farm name, then press ENTER/TAB to continue", True, (218, 165, 32))  # Goldenrod
        elif self.setup_season_selection == -1:
            instructions = self.small_font.render("Use arrow keys to select location, ENTER to continue to season selection", True, (218, 165, 32))  # Goldenrod
        else:
            instructions = self.small_font.render("Use arrow keys to select starting season, ENTER to start game", True, (218, 165, 32))  # Goldenrod
        
        inst_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, 750))
        self.screen.blit(instructions, inst_rect)
        
        # Back instruction
        back_text = self.small_font.render("ESC - Back to Main Menu", True, (180, 180, 180))  # Light gray
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, 770))
        self.screen.blit(back_text, back_rect)
    
    def draw_placeholder_screen(self, title):
        """Draw a placeholder screen for unimplemented features"""
        title_text = self.menu_title_font.render(title, True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(title_text, title_rect)
        
        info = self.ui_font.render("This feature is coming soon!", True, GRAY)
        info_rect = info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(info, info_rect)
        
        back = self.font.render("Press ESC to return to menu", True, WHITE)
        back_rect = back.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(back, back_rect)
    
    def draw_options_screen(self):
        """Draw the options menu using UI framework for text, legacy for buttons"""
        if UI_FRAMEWORK_AVAILABLE:
            return self.draw_options_screen_framework()
        else:
            return self.draw_options_screen_legacy()
    
    def draw_options_screen_framework(self):
        """Draw settings page using the new generic page framework"""
        from ui_framework import UIManager, GenericPagePanel
        
        # Draw gradient background
        ui = UIManager(self.screen)
        ui.draw_warm_gradient_background()
        
        # Create or update the options panel
        if not hasattr(self, 'options_panel'):
            self.options_panel = GenericPagePanel(
                "@ SETTINGS",
                "Configure game options and controls",
                width=600,
                height=500
            )
            self.options_panel.set_fonts(
                self.menu_title_font,
                self.ui_font,
                self.font,
                self.menu_font
            )
        
        # Clear and rebuild content
        self.options_panel.content_elements = []
        self.options_panel.input_fields = []
        self.options_panel.buttons = []
        
        # Add options buttons
        for option_name, option_func in self.options_items:
            self.options_panel.add_button(option_name, option_name.lower().replace(' ', '_'), enabled=True)
        
        # Render the panel
        ui.add_element(self.options_panel)
        ui.render()
    
    def draw_settings_buttons_overlay(self):
        """Draw interactive settings buttons on top of framework panel"""
        # Get actual screen dimensions
        actual_width = self.screen.get_width()
        actual_height = self.screen.get_height()
        
        # Calculate button positions
        button_start_y = actual_height // 2 - 100
        mouse_pos = pygame.mouse.get_pos()
        
        for i, (option_name, option_func) in enumerate(self.options_items):
            button_y = button_start_y + i * 60
            button_rect = pygame.Rect(actual_width // 2 - 150, button_y, 300, 45)
            
            is_hovered = button_rect.collidepoint(mouse_pos)
            if is_hovered:
                self.options_selection = i
            
            if i == self.options_selection:
                button_color = (85, 107, 47, 200)  # More opaque when selected
                text_color = (255, 255, 255)
                border_color = (144, 238, 144)
            else:
                button_color = (40, 50, 35, 150)  # Semi-transparent
                text_color = (200, 200, 200)
                border_color = (100, 120, 90)
            
            # Draw button
            button_surface = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
            button_surface.fill(button_color)
            self.screen.blit(button_surface, button_rect)
            pygame.draw.rect(self.screen, border_color, button_rect, 2, border_radius=6)
            
            # Button text with status
            if option_name == "Fullscreen":
                status = "ON" if self.fullscreen else "OFF"
                display_text = f"{option_name}: {status}"
            elif option_name == "Monitor":
                monitor_info = f"Monitor {self.current_display + 1}"
                display_text = f"{option_name}: {monitor_info}"
            elif option_name == "Sound Volume":
                sound_status = "ON" if getattr(self, 'sound_enabled', True) else "OFF"
                display_text = f"{option_name}: {sound_status}"
            else:
                display_text = option_name
            
            text = self.ui_font.render(display_text, True, text_color)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            
            # Store button positions for click handling
            if not hasattr(self, 'options_button_rects'):
                self.options_button_rects = {}
            self.options_button_rects[i] = button_rect
    
    def draw_options_screen_legacy(self):
        """Legacy options screen rendering (fallback)"""
        # Warm gradient background
        self.draw_warm_gradient_background()
        
        # Calculate vertical centering
        total_options = len(self.options_items)
        menu_height = 80 + (total_options * 50) + 40  # title + buttons + padding
        start_y = (SCREEN_HEIGHT - menu_height) // 2
        
        # Title with proper emoji rendering
        title_y = start_y + 40
        self.draw_title_with_emoji("⚙️", "SETTINGS", SCREEN_WIDTH // 2, title_y)
        
        # Store button start position
        self.options_buttons_start_y = title_y + 80
        
        # Options items with professional styling
        mouse_pos = pygame.mouse.get_pos()
        for i, (option_name, option_func) in enumerate(self.options_items):
            button_y = self.options_buttons_start_y + i * 50
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, button_y, 400, 45)
            
            is_hovered = button_rect.collidepoint(mouse_pos)
            if is_hovered:
                self.options_selection = i
            
            if i == self.options_selection:
                # Selected state - pleasant, readable colors
                button_color = (85, 107, 47, 180)  # Olive green
                text_color = (255, 255, 255)
                border_color = (144, 238, 144)  # Light green
                
                # Soft glow effect
                glow_surface = pygame.Surface((button_rect.width + 20, button_rect.height + 20), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (144, 238, 144, 40), (0, 0, button_rect.width + 20, button_rect.height + 20), border_radius=8)
                self.screen.blit(glow_surface, (button_rect.x - 10, button_rect.y - 10))
            else:
                # Normal state - subtle background
                button_color = (60, 70, 50, 120)  # Dark olive
                text_color = (220, 220, 220)  # Light gray
                border_color = (120, 140, 100)  # Muted green
            
            # Draw button background with rounded corners effect
            button_surface = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
            button_surface.fill(button_color)
            self.screen.blit(button_surface, button_rect)
            
            # Draw elegant border
            pygame.draw.rect(self.screen, border_color, button_rect, 2, border_radius=6)
            
            # Special handling for options with status
            if option_name == "Fullscreen":
                status = "ON" if self.fullscreen else "OFF"
                display_text = f"{option_name}: {status}"
            elif option_name == "Monitor":
                monitor_info = f"Monitor {self.current_display + 1}"
                display_text = f"{option_name}: {monitor_info}"
            elif option_name == "Sound Volume":
                sound_status = "ON" if getattr(self, 'sound_enabled', True) else "OFF"
                display_text = f"{option_name}: {sound_status}"
            else:
                display_text = option_name
            
            # Draw text
            text = self.menu_font.render(display_text, True, text_color)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            
            # Add subtle selection indicator (arrow on right)
            if i == self.options_selection:
                indicator_color = (218, 165, 32)  # Goldenrod arrow
                pygame.draw.polygon(self.screen, indicator_color, [
                    (button_rect.right - 25, button_rect.centery - 6),
                    (button_rect.right - 15, button_rect.centery),
                    (button_rect.right - 25, button_rect.centery + 6)
                ])
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.fullscreen = not self.fullscreen
        self.create_window()
    
    def get_current_display(self):
        """Try to detect which display the terminal is on"""
        # Try to get display from environment variable (set by some terminals)
        display_env = os.environ.get('DISPLAY', ':0')
        
        # For multi-monitor setups, try to detect current display
        # This is a simple heuristic - in practice, we'll default to display 0
        try:
            if hasattr(pygame.display, 'get_desktop_sizes'):
                # Pygame 2.0+ has better multi-monitor support
                return 0  # Default to primary display
            else:
                return 0
        except:
            return 0
    
    def get_available_displays(self):
        """Get list of available displays"""
        displays = []
        try:
            if hasattr(pygame.display, 'get_desktop_sizes'):
                # Pygame 2.0+ multi-monitor support
                desktop_sizes = pygame.display.get_desktop_sizes()
                for i, size in enumerate(desktop_sizes):
                    displays.append(f"Monitor {i+1} ({size[0]}x{size[1]})")
            else:
                # Fallback for older pygame versions
                displays.append("Primary Monitor")
        except:
            displays.append("Primary Monitor")
        
        return displays if displays else ["Primary Monitor"]
    
    def create_window(self):
        """Create the game window on the specified display"""
        global SCREEN_WIDTH, SCREEN_HEIGHT
        
        # Set window position for specific display (Linux/X11)
        if len(self.available_displays) > 1 and self.current_display > 0:
            try:
                # Try to position window on specified display
                # This is a simple approach - more complex positioning would require
                # platform-specific code
                os.environ['SDL_VIDEO_WINDOW_POS'] = f'{self.current_display * 1920},0'
            except:
                pass
        
        global SCREEN_WIDTH, SCREEN_HEIGHT
        
        if self.fullscreen:
            # Use borderless fullscreen instead of exclusive fullscreen
            self.screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
            SCREEN_WIDTH, SCREEN_HEIGHT = self.screen.get_size()
        else:
            SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def update_menu_options(self):
        """Update main menu options based on game state"""
        if self.game_in_progress:
            self.menu_options = ["Continue Game", "New Game", "Load Game", "Save Game", "Achievements", "Help", "Settings", "About", "Exit"]
        else:
            self.menu_options = ["New Game", "Load Game", "Achievements", "Help", "Settings", "About", "Exit"]
    
    def update_pause_menu_options(self):
        """Update pause menu options"""
        self.pause_menu_options = ["Resume Game", "Save Game", "Load Game", "Settings", "Main Menu", "Exit Game"]
    
    def update_options_items(self):
        """Update the options menu items"""
        self.options_items = [
            ("Fullscreen", lambda: self.toggle_fullscreen()),
        ]
        
        # Add monitor selection if multiple monitors available
        if len(self.available_displays) > 1:
            self.options_items.append(("Monitor", lambda: self.cycle_display()))
        
        self.options_items.extend([
            ("Sound Volume", lambda: self.toggle_sound()),
            ("Interface Help", lambda: self.show_interface_controls()),
        ])
        
        # Add appropriate back option based on where we came from
        if self.previous_game_state == GameState.PAUSE_MENU:
            self.options_items.append(("Back to Game", lambda: self.return_to_pause_menu()))
        else:
            self.options_items.append(("Back to Menu", lambda: self.return_to_menu()))
    
    def cycle_display(self):
        """Cycle to the next available display"""
        self.current_display = (self.current_display + 1) % len(self.available_displays)
        self.create_window()
    
    def show_interface_controls(self):
        """Show the interface controls screen"""
        self.game_state = GameState.TUTORIALS  # Use existing TUTORIALS state
    
    def show_help(self):
        """Show the help screen"""
        self.game_state = GameState.HELP
    
    def draw_interface_controls(self):
        """Draw the interface controls screen using UI framework"""
        if not UI_FRAMEWORK_AVAILABLE:
            return self.draw_interface_controls_legacy()
        
        def populate_content(content_area):
            fonts = self.create_framework_fonts()
            content_area.add_header("Mouse Controls:", fonts['ui']) \
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
        
        ui = self.create_framework_page("CONTROLS", "⌨️", populate_content)
        if ui:
            ui.render()
            
            # Instructions at bottom
            instructions = self.font.render("Press ESC to return to Options menu", True, (140, 120, 100))
            inst_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(instructions, inst_rect)
    
    def draw_about_screen(self):
        """Draw the about screen using the framework"""
        if UI_FRAMEWORK_AVAILABLE:
            from ui_framework import UIManager, GenericPagePanel
            
            # Draw gradient background
            ui = UIManager(self.screen)
            ui.draw_warm_gradient_background()
            
            # Create about panel with more height for content
            about_panel = GenericPagePanel(
                "i ABOUT",
                "Field Station - A Scientific Farming Simulator",
                width=700,
                height=600
            )
            about_panel.set_fonts(
                self.menu_title_font,
                self.ui_font,
                self.font,
                self.menu_font
            )
            
            # Add about content
            about_panel.add_text("Version 0.1", center=True)
            about_panel.add_spacer()
            about_panel.add_text("Field Station is an educational farming game that combines", center=True)
            about_panel.add_text("real agricultural science with engaging gameplay.", center=True)
            about_panel.add_spacer()
            about_panel.add_header("Features:")
            about_panel.add_text("• Realistic crop growth simulation")
            about_panel.add_text("• Scientific data tracking")
            about_panel.add_text("• Weather and seasonal effects")
            about_panel.add_text("• Soil quality management")
            about_panel.add_spacer()
            about_panel.add_text("Created with Python and Pygame", (140, 120, 100), center=True)
            about_panel.add_spacer()
            about_panel.add_button("BACK", "back")
            
            # Store panel reference for event handling
            self.about_panel = about_panel
            
            ui.add_element(about_panel)
            ui.render()
            return
        
        # Fallback to legacy
        self.draw_about_screen_legacy()
    
    def draw_about_screen_legacy(self):
        """Legacy about screen rendering"""
        pass
    
    def draw_achievements_screen(self):
        """Draw the achievements screen using the framework"""
        if UI_FRAMEWORK_AVAILABLE:
            from ui_framework import UIManager, GenericPagePanel
            
            # Draw gradient background
            ui = UIManager(self.screen)
            ui.draw_warm_gradient_background()
            
            # Create achievements panel
            achievements_panel = GenericPagePanel(
                "* ACHIEVEMENTS",
                "Track your farming accomplishments",
                width=700,
                height=550
            )
            achievements_panel.set_fonts(
                self.menu_title_font,
                self.ui_font,
                self.font,
                self.menu_font
            )
            
            # Add achievements content
            achievements_panel.add_header("Unlocked Achievements:")
            achievements_panel.add_text("🌱 First Seed - Plant your first crop")
            achievements_panel.add_text("🌾 First Harvest - Harvest your first crop")
            achievements_panel.add_spacer()
            achievements_panel.add_header("Locked Achievements:")
            achievements_panel.add_text("🏆 Master Farmer - Harvest 100 crops", (120, 120, 120))
            achievements_panel.add_text("💰 Wealthy Farmer - Earn $10,000", (120, 120, 120))
            achievements_panel.add_text("📅 Year One - Complete a full year", (120, 120, 120))
            achievements_panel.add_spacer()
            achievements_panel.add_button("BACK", "back")
            
            # Store panel reference for event handling
            self.achievements_panel = achievements_panel
            
            ui.add_element(achievements_panel)
            ui.render()
            return
        
        # Fallback to legacy
        self.draw_achievements_screen_legacy()
    
    def draw_achievements_screen_legacy(self):
        """Legacy achievements screen rendering"""
        pass
    
    def draw_help_screen(self):
        """Draw the help screen using the framework"""
        if UI_FRAMEWORK_AVAILABLE:
            from ui_framework import UIManager, GenericPagePanel
            
            # Draw gradient background
            ui = UIManager(self.screen)
            ui.draw_warm_gradient_background()
            
            # Create help panel
            help_panel = GenericPagePanel(
                "? HELP & TUTORIALS",
                "Learn how to play Field Station",
                width=700,
                height=600
            )
            help_panel.set_fonts(
                self.menu_title_font,
                self.ui_font,
                self.font,
                self.menu_font
            )
            
            # Add help content
            help_panel.add_header("Controls:")
            help_panel.add_text("• Mouse: Click tiles to interact")
            help_panel.add_text("• Arrow Keys/WASD: Move camera")
            help_panel.add_text("• Mouse Wheel: Zoom in/out")
            help_panel.add_text("• Space: Pause/unpause")
            help_panel.add_text("• P: Plant crop on selected tile")
            help_panel.add_text("• H: Harvest crop on selected tile")
            help_panel.add_text("• A: Toggle auto-harvest")
            help_panel.add_spacer()
            help_panel.add_header("Game Tips:")
            help_panel.add_text("• Different crops grow best in different seasons")
            help_panel.add_text("• Monitor soil quality and moisture levels")
            help_panel.add_text("• Some crops add nitrogen to the soil")
            help_panel.add_text("• Use the market to track crop prices")
            help_panel.add_spacer()
            help_panel.add_button("BACK", "back")
            
            # Store panel reference for event handling
            self.help_panel = help_panel
            
            ui.add_element(help_panel)
            ui.render()
            return
        
        # Fallback to legacy
        self.draw_help_screen_legacy()
    
    def draw_help_screen_legacy(self):
        """Legacy help screen rendering"""
        # Simple fallback implementation
        self.screen.fill((30, 40, 30))
        title = self.menu_title_font.render("HELP", True, (144, 238, 144))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(title, title_rect)
        
        content = self.font.render("Help content not available in legacy mode", True, (200, 200, 200))
        content_rect = content.get_rect(center=(self.screen.get_width() // 2, 200))
        self.screen.blit(content, content_rect)
    
    def return_to_game(self):
        """Return to the game"""
        self.game_state = GameState.GAME
        self.previous_game_state = None
    
    def return_to_menu(self):
        """Return to main menu"""
        self.game_state = GameState.MENU
        self.previous_game_state = None
    
    def return_to_pause_menu(self):
        """Return to pause menu"""
        self.game_state = GameState.PAUSE_MENU
        self.previous_game_state = None
    
    def toggle_sound(self):
        """Toggle sound on/off (placeholder for now)"""
        # This is a placeholder - you can implement actual sound control later
        if not hasattr(self, 'sound_enabled'):
            self.sound_enabled = True
        self.sound_enabled = not self.sound_enabled
        status = "ON" if self.sound_enabled else "OFF"
        self.show_message(f"Sound: {status}", WHITE, 2000)
    
    def handle_options_event(self, event):
        """Handle events in the options menu"""
        # Handle ESC key specially
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_state = self.previous_game_state or GameState.MENU
            return True
        
        # If using UI framework, delegate to panel
        if UI_FRAMEWORK_AVAILABLE and hasattr(self, 'options_panel'):
            result = self.options_panel.handle_event(event)
            
            if result['type'] == 'button_click':
                # Map button IDs back to option functions
                for option_name, option_func in self.options_items:
                    if result['id'] == option_name.lower().replace(' ', '_'):
                        option_func()
                        break
            return True
        
        # Fallback to legacy handling
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.options_selection = (self.options_selection - 1) % len(self.options_items)
            elif event.key == pygame.K_DOWN:
                self.options_selection = (self.options_selection + 1) % len(self.options_items)
            elif event.key == pygame.K_RETURN:
                option_name, option_func = self.options_items[self.options_selection]
                option_func()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                for i, (option_name, option_func) in enumerate(self.options_items):
                    # Use the actual button positions from draw_options_screen
                    if not hasattr(self, 'options_buttons_start_y'):
                        # Fallback if options screen hasn't been drawn yet
                        self.options_buttons_start_y = SCREEN_HEIGHT // 2 - 100
                    button_y = self.options_buttons_start_y + i * 50
                    button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, button_y, 400, 45)
                    if button_rect.collidepoint(mouse_pos):
                        self.options_selection = i
                        option_func()
                        break
        
        return True
    
    def handle_help_event(self, event):
        """Handle events in the help screen"""
        # Handle ESC key specially
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_state = GameState.MENU
            return True
        
        # If using UI framework, delegate to panel
        if UI_FRAMEWORK_AVAILABLE and hasattr(self, 'help_panel'):
            result = self.help_panel.handle_event(event)
            
            if result['type'] == 'button_click':
                if result['id'] == 'back':
                    self.game_state = GameState.MENU
            return True
        
        return True
    
    def handle_about_event(self, event):
        """Handle events in the about screen"""
        # Handle ESC key specially
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_state = GameState.MENU
            return True
        
        # If using UI framework, delegate to panel
        if UI_FRAMEWORK_AVAILABLE and hasattr(self, 'about_panel'):
            result = self.about_panel.handle_event(event)
            
            if result['type'] == 'button_click':
                if result['id'] == 'back':
                    self.game_state = GameState.MENU
            return True
        
        return True
    
    def handle_achievements_event(self, event):
        """Handle events in the achievements screen"""
        # Handle ESC key specially
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_state = GameState.MENU
            return True
        
        # If using UI framework, delegate to panel
        if UI_FRAMEWORK_AVAILABLE and hasattr(self, 'achievements_panel'):
            result = self.achievements_panel.handle_event(event)
            
            if result['type'] == 'button_click':
                if result['id'] == 'back':
                    self.game_state = GameState.MENU
            return True
        
        return True
    
    def handle_farm_setup_event(self, event):
        """Handle events in the garden setup screen"""
        # Handle ESC key specially
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_state = GameState.MENU
            return True
        
        # If using UI framework, delegate to panel
        if UI_FRAMEWORK_AVAILABLE and hasattr(self, 'farm_setup_panel'):
            result = self.farm_setup_panel.handle_event(event)
            
            if result['type'] == 'button_click':
                if result['id'] == 'start':
                    self.start_new_game_with_setup()
                elif result['id'] == 'back':
                    self.game_state = GameState.MENU
            elif result['type'] == 'field_change':
                if result['id'] == 'farm_name':
                    self.farm_name = result['value']
            elif result['type'] == 'field_submit':
                if result['id'] == 'farm_name':
                    self.farm_name = result['value']
                    self.setup_name_input_active = False
            elif result['type'] == 'field_focus':
                if result['id'] == 'farm_name':
                    self.setup_name_input_active = True
                else:
                    self.setup_name_input_active = False
            
            # Handle option list clicks (locations and seasons)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                # This is a simplified version - would need more complex handling for option lists
                # For now, keeping the original mouse click handling below
        
        # Original handling for clicks on options
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if clicking on name input field
                name_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 300, 400, 40)
                if name_rect.collidepoint(mouse_pos):
                    self.setup_name_input_active = True
                
                # Check if clicking on location options
                elif not self.setup_name_input_active:
                    for i, location in enumerate(self.available_locations):
                        location_rect = pygame.Rect(SCREEN_WIDTH // 2 - 300, 400 + i * 40, 600, 35)
                        if location_rect.collidepoint(mouse_pos):
                            self.setup_location_selection = i
                            self.setup_season_selection = -1  # Switch to location mode
                            break
                    
                    # Check if clicking on season options
                    for i, (season_name, season_desc) in enumerate(self.available_seasons):
                        season_rect = pygame.Rect(SCREEN_WIDTH // 2 - 300, 510 + i * 40, 600, 35)
                        if season_rect.collidepoint(mouse_pos):
                            self.setup_season_selection = i
                            break
                
                # Check if clicking on Start Game button
                start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 680, 200, 50)
                if start_button_rect.collidepoint(mouse_pos) and self.farm_name.strip():
                    self.start_new_game_with_setup()
        
        return True
    
    def start_new_game_with_setup(self):
        """Start a new game with the chosen farm setup"""
        if not self.farm_name.strip():
            return  # Don't start without a name
        
        # Only start if both location and season are selected
        if self.setup_season_selection < 0:
            return  # Season not selected yet
        
        self.farm_location = self.available_locations[self.setup_location_selection]
        self.game_state = GameState.GAME
        self.reset_game()
        self.apply_location_settings()
        self.apply_season_settings()
        self.game_in_progress = True
    
    def apply_location_settings(self):
        """Apply location-specific settings to the game"""
        if "Champaign, Illinois" in self.farm_location:
            # Apply Champaign, Illinois specific settings
            # Central Illinois prairie soil - high quality but variable
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    tile = self.grid[y][x]
                    # Prairie soil: good quality, moderate moisture, good nitrogen
                    tile.soil_quality = random.uniform(0.6, 0.9)  # Rich prairie soil
                    tile.moisture = random.uniform(0.4, 0.7)     # Moderate moisture
                    tile.nitrogen = random.uniform(0.5, 0.8)     # Good nitrogen from prairie
    
    def apply_season_settings(self):
        """Apply the selected starting season"""
        season_mapping = [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER]
        if 0 <= self.setup_season_selection < len(season_mapping):
            self.season = season_mapping[self.setup_season_selection]
        else:
            self.season = Season.SPRING  # Default fallback
    
    def handle_menu_event(self, event):
        """Handle events in the menu"""
        # Handle ESC key specially
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # ESC in main menu returns to game if one is in progress
            if self.game_in_progress:
                self.game_state = GameState.GAME
                return True
            # If no game in progress, ESC does nothing (stay in menu)
            return True
        
        # If using UI framework, delegate to menu panel
        if UI_FRAMEWORK_AVAILABLE and hasattr(self, 'menu_panel'):
            handled = self.menu_panel.handle_event(event)
            
            # Check if an option was clicked
            clicked_option = self.menu_panel.get_clicked_option()
            if clicked_option:
                self.menu_selection = self.menu_panel.selected_index
                return self.activate_menu_item()
            
            # Sync selection state
            if self.menu_panel.selected_index != self.menu_selection:
                self.menu_selection = self.menu_panel.selected_index
            
            return True
        
        # Fallback to legacy handling
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN:
                return self.activate_menu_item()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                # Use the actual button rects stored during drawing
                if hasattr(self, 'main_menu_button_rects'):
                    for i, rect in self.main_menu_button_rects.items():
                        if rect.collidepoint(mouse_pos):
                            self.menu_selection = i
                            return self.activate_menu_item()
        
        return True
    
    def handle_pause_menu_event(self, event):
        """Handle events in the pause menu"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # ESC in pause menu returns to game
                self.game_state = GameState.GAME
                return True
            elif event.key == pygame.K_UP:
                self.menu_selection = (self.menu_selection - 1) % len(self.pause_menu_options)
            elif event.key == pygame.K_DOWN:
                self.menu_selection = (self.menu_selection + 1) % len(self.pause_menu_options)
            elif event.key == pygame.K_RETURN:
                result = self.activate_pause_menu_item()
                return result
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                for i in range(len(self.pause_menu_options)):
                    if self.get_menu_item_rect(i).collidepoint(mouse_pos):
                        self.menu_selection = i
                        result = self.activate_pause_menu_item()
                        return result
        
        return True
    
    def activate_pause_menu_item(self):
        """Activate the currently selected pause menu item"""
        selected = self.pause_menu_options[self.menu_selection]
        if selected == "Resume Game":
            self.game_state = GameState.GAME
        elif selected == "Save Game":
            self.save_game()
            # Stay in pause menu
        elif selected == "Load Game":
            if self.load_game():
                self.game_state = GameState.GAME
            # If load failed, stay in pause menu
        elif selected == "Settings":
            self.previous_game_state = GameState.PAUSE_MENU
            self.game_state = GameState.OPTIONS
            self.update_options_items()
        elif selected == "Main Menu":
            self.game_state = GameState.MENU
            self.update_menu_options()
        elif selected == "Exit Game":
            return False
        return True
    
    def activate_menu_item(self):
        """Activate the currently selected menu item"""
        selected = self.menu_options[self.menu_selection]
        if selected == "Continue Game":
            # Return to the game in progress
            self.game_state = GameState.GAME
        elif selected == "Save Game":
            if self.game_in_progress:
                self.save_game()
                # Stay in menu
            else:
                self.show_message("No game to save!", RED)
        elif selected == "New Game":
            self.game_state = GameState.FARM_SETUP
            self.farm_name = ""
            self.setup_name_input_active = True
        elif selected == "Load Game":
            if self.load_game():
                self.game_state = GameState.GAME
            # If load failed, stay in menu
        elif selected == "Achievements":
            self.game_state = GameState.ACHIEVEMENTS
        elif selected == "Help":
            self.game_state = GameState.HELP
        elif selected == "About":
            self.game_state = GameState.ABOUT
        elif selected == "Settings" or selected == "Options":  # Handle both names
            self.previous_game_state = GameState.MENU
            self.game_state = GameState.OPTIONS
            self.update_options_items()  # Refresh options to show "Back to Menu"
        elif selected == "Exit":
            return False
        return True
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.grid = [[Tile(x, y, 
                          random.uniform(0.4, 0.8),  # soil quality
                          random.uniform(0.3, 0.6),  # moisture
                          random.uniform(0.3, 0.7))   # nitrogen
                     for x in range(GRID_WIDTH)] 
                    for y in range(GRID_HEIGHT)]
        self.money = 500
        self.day = 1
        self.season = Season.SPRING
        self.weather = Weather.SUNNY
        self.paused = False
        self.speed = 1
        self.last_day_update = pygame.time.get_ticks()
        
        # Reset date system
        self.start_date = datetime(2025, 3, 1)
        self.current_date = self.start_date
        
        # Auto-zoom and center the tiles at game start
        self.auto_zoom_and_center()
    
    def auto_zoom_and_center(self):
        """Auto-zoom and center all tiles to fit nicely on screen at game start"""
        # Calculate the total world size of the grid in pixels
        world_width = GRID_WIDTH * TILE_WIDTH
        world_height = GRID_HEIGHT * TILE_HEIGHT
        
        # Calculate zoom level to fit all tiles with some padding
        padding = 100  # Leave some space around the edges
        zoom_x = (SCREEN_WIDTH - padding) / world_width
        zoom_y = (SCREEN_HEIGHT - padding) / world_height
        
        # Use the smaller zoom to ensure everything fits
        auto_zoom = min(zoom_x, zoom_y, 3.0)  # Cap at 3x for reasonable size
        auto_zoom = max(auto_zoom, self.min_zoom)  # Don't go below minimum
        
        self.zoom_level = auto_zoom
        
        # Center the camera on the middle of the grid
        # For a 3x3 grid, the center tile is at (1, 1)
        # Calculate the screen position of the center tile using isometric conversion
        center_grid_x, center_grid_y = 1, 1  # Center of 3x3 grid
        
        # Calculate where this center tile would appear with no camera offset
        tile_w = int(TILE_WIDTH * self.zoom_level)
        tile_h = int(TILE_HEIGHT * self.zoom_level)
        
        # Isometric conversion for center tile
        center_world_x = (center_grid_x - center_grid_y) * tile_w // 2
        center_world_y = (center_grid_x + center_grid_y) * tile_h // 2
        
        # Position camera so the center tile appears at screen center
        self.camera_x = SCREEN_WIDTH // 2 - center_world_x
        self.camera_y = SCREEN_HEIGHT // 2 - center_world_y
    
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.QUIT:
            return False
        
        # Menu state handling
        if self.game_state == GameState.MENU:
            return self.handle_menu_event(event)
        
        # Options menu
        elif self.game_state == GameState.OPTIONS:
            return self.handle_options_event(event)
        
        # Pause menu
        elif self.game_state == GameState.PAUSE_MENU:
            return self.handle_pause_menu_event(event)
        
        # Interface controls screen (using TUTORIALS state for Options > Interface)
        elif self.game_state == GameState.TUTORIALS:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game_state = GameState.OPTIONS  # Return to options menu
            return True
        
        # Help screen
        elif self.game_state == GameState.HELP:
            return self.handle_help_event(event)
        
        # Farm setup screen
        elif self.game_state == GameState.FARM_SETUP:
            return self.handle_farm_setup_event(event)
        
        # About screen
        elif self.game_state == GameState.ABOUT:
            return self.handle_about_event(event)
        
        # Achievements screen
        elif self.game_state == GameState.ACHIEVEMENTS:
            return self.handle_achievements_event(event)
            
        # Other placeholder screens
        elif self.game_state in [GameState.LOAD]:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game_state = GameState.MENU
            return True
        
        # Game state handling
        elif self.game_state == GameState.GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Go to main menu as requested by user
                    self.game_in_progress = True
                    self.update_menu_options()
                    self.game_state = GameState.MENU
                    return True
                
                # Add keys to pressed set for continuous movement
                self.keys_pressed.add(event.key)
                
                # Game control
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.speed = min(5, self.speed + 1)
                elif event.key == pygame.K_MINUS:
                    self.speed = max(1, self.speed - 1)
                
                # Field Station controls
                elif event.key == pygame.K_a:
                    self.auto_harvest = not self.auto_harvest
                    status = "ON" if self.auto_harvest else "OFF"
                    self.show_message(f"Auto-harvest {status}", GREEN if self.auto_harvest else YELLOW)
                
                # Keyboard shortcuts for actions
                elif event.key == pygame.K_p:
                    if self.selected_tile_pos:
                        x, y = self.selected_tile_pos
                        self.plant_crop(x, y)
                    else:
                        self.show_message("Select a tile first!", YELLOW)
                
                elif event.key == pygame.K_h:
                    if self.selected_tile_pos:
                        x, y = self.selected_tile_pos
                        self.harvest_crop(x, y)
                    else:
                        self.show_message("Select a tile first!", YELLOW)
                
                # Save/Load shortcuts
                elif event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.save_game()
                elif event.key == pygame.K_l and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.load_game()
                
                # Debug mode toggle
                elif event.key == pygame.K_F1:
                    self.debug_mode = not self.debug_mode
                    status = "ON" if self.debug_mode else "OFF"
                    self.show_message(f"Debug mode {status}", YELLOW)
            
            elif event.type == pygame.KEYUP:
                # Remove keys from pressed set when released
                self.keys_pressed.discard(event.key)
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    # Check for UI button clicks first
                    ui_clicked = self.handle_ui_click(mouse_x, mouse_y)
                    
                    if not ui_clicked:
                        # Check if clicking on a tile to open popup
                        grid_pos = self.screen_to_grid(mouse_x, mouse_y)
                        
                        if self.debug_mode:
                            world_x = mouse_x - self.camera_x
                            world_y = mouse_y - self.camera_y
                            self.show_message(f"Click: screen({mouse_x}, {mouse_y}) world({world_x:.1f}, {world_y:.1f}) -> {grid_pos}", WHITE, 3000)
                        
                        if grid_pos:
                            # Open tile popup immediately - like Banished
                            self.open_tile_popup(grid_pos)
                            self.selected_tile_pos = grid_pos  # Also select the tile
                            
                            if self.debug_mode:
                                self.show_message(f"✓ Opened popup for tile {grid_pos}", GREEN, 2000)
                        else:
                            # No tile selected - clicking in dead space is fine
                            if self.debug_mode:
                                self.show_message("Dead space click - no tile selected", YELLOW, 2000)
                                # Clicking on empty area - close popup but don't start dragging yet
                                self.close_tile_popup()
                                self.selected_tile_pos = None
                                
                                if self.debug_mode:
                                    self.show_message("✗ No tile found", YELLOW, 2000)
                        
                        # Set up potential dragging (but don't start yet)
                        self.mouse_down = True
                        self.drag_start = pygame.mouse.get_pos()
                        
                elif event.button == 2:  # Middle mouse - start dragging immediately
                    self.mouse_dragging = True
                    self.drag_start = pygame.mouse.get_pos()
                    
                # Right click removed - harvest available in popup interface
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_down = False
                    self.mouse_dragging = False
                    self.dragging_panel = None  # Stop panel dragging
                elif event.button == 2:
                    self.mouse_dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # Handle panel dragging first
                if self.dragging_panel:
                    panel_data = self.modular_panels[self.dragging_panel]
                    new_x = mouse_x - self.drag_offset[0]
                    new_y = mouse_y - self.drag_offset[1]
                    
                    # Keep panel on screen
                    new_x = max(0, min(SCREEN_WIDTH - panel_data['rect'].width, new_x))
                    new_y = max(0, min(SCREEN_HEIGHT - panel_data['rect'].height, new_y))
                    
                    panel_data['rect'].x = new_x
                    panel_data['rect'].y = new_y
                
                elif self.mouse_dragging:
                    # Pan camera based on mouse movement
                    start_x, start_y = self.drag_start
                    
                    # Update camera position
                    self.camera_x += mouse_x - start_x
                    self.camera_y += mouse_y - start_y
                    
                    # Update drag start for continuous movement
                    self.drag_start = (mouse_x, mouse_y)
                    
                elif self.mouse_down:
                    # Check if we should start dragging based on distance moved
                    start_x, start_y = self.drag_start
                    distance = ((mouse_x - start_x) ** 2 + (mouse_y - start_y) ** 2) ** 0.5
                    
                    if distance > self.drag_threshold:
                        # Start dragging - close any popups first
                        self.close_tile_popup()
                        self.selected_tile_pos = None
                        self.mouse_dragging = True
                        
                else:
                    # Check for tooltip triggers on hover (only when not dragging/clicking)
                    grid_pos = self.screen_to_grid(mouse_x, mouse_y)
                    if grid_pos and not self.tile_popup_active and not self.mouse_down:
                        x, y = grid_pos
                        tile = self.grid[y][x]
                        if tile.crop:
                            full_crop_name = CROP_TYPES[tile.crop].name
                            self.show_tooltip(full_crop_name, (mouse_x, mouse_y))
            
            elif event.type == pygame.MOUSEWHEEL:
                # Mouse wheel zoom
                zoom_factor = 1.1 if event.y > 0 else 1.0 / 1.1
                new_zoom = self.zoom_level * zoom_factor
                
                # Clamp zoom level
                if self.min_zoom <= new_zoom <= self.max_zoom:
                    self.zoom_level = new_zoom
        
        return True
    
    def handle_ui_click(self, mouse_x, mouse_y):
        """Handle clicks on UI elements, returns True if UI was clicked"""
        # Check popup UI first
        if self.tile_popup_active:
            # Check X close button
            if self.popup_close_rect and self.popup_close_rect.collidepoint(mouse_x, mouse_y):
                self.close_tile_popup()
                return True
            
            # Check if clicking inside popup to handle dropdown
            if self.popup_rect and self.popup_rect.collidepoint(mouse_x, mouse_y):
                self.handle_popup_click(mouse_x, mouse_y)
                return True
        
        # Check settings button first
        if hasattr(self, 'settings_button_rect') and self.settings_button_rect and self.settings_button_rect.collidepoint(mouse_x, mouse_y):
            # Open main menu when settings is clicked (user preference)
            self.game_in_progress = True
            self.update_menu_options()
            self.game_state = GameState.MENU
            return True
        
        # UI elements are now directly on the game area (no grey bar)
        # Check if clicking in the UI areas
        
        # Old top-left UI controls REMOVED (now handled by modular speed panel)
        # All pause and speed button clicks now handled in modular panels section
        
        # Check modular UI icons (bottom-right)
        for icon_name, icon_data in self.ui_icons.items():
            icon_rect = pygame.Rect(icon_data['pos'][0] - self.icon_size//2, icon_data['pos'][1] - self.icon_size//2, self.icon_size, self.icon_size)
            if icon_rect.collidepoint(mouse_x, mouse_y):
                if icon_name == 'settings':
                    # Settings goes to main menu
                    self.game_in_progress = True
                    self.update_menu_options()
                    self.game_state = GameState.MENU
                else:
                    # Other icons toggle panels
                    self.toggle_modular_panel(icon_name)
                return True
        
        # Check if clicking on modular panel header for dragging or content for interaction
        for panel_id, panel_data in self.modular_panels.items():
            if panel_data.get('visible', False):
                panel_rect = panel_data['rect']
                
                # Check if clicking anywhere on the panel
                if panel_rect.collidepoint(mouse_x, mouse_y):
                    header_rect = pygame.Rect(panel_rect.x, panel_rect.y, panel_rect.width, 30)
                    
                    # Check header area for dragging/closing
                    if header_rect.collidepoint(mouse_x, mouse_y):
                        # Check close button first
                        close_rect = pygame.Rect(panel_rect.x + panel_rect.width - 25, panel_rect.y + 5, 20, 20)
                        if close_rect.collidepoint(mouse_x, mouse_y):
                            self.close_modular_panel(panel_id)
                        else:
                            # Start dragging
                            self.dragging_panel = panel_id
                            self.drag_offset = (mouse_x - panel_rect.x, mouse_y - panel_rect.y)
                        return True
                    
                    # Check content area for interactive elements
                    elif panel_id == 'speed' and hasattr(self, 'speed_panel_buttons'):
                        for button_id, button_rect in self.speed_panel_buttons.items():
                            if button_rect.collidepoint(mouse_x, mouse_y):
                                if button_id == 'pause':
                                    self.paused = not self.paused
                                elif button_id.startswith('speed_'):
                                    speed_value = int(button_id.split('_')[1])
                                    self.speed = speed_value
                                return True
                    
                    # If we clicked in the panel but didn't handle it, still consume the click
                    return True
        
        return False
    
    def toggle_modular_panel(self, panel_type):
        """Toggle visibility of a modular panel"""
        if panel_type in self.modular_panels:
            # Panel exists, toggle visibility
            self.modular_panels[panel_type]['visible'] = not self.modular_panels[panel_type]['visible']
        else:
            # Create new panel
            self.create_modular_panel(panel_type)
    
    def create_modular_panel(self, panel_type):
        """Create a new modular panel"""
        # Default panel positions (staggered)
        base_x = SCREEN_WIDTH - 320
        base_y = 100 + len(self.modular_panels) * 50
        
        # Panel titles
        titles = {
            'field_study': 'Field Study',
            'resources': 'Resources',
            'speed': 'Speed Controls',
            'help': 'Help & Controls'
        }
        
        panel_data = {
            'type': panel_type,
            'title': titles.get(panel_type, panel_type.title()),
            'visible': True,
            'rect': pygame.Rect(base_x, base_y, 300, 200)  # Default size
        }
        
        # Adjust size based on panel type
        if panel_type == 'field_study':
            panel_data['rect'].height = 150
        elif panel_type == 'resources':
            panel_data['rect'].height = 100
        elif panel_type == 'speed':
            panel_data['rect'].height = 80
        elif panel_type == 'help':
            panel_data['rect'].height = 120
        
        self.modular_panels[panel_type] = panel_data
    
    def close_modular_panel(self, panel_id):
        """Close a modular panel"""
        if panel_id in self.modular_panels:
            self.modular_panels[panel_id]['visible'] = False
    
    def open_tile_popup(self, grid_pos):
        """Open the Banished-style tile popup interface"""
        self.tile_popup_active = True
        self.tile_popup_pos = grid_pos
        self.popup_crop_selection = None  # Nothing selected initially
        self.popup_dropdown_open = False
        
        # Position popup near the clicked tile
        tile_screen_x, tile_screen_y = self.grid_to_screen(grid_pos[0], grid_pos[1])
        popup_width, popup_height = 250, 200
        
        # Adjust position to keep popup on screen
        popup_x = tile_screen_x + 50
        popup_y = tile_screen_y - popup_height // 2
        
        # Keep popup within screen bounds
        popup_x = max(10, min(popup_x, SCREEN_WIDTH - popup_width - 10))
        popup_y = max(10, min(popup_y, SCREEN_HEIGHT - popup_height - 10))
        
        self.popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        # X close button in top right corner
        self.popup_close_rect = pygame.Rect(popup_x + popup_width - 25, popup_y + 5, 20, 20)
        
    def close_tile_popup(self):
        """Close the tile popup interface"""
        self.tile_popup_active = False
        self.tile_popup_pos = None
        self.popup_rect = None
        
    def get_valid_crops_for_season(self):
        """Get list of crops that can be planted in current season"""
        valid_crops = []
        for crop_name, crop_type in CROP_TYPES.items():
            if self.season in crop_type.seasons:
                valid_crops.append(crop_name)
        return valid_crops
    
    def handle_popup_click(self, mouse_x, mouse_y):
        """Handle clicks within the popup"""
        if not self.tile_popup_active or not self.tile_popup_pos:
            return
            
        x, y = self.tile_popup_pos
        tile = self.grid[y][x]
        
        # Check for harvest button click if tile has a crop
        if tile.crop:
            if hasattr(self, 'popup_harvest_button_rect') and self.popup_harvest_button_rect:
                if self.popup_harvest_button_rect.collidepoint(mouse_x, mouse_y):
                    self.harvest_crop(x, y)
                    self.close_tile_popup()
            return
        
        # Check if clicking on dropdown button or dropdown items
        dropdown_x = self.popup_rect.x + 10
        dropdown_y = self.popup_rect.y + 80
        dropdown_width = 200
        dropdown_height = 25
        
        dropdown_button_rect = pygame.Rect(dropdown_x, dropdown_y, dropdown_width, dropdown_height)
        
        if dropdown_button_rect.collidepoint(mouse_x, mouse_y):
            # Toggle dropdown
            self.popup_dropdown_open = not self.popup_dropdown_open
        elif self.popup_dropdown_open:
            # Check if clicking on a dropdown item
            valid_crops = self.get_valid_crops_for_season()
            item_y = dropdown_y + dropdown_height
            for i, crop_name in enumerate(valid_crops):
                item_rect = pygame.Rect(dropdown_x, item_y + i * 25, dropdown_width, 25)
                if item_rect.collidepoint(mouse_x, mouse_y):
                    # Select crop and plant immediately
                    self.popup_crop_selection = crop_name
                    if self.plant_specific_crop(x, y, crop_name):
                        self.close_tile_popup()
                    break
    
    def draw_tile_popup(self):
        """Draw the Banished-style tile popup interface"""
        if not self.tile_popup_active or not self.popup_rect:
            return
            
        # Get the tile being edited
        x, y = self.tile_popup_pos
        tile = self.grid[y][x]
        
        # Draw main popup background
        popup_bg = pygame.Surface((self.popup_rect.width, self.popup_rect.height))
        popup_bg.set_alpha(240)
        popup_bg.fill((60, 60, 60))
        self.screen.blit(popup_bg, self.popup_rect.topleft)
        
        # Draw border
        pygame.draw.rect(self.screen, WHITE, self.popup_rect, 2)
        
        # Draw X close button
        pygame.draw.rect(self.screen, (80, 80, 80), self.popup_close_rect)
        pygame.draw.rect(self.screen, WHITE, self.popup_close_rect, 1)
        # Draw X
        x_offset = 5
        pygame.draw.line(self.screen, WHITE, 
                        (self.popup_close_rect.x + x_offset, self.popup_close_rect.y + x_offset),
                        (self.popup_close_rect.x + self.popup_close_rect.width - x_offset, 
                         self.popup_close_rect.y + self.popup_close_rect.height - x_offset), 2)
        pygame.draw.line(self.screen, WHITE, 
                        (self.popup_close_rect.x + self.popup_close_rect.width - x_offset, 
                         self.popup_close_rect.y + x_offset),
                        (self.popup_close_rect.x + x_offset, 
                         self.popup_close_rect.y + self.popup_close_rect.height - x_offset), 2)
        
        # Draw title
        title = f"Tile ({x}, {y})"
        title_text = self.font.render(title, True, WHITE)
        title_x = self.popup_rect.x + 10
        title_y = self.popup_rect.y + 10
        self.screen.blit(title_text, (title_x, title_y))
        
        # Soil information with color coding (moved from left panel)
        current_y = title_y + 30
        
        # Soil quality
        soil_color = GREEN if tile.soil_quality > 0.7 else YELLOW if tile.soil_quality > 0.4 else RED
        soil_text = self.small_font.render(f"Soil Quality: {tile.soil_quality:.2f}", True, soil_color)
        self.screen.blit(soil_text, (title_x, current_y))
        current_y += 18
        
        # Moisture
        moisture_color = BLUE if tile.moisture > 0.5 else LIGHT_BROWN
        moisture_text = self.small_font.render(f"Moisture: {tile.moisture:.2f}", True, moisture_color)
        self.screen.blit(moisture_text, (title_x, current_y))
        current_y += 18
        
        # Nitrogen
        nitrogen_color = GREEN if tile.nitrogen > 0.5 else YELLOW if tile.nitrogen > 0.3 else RED
        nitrogen_text = self.small_font.render(f"Nitrogen: {tile.nitrogen:.2f}", True, nitrogen_color)
        self.screen.blit(nitrogen_text, (title_x, current_y))
        current_y += 25
        
        # Current crop status
        if tile.crop:
            crop_name = self.get_short_crop_name(tile.crop)
            crop_text = f"Current: {crop_name}"
            progress_text = f"Yield: {int(tile.growth_progress * 100)}%"
        else:
            crop_text = "Current: Empty"
            progress_text = ""
            
        crop_render = self.small_font.render(crop_text, True, WHITE)
        self.screen.blit(crop_render, (title_x, current_y))
        
        if tile.crop and progress_text:
            current_y += 20
            progress_render = self.small_font.render(progress_text, True, WHITE)
            self.screen.blit(progress_render, (title_x, current_y))
            
            # Progress bar
            current_y += 20
            bar_width = 200
            bar_height = 10
            bar_x = title_x
            bar_y = current_y
            
            # Background bar
            pygame.draw.rect(self.screen, (40, 40, 40), 
                           (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, (100, 100, 100), 
                           (bar_x, bar_y, bar_width, bar_height), 1)
            
            # Progress bar
            progress_width = int(bar_width * tile.growth_progress)
            if progress_width > 0:
                bar_color = GREEN if tile.growth_progress >= 1.0 else YELLOW
                pygame.draw.rect(self.screen, bar_color, 
                               (bar_x, bar_y, progress_width, bar_height))
            
            current_y += 25
            
            # Harvest button
            harvest_button_y = current_y
            harvest_button_rect = pygame.Rect(title_x, harvest_button_y, 120, 25)
            
            # Draw harvest button
            if tile.growth_progress >= 1.0:
                button_color = (0, 100, 0)  # Green for ready
                button_text = "Harvest"
                text_color = GREEN
            else:
                button_color = (80, 80, 0)  # Yellow-ish for early
                button_text = f"Harvest ({int(tile.growth_progress * 100)}%)"
                text_color = YELLOW
            
            pygame.draw.rect(self.screen, button_color, harvest_button_rect)
            pygame.draw.rect(self.screen, text_color, harvest_button_rect, 2)
            
            harvest_render = self.small_font.render(button_text, True, WHITE)
            text_x = harvest_button_rect.x + (harvest_button_rect.width - harvest_render.get_width()) // 2
            text_y = harvest_button_rect.y + (harvest_button_rect.height - harvest_render.get_height()) // 2
            self.screen.blit(harvest_render, (text_x, text_y))
            
            # Store button rect for click handling
            self.popup_harvest_button_rect = harvest_button_rect
            
        elif not tile.crop:
            # Dropdown for crop selection
            current_y += 30
            dropdown_label = self.small_font.render("Select Crop:", True, WHITE)
            self.screen.blit(dropdown_label, (title_x, current_y))
            
            current_y += 25
            dropdown_x = title_x
            dropdown_y = current_y
            dropdown_width = 200
            dropdown_height = 25
            
            # Draw dropdown button
            dropdown_bg = (80, 80, 80) if not self.popup_dropdown_open else (100, 100, 100)
            pygame.draw.rect(self.screen, dropdown_bg, 
                           (dropdown_x, dropdown_y, dropdown_width, dropdown_height))
            pygame.draw.rect(self.screen, WHITE, 
                           (dropdown_x, dropdown_y, dropdown_width, dropdown_height), 1)
            
            # Dropdown text
            if self.popup_crop_selection:
                dropdown_text = self.popup_crop_selection.title()
            else:
                dropdown_text = "-- Select --"
            text_render = self.small_font.render(dropdown_text, True, WHITE)
            self.screen.blit(text_render, (dropdown_x + 5, dropdown_y + 5))
            
            # Dropdown arrow
            arrow_x = dropdown_x + dropdown_width - 20
            arrow_y = dropdown_y + dropdown_height // 2
            if self.popup_dropdown_open:
                # Up arrow
                pygame.draw.polygon(self.screen, WHITE, [
                    (arrow_x, arrow_y + 3),
                    (arrow_x + 10, arrow_y + 3),
                    (arrow_x + 5, arrow_y - 3)
                ])
            else:
                # Down arrow
                pygame.draw.polygon(self.screen, WHITE, [
                    (arrow_x, arrow_y - 3),
                    (arrow_x + 10, arrow_y - 3),
                    (arrow_x + 5, arrow_y + 3)
                ])
            
            # Draw dropdown items if open
            if self.popup_dropdown_open:
                valid_crops = self.get_valid_crops_for_season()
                if valid_crops:
                    item_y = dropdown_y + dropdown_height
                    # Draw dropdown background
                    dropdown_menu_height = len(valid_crops) * 25
                    pygame.draw.rect(self.screen, (50, 50, 50), 
                                   (dropdown_x, item_y, dropdown_width, dropdown_menu_height))
                    pygame.draw.rect(self.screen, WHITE, 
                                   (dropdown_x, item_y, dropdown_width, dropdown_menu_height), 1)
                    
                    # Draw each crop option
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for i, crop_name in enumerate(valid_crops):
                        item_rect = pygame.Rect(dropdown_x, item_y + i * 25, dropdown_width, 25)
                        
                        # Highlight on hover
                        if item_rect.collidepoint(mouse_x, mouse_y):
                            pygame.draw.rect(self.screen, (80, 80, 80), item_rect)
                        
                        crop_text = self.get_short_crop_name(crop_name)
                        text_render = self.small_font.render(crop_text, True, WHITE)
                        self.screen.blit(text_render, (dropdown_x + 5, item_y + i * 25 + 5))
                else:
                    # No crops available for this season
                    no_crops = self.small_font.render("No crops for this season", True, RED)
                    self.screen.blit(no_crops, (dropdown_x, dropdown_y + dropdown_height + 5))
    
    def update_camera(self):
        """Update camera position based on held keys"""
        camera_speed = 5  # Pixels per frame
        
        # Fixed directions: W = up (negative Y), S = down (positive Y)
        # A = left (negative X), D = right (positive X)
        if pygame.K_w in self.keys_pressed or pygame.K_UP in self.keys_pressed:
            self.camera_y += camera_speed  # Move view up (camera down)
        if pygame.K_s in self.keys_pressed or pygame.K_DOWN in self.keys_pressed:
            self.camera_y -= camera_speed  # Move view down (camera up)  
        if pygame.K_a in self.keys_pressed or pygame.K_LEFT in self.keys_pressed:
            self.camera_x += camera_speed  # Move view left (camera right)
        if pygame.K_d in self.keys_pressed or pygame.K_RIGHT in self.keys_pressed:
            self.camera_x -= camera_speed  # Move view right (camera left)
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False
            
            # Clear screen - use seasonal background only for active game
            if self.game_state == GameState.GAME:
                self.screen.fill(self.get_seasonal_background_color())
            else:
                # Don't fill with black for menu/options - we'll draw background image
                if self.game_state not in [GameState.MENU, GameState.OPTIONS]:
                    self.screen.fill(BLACK)
            
            # Draw based on current state
            if self.game_state == GameState.MENU:
                self.draw_menu()
            
            elif self.game_state == GameState.FARM_SETUP:
                self.draw_farm_setup()
            
            elif self.game_state == GameState.GAME:
                # Update camera position from held keys
                self.update_camera()
                
                # Update messages
                self.update_messages()
                
                # Update game state
                if not self.paused:
                    current_time = pygame.time.get_ticks()
                    # Day updates based on Banished-style timing but faster for field station
                    # Banished: 1 year = 1 hour, so 1 day = ~1.64 minutes
                    # Field Station: 1 day = 30 seconds at 1x (more natural pacing)
                    base_day_time = 30000  # milliseconds per day at 1x speed  
                    day_update_time = base_day_time / self.speed
                    
                    if current_time - self.last_day_update > day_update_time:
                        self.update_day()
                        self.last_day_update = current_time
                
                # Draw grid
                for row in self.grid:
                    for tile in row:
                        self.draw_tile(tile)
                
                # Draw UI
                self.draw_ui()
                
                # Draw tile popup if active
                self.draw_tile_popup()
                
                # Draw messages last (on top)
                self.draw_messages()
                
                # Draw tooltips (very last)
                self.draw_tooltip()
                
                # Draw debug info if enabled
                if self.debug_mode:
                    self.draw_debug_info()
            
            elif self.game_state == GameState.LOAD:
                self.draw_placeholder_screen("LOAD GAME")
            
            elif self.game_state == GameState.TUTORIALS:
                self.draw_interface_controls()
            
            elif self.game_state == GameState.ACHIEVEMENTS:
                self.draw_achievements_screen()
            
            elif self.game_state == GameState.ABOUT:
                self.draw_about_screen()
            
            elif self.game_state == GameState.OPTIONS:
                self.draw_options_screen()
            
            elif self.game_state == GameState.HELP:
                self.draw_help_screen()
            
            elif self.game_state == GameState.PAUSE_MENU:
                # Draw the game in the background first
                self.screen.fill(self.get_seasonal_background_color())
                self.draw_grid()
                self.draw_ui()
                
                # Then draw pause menu overlay
                self.draw_pause_menu()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = FieldStation()
    game.run()