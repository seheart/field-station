#!/usr/bin/env python3
import pygame
import sys
import math
import random
import os
import json
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple, List

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
        self.farm_location = "Champaign, Illinois, USA"
        self.setup_name_input_active = True  # Start with name input active
        self.setup_location_selection = 0  # Index in available locations
        self.available_locations = [
            "Champaign, Illinois, USA",
            # More locations will be added later
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
    
    def screen_to_grid(self, x, y) -> Optional[Tuple[int, int]]:
        """Convert screen coordinates to grid coordinates - SIMPLIFIED AND ROBUST"""
        # Adjust for camera offset
        world_x = x - self.camera_x
        world_y = y - self.camera_y
        
        # Apply zoom to tile size
        tile_w = TILE_WIDTH * self.zoom_level
        tile_h = TILE_HEIGHT * self.zoom_level
        
        # Isometric coordinate conversion
        # Standard isometric formula: 
        # grid_x = (world_x / tile_w + world_y / tile_h) / 2
        # grid_y = (world_y / tile_h - world_x / tile_w) / 2
        grid_x_float = (world_x / tile_w + world_y / tile_h) / 2
        grid_y_float = (world_y / tile_h - world_x / tile_w) / 2
        
        # Round to nearest grid position for generous clicking
        grid_x = round(grid_x_float)
        grid_y = round(grid_y_float)
        
        # Simple bounds check
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            # MUCH more generous tolerance - if we're close to a valid grid position, accept it
            # This makes clicking much more forgiving
            tolerance = 0.8  # Very generous - almost any click near a tile works
            
            dx = abs(grid_x_float - grid_x)
            dy = abs(grid_y_float - grid_y)
            
            if dx <= tolerance and dy <= tolerance:
                return (grid_x, grid_y)
        
        return None
    
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
                
                # Draw tile bounds (diamond)
                points = [
                    (tile_screen_x, tile_screen_y + tile_h // 2),
                    (tile_screen_x + tile_w // 2, tile_screen_y),
                    (tile_screen_x + tile_w, tile_screen_y + tile_h // 2),
                    (tile_screen_x + tile_w // 2, tile_screen_y + tile_h)
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
            self.farm_location = save_data.get('farm_location', 'Champaign, Illinois, USA')
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
        
        # Options icon
        options_x = SCREEN_WIDTH - 45
        options_y = bar_y + 20
        self.draw_options_icon(options_x, options_y)
    
    def draw_main_area_panels(self):
        """Draw tile info and farm stats panels in main area"""
        # Left side - Tile info (always visible, shows selected or hovered tile)
        display_tile = None
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_pos = self.screen_to_grid(mouse_x, mouse_y)
        
        # Show selected tile or hovered tile
        if hasattr(self, 'selected_tile_pos') and self.selected_tile_pos:
            display_tile = self.selected_tile_pos
        elif grid_pos and mouse_y < SCREEN_HEIGHT - 150:  # Hover tile if no selection
            display_tile = grid_pos
            
        if display_tile:
            x, y = display_tile
            tile = self.grid[y][x]
            
            # Tile info panel with semi-transparent background
            panel_width = 240
            panel_height = 160
            panel_rect = pygame.Rect(20, 100, panel_width, panel_height)
            
            # Draw semi-transparent background
            s = pygame.Surface((panel_width, panel_height))
            s.set_alpha(200)  # Semi-transparent
            s.fill((20, 20, 20))
            self.screen.blit(s, panel_rect)
            pygame.draw.rect(self.screen, WHITE, panel_rect, 1)
            
            # Title with selection indicator
            title_text = f"Tile ({x}, {y})"
            if hasattr(self, 'selected_tile_pos') and self.selected_tile_pos == (x, y):
                title_text += " [SELECTED]"
            title = self.ui_font.render(title_text, True, YELLOW)
            self.screen.blit(title, (panel_rect.x + 10, panel_rect.y + 8))
            
            # Soil info with color coding
            y_pos = panel_rect.y + 32
            soil_color = GREEN if tile.soil_quality > 0.7 else YELLOW if tile.soil_quality > 0.4 else RED
            soil_text = self.font.render(f"Soil: {tile.soil_quality:.2f}", True, soil_color)
            self.screen.blit(soil_text, (panel_rect.x + 10, y_pos))
            
            moisture_color = BLUE if tile.moisture > 0.5 else LIGHT_BROWN
            moisture_text = self.font.render(f"Moisture: {tile.moisture:.2f}", True, moisture_color)
            self.screen.blit(moisture_text, (panel_rect.x + 10, y_pos + 18))
            
            nitrogen_color = GREEN if tile.nitrogen > 0.5 else YELLOW if tile.nitrogen > 0.3 else RED
            nitrogen_text = self.font.render(f"Nitrogen: {tile.nitrogen:.2f}", True, nitrogen_color)
            self.screen.blit(nitrogen_text, (panel_rect.x + 10, y_pos + 36))
            
            # Crop info and action buttons
            if tile.crop:
                crop_name = self.get_short_crop_name(tile.crop)
                crop_text = self.font.render(f"Crop: {crop_name}", True, WHITE)
                self.screen.blit(crop_text, (panel_rect.x + 10, y_pos + 58))
                
                growth_color = GREEN if tile.growth_progress >= 1.0 else YELLOW
                growth_text = self.font.render(f"Growth: {tile.growth_progress:.1%}", True, growth_color)
                self.screen.blit(growth_text, (panel_rect.x + 10, y_pos + 76))
                
                days_text = self.font.render(f"Days: {tile.days_planted}/{crop_type.growth_time}", True, WHITE)
                self.screen.blit(days_text, (panel_rect.x + 10, y_pos + 94))
                
                self.screen.blit(action_btn, (panel_rect.x + 10, y_pos + 112))
            else:
                empty_text = self.font.render("Empty tile", True, GRAY)
                self.screen.blit(empty_text, (panel_rect.x + 10, y_pos + 58))
                
                plant_text = self.font.render("Press P to Plant", True, GREEN)
                self.screen.blit(plant_text, (panel_rect.x + 10, y_pos + 76))
        
        # Right side - Farm stats panel (transparent background)
        stats_width = 200
        stats_height = 140
        stats_rect = pygame.Rect(SCREEN_WIDTH - stats_width - 20, 100, stats_width, stats_height)
        
        # Draw semi-transparent background
        s = pygame.Surface((stats_width, stats_height))
        s.set_alpha(200)  # Semi-transparent
        s.fill((20, 20, 20))
        self.screen.blit(s, stats_rect)
        pygame.draw.rect(self.screen, WHITE, stats_rect, 1)
        
        # Game statistics
        stats_title = self.ui_font.render("Farm Stats", True, YELLOW)
        self.screen.blit(stats_title, (stats_rect.x + 10, stats_rect.y + 8))
        
        y_pos = stats_rect.y + 32
        day_text = self.font.render(f"Day: {self.day}", True, WHITE)
        self.screen.blit(day_text, (stats_rect.x + 10, y_pos))
        
        season_color = {
            Season.SPRING: LIGHT_GREEN,
            Season.SUMMER: YELLOW,
            Season.FALL: (255, 140, 0),  # Orange
            Season.WINTER: WHITE
        }
        season_text = self.font.render(f"Season: {self.season.name.title()}", True, season_color[self.season])
        self.screen.blit(season_text, (stats_rect.x + 10, y_pos + 18))
        
        # Count planted/grown crops
        planted_crops = sum(1 for row in self.grid for tile in row if tile.crop)
        mature_crops = sum(1 for row in self.grid for tile in row if tile.crop and tile.growth_progress >= 1.0)
        
        crops_text = self.font.render(f"Planted: {planted_crops}", True, WHITE)
        self.screen.blit(crops_text, (stats_rect.x + 10, y_pos + 36))
        
        ready_text = self.font.render(f"Ready: {mature_crops}", True, GREEN if mature_crops > 0 else WHITE)
        self.screen.blit(ready_text, (stats_rect.x + 10, y_pos + 54))
        
        # Auto-harvest status
        auto_color = GREEN if self.auto_harvest else GRAY
        auto_text = self.font.render(f"Auto-Harvest: {'ON' if self.auto_harvest else 'OFF'}", True, auto_color)
        self.screen.blit(auto_text, (stats_rect.x + 10, y_pos + 72))
        
        # Market prices panel (bottom left)
        self.draw_market_panel()
    
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
        # Background panel - only bottom panel, no top grey bar
        pygame.draw.rect(self.screen, DARK_GRAY, (0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 150))
        
        # Top left - Speed controls and pause
        x_offset = 10
        y_offset = 15
        
        # Pause button
        pause_color = YELLOW if self.paused else WHITE
        pause_text = "⏸ PAUSED" if self.paused else "⏸ Pause"
        pause_btn = self.font.render(pause_text, True, pause_color)
        self.screen.blit(pause_btn, (x_offset, y_offset))
        pause_width = pause_btn.get_width()
        
        # Speed buttons - based on Banished progression  
        speed_x = x_offset + pause_width + 20
        speeds = [1, 2, 5]  # Banished-like progression
        for i, spd in enumerate(speeds):
            speed_color = YELLOW if self.speed == spd else WHITE
            speed_bg = DARK_GRAY if self.speed != spd else (50, 50, 0)  # Highlight current speed
            
            # Draw button background for easier clicking
            button_rect = pygame.Rect(speed_x + i * 60, y_offset - 2, 55, 25)
            pygame.draw.rect(self.screen, speed_bg, button_rect)
            pygame.draw.rect(self.screen, speed_color, button_rect, 1)
            
            # Speed icons and text
            if spd == 1:
                speed_text = "▶ 1x"
            elif spd == 2:  
                speed_text = "▶▶ 2x"
            else:  # spd == 5
                speed_text = "▶▶▶ 5x"
                
            speed_btn = self.font.render(speed_text, True, speed_color)
            text_rect = speed_btn.get_rect(center=button_rect.center)
            self.screen.blit(speed_btn, text_rect)
        
        # Time indicator circle - sun/globe showing day progress
        circle_x = speed_x + 3 * 60 + 20  # After speed buttons
        circle_y = y_offset + 12  # Center with buttons
        self.draw_time_indicator(circle_x, circle_y)
        
        # Top center - Farm info, date, season, and weather (like Banished layout)
        center_x = SCREEN_WIDTH // 2
        
        # Farm name and location (if set)
        if hasattr(self, 'farm_name') and self.farm_name:
            farm_info = f"{self.farm_name} - {self.farm_location}"
            farm_text = self.ui_font.render(farm_info, True, LIGHT_GREEN)
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
        
        # Bottom bar - organized layout
        self.draw_bottom_bar()
        
        # Settings gear icon in top-right corner
        self.draw_settings_button()
        
        
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
    
    def get_menu_item_rect(self, index):
        """Get the rectangle for a menu item for mouse detection"""
        return pygame.Rect(SCREEN_WIDTH // 2 - 200, 350 + index * 60 - 25, 400, 50)
    
    def draw_menu(self):
        """Draw the main menu"""
        # Title
        title = self.menu_title_font.render("FIELD STATION", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        subtitle = self.ui_font.render("Scientific Field Research Simulation", True, LIGHT_GREEN)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 210))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        mouse_pos = pygame.mouse.get_pos()
        self.draw_menu_options(self.menu_options)
    
    def draw_pause_menu(self):
        """Draw the pause menu with semi-transparent background"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title = self.menu_font.render("GAME PAUSED", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)
        
        # Menu options
        mouse_pos = pygame.mouse.get_pos()
        self.draw_menu_options(self.pause_menu_options)
    
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
    
    def draw_farm_setup(self):
        """Draw the farm setup screen"""
        # Title
        title = self.menu_title_font.render("NEW FARM SETUP", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.ui_font.render("Create your personalized field research experience", True, LIGHT_GREEN)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Farm name section
        name_label = self.menu_font.render("Farm Name:", True, WHITE)
        name_label_rect = name_label.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.screen.blit(name_label, name_label_rect)
        
        # Name input field
        name_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 300, 400, 40)
        if self.setup_name_input_active:
            pygame.draw.rect(self.screen, (60, 60, 60), name_rect)
            pygame.draw.rect(self.screen, YELLOW, name_rect, 3)
        else:
            pygame.draw.rect(self.screen, (40, 40, 40), name_rect)
            pygame.draw.rect(self.screen, GRAY, name_rect, 2)
        
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
            placeholder = self.font.render("Enter your farm name...", True, GRAY)
            placeholder_rect = placeholder.get_rect(left=name_rect.left + 10, centery=name_rect.centery)
            self.screen.blit(placeholder, placeholder_rect)
        
        # Location section
        location_label = self.menu_font.render("Location:", True, WHITE)
        location_label_rect = location_label.get_rect(center=(SCREEN_WIDTH // 2, 370))
        self.screen.blit(location_label, location_label_rect)
        
        # Location options
        for i, location in enumerate(self.available_locations):
            y_pos = 400 + i * 50
            location_rect = pygame.Rect(SCREEN_WIDTH // 2 - 300, y_pos, 600, 40)
            
            if i == self.setup_location_selection and not self.setup_name_input_active:
                pygame.draw.rect(self.screen, (60, 60, 60), location_rect)
                pygame.draw.rect(self.screen, YELLOW, location_rect, 3)
                prefix = "> "
                color = YELLOW
            else:
                pygame.draw.rect(self.screen, (30, 30, 30), location_rect)
                pygame.draw.rect(self.screen, GRAY, location_rect, 1)
                prefix = "  "
                color = WHITE
            
            location_text = self.font.render(prefix + location, True, color)
            location_text_rect = location_text.get_rect(left=location_rect.left + 10, centery=location_rect.centery)
            self.screen.blit(location_text, location_text_rect)
        
        # Start Game button
        start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 600, 200, 50)
        can_start = bool(self.farm_name.strip())
        
        if can_start:
            pygame.draw.rect(self.screen, (0, 100, 0), start_button_rect)
            pygame.draw.rect(self.screen, GREEN, start_button_rect, 2)
            button_color = WHITE
        else:
            pygame.draw.rect(self.screen, (50, 50, 50), start_button_rect)
            pygame.draw.rect(self.screen, GRAY, start_button_rect, 2)
            button_color = GRAY
        
        start_text = self.menu_font.render("START GAME", True, button_color)
        start_text_rect = start_text.get_rect(center=start_button_rect.center)
        self.screen.blit(start_text, start_text_rect)
        
        # Instructions
        if self.setup_name_input_active:
            instructions = self.small_font.render("Type your farm name, then press ENTER/TAB to continue", True, LIGHT_GREEN)
        else:
            instructions = self.small_font.render("Use arrow keys to select location, ENTER to start game", True, LIGHT_GREEN)
        
        inst_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, 700))
        self.screen.blit(instructions, inst_rect)
        
        # Back instruction
        back_text = self.small_font.render("ESC - Back to Main Menu", True, GRAY)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, 730))
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
        """Draw the options menu"""
        title = self.menu_title_font.render("OPTIONS", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Options items
        mouse_pos = pygame.mouse.get_pos()
        for i, (option_name, option_func) in enumerate(self.options_items):
            y_pos = 300 + i * 80
            
            # Create clickable rectangle
            option_rect = pygame.Rect(SCREEN_WIDTH // 2 - 300, y_pos - 30, 600, 60)
            
            # Mouse hover detection
            if option_rect.collidepoint(mouse_pos):
                self.options_selection = i
            
            # Highlight selected option
            if i == self.options_selection:
                pygame.draw.rect(self.screen, (40, 40, 40), option_rect)
                color = YELLOW
                prefix = "> "
            else:
                color = WHITE
                prefix = "  "
            
            # Special handling for options with status
            if option_name == "Fullscreen":
                status = "ON" if self.fullscreen else "OFF"
                display_text = f"{prefix}{option_name}: {status}"
            elif option_name == "Monitor":
                current_monitor = self.available_displays[self.current_display] if self.current_display < len(self.available_displays) else "Unknown"
                display_text = f"{prefix}{option_name}: {current_monitor}"
            else:
                display_text = f"{prefix}{option_name}"
            
            text = self.menu_font.render(display_text, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            self.screen.blit(text, text_rect)
        
        # Instructions
        instructions = self.font.render("Use arrow keys or mouse to select, ENTER or click to activate", True, GRAY)
        inst_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        self.screen.blit(instructions, inst_rect)
    
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
            self.menu_options = ["Continue Game", "Save Game", "New Game", "Load Game", "Tutorials", "Achievements", "Options", "Exit"]
        else:
            self.menu_options = ["New Game", "Load Game", "Tutorials", "Achievements", "Options", "Exit"]
    
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
            ("Interface", lambda: self.show_interface_controls()),
            ("Help", lambda: self.show_help()),
        ])
        
        # Add appropriate back option based on where we came from
        if self.previous_game_state == GameState.GAME:
            self.options_items.append(("Back to Game", lambda: self.return_to_game()))
        else:
            self.options_items.append(("Back to Menu", lambda: self.return_to_menu()))
    
    def cycle_display(self):
        """Cycle to the next available display"""
        self.current_display = (self.current_display + 1) % len(self.available_displays)
        self.create_window()
    
    def show_interface_controls(self):
        """Show the interface controls screen"""
        self.game_state = GameState.TUTORIALS  # Reuse tutorials state for interface screen
    
    def show_help(self):
        """Show the help screen"""
        self.game_state = GameState.HELP
    
    def draw_interface_controls(self):
        """Draw the interface controls screen"""
        title = self.menu_title_font.render("INTERFACE CONTROLS", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw controls list
        y_start = 180
        for i, control_line in enumerate(self.interface_controls):
            if control_line == "":
                continue  # Skip empty lines for spacing
            
            # Different colors for headers and controls
            if control_line.endswith(":"):
                color = YELLOW
                font = self.ui_font
            elif control_line.startswith("  "):
                color = WHITE
                font = self.font
            else:
                color = LIGHT_GREEN
                font = self.ui_font
            
            text = font.render(control_line, True, color)
            self.screen.blit(text, (100, y_start + i * 25))
        
        # Instructions
        instructions = self.font.render("Press ESC to return to Options menu", True, GRAY)
        inst_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(instructions, inst_rect)
    
    def draw_help_screen(self):
        """Draw the help screen"""
        title = self.menu_title_font.render("HELP & TUTORIAL", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Draw help content in two columns for better space usage
        left_column = []
        right_column = []
        current_col = left_column
        
        for line in self.help_content:
            if line.startswith("TIPS:"):
                current_col = right_column
            current_col.append(line)
        
        # Draw left column
        y_start = 140
        for i, line in enumerate(left_column):
            if line == "":
                continue
                
            if line.endswith(":"):
                color = YELLOW
                font = self.ui_font
            elif line.startswith("  •"):
                color = WHITE
                font = self.font
            else:
                color = LIGHT_GREEN
                font = self.font
            
            text = font.render(line, True, color)
            self.screen.blit(text, (50, y_start + i * 22))
        
        # Draw right column
        for i, line in enumerate(right_column):
            if line == "":
                continue
                
            if line.endswith(":"):
                color = YELLOW
                font = self.ui_font
            elif line.startswith("  •"):
                color = WHITE
                font = self.font
            else:
                color = LIGHT_GREEN
                font = self.font
            
            text = font.render(line, True, color)
            self.screen.blit(text, (SCREEN_WIDTH // 2 + 50, y_start + i * 22))
        
        # Instructions
        instructions = self.font.render("Press ESC to return to Options menu", True, GRAY)
        inst_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(instructions, inst_rect)
    
    def return_to_game(self):
        """Return to the game"""
        self.game_state = GameState.GAME
        self.previous_game_state = None
    
    def return_to_menu(self):
        """Return to main menu"""
        self.game_state = GameState.MENU
        self.previous_game_state = None
    
    def handle_options_event(self, event):
        """Handle events in the options menu"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_state = GameState.MENU
            elif event.key == pygame.K_UP:
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
                    y_pos = 300 + i * 80
                    option_rect = pygame.Rect(SCREEN_WIDTH // 2 - 300, y_pos - 30, 600, 60)
                    if option_rect.collidepoint(mouse_pos):
                        self.options_selection = i
                        option_func()
                        break
        
        return True
    
    def handle_farm_setup_event(self, event):
        """Handle events in the garden setup screen"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_state = GameState.MENU
                return True
            
            if self.setup_name_input_active:
                # Handle text input for farm name
                if event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                    # Move to location selection
                    self.setup_name_input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.farm_name = self.farm_name[:-1]
                else:
                    # Add character if it's printable
                    if len(event.unicode) == 1 and event.unicode.isprintable():
                        if len(self.farm_name) < 30:  # Limit name length
                            self.farm_name += event.unicode
            else:
                # Handle location selection
                if event.key == pygame.K_UP:
                    self.setup_location_selection = (self.setup_location_selection - 1) % len(self.available_locations)
                elif event.key == pygame.K_DOWN:
                    self.setup_location_selection = (self.setup_location_selection + 1) % len(self.available_locations)
                elif event.key == pygame.K_RETURN:
                    # Start the game with selected settings
                    self.start_new_game_with_setup()
                elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_TAB:
                    # Go back to name input
                    self.setup_name_input_active = True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if clicking on name input field
                name_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 300, 400, 40)
                if name_rect.collidepoint(mouse_pos):
                    self.setup_name_input_active = True
                
                # Check if clicking on location options
                elif not self.setup_name_input_active:
                    for i, location in enumerate(self.available_locations):
                        location_rect = pygame.Rect(SCREEN_WIDTH // 2 - 300, 400 + i * 50, 600, 40)
                        if location_rect.collidepoint(mouse_pos):
                            self.setup_location_selection = i
                            break
                
                # Check if clicking on Start Game button
                start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 600, 200, 50)
                if start_button_rect.collidepoint(mouse_pos) and self.farm_name.strip():
                    self.start_new_game_with_setup()
        
        return True
    
    def start_new_game_with_setup(self):
        """Start a new game with the chosen farm setup"""
        if not self.farm_name.strip():
            return  # Don't start without a name
        
        self.farm_location = self.available_locations[self.setup_location_selection]
        self.game_state = GameState.GAME
        self.reset_game()
        self.apply_location_settings()
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
    
    def handle_menu_event(self, event):
        """Handle events in the menu"""
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
                for i in range(len(self.menu_options)):
                    if self.get_menu_item_rect(i).collidepoint(mouse_pos):
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
                return self.activate_pause_menu_item()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                for i in range(len(self.pause_menu_options)):
                    if self.get_menu_item_rect(i).collidepoint(mouse_pos):
                        self.menu_selection = i
                        return self.activate_pause_menu_item()
        
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
        elif selected == "Tutorials":
            self.game_state = GameState.TUTORIALS
        elif selected == "Achievements":
            self.game_state = GameState.ACHIEVEMENTS
        elif selected == "Options":
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
        # Calculate the center point of the grid in world coordinates
        center_x = (GRID_WIDTH - 1) * TILE_WIDTH // 2
        center_y = (GRID_HEIGHT - 1) * TILE_HEIGHT // 2
        
        # Position camera so grid center appears at screen center
        self.camera_x = SCREEN_WIDTH // 2 - center_x * self.zoom_level
        self.camera_y = SCREEN_HEIGHT // 2 - center_y * self.zoom_level
    
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
        
        # Interface controls screen (using TUTORIALS state)
        elif self.game_state == GameState.TUTORIALS:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game_state = GameState.OPTIONS  # Return to options, not main menu
            return True
        
        # Help screen
        elif self.game_state == GameState.HELP:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game_state = GameState.OPTIONS  # Return to options, not main menu
            return True
        
        # Farm setup screen
        elif self.game_state == GameState.FARM_SETUP:
            return self.handle_farm_setup_event(event)
        
        # Other placeholder screens
        elif self.game_state in [GameState.LOAD, GameState.ACHIEVEMENTS]:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game_state = GameState.MENU
            return True
        
        # Game state handling
        elif self.game_state == GameState.GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Go to pause menu instead of main menu for better UX
                    self.game_in_progress = True
                    self.previous_game_state = GameState.GAME
                    self.game_state = GameState.PAUSE_MENU
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
                            # Try a backup method - brute force check all tiles
                            backup_tile = self.find_closest_tile(mouse_x, mouse_y)
                            if backup_tile:
                                self.open_tile_popup(backup_tile)
                                self.selected_tile_pos = backup_tile
                                if self.debug_mode:
                                    self.show_message(f"✓ Backup method found tile {backup_tile}", GREEN, 2000)
                            else:
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
                elif event.button == 2:
                    self.mouse_dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                if self.mouse_dragging:
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
            # Open pause menu when settings is clicked
            self.game_in_progress = True
            self.previous_game_state = GameState.GAME
            self.game_state = GameState.PAUSE_MENU
            return True
        
        # UI elements are now directly on the game area (no grey bar)
        # Check if clicking in the UI areas
        
        # Pause button area
        x_offset = 10
        y_offset = 15
        pause_rect = pygame.Rect(x_offset, y_offset, 80, 25)
        
        if pause_rect.collidepoint(mouse_x, mouse_y):
            self.paused = not self.paused
            return True
        
        # Speed buttons - match the drawing layout
        pause_width = 80  # Approximate pause button width
        speed_x = x_offset + pause_width + 20
        speeds = [1, 2, 5]  # Banished-like progression
        for i, spd in enumerate(speeds):
            button_rect = pygame.Rect(speed_x + i * 60, y_offset - 2, 55, 25)
            if button_rect.collidepoint(mouse_x, mouse_y):
                self.speed = spd
                return True
        
        # Options icon click (bottom right)
        options_x = SCREEN_WIDTH - 45
        options_y = SCREEN_HEIGHT - 130
        options_rect = pygame.Rect(options_x, options_y, 24, 24)
        if options_rect.collidepoint(mouse_x, mouse_y):
            self.previous_game_state = GameState.GAME
            self.game_state = GameState.OPTIONS
            self.update_options_items()  # Refresh options to show "Back to Game"
            return True
        
        return False
    
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
        
        # Current crop status
        current_y = title_y + 30
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
            
            # Clear screen
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
                self.draw_placeholder_screen("ACHIEVEMENTS")
            
            elif self.game_state == GameState.OPTIONS:
                self.draw_options_screen()
            
            elif self.game_state == GameState.HELP:
                self.draw_help_screen()
            
            elif self.game_state == GameState.PAUSE_MENU:
                # Draw the game in the background first
                self.screen.fill(BLACK)
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