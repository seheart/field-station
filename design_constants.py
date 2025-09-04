"""
Field Station Design System Constants
A comprehensive set of design tokens for consistent UI/UX
"""

# ============================================================================
# COLOR PALETTE
# ============================================================================

# Core Earth Tones - Primary Palette
SOIL_DARK = (44, 24, 16)        # #2C1810 - Rich dark earth
SOIL_MEDIUM = (74, 52, 38)      # #4A3426 - Fertile soil  
SOIL_LIGHT = (107, 78, 61)      # #6B4E3D - Dry earth

GRASS_DARK = (45, 80, 22)       # #2D5016 - Deep grass
GRASS_MEDIUM = (75, 124, 47)    # #4B7C2F - Healthy vegetation
GRASS_LIGHT = (115, 179, 71)    # #73B347 - Young growth

WATER_DARK = (27, 58, 75)       # #1B3A4B - Deep water
WATER_MEDIUM = (46, 95, 124)    # #2E5F7C - Clean water
WATER_LIGHT = (74, 144, 164)    # #4A90A4 - Shallow water

# Seasonal Accent Colors
SPRING_GREEN = (143, 209, 79)   # #8FD14F - New growth
SUMMER_GOLD = (255, 184, 51)    # #FFB833 - Warm sun
FALL_ORANGE = (230, 126, 34)    # #E67E22 - Harvest time
WINTER_BLUE = (133, 193, 233)   # #85C1E9 - Frost & snow

# Semantic Colors - Status & Feedback
SUCCESS_GREEN = (39, 174, 96)   # #27AE60 - Positive actions
WARNING_YELLOW = (243, 156, 18)  # #F39C12 - Caution states
ERROR_RED = (231, 76, 60)       # #E74C3C - Problems/errors
INFO_BLUE = (52, 152, 219)      # #3498DB - Information
NEUTRAL_GRAY = (127, 140, 141)  # #7F8C8D - Inactive states

# UI Surface Colors
SURFACE_PRIMARY = (26, 26, 26)   # #1A1A1A - Main UI backgrounds
SURFACE_RAISED = (45, 45, 45)    # #2D2D2D - Elevated elements
SURFACE_OVERLAY = (58, 58, 58)   # #3A3A3A - Modals/popups
SURFACE_BORDER = (74, 74, 74)    # #4A4A4A - Borders/dividers

# Text Colors
TEXT_PRIMARY = (255, 255, 255)   # #FFFFFF - Main content
TEXT_SECONDARY = (184, 184, 184) # #B8B8B8 - Supporting content
TEXT_DISABLED = (102, 102, 102)  # #666666 - Inactive text
TEXT_INVERSE = (26, 26, 26)      # #1A1A1A - Text on light bg

# Legacy colors (for backward compatibility - will phase out)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = SUCCESS_GREEN
LIGHT_GREEN = GRASS_LIGHT
DARK_GREEN = GRASS_DARK
RED = ERROR_RED
YELLOW = WARNING_YELLOW
BLUE = INFO_BLUE
LIGHT_BLUE = WATER_LIGHT
GRAY = NEUTRAL_GRAY
DARK_GRAY = SURFACE_PRIMARY
LIGHT_BROWN = SOIL_LIGHT
BROWN = SOIL_MEDIUM

# ============================================================================
# TYPOGRAPHY SCALE
# ============================================================================

# Font Sizes (in pixels)
FONT_HEADING_1 = 32    # Major sections
FONT_HEADING_2 = 24    # Panel titles
FONT_HEADING_3 = 20    # Subsections
FONT_BODY_LARGE = 18   # Important text
FONT_BODY_BASE = 16    # Standard text
FONT_BODY_SMALL = 14   # Secondary info
FONT_CAPTION = 12      # Labels/hints
FONT_MICRO = 10        # Tiny details

# Line Heights (in pixels)
LINE_HEIGHT_HEADING_1 = 40
LINE_HEIGHT_HEADING_2 = 32
LINE_HEIGHT_HEADING_3 = 28
LINE_HEIGHT_BODY = 24
LINE_HEIGHT_SMALL = 20
LINE_HEIGHT_CAPTION = 16
LINE_HEIGHT_MICRO = 14

# Font Weights (for systems that support it)
FONT_WEIGHT_BOLD = 700
FONT_WEIGHT_SEMIBOLD = 600
FONT_WEIGHT_MEDIUM = 500
FONT_WEIGHT_REGULAR = 400

# ============================================================================
# SPACING SYSTEM (8px base unit)
# ============================================================================

SPACE_XXS = 4     # 0.5 units - Tight spacing
SPACE_XS = 8      # 1 unit - Compact elements
SPACE_SM = 12     # 1.5 units - Related items
SPACE_MD = 16     # 2 units - Standard spacing
SPACE_LG = 24     # 3 units - Section breaks
SPACE_XL = 32     # 4 units - Major sections
SPACE_XXL = 48    # 6 units - Page margins
SPACE_XXXL = 64   # 8 units - Large separations

# Component-specific spacing
PANEL_PADDING = SPACE_MD
BUTTON_PADDING_H = SPACE_MD
BUTTON_PADDING_V = SPACE_XS
LIST_ITEM_GAP = SPACE_XS
SECTION_GAP = SPACE_LG
FORM_FIELD_GAP = SPACE_MD

# ============================================================================
# LAYOUT DIMENSIONS
# ============================================================================

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SAFE_AREA_PADDING = SPACE_XL

# Panel dimensions
PANEL_MIN_WIDTH = 240
PANEL_MAX_WIDTH = 480
PANEL_HEADER_HEIGHT = 32
PANEL_BORDER_RADIUS = 8

