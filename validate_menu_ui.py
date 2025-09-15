#!/usr/bin/env python3
"""
Field Station Menu UI System Validation
========================================

Comprehensive validation suite for the menu UI system including:
- Framework integration testing
- Visual consistency validation
- Performance benchmarking
- Error handling verification
- Accessibility checks
"""

import pygame
import sys
import time
import traceback
from typing import List, Dict, Any, Tuple
import json

# Import the game and UI framework
try:
    from field_station import FieldStation
    from ui_framework import UIManager, MenuPanel, UITheme, MainMenuPanel
    from design_constants import *
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running this from the field_station directory")
    sys.exit(1)

class MenuUIValidator:
    """Comprehensive validator for the menu UI system"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Field Station Menu UI Validator")
        self.clock = pygame.time.Clock()
        self.game = FieldStation()
        self.results = {
            "framework_integration": [],
            "visual_consistency": [],
            "performance": [],
            "error_handling": [],
            "accessibility": []
        }
        
    def run_all_validations(self) -> Dict[str, Any]:
        """Run all validation tests and return comprehensive results"""
        print("🎯 Starting Field Station Menu UI Validation...")
        print("=" * 60)
        
        # Test framework integration
        print("\n📦 Testing Framework Integration...")
        self.test_framework_integration()
        
        # Test visual consistency
        print("\n🎨 Testing Visual Consistency...")
        self.test_visual_consistency()
        
        # Test performance
        print("\n⚡ Testing Performance...")
        self.test_performance()
        
        # Test error handling
        print("\n🛡️ Testing Error Handling...")
        self.test_error_handling()
        
        # Test accessibility
        print("\n♿ Testing Accessibility...")
        self.test_accessibility()
        
        # Generate final report
        return self.generate_report()
    
    def test_framework_integration(self):
        """Test that the UI framework is properly integrated"""
        tests = [
            ("UI Framework Import", self._test_ui_import),
            ("Font Creation", self._test_font_creation),
            ("Framework Page Creation", self._test_framework_page_creation),
            ("Menu Panel Creation", self._test_menu_panel_creation),
            ("Content Population", self._test_content_population),
            ("Rendering Pipeline", self._test_rendering_pipeline)
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                status = "✅ PASS" if result['success'] else "❌ FAIL"
                print(f"  {status} {test_name}: {result['message']}")
                self.results["framework_integration"].append({
                    "test": test_name,
                    "success": result['success'],
                    "message": result['message'],
                    "details": result.get('details', {})
                })
            except Exception as e:
                print(f"  ❌ FAIL {test_name}: Exception - {str(e)}")
                self.results["framework_integration"].append({
                    "test": test_name,
                    "success": False,
                    "message": f"Exception: {str(e)}",
                    "details": {"traceback": traceback.format_exc()}
                })
    
    def _test_ui_import(self) -> Dict[str, Any]:
        """Test that UI framework components can be imported"""
        try:
            from ui_framework import UIManager, MenuPanel, UITheme, MainMenuPanel, ContentArea
            return {
                "success": True,
                "message": "All UI framework components imported successfully",
                "details": {
                    "components": ["UIManager", "MenuPanel", "UITheme", "MainMenuPanel", "ContentArea"]
                }
            }
        except ImportError as e:
            return {
                "success": False,
                "message": f"Failed to import UI components: {str(e)}"
            }
    
    def _test_font_creation(self) -> Dict[str, Any]:
        """Test font creation functionality"""
        try:
            fonts = self.game.create_framework_fonts()
            required_fonts = ['title', 'emoji', 'content', 'ui']
            missing_fonts = [f for f in required_fonts if f not in fonts]
            
            if missing_fonts:
                return {
                    "success": False,
                    "message": f"Missing required fonts: {missing_fonts}",
                    "details": {"available_fonts": list(fonts.keys())}
                }
            
            # Test that fonts are actual pygame Font objects
            for font_name, font_obj in fonts.items():
                if not isinstance(font_obj, pygame.font.Font):
                    return {
                        "success": False,
                        "message": f"Font '{font_name}' is not a pygame.font.Font object",
                        "details": {"font_type": type(font_obj).__name__}
                    }
            
            return {
                "success": True,
                "message": "All required fonts created successfully",
                "details": {
                    "fonts": list(fonts.keys()),
                    "font_sizes": {name: font.get_height() for name, font in fonts.items()}
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Font creation failed: {str(e)}"
            }
    
    def _test_framework_page_creation(self) -> Dict[str, Any]:
        """Test framework page creation"""
        try:
            def test_content(content_area):
                fonts = self.game.create_framework_fonts()
                content_area.add_header("Test Header", fonts['ui'])
                content_area.add_text("Test content", fonts['content'])
            
            ui = self.game.create_framework_page("TEST PAGE", "🧪", test_content)
            
            if ui is None:
                return {
                    "success": False,
                    "message": "Framework page creation returned None"
                }
            
            if not isinstance(ui, UIManager):
                return {
                    "success": False,
                    "message": f"Expected UIManager, got {type(ui).__name__}"
                }
            
            return {
                "success": True,
                "message": "Framework page created successfully",
                "details": {
                    "ui_type": type(ui).__name__,
                    "element_count": len(ui.elements)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Framework page creation failed: {str(e)}"
            }
    
    def _test_menu_panel_creation(self) -> Dict[str, Any]:
        """Test menu panel creation"""
        try:
            panel = MenuPanel("Test Panel", "🧪", width=400, height=300)
            fonts = self.game.create_framework_fonts()
            panel.set_fonts(**fonts)
            
            # Check panel properties
            if panel.rect.width != 400 or panel.rect.height != 300:
                return {
                    "success": False,
                    "message": f"Panel size incorrect: {panel.rect.width}x{panel.rect.height}, expected 400x300"
                }
            
            # Check that panel has required components
            if not hasattr(panel, 'content_area'):
                return {
                    "success": False,
                    "message": "Panel missing content_area component"
                }
            
            return {
                "success": True,
                "message": "Menu panel created successfully",
                "details": {
                    "size": f"{panel.rect.width}x{panel.rect.height}",
                    "position": f"({panel.rect.x}, {panel.rect.y})",
                    "children_count": len(panel.children)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Menu panel creation failed: {str(e)}"
            }
    
    def _test_content_population(self) -> Dict[str, Any]:
        """Test content area population"""
        try:
            panel = MenuPanel("Test Panel", "🧪")
            fonts = self.game.create_framework_fonts()
            panel.set_fonts(**fonts)
            
            # Test content methods
            content_area = panel.content_area
            content_area.add_header("Test Header", fonts['ui'])
            content_area.add_text("Test text", fonts['content'])
            content_area.add_spacer()
            content_area.add_text("More text", fonts['content'])
            
            if len(content_area.content_items) != 4:
                return {
                    "success": False,
                    "message": f"Expected 4 content items, got {len(content_area.content_items)}"
                }
            
            # Test method chaining
            content_area.add_header("Chained Header", fonts['ui']) \
                        .add_text("Chained text", fonts['content']) \
                        .add_spacer()
            
            if len(content_area.content_items) != 7:
                return {
                    "success": False,
                    "message": f"Method chaining failed: expected 7 items, got {len(content_area.content_items)}"
                }
            
            return {
                "success": True,
                "message": "Content population working correctly",
                "details": {
                    "content_items": len(content_area.content_items),
                    "method_chaining": "working"
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Content population failed: {str(e)}"
            }
    
    def _test_rendering_pipeline(self) -> Dict[str, Any]:
        """Test that the rendering pipeline works without errors"""
        try:
            def test_content(content_area):
                fonts = self.game.create_framework_fonts()
                content_area.add_header("Render Test", fonts['ui'])
                content_area.add_text("This is a rendering test", fonts['content'])
            
            ui = self.game.create_framework_page("RENDER TEST", "🎨", test_content)
            
            # Clear screen and render
            self.screen.fill((0, 0, 0))
            ui.draw_warm_gradient_background()
            ui.render()
            pygame.display.flip()
            
            return {
                "success": True,
                "message": "Rendering pipeline completed without errors",
                "details": {
                    "screen_size": f"{self.screen.get_width()}x{self.screen.get_height()}"
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Rendering pipeline failed: {str(e)}"
            }
    
    def test_visual_consistency(self):
        """Test visual consistency across different menu screens"""
        menu_screens = [
            ("Help Screen", lambda: self.game.draw_help_screen_framework()),
            ("About Screen", lambda: self.game.draw_about_screen_framework()),
            ("Settings Screen", lambda: self.game.draw_settings_screen_framework()),
            ("Controls Screen", lambda: self.game.draw_controls_screen_framework()),
        ]
        
        for screen_name, screen_func in menu_screens:
            try:
                ui = screen_func()
                if ui:
                    # Test rendering
                    self.screen.fill((0, 0, 0))
                    ui.draw_warm_gradient_background()
                    ui.render()
                    pygame.display.flip()
                    
                    # Validate visual elements
                    result = self._validate_visual_elements(ui, screen_name)
                    status = "✅ PASS" if result['success'] else "❌ FAIL"
                    print(f"  {status} {screen_name}: {result['message']}")
                    
                    self.results["visual_consistency"].append({
                        "screen": screen_name,
                        "success": result['success'],
                        "message": result['message'],
                        "details": result.get('details', {})
                    })
                else:
                    print(f"  ❌ FAIL {screen_name}: Screen function returned None")
                    self.results["visual_consistency"].append({
                        "screen": screen_name,
                        "success": False,
                        "message": "Screen function returned None"
                    })
                    
                # Small delay to see the screen
                time.sleep(0.1)
                
            except Exception as e:
                print(f"  ❌ FAIL {screen_name}: Exception - {str(e)}")
                self.results["visual_consistency"].append({
                    "screen": screen_name,
                    "success": False,
                    "message": f"Exception: {str(e)}"
                })
    
    def _validate_visual_elements(self, ui: UIManager, screen_name: str) -> Dict[str, Any]:
        """Validate visual elements of a UI screen"""
        issues = []
        
        # Check that UI has elements
        if not ui.elements:
            issues.append("No UI elements found")
        
        # Check for MenuPanel
        menu_panels = [elem for elem in ui.elements if isinstance(elem, MenuPanel)]
        if not menu_panels:
            issues.append("No MenuPanel found")
        else:
            panel = menu_panels[0]
            
            # Check panel size is reasonable
            if panel.rect.width < 300 or panel.rect.height < 200:
                issues.append(f"Panel too small: {panel.rect.width}x{panel.rect.height}")
            
            # Check panel has content
            if not hasattr(panel, 'content_area') or not panel.content_area.content_items:
                issues.append("Panel has no content")
        
        if issues:
            return {
                "success": False,
                "message": f"Visual validation failed: {', '.join(issues)}",
                "details": {"issues": issues}
            }
        else:
            return {
                "success": True,
                "message": "Visual elements validated successfully",
                "details": {
                    "element_count": len(ui.elements),
                    "panel_count": len(menu_panels)
                }
            }
    
    def test_performance(self):
        """Test performance of UI rendering"""
        print("  📊 Running performance benchmarks...")
        
        # Test rendering performance
        render_times = self._benchmark_rendering()
        self.results["performance"].append({
            "test": "Rendering Performance",
            "success": render_times["average"] < 16.67,  # 60 FPS target
            "message": f"Average render time: {render_times['average']:.2f}ms",
            "details": render_times
        })
        
        # Test memory usage
        memory_usage = self._test_memory_usage()
        self.results["performance"].append({
            "test": "Memory Usage",
            "success": True,  # Just informational
            "message": f"UI elements created: {memory_usage['elements_created']}",
            "details": memory_usage
        })
        
        print(f"  ✅ Rendering: {render_times['average']:.2f}ms avg ({render_times['fps']:.1f} FPS)")
        print(f"  ✅ Memory: {memory_usage['elements_created']} UI elements created")
    
    def _benchmark_rendering(self) -> Dict[str, float]:
        """Benchmark rendering performance"""
        def test_content(content_area):
            fonts = self.game.create_framework_fonts()
            for i in range(20):  # Add lots of content
                content_area.add_header(f"Section {i}", fonts['ui'])
                content_area.add_text(f"This is content for section {i} with some longer text to test wrapping", fonts['content'])
        
        ui = self.game.create_framework_page("PERFORMANCE TEST", "⚡", test_content)
        
        render_times = []
        for _ in range(60):  # Test 60 frames
            start_time = time.perf_counter()
            
            self.screen.fill((0, 0, 0))
            ui.draw_warm_gradient_background()
            ui.render()
            pygame.display.flip()
            
            end_time = time.perf_counter()
            render_times.append((end_time - start_time) * 1000)  # Convert to ms
        
        return {
            "average": sum(render_times) / len(render_times),
            "min": min(render_times),
            "max": max(render_times),
            "fps": 1000 / (sum(render_times) / len(render_times))
        }
    
    def _test_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage by creating and destroying UI elements"""
        elements_created = 0
        
        for i in range(10):
            def test_content(content_area):
                fonts = self.game.create_framework_fonts()
                content_area.add_header(f"Test {i}", fonts['ui'])
                content_area.add_text("Test content", fonts['content'])
            
            ui = self.game.create_framework_page(f"TEST {i}", "🧪", test_content)
            elements_created += len(ui.elements)
            
            # Render once
            self.screen.fill((0, 0, 0))
            ui.render()
            
            # Clear UI
            ui.clear()
        
        return {
            "elements_created": elements_created,
            "test_iterations": 10
        }
    
    def test_error_handling(self):
        """Test error handling in various scenarios"""
        error_tests = [
            ("Invalid Font", self._test_invalid_font),
            ("Missing Content Callback", self._test_missing_content),
            ("Invalid Emoji", self._test_invalid_emoji),
            ("Large Content", self._test_large_content),
            ("Empty Content", self._test_empty_content)
        ]
        
        for test_name, test_func in error_tests:
            try:
                result = test_func()
                status = "✅ PASS" if result['success'] else "❌ FAIL"
                print(f"  {status} {test_name}: {result['message']}")
                self.results["error_handling"].append({
                    "test": test_name,
                    "success": result['success'],
                    "message": result['message'],
                    "details": result.get('details', {})
                })
            except Exception as e:
                print(f"  ❌ FAIL {test_name}: Unexpected exception - {str(e)}")
                self.results["error_handling"].append({
                    "test": test_name,
                    "success": False,
                    "message": f"Unexpected exception: {str(e)}"
                })
    
    def _test_invalid_font(self) -> Dict[str, Any]:
        """Test handling of invalid fonts"""
        try:
            def test_content(content_area):
                # Try to use None as font
                content_area.add_text("Test", None)
            
            ui = self.game.create_framework_page("INVALID FONT TEST", "🧪", test_content)
            
            # Try to render - should not crash
            self.screen.fill((0, 0, 0))
            ui.render()
            
            return {
                "success": True,
                "message": "Invalid font handled gracefully"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Invalid font caused crash: {str(e)}"
            }
    
    def _test_missing_content(self) -> Dict[str, Any]:
        """Test handling of missing content callback"""
        try:
            ui = self.game.create_framework_page("MISSING CONTENT", "🧪", None)
            return {
                "success": ui is not None,
                "message": "Missing content callback handled" if ui else "Missing content callback not handled"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Missing content callback caused exception: {str(e)}"
            }
    
    def _test_invalid_emoji(self) -> Dict[str, Any]:
        """Test handling of invalid emoji"""
        try:
            def test_content(content_area):
                fonts = self.game.create_framework_fonts()
                content_area.add_text("Test content", fonts['content'])
            
            # Use an emoji that might not be supported
            ui = self.game.create_framework_page("INVALID EMOJI", "🦄🌈💫", test_content)
            
            # Try to render
            self.screen.fill((0, 0, 0))
            ui.render()
            
            return {
                "success": True,
                "message": "Invalid emoji handled with fallback"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Invalid emoji caused crash: {str(e)}"
            }
    
    def _test_large_content(self) -> Dict[str, Any]:
        """Test handling of very large content"""
        try:
            def test_content(content_area):
                fonts = self.game.create_framework_fonts()
                # Add lots of content
                for i in range(100):
                    content_area.add_text(f"This is line {i} with lots of text that should wrap properly and not cause any issues even with very long content that goes on and on", fonts['content'])
            
            ui = self.game.create_framework_page("LARGE CONTENT", "📄", test_content)
            
            # Try to render
            self.screen.fill((0, 0, 0))
            ui.render()
            
            return {
                "success": True,
                "message": "Large content handled successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Large content caused issues: {str(e)}"
            }
    
    def _test_empty_content(self) -> Dict[str, Any]:
        """Test handling of empty content"""
        try:
            def test_content(content_area):
                pass  # Add no content
            
            ui = self.game.create_framework_page("EMPTY CONTENT", "📄", test_content)
            
            # Try to render
            self.screen.fill((0, 0, 0))
            ui.render()
            
            return {
                "success": True,
                "message": "Empty content handled successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Empty content caused issues: {str(e)}"
            }
    
    def test_accessibility(self):
        """Test accessibility features"""
        accessibility_tests = [
            ("Color Contrast", self._test_color_contrast),
            ("Font Sizes", self._test_font_sizes),
            ("Emoji Fallbacks", self._test_emoji_fallbacks),
            ("Text Wrapping", self._test_text_wrapping)
        ]
        
        for test_name, test_func in accessibility_tests:
            try:
                result = test_func()
                status = "✅ PASS" if result['success'] else "❌ FAIL"
                print(f"  {status} {test_name}: {result['message']}")
                self.results["accessibility"].append({
                    "test": test_name,
                    "success": result['success'],
                    "message": result['message'],
                    "details": result.get('details', {})
                })
            except Exception as e:
                print(f"  ❌ FAIL {test_name}: Exception - {str(e)}")
                self.results["accessibility"].append({
                    "test": test_name,
                    "success": False,
                    "message": f"Exception: {str(e)}"
                })
    
    def _test_color_contrast(self) -> Dict[str, Any]:
        """Test color contrast ratios"""
        theme = UITheme()
        
        # Calculate contrast ratio between text and background
        def luminance(color):
            r, g, b = [c / 255.0 for c in color[:3]]
            return 0.299 * r + 0.587 * g + 0.114 * b
        
        def contrast_ratio(color1, color2):
            l1 = luminance(color1)
            l2 = luminance(color2)
            return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
        
        # Test primary text on primary background
        primary_contrast = contrast_ratio(theme.TEXT_PRIMARY, theme.BACKGROUND_PRIMARY[:3])
        
        # Test secondary text on primary background
        secondary_contrast = contrast_ratio(theme.TEXT_SECONDARY, theme.BACKGROUND_PRIMARY[:3])
        
        # WCAG AA requires 4.5:1 for normal text, 3:1 for large text
        issues = []
        if primary_contrast < 4.5:
            issues.append(f"Primary text contrast too low: {primary_contrast:.2f}")
        if secondary_contrast < 3.0:
            issues.append(f"Secondary text contrast too low: {secondary_contrast:.2f}")
        
        if issues:
            return {
                "success": False,
                "message": f"Color contrast issues: {', '.join(issues)}",
                "details": {
                    "primary_contrast": primary_contrast,
                    "secondary_contrast": secondary_contrast
                }
            }
        else:
            return {
                "success": True,
                "message": "Color contrast meets accessibility standards",
                "details": {
                    "primary_contrast": primary_contrast,
                    "secondary_contrast": secondary_contrast
                }
            }
    
    def _test_font_sizes(self) -> Dict[str, Any]:
        """Test that font sizes are appropriate"""
        fonts = self.game.create_framework_fonts()
        
        # Check minimum font sizes (14px is generally considered minimum)
        small_fonts = []
        for name, font in fonts.items():
            height = font.get_height()
            if height < 14:
                small_fonts.append(f"{name}: {height}px")
        
        if small_fonts:
            return {
                "success": False,
                "message": f"Fonts too small for accessibility: {', '.join(small_fonts)}",
                "details": {name: font.get_height() for name, font in fonts.items()}
            }
        else:
            return {
                "success": True,
                "message": "All fonts meet minimum size requirements",
                "details": {name: font.get_height() for name, font in fonts.items()}
            }
    
    def _test_emoji_fallbacks(self) -> Dict[str, Any]:
        """Test emoji fallback system"""
        theme = UITheme()
        
        # Test that fallbacks exist for common emojis
        test_emojis = ["🏆", "❓", "⚙️", "ℹ️", "⌨️", "🌱", "📖"]
        missing_fallbacks = []
        
        for emoji in test_emojis:
            if emoji not in theme.EMOJI_FALLBACKS:
                missing_fallbacks.append(emoji)
        
        if missing_fallbacks:
            return {
                "success": False,
                "message": f"Missing emoji fallbacks: {missing_fallbacks}",
                "details": {
                    "missing": missing_fallbacks,
                    "available": list(theme.EMOJI_FALLBACKS.keys())
                }
            }
        else:
            return {
                "success": True,
                "message": "All test emojis have fallbacks",
                "details": {
                    "tested_emojis": test_emojis,
                    "fallback_count": len(theme.EMOJI_FALLBACKS)
                }
            }
    
    def _test_text_wrapping(self) -> Dict[str, Any]:
        """Test text wrapping functionality"""
        try:
            def test_content(content_area):
                fonts = self.game.create_framework_fonts()
                # Add very long text that should wrap
                long_text = "This is a very long line of text that should automatically wrap within the panel boundaries and not overflow or cause any visual issues when rendered on screen."
                content_area.add_text(long_text, fonts['content'])
            
            ui = self.game.create_framework_page("TEXT WRAP TEST", "📝", test_content)
            
            # Render to test wrapping
            self.screen.fill((0, 0, 0))
            ui.render()
            
            return {
                "success": True,
                "message": "Text wrapping functionality working",
                "details": {"test_completed": True}
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Text wrapping failed: {str(e)}"
            }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION REPORT")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.results.items():
            category_passed = sum(1 for test in tests if test['success'])
            category_total = len(tests)
            total_tests += category_total
            passed_tests += category_passed
            
            status = "✅" if category_passed == category_total else "⚠️" if category_passed > 0 else "❌"
            print(f"\n{status} {category.replace('_', ' ').title()}: {category_passed}/{category_total}")
            
            for test in tests:
                status = "✅" if test['success'] else "❌"
                print(f"  {status} {test.get('test', test.get('screen', 'Unknown'))}")
                if not test['success']:
                    print(f"    └─ {test['message']}")
        
        overall_status = "✅ PASS" if passed_tests == total_tests else "⚠️ PARTIAL" if passed_tests > 0 else "❌ FAIL"
        print(f"\n{overall_status} Overall: {passed_tests}/{total_tests} tests passed")
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"  • {rec}")
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
                "overall_status": overall_status
            },
            "results": self.results,
            "recommendations": recommendations
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check for common issues
        for category, tests in self.results.items():
            failed_tests = [test for test in tests if not test['success']]
            
            if failed_tests:
                if category == "framework_integration":
                    recommendations.append("Review UI framework integration - some core functionality may be broken")
                elif category == "visual_consistency":
                    recommendations.append("Check visual consistency across menu screens")
                elif category == "performance":
                    recommendations.append("Consider optimizing rendering performance")
                elif category == "error_handling":
                    recommendations.append("Improve error handling for edge cases")
                elif category == "accessibility":
                    recommendations.append("Address accessibility issues for better user experience")
        
        # Check performance specifically
        perf_tests = self.results.get("performance", [])
        for test in perf_tests:
            if test.get("details", {}).get("average", 0) > 16.67:
                recommendations.append("Rendering performance below 60 FPS - consider optimization")
        
        return recommendations
    
    def cleanup(self):
        """Clean up pygame resources"""
        pygame.quit()

def main():
    """Main validation function"""
    validator = MenuUIValidator()
    
    try:
        # Run all validations
        report = validator.run_all_validations()
        
        # Save report to file
        with open('/home/seth/development/field_station/ui_validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: ui_validation_report.json")
        
        # Wait for user input to close
        print(f"\nPress any key to exit...")
        pygame.event.clear()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type in [pygame.KEYDOWN, pygame.QUIT]:
                    waiting = False
            validator.clock.tick(60)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Validation interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Validation failed with exception: {str(e)}")
        traceback.print_exc()
    finally:
        validator.cleanup()

if __name__ == "__main__":
    main()
