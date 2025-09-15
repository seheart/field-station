#!/usr/bin/env python3
"""
Create hand-drawn style background art for Field Station menu
Inspired by organic, flowing line art with stone and natural elements
"""

import pygame
import math
import random
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Canvas size
WIDTH = 1200
HEIGHT = 800

# Colors matching our organic palette
BACKGROUND_COLOR = (139, 115, 85)  # Warm soil medium
LINE_COLORS = [
    (75, 59, 48),      # Soil dark - main lines
    (160, 145, 107),   # Soil light - lighter lines
    (107, 123, 94),    # Sage green - vegetation
    (122, 132, 113),   # Soft meadow - subtle lines
    (93, 107, 79),     # Deep forest - accent lines
]

def create_organic_line_path(start_x: float, start_y: float, end_x: float, end_y: float, 
                           segments: int = 20, wobble: float = 0.3) -> List[Tuple[float, float]]:
    """Create an organic, hand-drawn style line with natural variation"""
    points = []
    
    for i in range(segments + 1):
        t = i / segments
        
        # Basic linear interpolation
        x = start_x + (end_x - start_x) * t
        y = start_y + (end_y - start_y) * t
        
        # Add organic wobble using sine waves with different frequencies
        wobble_x = wobble * (
            math.sin(t * math.pi * 3 + random.uniform(0, math.pi)) * 0.6 +
            math.sin(t * math.pi * 7 + random.uniform(0, math.pi)) * 0.3 +
            math.sin(t * math.pi * 13 + random.uniform(0, math.pi)) * 0.1
        )
        
        wobble_y = wobble * (
            math.cos(t * math.pi * 4 + random.uniform(0, math.pi)) * 0.5 +
            math.cos(t * math.pi * 8 + random.uniform(0, math.pi)) * 0.3 +
            math.cos(t * math.pi * 11 + random.uniform(0, math.pi)) * 0.2
        )
        
        points.append((x + wobble_x, y + wobble_y))
    
    return points

def draw_organic_stone_structure(surface: pygame.Surface):
    """Draw organic stone-like structures similar to the bridge reference"""
    
    # Main stone arch/bridge structure
    arch_center_x = WIDTH * 0.3
    arch_center_y = HEIGHT * 0.4
    arch_width = 200
    arch_height = 80
    
    # Draw arch outline with organic lines
    arch_points = []
    for angle in range(0, 181, 5):  # Half circle
        rad = math.radians(angle)
        x = arch_center_x + math.cos(rad) * arch_width * 0.5
        y = arch_center_y - math.sin(rad) * arch_height
        
        # Add organic variation
        wobble = 8 * (math.sin(angle * 0.1) * 0.6 + math.cos(angle * 0.07) * 0.4)
        x += wobble
        y += wobble * 0.5
        
        arch_points.append((x, y))
    
    # Draw the arch
    if len(arch_points) > 2:
        pygame.draw.lines(surface, LINE_COLORS[0], False, arch_points, 3)
        
        # Add inner arch line
        inner_arch = [(x, y - 15) for x, y in arch_points[10:-10]]
        if len(inner_arch) > 2:
            pygame.draw.lines(surface, LINE_COLORS[1], False, inner_arch, 2)
    
    # Stone blocks/masonry pattern
    block_lines = []
    for i in range(8):
        start_x = arch_center_x - arch_width * 0.4 + i * 25
        start_y = arch_center_y + 20
        end_x = start_x + random.uniform(15, 35)
        end_y = start_y + random.uniform(-5, 15)
        
        line_path = create_organic_line_path(start_x, start_y, end_x, end_y, 8, 3)
        block_lines.append(line_path)
    
    # Draw stone block lines
    for line_path in block_lines:
        if len(line_path) > 1:
            pygame.draw.lines(surface, LINE_COLORS[0], False, line_path, 2)

