# 🎨 Field Station Design System

**A comprehensive visual language for scientific agricultural simulation**

---

## 🌍 Design Philosophy

Field Station's design system bridges the gap between scientific accuracy and approachable gameplay. Our visual language emphasizes:

- **Scientific Clarity**: Information-rich displays without overwhelming complexity
- **Natural Aesthetics**: Earth tones and organic shapes reflecting agricultural themes
- **Accessibility First**: WCAG 2.1 AA compliant colors and readable typography
- **Consistent Interaction**: Predictable patterns for all user interactions

---

## 🎨 Color Palette

### Primary Colors - Earth & Agriculture

#### Core Palette
```
SOIL_DARK       #2C1810   RGB(44, 24, 16)     - Rich dark earth
SOIL_MEDIUM     #4A3426   RGB(74, 52, 38)     - Fertile soil
SOIL_LIGHT      #6B4E3D   RGB(107, 78, 61)    - Dry earth

GRASS_DARK      #2D5016   RGB(45, 80, 22)     - Deep grass
GRASS_MEDIUM    #4B7C2F   RGB(75, 124, 47)    - Healthy vegetation
GRASS_LIGHT     #73B347   RGB(115, 179, 71)   - Young growth

WATER_DARK      #1B3A4B   RGB(27, 58, 75)     - Deep water
WATER_MEDIUM    #2E5F7C   RGB(46, 95, 124)    - Clean water
WATER_LIGHT     #4A90A4   RGB(74, 144, 164)   - Shallow water
```

#### Seasonal Accents
```
SPRING_GREEN    #8FD14F   RGB(143, 209, 79)   - New growth
SUMMER_GOLD     #FFB833   RGB(255, 184, 51)   - Warm sun
FALL_ORANGE     #E67E22   RGB(230, 126, 34)   - Harvest time
WINTER_BLUE     #85C1E9   RGB(133, 193, 233)  - Frost & snow
```

### Semantic Colors - Status & Feedback

#### System States
```
SUCCESS_GREEN   #27AE60   RGB(39, 174, 96)    - Positive actions
WARNING_YELLOW  #F39C12   RGB(243, 156, 18)   - Caution states
ERROR_RED       #E74C3C   RGB(231, 76, 60)    - Problems/errors
INFO_BLUE       #3498DB   RGB(52, 152, 219)   - Information
NEUTRAL_GRAY    #7F8C8D   RGB(127, 140, 141)  - Inactive states
```

#### UI Surface Colors
```
SURFACE_PRIMARY   #1A1A1A   RGB(26, 26, 26)     - Main UI backgrounds
SURFACE_RAISED    #2D2D2D   RGB(45, 45, 45)     - Elevated elements
SURFACE_OVERLAY   #3A3A3A   RGB(58, 58, 58)     - Modals/popups
SURFACE_BORDER    #4A4A4A   RGB(74, 74, 74)     - Borders/dividers
```

### Accessibility Contrast Ratios

All color combinations meet WCAG 2.1 AA standards:
- **Text on backgrounds**: Minimum 4.5:1 contrast ratio
- **Large text**: Minimum 3:1 contrast ratio
- **Interactive elements**: Minimum 3:1 contrast ratio

---

## 📝 Typography System

### Font Stack

```css
Primary: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
Monospace: "JetBrains Mono", "Consolas", "Monaco", monospace
Display: "Outfit", "Inter", sans-serif
```

### Type Scale (Base: 16px)

```
HEADING_1    32px / 40px line-height   Font-weight: 700   - Major sections
HEADING_2    24px / 32px line-height   Font-weight: 600   - Panel titles
HEADING_3    20px / 28px line-height   Font-weight: 600   - Subsections
BODY_LARGE   18px / 28px line-height   Font-weight: 400   - Important text
BODY_BASE    16px / 24px line-height   Font-weight: 400   - Standard text
BODY_SMALL   14px / 20px line-height   Font-weight: 400   - Secondary info
CAPTION      12px / 16px line-height   Font-weight: 500   - Labels/hints
MICRO        10px / 14px line-height   Font-weight: 500   - Tiny details
```

### Text Colors

```
TEXT_PRIMARY     #FFFFFF   - Main content (on dark)
TEXT_SECONDARY   #B8B8B8   - Supporting content
TEXT_DISABLED    #666666   - Inactive text
TEXT_INVERSE     #1A1A1A   - Text on light backgrounds
```

---

## 🎯 Icon System

### Icon Principles

