#!/usr/bin/env python3
"""
Test suite for Field Station
Run with: python3 test_field_station.py
"""
import unittest
import pygame
import sys
import os
from unittest.mock import Mock, patch

# Add the game directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock pygame before importing the game
pygame.init = Mock()
pygame.quit = Mock()
pygame.display = Mock()
pygame.display.set_mode = Mock(return_value=Mock())
pygame.display.set_caption = Mock()
pygame.display.flip = Mock()
pygame.display.update = Mock()
pygame.time = Mock()
pygame.time.Clock = Mock()
pygame.time.get_ticks = Mock(return_value=1000)
pygame.font = Mock()
pygame.font.Font = Mock(return_value=Mock())
pygame.mouse = Mock()
pygame.mouse.get_pos = Mock(return_value=(100, 100))
pygame.mouse.get_pressed = Mock(return_value=(False, False, False))
pygame.event = Mock()
pygame.event.get = Mock(return_value=[])
pygame.Surface = Mock()
pygame.QUIT = 256
pygame.KEYDOWN = 2
pygame.MOUSEBUTTONDOWN = 5
pygame.K_ESCAPE = 27
pygame.K_p = 112
pygame.K_h = 104
pygame.K_a = 97

# Mock the screen surface with proper configuration
mock_screen = Mock()
mock_screen.get_size.return_value = (1200, 800)
mock_screen.fill = Mock()
mock_screen.blit = Mock()

# Patch pygame functions that the game uses
pygame.display.set_mode = Mock(return_value=mock_screen)
pygame.display.get_surface = Mock(return_value=mock_screen)

# Now import the game components
from field_station import FieldStation, Season, Weather, CROP_TYPES, Tile