def draw_organic_foliage(surface: pygame.Surface):
    """Draw organic foliage and vegetation elements"""
    
    # Tree/bush clusters
    foliage_centers = [
        (WIDTH * 0.15, HEIGHT * 0.25),
        (WIDTH * 0.85, HEIGHT * 0.3),
        (WIDTH * 0.7, HEIGHT * 0.15),
    ]
    
    for center_x, center_y in foliage_centers:
        # Draw organic leaf clusters
        for i in range(12):
            angle = (i / 12) * 2 * math.pi
            radius = random.uniform(30, 60)
            
            leaf_x = center_x + math.cos(angle) * radius
            leaf_y = center_y + math.sin(angle) * radius * 0.7  # Flatten slightly
            
            # Create organic leaf shape
            leaf_points = []
            for j in range(8):
                leaf_angle = (j / 8) * 2 * math.pi
                leaf_radius = random.uniform(8, 15)
                
                px = leaf_x + math.cos(leaf_angle) * leaf_radius
                py = leaf_y + math.sin(leaf_angle) * leaf_radius * 0.6
                
                leaf_points.append((px, py))
            
            if len(leaf_points) > 2:
                pygame.draw.lines(surface, LINE_COLORS[2], True, leaf_points, 1)

def draw_flowing_water(surface: pygame.Surface):
    """Draw organic water flow lines"""
    
    # Main water flow
    water_start_x = WIDTH * 0.1
    water_start_y = HEIGHT * 0.7
    water_end_x = WIDTH * 0.6
    water_end_y = HEIGHT * 0.8
    
    # Multiple flowing lines for water effect
    for i in range(5):
        offset_y = i * 8 - 16
        start_y = water_start_y + offset_y
        end_y = water_end_y + offset_y + random.uniform(-10, 10)
        
        water_path = create_organic_line_path(
            water_start_x, start_y, water_end_x, end_y, 
            segments=30, wobble=12
        )
        
        # Draw water flow line
        if len(water_path) > 1:
            line_width = max(1, 3 - i)
            color_idx = min(3, i)
            pygame.draw.lines(surface, LINE_COLORS[color_idx], False, water_path, line_width)

def draw_organic_terrain_lines(surface: pygame.Surface):
    """Draw organic terrain contour lines"""
    
    # Terrain contours
    for level in range(4):
        base_y = HEIGHT * (0.6 + level * 0.08)
        
        # Create flowing terrain line
        terrain_points = []
        for x in range(0, WIDTH, 15):
            y = base_y + 30 * math.sin(x * 0.008 + level) + 15 * math.cos(x * 0.015 + level * 0.5)
            
            # Add organic variation
            organic_y = y + random.uniform(-5, 5)
            terrain_points.append((x, organic_y))
        
        if len(terrain_points) > 1:
            pygame.draw.lines(surface, LINE_COLORS[4], False, terrain_points, 1)

def draw_scattered_stones(surface: pygame.Surface):
    """Draw scattered stone elements"""
    
    stone_positions = [
        (WIDTH * 0.2, HEIGHT * 0.6),
        (WIDTH * 0.45, HEIGHT * 0.55),
        (WIDTH * 0.75, HEIGHT * 0.7),
        (WIDTH * 0.9, HEIGHT * 0.6),
    ]
    
    for stone_x, stone_y in stone_positions:
        # Draw organic stone shape
        stone_points = []
        num_points = random.randint(6, 10)
        
        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi
            radius = random.uniform(8, 18)
            
            px = stone_x + math.cos(angle) * radius
            py = stone_y + math.sin(angle) * radius * 0.8
            
            stone_points.append((px, py))
        
        if len(stone_points) > 2:
            pygame.draw.lines(surface, LINE_COLORS[0], True, stone_points, 2)

def create_background_art():
    """Create the main background art"""
    
    # Create surface
    surface = pygame.Surface((WIDTH, HEIGHT))
    surface.fill(BACKGROUND_COLOR)
    
    # Set random seed for consistent generation
    random.seed(42)
    
    # Draw all elements
    draw_organic_terrain_lines(surface)
    draw_flowing_water(surface)
    draw_scattered_stones(surface)
    draw_organic_stone_structure(surface)
    draw_organic_foliage(surface)
    
    return surface

def main():
    """Generate and save the background art"""
    print("Creating organic background art...")
    
    # Create the artwork
    background_surface = create_background_art()
    
    # Save as PNG
    output_path = "menu_background_organic.png"
    pygame.image.save(background_surface, output_path)
    
    print(f"Background art saved as: {output_path}")
    print(f"Dimensions: {WIDTH}x{HEIGHT}")
    
    # Also create a preview window
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Field Station - Background Art Preview")
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    running = False
        
        screen.blit(background_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