1. **Consistent Weight**: 2px stroke width at 24px base size
2. **Rounded Corners**: 2px radius for friendlier appearance
3. **Clear Metaphors**: Instantly recognizable agricultural symbols
4. **Scalable Design**: Works from 16px to 48px

### Core Icon Set

#### Farm Management
```
🌾 Wheat        - Crops/harvest
🌱 Seedling     - Planting/growth
💧 Water Drop   - Irrigation/moisture
⚗️ Flask        - Soil chemistry/nitrogen
🌡️ Thermometer  - Temperature/seasons
☀️ Sun          - Weather/daylight
🌧️ Rain         - Precipitation
```

#### UI Controls
```
➕ Plus         - Add/create new
➖ Minus        - Remove/decrease
✏️ Pencil       - Edit/modify
🗑️ Trash        - Delete/remove
⚙️ Gear         - Settings/options
❓ Question     - Help/information
📊 Chart        - Statistics/data
💰 Money Bag    - Resources/economy
⏱️ Timer        - Speed/time control
📌 Pin          - Lock/anchor
🔄 Arrows       - Refresh/rotate
✅ Checkmark    - Confirm/success
❌ X Mark       - Cancel/close
```

### Icon Sizes

```
ICON_SMALL    16px × 16px   - Inline text icons
ICON_MEDIUM   24px × 24px   - Standard buttons
ICON_LARGE    32px × 32px   - Primary actions
ICON_XLARGE   48px × 48px   - Feature highlights
```

---

## 🔲 Button & Control Standards

### Button Types

#### Primary Button
```
Background:     GRASS_MEDIUM (#4B7C2F)
Text:           TEXT_PRIMARY (#FFFFFF)
Border:         None
Hover:          GRASS_LIGHT (#73B347)
Active:         GRASS_DARK (#2D5016)
Disabled:       NEUTRAL_GRAY (#7F8C8D)
Height:         40px
Padding:        16px horizontal
Border-radius:  6px
```

#### Secondary Button
```
Background:     Transparent
Text:           TEXT_PRIMARY (#FFFFFF)
Border:         2px solid SURFACE_BORDER (#4A4A4A)
Hover:          SURFACE_RAISED (#2D2D2D)
Active:         SURFACE_PRIMARY (#1A1A1A)
Disabled:       Opacity 0.5
Height:         40px
Padding:        16px horizontal
Border-radius:  6px
```

#### Icon Button
```
Background:     SURFACE_RAISED (#2D2D2D)
Icon:           TEXT_SECONDARY (#B8B8B8)
Border:         1px solid SURFACE_BORDER (#4A4A4A)
Hover:          SURFACE_OVERLAY (#3A3A3A)
Active:         SURFACE_PRIMARY (#1A1A1A)
Size:           32px × 32px (square)
Border-radius:  6px
```

### Input Controls

#### Text Input
```
Background:     SURFACE_PRIMARY (#1A1A1A)
Text:           TEXT_PRIMARY (#FFFFFF)
Border:         1px solid SURFACE_BORDER (#4A4A4A)
Focus:          2px solid INFO_BLUE (#3498DB)
Height:         36px
Padding:        8px horizontal
Border-radius:  4px
```

#### Dropdown/Select
```
Background:     SURFACE_RAISED (#2D2D2D)
Text:           TEXT_PRIMARY (#FFFFFF)
Border:         1px solid SURFACE_BORDER (#4A4A4A)
Arrow:          TEXT_SECONDARY (#B8B8B8)
Height:         36px
Padding:        8px horizontal
Border-radius:  4px
```

#### Toggle Switch
```
Track:          SURFACE_BORDER (#4A4A4A)
Track Active:   SUCCESS_GREEN (#27AE60)
Knob:           TEXT_PRIMARY (#FFFFFF)
Size:           48px × 24px
Animation:      200ms ease-in-out
```

---

## 📐 Spacing & Layout System

### Base Grid Unit

**8px** base unit - All spacing follows multiples of 8

### Spacing Scale

```
SPACE_XXS    4px    (0.5 units)  - Tight spacing
SPACE_XS     8px    (1 unit)     - Compact elements
SPACE_SM     12px   (1.5 units)  - Related items
SPACE_MD     16px   (2 units)    - Standard spacing
SPACE_LG     24px   (3 units)    - Section breaks
SPACE_XL     32px   (4 units)    - Major sections
SPACE_XXL    48px   (6 units)    - Page margins
SPACE_XXXL   64px   (8 units)    - Large separations
```

### Layout Containers

