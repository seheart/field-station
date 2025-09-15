"""
Field Station UI Framework

A lightweight, pygame-based UI framework that provides:
- Reusable UI components
- Consistent styling and theming
- Automatic layout management
- Event handling abstraction
- Emoji/icon support with fallbacks
"""

import pygame
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

# Fallback constants - don't import from field_station to avoid circular imports
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

class UITheme:
    """Centralized theme management for consistent styling"""
    
    # Colors
    BACKGROUND_PRIMARY = (60, 70, 50, 200)  # Dark olive with opacity
    BACKGROUND_SECONDARY = (45, 55, 40, 180)
    BACKGROUND_TERTIARY = (35, 45, 30, 150)
    
    BORDER_PRIMARY = (144, 238, 144)  # Light green
    BORDER_SECONDARY = (120, 200, 120)
    
    TEXT_PRIMARY = (255, 255, 255)  # White
    TEXT_SECONDARY = (200, 200, 200)  # Light gray
    TEXT_ACCENT = (218, 165, 32)  # Goldenrod
    TEXT_SHADOW = (20, 25, 15)  # Dark shadow
    
    # Spacing and sizing
    PANEL_MARGIN = 40
    LINE_HEIGHT = 22
    TITLE_HEIGHT = 120
    BORDER_RADIUS = 8
    BORDER_WIDTH = 3
    SHADOW_OFFSET = 4
    
    # Emoji fallbacks
    EMOJI_FALLBACKS = {
        "🏆": "[*]", "❓": "[?]", "⚙️": "[G]", "ℹ️": "[i]",
        "⌨️": "[K]", "🌱": "[S]", "📖": "[B]", "🎯": "[T]",
        "🎮": "[G]", "💾": "[S]", "🔊": "[A]", "🔇": "[M]"
    }

class Alignment(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"

@dataclass
class Rect:
    """Enhanced rectangle with utility methods"""
    x: int
    y: int
    width: int
    height: int
    
    def to_pygame_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    @property
    def center_x(self) -> int:
        return self.x + self.width // 2
    
    @property
    def center_y(self) -> int:
        return self.y + self.height // 2
    
    @property
    def right(self) -> int:
        return self.x + self.width
    
    @property
    def bottom(self) -> int:
        return self.y + self.height

class UIElement(ABC):
    """Base class for all UI elements"""
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 100, height: int = 30):
        self.rect = Rect(x, y, width, height)
        self.visible = True
        self.enabled = True
        self.theme = UITheme()
        
    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """Render this UI element to the screen"""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame event. Return True if event was consumed."""
        return False
    
    def set_position(self, x: int, y: int) -> 'UIElement':
        """Set position and return self for chaining"""
        self.rect.x = x
        self.rect.y = y
        return self
    
    def set_size(self, width: int, height: int) -> 'UIElement':
        """Set size and return self for chaining"""
        self.rect.width = width
        self.rect.height = height
        return self

class Panel(UIElement):
    """Base panel with background, border, and shadow"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 style: str = "primary", title: str = "", title_emoji: str = ""):
        super().__init__(x, y, width, height)
        self.style = style
        self.title = title
        self.title_emoji = title_emoji
        self.children: List[UIElement] = []
        
        # Style-specific settings
        if style == "primary":
            self.bg_color = self.theme.BACKGROUND_PRIMARY
            self.border_color = self.theme.BORDER_PRIMARY
            self.shadow_size = 6
        elif style == "secondary":
            self.bg_color = self.theme.BACKGROUND_SECONDARY
            self.border_color = self.theme.BORDER_SECONDARY
            self.shadow_size = 4
        else:  # tertiary
            self.bg_color = self.theme.BACKGROUND_TERTIARY
            self.border_color = self.theme.BORDER_SECONDARY
            self.shadow_size = 2
    
    def add_child(self, child: UIElement) -> 'Panel':
        """Add child element and return self for chaining"""
        self.children.append(child)
        return self
    
    def render(self, screen: pygame.Surface) -> None:
        """Render panel with shadow, background, border, and children"""
        if not self.visible:
            return
            
        pygame_rect = self.rect.to_pygame_rect()
        
        # Draw shadow
        if self.shadow_size > 0:
            shadow_rect = pygame.Rect(
                pygame_rect.x + self.shadow_size,
                pygame_rect.y + self.shadow_size,
                pygame_rect.width,
                pygame_rect.height
            )
            shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            shadow_surface.fill((0, 0, 0, 50))
            screen.blit(shadow_surface, shadow_rect)
        
        # Draw background
        panel_surface = pygame.Surface((pygame_rect.width, pygame_rect.height), pygame.SRCALPHA)
        panel_surface.fill(self.bg_color)
        screen.blit(panel_surface, pygame_rect)
        
        # Draw border
        pygame.draw.rect(screen, self.border_color, pygame_rect, 
                        self.theme.BORDER_WIDTH, border_radius=self.theme.BORDER_RADIUS)
        
        # Render children
        for child in self.children:
            child.render(screen)

