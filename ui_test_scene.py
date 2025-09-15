#!/usr/bin/env python3
"""
UI Test Scene - Field Station Theme Visualization
A test environment for developing the Field Research Station visual theme
"""

import pygame
import sys
from design_constants import *

# Initialize Pygame
pygame.init()

# Screen setup
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Field Station - UI Theme Test")

# Fonts
font_title = pygame.font.Font(None, FONT_HEADING_2)
font_body = pygame.font.Font(None, FONT_BODY_BASE)
font_small = pygame.font.Font(None, FONT_CAPTION)

def draw_research_panel(screen, x, y, w, h, style="primary", title=None):
    """Draw a field research themed panel with agricultural notebook aesthetic"""
    
    # 1. Shadow (stronger for higher hierarchy)
    shadow_offset = 6 if style == "primary" else 4 if style == "secondary" else 2
    shadow_alpha = 80 if style == "primary" else 60 if style == "secondary" else 40
    
    shadow_surf = pygame.Surface((w, h))
    shadow_surf.set_alpha(shadow_alpha)
    shadow_surf.fill(BLACK)
    screen.blit(shadow_surf, (x + shadow_offset, y + shadow_offset))
    
    # 2. Main background
    if style == "primary":
        bg_color = SURFACE_PRIMARY
        alpha = 255
        border_width = 3
    elif style == "secondary":
        bg_color = SURFACE_RAISED
        alpha = 220
        border_width = 2
    else:  # tertiary
        bg_color = SURFACE_OVERLAY
        alpha = 180
        border_width = 1
    
    # Create panel surface
    panel_surf = pygame.Surface((w, h))
    if alpha < 255:
        panel_surf.set_alpha(alpha)
    panel_surf.fill(bg_color)
    
    # 3. Add graph paper pattern (subtle)
    if style in ["primary", "secondary"]:
        grid_size = 16 if style == "primary" else 24
        grid_alpha = 15 if style == "primary" else 10
        grid_color = (*TEXT_SECONDARY, grid_alpha)
        
        # Vertical lines
        for gx in range(grid_size, w, grid_size):
            pygame.draw.line(panel_surf, grid_color, (gx, 0), (gx, h))
        # Horizontal lines
        for gy in range(grid_size, h, grid_size):
            pygame.draw.line(panel_surf, grid_color, (0, gy), (w, gy))
    
    # 4. Add soil gradient at bottom (subtle earth connection)
    if style == "primary":
        gradient_height = 40
        for i in range(gradient_height):
            alpha = int(30 * (1 - i / gradient_height))
            color = (*SOIL_MEDIUM, alpha)
            pygame.draw.line(panel_surf, color, (0, h - i), (w, h - i))
    
    # Blit the panel
    screen.blit(panel_surf, (x, y))
    
    # 5. Draw borders
    # Outer border
    pygame.draw.rect(screen, SURFACE_BORDER, (x, y, w, h), border_width)
    
    # Inner border for primary panels (double-line effect)
    if style == "primary":
        pygame.draw.rect(screen, (*SURFACE_BORDER, 128), (x+4, y+4, w-8, h-8), 1)
    
    # 6. Corner measurement ticks (scientific notebook style)
    if style in ["primary", "secondary"]:
        tick_length = 12 if style == "primary" else 8
        tick_color = TEXT_SECONDARY
        
        # Top-left corner
        for i in range(3):
            offset = i * 4
            pygame.draw.line(screen, tick_color, (x + offset, y), (x + offset, y + tick_length - offset), 1)
            pygame.draw.line(screen, tick_color, (x, y + offset), (x + tick_length - offset, y + offset), 1)
        
        # Top-right corner
        for i in range(3):
            offset = i * 4
            pygame.draw.line(screen, tick_color, (x + w - offset, y), (x + w - offset, y + tick_length - offset), 1)
            pygame.draw.line(screen, tick_color, (x + w, y + offset), (x + w - tick_length + offset, y + offset), 1)
        
        # Bottom corners (lighter)
        tick_color = (*TEXT_SECONDARY, 128)
        # Bottom-left
        for i in range(2):
            offset = i * 4
            pygame.draw.line(screen, tick_color, (x + offset, y + h), (x + offset, y + h - tick_length + offset), 1)
        # Bottom-right
        for i in range(2):
            offset = i * 4
            pygame.draw.line(screen, tick_color, (x + w - offset, y + h), (x + w - offset, y + h - tick_length + offset), 1)
    
    # 7. Header with title (if provided)
    if title:
        header_height = PANEL_HEADER_HEIGHT
        
        # Header background
        header_color = SURFACE_RAISED if style == "primary" else SURFACE_OVERLAY
        pygame.draw.rect(screen, header_color, (x + 1, y + 1, w - 2, header_height))
        
        # Header separator line (notebook style)
        pygame.draw.line(screen, SURFACE_BORDER, (x, y + header_height), (x + w, y + header_height), 1)
        
        # Dotted line effect (like perforated notebook)
        for dx in range(0, w, 8):
            pygame.draw.circle(screen, (*SURFACE_BORDER, 128), (x + dx + 4, y + header_height), 1)
        
        # Title text
        title_surf = font_body.render(title, True, TEXT_PRIMARY)
        title_rect = title_surf.get_rect(midleft=(x + SPACE_MD, y + header_height // 2))
        screen.blit(title_surf, title_rect)
        
        # Small botanical decoration in corner (placeholder)
        decoration = "🌱" if style == "primary" else "•"
        deco_surf = font_small.render(decoration, True, GRASS_MEDIUM)
        deco_rect = deco_surf.get_rect(midright=(x + w - SPACE_SM, y + header_height // 2))
        screen.blit(deco_surf, deco_rect)
    
    return (x, y, w, h)


def draw_button_examples(screen, x, y):
    """Draw example buttons with the theme"""
    
    # Primary button
    btn_width, btn_height = 120, BUTTON_HEIGHT
    
    # Primary button - normal state
    btn_rect = pygame.Rect(x, y, btn_width, btn_height)
    pygame.draw.rect(screen, GRASS_MEDIUM, btn_rect, border_radius=BUTTON_BORDER_RADIUS)
    pygame.draw.rect(screen, GRASS_DARK, btn_rect, 2, border_radius=BUTTON_BORDER_RADIUS)
    
    text_surf = font_body.render("Plant Crop", True, TEXT_PRIMARY)
    text_rect = text_surf.get_rect(center=btn_rect.center)
    screen.blit(text_surf, text_rect)
    
    # Primary button - hover state
    btn_rect = pygame.Rect(x + 140, y, btn_width, btn_height)
    pygame.draw.rect(screen, GRASS_LIGHT, btn_rect, border_radius=BUTTON_BORDER_RADIUS)
    pygame.draw.rect(screen, GRASS_DARK, btn_rect, 2, border_radius=BUTTON_BORDER_RADIUS)
    
    text_surf = font_body.render("Plant (Hover)", True, TEXT_PRIMARY)
    text_rect = text_surf.get_rect(center=btn_rect.center)
    screen.blit(text_surf, text_rect)
    
    # Secondary button
    btn_rect = pygame.Rect(x, y + 50, btn_width, btn_height)
    pygame.draw.rect(screen, SURFACE_BORDER, btn_rect, 2, border_radius=BUTTON_BORDER_RADIUS)
    
    text_surf = font_body.render("Cancel", True, TEXT_PRIMARY)
    text_rect = text_surf.get_rect(center=btn_rect.center)
    screen.blit(text_surf, text_rect)
    
    # Icon button
    icon_size = ICON_BUTTON_SIZE
    icon_rect = pygame.Rect(x + 140, y + 50, icon_size, icon_size)
    pygame.draw.rect(screen, SURFACE_RAISED, icon_rect, border_radius=BUTTON_BORDER_RADIUS)
    pygame.draw.rect(screen, SURFACE_BORDER, icon_rect, 1, border_radius=BUTTON_BORDER_RADIUS)
    
    icon_surf = font_body.render("?", True, TEXT_SECONDARY)
    icon_rect_center = icon_surf.get_rect(center=icon_rect.center)
    screen.blit(icon_surf, icon_rect_center)


def draw_input_examples(screen, x, y):
    """Draw example input controls"""
    
    # Text input field
    input_rect = pygame.Rect(x, y, 200, INPUT_HEIGHT)
    pygame.draw.rect(screen, SURFACE_PRIMARY, input_rect, border_radius=INPUT_BORDER_RADIUS)
    pygame.draw.rect(screen, SURFACE_BORDER, input_rect, 1, border_radius=INPUT_BORDER_RADIUS)
    
    placeholder = font_small.render("Farm Name...", True, TEXT_DISABLED)
    screen.blit(placeholder, (input_rect.x + SPACE_XS, input_rect.centery - placeholder.get_height()//2))
    
    # Dropdown (closed)
    dropdown_rect = pygame.Rect(x, y + 45, 200, INPUT_HEIGHT)
    pygame.draw.rect(screen, SURFACE_RAISED, dropdown_rect, border_radius=INPUT_BORDER_RADIUS)
    pygame.draw.rect(screen, SURFACE_BORDER, dropdown_rect, 1, border_radius=INPUT_BORDER_RADIUS)
    
    dropdown_text = font_small.render("Select Season ▼", True, TEXT_PRIMARY)
    screen.blit(dropdown_text, (dropdown_rect.x + SPACE_XS, dropdown_rect.centery - dropdown_text.get_height()//2))
    
    # Checkbox examples
    check_y = y + 90
    # Unchecked
    checkbox_rect = pygame.Rect(x, check_y, 16, 16)
    pygame.draw.rect(screen, SURFACE_PRIMARY, checkbox_rect)
    pygame.draw.rect(screen, SURFACE_BORDER, checkbox_rect, 1)
    label = font_small.render("Auto-harvest", True, TEXT_PRIMARY)
    screen.blit(label, (x + 24, check_y))
    
    # Checked
    checkbox_rect = pygame.Rect(x + 120, check_y, 16, 16)
    pygame.draw.rect(screen, SURFACE_PRIMARY, checkbox_rect)
    pygame.draw.rect(screen, SURFACE_BORDER, checkbox_rect, 1)
    # Draw checkmark
    pygame.draw.lines(screen, SUCCESS_GREEN, False, 
                     [(x + 123, check_y + 8), (x + 127, check_y + 12), (x + 133, check_y + 4)], 2)
    label = font_small.render("Enabled", True, TEXT_PRIMARY)
    screen.blit(label, (x + 144, check_y))


def main():
    """Main loop for UI test scene"""
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Clear screen with a pleasant background
        SCREEN.fill(get_seasonal_colors("spring")["background"])
        
        # Draw title
        title = font_title.render("Field Station - UI Theme Test", True, GRASS_DARK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 40))
        SCREEN.blit(title, title_rect)
        
        # Draw panel examples
        panel_y = 100
        
        # Primary panel (menu style)
        draw_research_panel(SCREEN, 50, panel_y, 350, 250, "primary", "Primary Panel - Menu")
        
        # Add some content to primary panel
        content_y = panel_y + 50
        sample_text = font_body.render("Game Menu Options:", True, TEXT_PRIMARY)
        SCREEN.blit(sample_text, (70, content_y))
        
        menu_items = ["New Farm", "Continue", "Settings", "Achievements"]
        for i, item in enumerate(menu_items):
            item_text = font_small.render(f"• {item}", True, TEXT_SECONDARY)
            SCREEN.blit(item_text, (80, content_y + 30 + i * 25))
        
        # Secondary panel (info style)
        draw_research_panel(SCREEN, 450, panel_y, 300, 200, "secondary", "Secondary - Info")
        
        # Add some content
        info_y = panel_y + 50
        info_lines = [
            "Soil Quality: 0.75",
            "Moisture: 0.60",
            "Nitrogen: 0.45",
            "Season: Spring"
        ]
        for i, line in enumerate(info_lines):
            color = SUCCESS_GREEN if i == 0 else WARNING_YELLOW if i == 2 else TEXT_PRIMARY
            info_text = font_small.render(line, True, color)
            SCREEN.blit(info_text, (470, info_y + i * 20))
        
        # Tertiary panel (tooltip style)
        draw_research_panel(SCREEN, 800, panel_y, 200, 100, "tertiary", None)
        
        # Tooltip content
        tooltip_text = font_small.render("Quick Tip:", True, TEXT_PRIMARY)
        SCREEN.blit(tooltip_text, (810, panel_y + 10))
        
        tip_text = "Click tiles to interact"
        tip_lines = [tip_text[i:i+20] for i in range(0, len(tip_text), 20)]
        for i, line in enumerate(tip_lines):
            line_surf = font_small.render(line, True, TEXT_SECONDARY)
            SCREEN.blit(line_surf, (810, panel_y + 30 + i * 18))
        
        # Draw UI component examples
        components_y = panel_y + 280
        
        # Section label
        section_label = font_body.render("Component Examples:", True, GRASS_DARK)
        SCREEN.blit(section_label, (50, components_y))
        
        # Buttons
        draw_button_examples(SCREEN, 50, components_y + 30)
        
        # Input controls
        draw_input_examples(SCREEN, 400, components_y + 30)
        
        # Color palette display
        palette_y = components_y + 150
        palette_label = font_body.render("Theme Colors:", True, GRASS_DARK)
        SCREEN.blit(palette_label, (50, palette_y))
        
        # Draw color swatches
        colors = [
            ("Soil", SOIL_MEDIUM),
            ("Grass", GRASS_MEDIUM),
            ("Water", WATER_MEDIUM),
            ("Success", SUCCESS_GREEN),
            ("Warning", WARNING_YELLOW),
            ("Error", ERROR_RED)
        ]
        
        for i, (name, color) in enumerate(colors):
            x = 50 + (i % 3) * 150
            y = palette_y + 30 + (i // 3) * 40
            
            # Swatch
            pygame.draw.rect(SCREEN, color, (x, y, 30, 30))
            pygame.draw.rect(SCREEN, SURFACE_BORDER, (x, y, 30, 30), 1)
            
            # Label
            label = font_small.render(name, True, TEXT_PRIMARY)
            SCREEN.blit(label, (x + 40, y + 8))
        
        # Instructions
        instructions = font_small.render("Press ESC to exit", True, TEXT_DISABLED)
        inst_rect = instructions.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
        SCREEN.blit(instructions, inst_rect)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()