#### Game Canvas
```
Full Screen:    1280px × 720px minimum
Safe Area:      1216px × 656px (32px padding)
Grid Overlay:   64px × 64px major, 8px × 8px minor
```

#### Panels
```
Min Width:      240px
Max Width:      480px
Padding:        16px (SPACE_MD)
Header Height:  32px
Border Radius:  8px
Shadow:         0 4px 16px rgba(0,0,0,0.2)
```

#### Modals/Popups
```
Min Width:      320px
Max Width:      640px
Padding:        24px (SPACE_LG)
Border Radius:  12px
Backdrop:       rgba(0,0,0,0.6)
```

### Component Spacing

#### Lists
```
Item Padding:   12px vertical, 16px horizontal
Item Gap:       8px between items
Section Gap:    24px between sections
```

#### Forms
```
Label Gap:      8px from input
Field Gap:      16px between fields
Section Gap:    32px between sections
```

#### Cards
```
Padding:        16px all sides
Content Gap:    12px between elements
Card Gap:       16px between cards
```

---

## 🎮 Interaction States

### Hover States
- **Brightness**: +10% lightness
- **Transition**: 150ms ease-in-out
- **Cursor**: Pointer for clickable, Default for static

### Focus States
- **Outline**: 2px solid INFO_BLUE (#3498DB)
- **Offset**: 2px
- **Animation**: Subtle pulse (optional for important elements)

### Active/Pressed States
- **Scale**: 0.98 transform
- **Brightness**: -10% lightness
- **Duration**: 100ms

### Disabled States
- **Opacity**: 0.5
- **Cursor**: Not-allowed
- **Interactions**: None

---

## 🎬 Animation Guidelines

### Timing Functions
```
EASE_IN_OUT:    cubic-bezier(0.4, 0, 0.2, 1)    - Standard transitions
EASE_OUT:       cubic-bezier(0, 0, 0.2, 1)       - Enter animations
EASE_IN:        cubic-bezier(0.4, 0, 1, 1)       - Exit animations
LINEAR:         linear                            - Continuous animations
```

### Duration Standards
```
INSTANT:        0ms        - No animation
QUICK:          150ms      - Micro interactions
NORMAL:         250ms      - Standard transitions
SLOW:           400ms      - Complex animations
VERY_SLOW:      600ms      - Page transitions
```

### Common Animations
```
Fade In/Out:    250ms ease-in-out, opacity 0→1
Slide In:       250ms ease-out, translateY 10px→0
Scale In:       200ms ease-out, scale 0.95→1
Rotate:         400ms ease-in-out, 360deg
```

---

## 📱 Responsive Breakpoints

```
MOBILE:         < 640px
TABLET:         640px - 1024px
DESKTOP:        1024px - 1440px
LARGE:          > 1440px
```

### Adaptive Strategies
- **Mobile**: Stack panels vertically, full-width
- **Tablet**: 2-column layouts, collapsible sidebars
- **Desktop**: Full layout, all panels visible
- **Large**: Increased spacing, larger type scale

---

## 🎯 Implementation Checklist

### Phase 1: Foundation
- [ ] Create color constants file
- [ ] Implement typography scale
- [ ] Set up spacing variables
- [ ] Create reusable button components

### Phase 2: Components
- [ ] Design icon set (SVG/PNG)
- [ ] Build panel system
- [ ] Create form controls
- [ ] Implement state management

### Phase 3: Polish
- [ ] Add animations
- [ ] Implement dark/light themes
- [ ] Accessibility testing
- [ ] Performance optimization

---

## 📚 Usage Examples

### Color Usage
```python
# Correct semantic usage
SUCCESS_COLOR = "#27AE60"  # For positive feedback
ERROR_COLOR = "#E74C3C"     # For error states

# Seasonal theming
if season == Season.SPRING:
    accent_color = SPRING_GREEN
elif season == Season.FALL:
    accent_color = FALL_ORANGE
```

### Spacing Usage
```python
# Consistent spacing
panel_padding = SPACE_MD  # 16px
button_margin = SPACE_SM  # 12px
section_gap = SPACE_XL    # 32px
```

### Typography Usage
```python
# Hierarchical text
title_font = pygame.font.Font(None, 24)  # HEADING_2
body_font = pygame.font.Font(None, 16)   # BODY_BASE
caption_font = pygame.font.Font(None, 12)  # CAPTION
```

---

**Design System v1.0** - Created for Field Station Agricultural Simulation
*Last Updated: September 2024*