# Modal/Popup dimensions
MODAL_MIN_WIDTH = 320
MODAL_MAX_WIDTH = 640
MODAL_PADDING = SPACE_LG
MODAL_BORDER_RADIUS = 12

# Button dimensions
BUTTON_HEIGHT = 40
BUTTON_MIN_WIDTH = 80
BUTTON_BORDER_RADIUS = 6
ICON_BUTTON_SIZE = 32

# Input dimensions
INPUT_HEIGHT = 36
INPUT_BORDER_RADIUS = 4

# ============================================================================
# ICON SIZES
# ============================================================================

ICON_SMALL = 16    # Inline text icons
ICON_MEDIUM = 24   # Standard buttons
ICON_LARGE = 32    # Primary actions
ICON_XLARGE = 48   # Feature highlights

# ============================================================================
# ANIMATION TIMINGS (in milliseconds)
# ============================================================================

ANIM_INSTANT = 0      # No animation
ANIM_QUICK = 150      # Micro interactions
ANIM_NORMAL = 250     # Standard transitions
ANIM_SLOW = 400       # Complex animations
ANIM_VERY_SLOW = 600  # Page transitions

# ============================================================================
# Z-INDEX LAYERS
# ============================================================================

Z_BACKGROUND = 0
Z_TILES = 10
Z_OBJECTS = 20
Z_EFFECTS = 30
Z_UI_PANELS = 40
Z_UI_POPUPS = 50
Z_UI_MODALS = 60
Z_UI_TOOLTIPS = 70
Z_UI_NOTIFICATIONS = 80
Z_DEBUG = 90

# ============================================================================
# GAME-SPECIFIC CONSTANTS
# ============================================================================

# Tile rendering
TILE_WIDTH = 64
TILE_HEIGHT = 32

# Grid dimensions
GRID_WIDTH = 3
GRID_HEIGHT = 3

# Zoom constraints
ZOOM_MIN = 0.3
ZOOM_MAX = 10.0
ZOOM_DEFAULT = 2.0

# Time/Speed settings
SPEEDS = [1, 2, 5, 10]
DEFAULT_SPEED = 1
DAY_DURATION_MS = 30000  # 30 seconds per day at 1x speed

# ============================================================================
# UI STATE COLORS
# ============================================================================

def get_button_colors(button_type="primary", state="normal"):
    """Get button colors based on type and state"""
    if button_type == "primary":
        if state == "hover":
            return {"bg": GRASS_LIGHT, "text": TEXT_PRIMARY}
        elif state == "active":
            return {"bg": GRASS_DARK, "text": TEXT_PRIMARY}
        elif state == "disabled":
            return {"bg": NEUTRAL_GRAY, "text": TEXT_DISABLED}
        else:  # normal
            return {"bg": GRASS_MEDIUM, "text": TEXT_PRIMARY}
    
    elif button_type == "secondary":
        if state == "hover":
            return {"bg": SURFACE_RAISED, "text": TEXT_PRIMARY, "border": SURFACE_BORDER}
        elif state == "active":
            return {"bg": SURFACE_PRIMARY, "text": TEXT_PRIMARY, "border": SURFACE_BORDER}
        elif state == "disabled":
            return {"bg": None, "text": TEXT_DISABLED, "border": TEXT_DISABLED}
        else:  # normal
            return {"bg": None, "text": TEXT_PRIMARY, "border": SURFACE_BORDER}
    
    else:  # icon button
        if state == "hover":
            return {"bg": SURFACE_OVERLAY, "icon": TEXT_PRIMARY}
        elif state == "active":
            return {"bg": SURFACE_PRIMARY, "icon": TEXT_PRIMARY}
        elif state == "disabled":
            return {"bg": SURFACE_RAISED, "icon": TEXT_DISABLED}
        else:  # normal
            return {"bg": SURFACE_RAISED, "icon": TEXT_SECONDARY}


def get_seasonal_colors(season):
    """Get color scheme based on season"""
    seasons = {
        "spring": {
            "primary": SPRING_GREEN,
            "background": (235, 245, 235),  # Light green tint
            "accent": GRASS_LIGHT
        },
        "summer": {
            "primary": SUMMER_GOLD,
            "background": (255, 250, 240),  # Warm tint
            "accent": (255, 204, 102)  # Light gold
        },
        "fall": {
            "primary": FALL_ORANGE,
            "background": (250, 240, 230),  # Warm neutral
            "accent": (204, 102, 51)  # Burnt orange
        },
        "winter": {
            "primary": WINTER_BLUE,
            "background": (240, 245, 250),  # Cool tint
            "accent": (204, 229, 255)  # Light blue
        }
    }
    return seasons.get(season.lower(), seasons["spring"])


def get_soil_quality_color(quality):
    """Get color based on soil quality value"""
    if quality > 0.7:
        return SUCCESS_GREEN
    elif quality > 0.4:
        return WARNING_YELLOW
    else:
        return ERROR_RED


def get_moisture_color(moisture):
    """Get color based on moisture level"""
    if moisture > 0.7:
        return WATER_DARK  # Too wet
    elif moisture > 0.5:
        return WATER_MEDIUM  # Good moisture
    elif moisture > 0.3:
        return WATER_LIGHT  # Getting dry
    else:
        return SOIL_LIGHT  # Too dry


def get_nitrogen_color(nitrogen):
    """Get color based on nitrogen level"""
    if nitrogen > 0.5:
        return SUCCESS_GREEN
    elif nitrogen > 0.3:
        return WARNING_YELLOW
    else:
        return ERROR_RED