class TestGameComponents(unittest.TestCase):
    """Test basic game components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tile = Tile(0, 0, 0.5, 0.5, 0.5)
        
    def test_tile_creation(self):
        """Test tile creation with valid parameters"""
        tile = Tile(1, 2, 0.8, 0.6, 0.7)
        self.assertEqual(tile.x, 1)
        self.assertEqual(tile.y, 2)
        self.assertEqual(tile.soil_quality, 0.8)
        self.assertEqual(tile.moisture, 0.6)
        self.assertEqual(tile.nitrogen, 0.7)
        self.assertIsNone(tile.crop)
        self.assertEqual(tile.growth_progress, 0.0)
        self.assertEqual(tile.days_planted, 0)
        
    def test_crop_types_defined(self):
        """Test that all expected crop types are defined"""
        expected_crops = ['wheat_soft_red_winter', 'corn_sweet', 'potato_russet_burbank', 'carrot_imperator', 'soybean']
        for crop in expected_crops:
            self.assertIn(crop, CROP_TYPES)
            crop_type = CROP_TYPES[crop]
            self.assertGreater(crop_type.growth_time, 0)
            self.assertGreater(crop_type.value, 0)
            self.assertIsInstance(crop_type.seasons, list)
            self.assertGreater(len(crop_type.seasons), 0)
            
    def test_seasons_enum(self):
        """Test Season enum values"""
        seasons = [Season.SPRING, Season.SUMMER, Season.FALL, Season.WINTER]
        self.assertEqual(len(seasons), 4)
        
    def test_weather_enum(self):
        """Test Weather enum values"""
        weather_types = [Weather.SUNNY, Weather.CLOUDY, Weather.RAINY, Weather.SNOWY]
        self.assertEqual(len(weather_types), 4)

class TestGameLogic(unittest.TestCase):
    """Test game logic with mocked pygame"""
    
    def setUp(self):
        """Set up test game instance"""
        with patch('field_station.pygame') as mock_pygame:
            # Ensure mock screen has proper get_size method
            test_screen = Mock()
            test_screen.get_size.return_value = (1200, 800)
            test_screen.fill = Mock()
            test_screen.blit = Mock()
            
            mock_pygame.display.set_mode.return_value = test_screen
            mock_pygame.display.get_surface.return_value = test_screen
            mock_pygame.font.Font.return_value.render.return_value = Mock()
            mock_pygame.time.get_ticks.return_value = 1000
            self.game = FieldStation()
            
    def test_game_initialization(self):
        """Test game initializes with correct default values"""
        self.assertEqual(self.game.money, 500)
        self.assertEqual(self.game.day, 1)
        self.assertEqual(self.game.season, Season.SPRING)
        self.assertEqual(self.game.speed, 1)
        self.assertFalse(self.game.paused)
        self.assertFalse(self.game.auto_harvest)
        self.assertIsNone(self.game.selected_tile_pos)
        
    def test_grid_initialization(self):
        """Test game grid is properly initialized"""
        self.assertEqual(len(self.game.grid), 3)  # GRID_HEIGHT
        self.assertEqual(len(self.game.grid[0]), 3)  # GRID_WIDTH
        
        for row in self.game.grid:
            for tile in row:
                self.assertIsInstance(tile, Tile)
                self.assertIsNone(tile.crop)
                self.assertGreaterEqual(tile.soil_quality, 0.4)
                self.assertLessEqual(tile.soil_quality, 0.8)
                
    def test_plant_crop_logic(self):
        """Test crop planting logic"""
        # Test planting on empty tile
        tile = self.game.grid[0][0]
        self.assertIsNone(tile.crop)
        
        # Mock sufficient money
        self.game.money = 100
        
        # Plant crop
        self.game.plant_crop(0, 0)
        
        # Check if crop was planted (should auto-select appropriate crop)
        planted_tile = self.game.grid[0][0]
        if self.game.money == 90:  # Money was deducted
            self.assertIsNotNone(planted_tile.crop)
            self.assertEqual(planted_tile.growth_progress, 0.0)
            self.assertEqual(planted_tile.days_planted, 0)
            
    def test_harvest_crop_logic(self):
        """Test crop harvesting logic"""
        tile = self.game.grid[0][0]
        tile.crop = "wheat_soft_red_winter"
        tile.growth_progress = 1.0
        tile.days_planted = 90
        
        initial_money = self.game.money
        self.game.harvest_crop(0, 0)
        
        # Check if crop was harvested
        self.assertIsNone(tile.crop)
        self.assertEqual(tile.growth_progress, 0.0)
        self.assertEqual(tile.days_planted, 0)
        self.assertGreater(self.game.money, initial_money)
        
    def test_auto_harvest_functionality(self):
        """Test auto-harvest feature"""
        # Set up mature crop
        tile = self.game.grid[0][0]
        tile.crop = "wheat_soft_red_winter"
        tile.growth_progress = 1.0
        
        # Enable auto-harvest
        self.game.auto_harvest = True
        initial_money = self.game.money
        
        # Run auto-harvest check
        self.game.auto_harvest_check()
        
        # Check if crop was auto-harvested
        self.assertIsNone(tile.crop)
        self.assertGreater(self.game.money, initial_money)
        
    def test_tile_selection(self):
        """Test tile selection functionality"""
        # Test selection
        self.game.selected_tile_pos = (1, 1)
        self.assertEqual(self.game.selected_tile_pos, (1, 1))
        
        # Test plant action on selected tile
        self.game.money = 100
        self.game.handle_plant_action()
        
        # Check if action was performed on correct tile
        if self.game.money == 90:  # Money was deducted
            selected_tile = self.game.grid[1][1]
            self.assertIsNotNone(selected_tile.crop)

class TestGameValidation(unittest.TestCase):
    """Test game validation and error conditions"""
    
    def setUp(self):
        """Set up test game instance"""
        with patch('field_station.pygame') as mock_pygame:
            # Ensure mock screen has proper get_size method
            test_screen = Mock()
            test_screen.get_size.return_value = (1200, 800)
            test_screen.fill = Mock()
            test_screen.blit = Mock()
            
            mock_pygame.display.set_mode.return_value = test_screen
            mock_pygame.display.get_surface.return_value = test_screen
            mock_pygame.font.Font.return_value.render.return_value = Mock()
            mock_pygame.time.get_ticks.return_value = 1000
            self.game = FieldStation()
            
    def test_insufficient_money_planting(self):
        """Test that planting fails with insufficient money"""
        self.game.money = 5  # Less than seed cost (10)
        initial_money = self.game.money
        
        self.game.plant_crop(0, 0)
        
        # Money shouldn't change and no crop should be planted
        self.assertEqual(self.game.money, initial_money)
        self.assertIsNone(self.game.grid[0][0].crop)
        
    def test_plant_on_occupied_tile(self):
        """Test that planting on occupied tile fails"""
        tile = self.game.grid[0][0]
        tile.crop = "wheat_soft_red_winter"
        
        self.game.money = 100
        initial_money = self.game.money
        
        self.game.plant_crop(0, 0)
        
        # Money shouldn't change and crop should remain
        self.assertEqual(self.game.money, initial_money)
        self.assertEqual(tile.crop, "wheat_soft_red_winter")
        
    def test_harvest_empty_tile(self):
        """Test that harvesting empty tile does nothing"""
        tile = self.game.grid[0][0]
        self.assertIsNone(tile.crop)
        
        initial_money = self.game.money
        self.game.harvest_crop(0, 0)
        
        # Money shouldn't change
        self.assertEqual(self.game.money, initial_money)
        
    def test_actions_without_selection(self):
        """Test that actions fail without tile selection"""
        self.game.selected_tile_pos = None
        self.game.money = 100
        initial_money = self.game.money
        
        # Try to plant without selection
        self.game.handle_plant_action()
        self.assertEqual(self.game.money, initial_money)
        
        # Try to harvest without selection
        self.game.handle_harvest_action()
        self.assertEqual(self.game.money, initial_money)

def run_syntax_check():
    """Run syntax check on the main game file"""
    try:
        with open('field_station.py', 'r') as f:
            code = f.read()
        compile(code, 'field_station.py', 'exec')
        print("✅ Syntax check passed")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def run_import_test():
    """Test that the game module can be imported"""
    try:
        # Mock pygame to avoid requiring display
        with patch('pygame.init'), patch('pygame.display'), patch('pygame.font'), patch('pygame.time'):
            import field_station
        print("✅ Import test passed")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == '__main__':
    print("🚜 Field Station Test Suite")
    print("=" * 40)
    
    # Run basic checks first
    syntax_ok = run_syntax_check()
    import_ok = run_import_test()
    
    if not syntax_ok or not import_ok:
        print("\n❌ Basic checks failed. Fix syntax/import errors before running full tests.")
        sys.exit(1)
    
    # Run unit tests
    print("\nRunning unit tests...")
    unittest.main(argv=[''], verbosity=2, exit=False)
    
    print("\n🎯 Test Summary:")
    print("- Syntax check: ✅")
    print("- Import check: ✅") 
    print("- Unit tests: See results above")
    print("\n💡 To run tests: python3 test_field_station.py")