class Text(UIElement):
    """Text rendering component with wrapping and styling"""
    
    def __init__(self, x: int, y: int, text: str, font: pygame.font.Font, 
                 color: Tuple[int, int, int] = None, max_width: int = None):
        # Calculate text dimensions
        if max_width:
            wrapped_lines = self._wrap_text(text, font, max_width)
            text_width = min(max_width, max(font.size(line)[0] for line in wrapped_lines))
            text_height = len(wrapped_lines) * font.get_height()
        else:
            text_width, text_height = font.size(text)
            
        super().__init__(x, y, text_width, text_height)
        self.text = text
        self.font = font
        self.color = color or self.theme.TEXT_PRIMARY
        self.max_width = max_width
        self.wrapped_lines = None
        
    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Word is too long, add it anyway
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
    
    def render(self, screen: pygame.Surface) -> None:
        """Render text with optional wrapping"""
        if not self.visible:
            return
            
        if self.max_width:
            if not self.wrapped_lines:
                self.wrapped_lines = self._wrap_text(self.text, self.font, self.max_width)
            
            y_offset = 0
            for line in self.wrapped_lines:
                text_surface = self.font.render(line, True, self.color)
                screen.blit(text_surface, (self.rect.x, self.rect.y + y_offset))
                y_offset += self.font.get_height()
        else:
            text_surface = self.font.render(self.text, True, self.color)
            screen.blit(text_surface, (self.rect.x, self.rect.y))

class Title(UIElement):
    """Title component with emoji support and consistent styling"""
    
    def __init__(self, x: int, y: int, title_text: str, emoji: str = "",
                 title_font: pygame.font.Font = None, emoji_font: pygame.font.Font = None):
        # We'll calculate size during render since we need fonts
        super().__init__(x, y, 400, 60)  # Default size, will adjust
        self.title_text = title_text
        self.emoji = emoji
        self.title_font = title_font
        self.emoji_font = emoji_font
        self.title_color = self.theme.BORDER_PRIMARY
        self.shadow_color = self.theme.TEXT_SHADOW
        
    def render(self, screen: pygame.Surface) -> None:
        """Render title with emoji and shadow effect"""
        if not self.visible or not self.title_font:
            return
            
        # Render emoji
        emoji_x = self.rect.x
        if self.emoji and self.emoji_font:
            # Try to render emoji, fall back to ASCII
            emoji_to_render = self.emoji
            try:
                emoji_surface = self.emoji_font.render(emoji_to_render, True, self.title_color)
                if emoji_surface.get_width() == 0:  # Emoji failed to render
                    raise ValueError("Emoji rendering failed")
            except:
                # Use ASCII fallback
                emoji_to_render = self.theme.EMOJI_FALLBACKS.get(self.emoji, "[?]")
                emoji_surface = self.title_font.render(emoji_to_render, True, self.title_color)
            
            screen.blit(emoji_surface, (emoji_x, self.rect.y))
            emoji_x += emoji_surface.get_width() + 15
        
        # Render title text with shadow
        # Shadow
        title_shadow = self.title_font.render(self.title_text, True, self.shadow_color)
        shadow_rect = title_shadow.get_rect(center=(emoji_x + title_shadow.get_width()//2 + 2, 
                                                   self.rect.y + title_shadow.get_height()//2 + 2))
        screen.blit(title_shadow, shadow_rect)
        
        # Main text
        title_surface = self.title_font.render(self.title_text, True, self.title_color)
        title_rect = title_surface.get_rect(center=(emoji_x + title_surface.get_width()//2, 
                                                   self.rect.y + title_surface.get_height()//2))
        screen.blit(title_surface, title_rect)

class ContentArea(UIElement):
    """Scrollable content area with automatic text layout"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.content_items: List[Dict[str, Any]] = []
        self.scroll_offset = 0
        self.line_height = self.theme.LINE_HEIGHT
        
    def add_text(self, text: str, color_or_font = None, 
                font: pygame.font.Font = None) -> 'ContentArea':
        """Add text item to content - flexible parameter handling"""
        # Handle different parameter patterns
        if color_or_font is None:
            # add_text("text")
            color = self.theme.TEXT_PRIMARY
            font = getattr(self, '_default_font', None)
        elif isinstance(color_or_font, tuple):
            # add_text("text", (255,255,255), font)
            color = color_or_font
            font = font or getattr(self, '_default_font', None)
        else:
            # add_text("text", font) 
            color = self.theme.TEXT_PRIMARY
            font = color_or_font
        
        self.content_items.append({
            'type': 'text',
            'text': text,
            'color': color,
            'font': font
        })
        return self
    
    def add_header(self, text: str, font: pygame.font.Font = None) -> 'ContentArea':
        """Add header text in accent color"""
        font_to_use = font or getattr(self, '_ui_font', None)
        return self.add_text(text, self.theme.TEXT_ACCENT, font_to_use)
    
    def add_spacer(self) -> 'ContentArea':
        """Add empty line spacing"""
        return self.add_text("", self.theme.TEXT_PRIMARY)
    
    def render(self, screen: pygame.Surface) -> None:
        """Render content with clipping and scroll support"""
        if not self.visible:
            return
            
        # Create clipping rect for content area
        pygame_rect = self.rect.to_pygame_rect()
        original_clip = screen.get_clip()
        screen.set_clip(pygame_rect)
        
        y_offset = self.rect.y - self.scroll_offset
        content_height = 0
        
        for item in self.content_items:
            if item['type'] == 'text' and item['font']:
                # Handle text wrapping
                max_width = self.rect.width - (self.theme.PANEL_MARGIN * 2)
                text = item['text']
                
                if text.strip():  # Non-empty text
                    words = text.split(' ')
                    current_line = []
                    
                    for word in words:
                        test_line = ' '.join(current_line + [word])
                        if item['font'].size(test_line)[0] <= max_width:
                            current_line.append(word)
                        else:
                            if current_line:
                                # Render current line
                                line_text = ' '.join(current_line)
                                text_surface = item['font'].render(line_text, True, item['color'])
                                screen.blit(text_surface, (self.rect.x + self.theme.PANEL_MARGIN, y_offset))
                                y_offset += self.line_height
                                content_height += self.line_height
                                current_line = [word]
                            else:
                                # Word too long, render anyway
                                text_surface = item['font'].render(word, True, item['color'])
                                screen.blit(text_surface, (self.rect.x + self.theme.PANEL_MARGIN, y_offset))
                                y_offset += self.line_height
                                content_height += self.line_height
                    
                    # Render remaining text
                    if current_line:
                        line_text = ' '.join(current_line)
                        text_surface = item['font'].render(line_text, True, item['color'])
                        screen.blit(text_surface, (self.rect.x + self.theme.PANEL_MARGIN, y_offset))
                        y_offset += self.line_height
                        content_height += self.line_height
                else:
                    # Empty line for spacing
                    y_offset += self.line_height
                    content_height += self.line_height
        
        # Show scroll indicator if content was cut off
        if content_height > self.rect.height:
            scroll_text = f"[Content continues... {content_height - self.rect.height}px hidden]"
            if hasattr(self, '_scroll_font'):  # Assume we have a small font available
                scroll_surface = self._scroll_font.render(scroll_text, True, self.theme.TEXT_SECONDARY)
                screen.blit(scroll_surface, (self.rect.x + 10, self.rect.bottom - 25))
        
        # Restore original clipping
        screen.set_clip(original_clip)

class MenuPanel(Panel):
    """Specialized panel for menu screens with title and content area"""
    
    def __init__(self, title: str, emoji: str = "", width: int = 700, height: int = 500, x: int = None, y: int = None):
        # Use provided position or center the panel on screen
        if x is None:
            x = SCREEN_WIDTH // 2 - width // 2
        if y is None:
            y = (SCREEN_HEIGHT - height) // 2
        
        super().__init__(x, y, width, height, style="primary")
        
        # Add title
        if title:
            title_y = self.rect.y + 60
            self.title_component = Title(
                SCREEN_WIDTH // 2 - 200, title_y, title, emoji
            )
            self.add_child(self.title_component)
        
        # Add content area
        content_y = self.rect.y + self.theme.TITLE_HEIGHT
        content_height = self.rect.height - self.theme.TITLE_HEIGHT - 60
        self.content_area = ContentArea(
            self.rect.x, content_y, 
            self.rect.width, content_height
        )
        self.add_child(self.content_area)
    
    def set_fonts(self, title_font: pygame.font.Font = None, emoji_font: pygame.font.Font = None, 
                  content_font: pygame.font.Font = None, ui_font: pygame.font.Font = None,
                  title: pygame.font.Font = None, emoji: pygame.font.Font = None,
                  content: pygame.font.Font = None, ui: pygame.font.Font = None) -> 'MenuPanel':
        """Set fonts for all components - accepts both parameter names and dict unpacking"""
        # Handle both direct parameters and dict unpacking
        title_font = title_font or title
        emoji_font = emoji_font or emoji  
        content_font = content_font or content
        ui_font = ui_font or ui
        
        if hasattr(self, 'title_component'):
            if title_font:
                self.title_component.title_font = title_font
            if emoji_font:
                self.title_component.emoji_font = emoji_font
        
        if content_font:
            self.content_area._default_font = content_font
            self.content_area._scroll_font = content_font  # For scroll indicator
        if ui_font:
            self.content_area._ui_font = ui_font
        return self

class MainMenuPanel(UIElement):
    """Specialized main menu panel that handles title area and button column layout"""
    
    def __init__(self, title_text: str, subtitle_text: str, menu_options: list, selected_index: int):
        super().__init__()
        self.title_text = title_text
        self.subtitle_text = subtitle_text  
        self.menu_options = menu_options
        self.selected_index = selected_index
        self.theme = UITheme()
        
        # Fonts (will be set by caller)
        self.title_font = None
        self.subtitle_font = None
        self.button_font = None
        
        # Store button rectangles for click detection
        self.button_rects = []  
        self.hovered_index = -1  # Track which button is being hovered
        self.clicked_option = None  # Store which option was clicked
        
    def set_fonts(self, title_font, subtitle_font, button_font):
        """Set the fonts for different parts of the menu"""
        self.title_font = title_font
        self.subtitle_font = subtitle_font
        self.button_font = button_font
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events for menu buttons"""
        if event.type == pygame.MOUSEMOTION:
            # Update hover state
            mouse_pos = event.pos
            self.hovered_index = -1
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(mouse_pos):
                    self.hovered_index = i
                    break
            return False  # Don't consume motion events
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                for i, rect in enumerate(self.button_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_index = i
                        self.clicked_option = self.menu_options[i]
                        return True  # Consume the click
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.menu_options)
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.menu_options)
                return True
            elif event.key == pygame.K_RETURN:
                self.clicked_option = self.menu_options[self.selected_index]
                return True
                
        return False
    
    def get_clicked_option(self) -> str:
        """Get and clear the clicked option"""
        option = self.clicked_option
        self.clicked_option = None
        return option
        
    def render(self, screen: pygame.Surface):
        """Render the main menu with proper layout"""
        if not all([self.title_font, self.subtitle_font, self.button_font]):
            return  # Can't render without fonts
            
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # VISUAL DEBUG: Draw screen bounds and center lines
        debug_font = pygame.font.Font(None, 20)
        
        
        # Calculate layout
        total_menu_items = len(self.menu_options)
        button_spacing = max(45, min(50, (screen_height - 300) // total_menu_items))
        menu_height = 80 + 40 + (total_menu_items * button_spacing) + 40
        start_y = max(50, (screen_height - menu_height) // 2)
        
        # Title area - centered
        title_y = start_y + 40
        
        # Title shadow
        shadow_title = self.title_font.render(self.title_text, True, (20, 25, 15))
        shadow_rect = shadow_title.get_rect(center=(screen_width // 2 + 2, title_y + 2))
        screen.blit(shadow_title, shadow_rect)
        
        # Main title
        title = self.title_font.render(self.title_text, True, (144, 238, 144))
        title_rect = title.get_rect(center=(screen_width // 2, title_y))
        screen.blit(title, title_rect)
        
        # Subtitle  
        subtitle_y = title_y + 60
        subtitle = self.subtitle_font.render(self.subtitle_text, True, (120, 200, 120))  # Slightly muted green
        subtitle_rect = subtitle.get_rect(center=(screen_width // 2, subtitle_y))
        screen.blit(subtitle, subtitle_rect)
        
        # Menu options - centered below subtitle
        menu_start_y = subtitle_y + 60
        
        # Clear and rebuild button rectangles
        self.button_rects = []
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, option in enumerate(self.menu_options):
            y = menu_start_y + (i * button_spacing)
            
            # Create button rectangle (wider for easier clicking)
            button_rect = pygame.Rect(screen_width // 2 - 150, y - 20, 300, 40)
            self.button_rects.append(button_rect)
            
            # Check if mouse is hovering
            is_hovered = button_rect.collidepoint(mouse_pos)
            if is_hovered:
                self.hovered_index = i
            
            # Determine button state
            is_selected = (i == self.selected_index) or (i == self.hovered_index)
            
            # Draw button background
            if is_selected:
                # Draw glow effect for selected/hovered
                glow_surface = pygame.Surface((button_rect.width + 10, button_rect.height + 10), pygame.SRCALPHA)
                glow_color = (144, 238, 144, 40) if i == self.selected_index else (100, 180, 100, 30)
                pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=8)
                screen.blit(glow_surface, (button_rect.x - 5, button_rect.y - 5))
                
                # Button background
                button_color = (85, 107, 47, 180) if i == self.selected_index else (60, 80, 40, 150)
                button_surface = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(button_surface, button_color, button_surface.get_rect(), border_radius=6)
                screen.blit(button_surface, button_rect)
                
                # Button border
                border_color = (144, 238, 144) if i == self.selected_index else (120, 200, 120)
                pygame.draw.rect(screen, border_color, button_rect, 2, border_radius=6)
            else:
                # Normal button
                button_surface = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(button_surface, (40, 50, 35, 100), button_surface.get_rect(), border_radius=6)
                screen.blit(button_surface, button_rect)
                pygame.draw.rect(screen, (80, 100, 70), button_rect, 1, border_radius=6)
            
            # Button text with icon - centered (icon only on hover)
            color = (255, 255, 255) if is_selected else (180, 180, 180)
            
            # Only show icon when hovering
            if is_hovered:
                from menu_icons import get_menu_icon
                icon = get_menu_icon(option)
                menu_text = f"{icon}  {option}"
            else:
                menu_text = option
                
            text = self.button_font.render(menu_text, True, color)
            text_rect = text.get_rect(center=button_rect.center)
            screen.blit(text, text_rect)
            
            # Add selection arrow for selected item
            if i == self.selected_index:
                arrow_color = (218, 165, 32)  # Goldenrod
                arrow_points = [
                    (button_rect.left + 20, button_rect.centery - 8),
                    (button_rect.left + 30, button_rect.centery),
                    (button_rect.left + 20, button_rect.centery + 8)
                ]
                pygame.draw.polygon(screen, arrow_color, arrow_points)
            

class GenericPagePanel(UIElement):
    """A reusable page panel for all game screens with consistent styling"""
    
    def __init__(self, title: str, subtitle: str = "", width: int = 800, height: int = 600):
        super().__init__()
        self.title = title
        self.subtitle = subtitle
        self.width = width
        self.height = height
        self.theme = UITheme()
        
        # Fonts
        self.title_font = None
        self.subtitle_font = None
        self.content_font = None
        self.button_font = None
        
        # Content elements
        self.content_elements = []  # List of (type, data) tuples
        self.buttons = []  # List of button data
        self.input_fields = []  # List of input field data
        
    def set_fonts(self, title_font=None, subtitle_font=None, content_font=None, button_font=None):
        """Set the fonts for different parts of the page"""
        if title_font:
            self.title_font = title_font
        if subtitle_font:
            self.subtitle_font = subtitle_font
        if content_font:
            self.content_font = content_font
        if button_font:
            self.button_font = button_font
            
    def add_text(self, text: str, color=(200, 200, 200), center=False):
        """Add a text line to the content"""
        self.content_elements.append(('text', {'text': text, 'color': color, 'center': center}))
        return self
        
    def add_header(self, text: str, color=(218, 165, 32)):
        """Add a header to the content"""
        self.content_elements.append(('header', {'text': text, 'color': color}))
        return self
        
    def add_spacer(self, height: int = 20):
        """Add vertical spacing"""
        self.content_elements.append(('spacer', {'height': height}))
        return self
        
    def add_input_field(self, label: str, field_id: str, value: str = "", active: bool = False, placeholder: str = ""):
        """Add an input field"""
        # Add as a content element instead of separate list for proper ordering
        self.content_elements.append(('input_field', {
            'label': label,
            'id': field_id,
            'value': value,
            'active': active,
            'placeholder': placeholder,
            'rect': None  # Will be set during render
        }))
        # Also keep in input_fields for event handling
        field_data = {
            'label': label,
            'id': field_id,
            'value': value,
            'active': active,
            'placeholder': placeholder,
            'rect': None
        }
        self.input_fields.append(field_data)
        return self
        
    def add_button(self, text: str, button_id: str, enabled: bool = True, selected: bool = False):
        """Add a button"""
        self.buttons.append({
            'text': text,
            'id': button_id,
            'enabled': enabled,
            'selected': selected,
            'rect': None  # Will be set during render
        })
        return self
        
    def add_option_list(self, label: str, options: list, selected_index: int = -1, option_id: str = ""):
        """Add a list of selectable options"""
        self.content_elements.append(('option_list', {
            'label': label,
            'options': options,
            'selected_index': selected_index,
            'id': option_id
        }))
        return self
        
    def render(self, screen: pygame.Surface):
        """Render the page with all its elements"""
        if not self.title_font:
            return  # Can't render without fonts
            
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Calculate panel position (centered)
        panel_x = (screen_width - self.width) // 2
        panel_y = (screen_height - self.height) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, self.width, self.height)
        
        # Draw panel background with transparency
        panel_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (30, 40, 25, 220), panel_surface.get_rect(), border_radius=10)
        screen.blit(panel_surface, panel_rect)
        
        # Draw panel border
        pygame.draw.rect(screen, (100, 120, 90), panel_rect, 2, border_radius=10)
        
        # Calculate content area bounds
        content_margin = 40
        content_x = panel_x + content_margin
        content_width = self.width - (content_margin * 2)
        
        # Reserve space for buttons at bottom
        button_area_height = 80 if self.buttons else 20
        content_bottom = panel_y + self.height - button_area_height
        
        # Draw title
        y_offset = panel_y + 30
        if self.title:
            # Title shadow
            shadow_title = self.title_font.render(self.title, True, (20, 25, 15))
            shadow_rect = shadow_title.get_rect(center=(screen_width // 2 + 2, y_offset + 2))
            screen.blit(shadow_title, shadow_rect)
            
            # Main title
            title_surface = self.title_font.render(self.title, True, (144, 238, 144))
            title_rect = title_surface.get_rect(center=(screen_width // 2, y_offset))
            screen.blit(title_surface, title_rect)
            y_offset += self.title_font.get_height() + 10
            
        # Draw subtitle
        if self.subtitle:
            subtitle_surface = self.subtitle_font.render(self.subtitle, True, (218, 165, 32))
            subtitle_rect = subtitle_surface.get_rect(center=(screen_width // 2, y_offset))
            screen.blit(subtitle_surface, subtitle_rect)
            y_offset += self.subtitle_font.get_height() + 20
        
        # Set up content area clipping
        content_area_rect = pygame.Rect(content_x, y_offset, content_width, content_bottom - y_offset)
        original_clip = screen.get_clip()
        screen.set_clip(content_area_rect)
            
        # Draw content elements with proper bounds checking
        for elem_type, elem_data in self.content_elements:
            # Check if we have space for this element
            if y_offset >= content_bottom - 20:  # Leave some margin
                # Add "..." to indicate more content
                if self.content_font:
                    more_text = self.content_font.render("...", True, (160, 160, 160))
                    more_rect = more_text.get_rect(center=(screen_width // 2, y_offset))
                    screen.blit(more_text, more_rect)
                break
            
            if elem_type == 'text':
                if elem_data['text'].strip():  # Only render non-empty text
                    text_surface = self.content_font.render(elem_data['text'], True, elem_data['color'])
                    if elem_data['center']:
                        text_rect = text_surface.get_rect(center=(screen_width // 2, y_offset))
                    else:
                        text_rect = text_surface.get_rect(left=content_x, top=y_offset)
                    screen.blit(text_surface, text_rect)
                    y_offset += self.content_font.get_height() + 5
                
            elif elem_type == 'header':
                if elem_data['text'].strip():
                    header_surface = self.button_font.render(elem_data['text'], True, elem_data['color'])
                    header_rect = header_surface.get_rect(left=content_x, top=y_offset)
                    screen.blit(header_surface, header_rect)
                    y_offset += self.button_font.get_height() + 8
                
            elif elem_type == 'spacer':
                y_offset += min(elem_data['height'], content_bottom - y_offset - 10)
                
            elif elem_type == 'option_list':
                # Draw label
                if elem_data['label']:
                    label_surface = self.button_font.render(elem_data['label'], True, (218, 165, 32))
                    label_rect = label_surface.get_rect(left=panel_x + 40, top=y_offset)
                    screen.blit(label_surface, label_rect)
                    y_offset += 35
                    
                # Draw options
                for i, option in enumerate(elem_data['options']):
                    option_rect = pygame.Rect(panel_x + 60, y_offset, self.width - 120, 30)
                    
                    is_selected = i == elem_data['selected_index']
                    
                    if is_selected:
                        # Selected option
                        option_surface = pygame.Surface((option_rect.width, option_rect.height), pygame.SRCALPHA)
                        pygame.draw.rect(option_surface, (85, 107, 47, 180), option_surface.get_rect(), border_radius=4)
                        screen.blit(option_surface, option_rect)
                        pygame.draw.rect(screen, (144, 238, 144), option_rect, 2, border_radius=4)
                        text_color = (255, 255, 255)
                    else:
                        # Normal option
                        option_surface = pygame.Surface((option_rect.width, option_rect.height), pygame.SRCALPHA)
                        pygame.draw.rect(option_surface, (40, 50, 35, 100), option_surface.get_rect(), border_radius=4)
                        screen.blit(option_surface, option_rect)
                        pygame.draw.rect(screen, (80, 100, 70), option_rect, 1, border_radius=4)
                        text_color = (180, 180, 180)
                        
                    # Option text
                    option_text = option if isinstance(option, str) else str(option)
                    text_surface = self.content_font.render(option_text, True, text_color)
                    text_rect = text_surface.get_rect(left=option_rect.left + 10, centery=option_rect.centery)
                    screen.blit(text_surface, text_rect)
                    
                    y_offset += 35
                    
            elif elem_type == 'input_field':
                field = elem_data
                # Label
                label_surface = self.button_font.render(field['label'], True, (218, 165, 32))
                label_rect = label_surface.get_rect(left=panel_x + 40, top=y_offset)
                screen.blit(label_surface, label_rect)
                y_offset += 30
                
                # Input box
                field_rect = pygame.Rect(panel_x + 40, y_offset, self.width - 80, 35)
                field['rect'] = field_rect  # Store for click detection
                
                # Also update the corresponding field in input_fields list for event handling
                for input_field in self.input_fields:
                    if input_field['id'] == field['id']:
                        input_field['rect'] = field_rect
                        input_field['value'] = field['value']
                        input_field['active'] = field['active']
                        break
                
                if field['active']:
                    # Active field
                    field_surface = pygame.Surface((field_rect.width, field_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(field_surface, (85, 107, 47, 180), field_surface.get_rect(), border_radius=6)
                    screen.blit(field_surface, field_rect)
                    pygame.draw.rect(screen, (144, 238, 144), field_rect, 2, border_radius=6)
                else:
                    # Inactive field
                    field_surface = pygame.Surface((field_rect.width, field_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(field_surface, (40, 50, 35, 150), field_surface.get_rect(), border_radius=6)
                    screen.blit(field_surface, field_rect)
                    pygame.draw.rect(screen, (80, 100, 70), field_rect, 1, border_radius=6)
                    
                # Field text
                display_text = field['value']
                if field['active'] and (pygame.time.get_ticks() // 500) % 2:
                    display_text += "|"  # Blinking cursor
                    
                if display_text and field['value']:  # Has actual value
                    text_surface = self.content_font.render(display_text, True, (255, 255, 255))
                    text_rect = text_surface.get_rect(left=field_rect.left + 10, centery=field_rect.centery)
                    screen.blit(text_surface, text_rect)
                elif field['placeholder']:  # Show placeholder
                    placeholder_surface = self.content_font.render(field['placeholder'], True, (160, 160, 160))
                    placeholder_rect = placeholder_surface.get_rect(left=field_rect.left + 10, centery=field_rect.centery)
                    screen.blit(placeholder_surface, placeholder_rect)
                    
                y_offset += 45
            
        # Restore original clipping
        screen.set_clip(original_clip)
        
        # Draw buttons at the bottom of the panel (within panel bounds)
        if self.buttons:
            button_height = 40
            button_margin = 20
            button_y = panel_y + self.height - button_height - button_margin
            button_width = 140  # Smaller buttons for better spacing
            
            # Stack buttons vertically with primary button on top
            button_vertical_spacing = 15
            button_x = (screen_width - button_width) // 2  # Center horizontally
            
            for i, button in enumerate(self.buttons):
                # Adjust Y position for stacked layout
                current_button_y = button_y - (len(self.buttons) - 1 - i) * (40 + button_vertical_spacing)
                button_rect = pygame.Rect(button_x, current_button_y, button_width, 40)
                button['rect'] = button_rect  # Store for click detection
                
                if button['enabled']:
                    if button['selected']:
                        # Selected/hovered button
                        button_surface = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
                        pygame.draw.rect(button_surface, (85, 107, 47, 200), button_surface.get_rect(), border_radius=6)
                        screen.blit(button_surface, button_rect)
                        pygame.draw.rect(screen, (144, 238, 144), button_rect, 2, border_radius=6)
                        text_color = (255, 255, 255)
                    else:
                        # Normal button
                        button_surface = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
                        pygame.draw.rect(button_surface, (60, 80, 40, 150), button_surface.get_rect(), border_radius=6)
                        screen.blit(button_surface, button_rect)
                        pygame.draw.rect(screen, (100, 120, 90), button_rect, 1, border_radius=6)
                        text_color = (220, 220, 220)
                else:
                    # Disabled button
                    button_surface = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(button_surface, (40, 40, 40, 100), button_surface.get_rect(), border_radius=6)
                    screen.blit(button_surface, button_rect)
                    pygame.draw.rect(screen, (60, 60, 60), button_rect, 1, border_radius=6)
                    text_color = (120, 120, 120)
                    
                # Button text
                text_surface = self.button_font.render(button['text'], True, text_color)
                text_rect = text_surface.get_rect(center=button_rect.center)
                screen.blit(text_surface, text_rect)
                
    def handle_event(self, event: pygame.event.Event) -> dict:
        """Handle events and return any actions"""
        result = {'type': None, 'id': None, 'value': None}
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            # Check buttons
            for button in self.buttons:
                if button['rect'] and button['rect'].collidepoint(mouse_pos) and button['enabled']:
                    result = {'type': 'button_click', 'id': button['id'], 'value': button['text']}
                    return result
                    
            # Check input fields
            for field in self.input_fields:
                if field['rect'] and field['rect'].collidepoint(mouse_pos):
                    # Deactivate all fields first
                    for f in self.input_fields:
                        f['active'] = False
                    # Activate clicked field
                    field['active'] = True
                    result = {'type': 'field_focus', 'id': field['id'], 'value': field['value']}
                    return result
                    
        elif event.type == pygame.KEYDOWN:
            # Handle text input for active fields
            for field in self.input_fields:
                if field['active']:
                    if event.key == pygame.K_BACKSPACE:
                        field['value'] = field['value'][:-1]
                        result = {'type': 'field_change', 'id': field['id'], 'value': field['value']}
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        # Handle Enter key - deactivate field (submit)
                        field['active'] = False
                        result = {'type': 'field_submit', 'id': field['id'], 'value': field['value']}
                    elif event.key == pygame.K_TAB:
                        # Move to next field
                        current_index = self.input_fields.index(field)
                        field['active'] = False
                        next_index = (current_index + 1) % len(self.input_fields)
                        self.input_fields[next_index]['active'] = True
                        result = {'type': 'field_focus', 'id': self.input_fields[next_index]['id'], 'value': self.input_fields[next_index]['value']}
                    elif event.unicode and len(field['value']) < 30:
                        field['value'] += event.unicode
                        result = {'type': 'field_change', 'id': field['id'], 'value': field['value']}
                    return result
                    
        return result

class UIManager:
    """Main UI management class that handles rendering and events"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.elements: List[UIElement] = []
        self.theme = UITheme()
        
    def add_element(self, element: UIElement) -> 'UIManager':
        """Add UI element"""
        self.elements.append(element)
        return self
    
    def remove_element(self, element: UIElement) -> 'UIManager':
        """Remove UI element"""
        if element in self.elements:
            self.elements.remove(element)
        return self
    
    def clear(self) -> 'UIManager':
        """Clear all elements"""
        self.elements.clear()
        return self
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle event, return True if consumed by any element"""
        for element in reversed(self.elements):  # Top elements first
            if element.handle_event(event):
                return True
        return False
    
    def render(self) -> None:
        """Render all UI elements"""
        for element in self.elements:
            element.render(self.screen)
    
    def draw_warm_gradient_background(self) -> None:
        """Draw the game's signature warm gradient background"""
        # Top color (darker)
        top_color = (25, 35, 20)  # Dark green
        # Bottom color (lighter)
        bottom_color = (45, 60, 35)  # Medium green
        
        # Get actual screen dimensions
        actual_width = self.screen.get_width()
        actual_height = self.screen.get_height()
        
        # Draw gradient
        for y in range(actual_height):
            ratio = y / actual_height
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            
            pygame.draw.line(self.screen, (r, g, b), (0, y), (actual_width, y))