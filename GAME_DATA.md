# 🔬 Field Station - Data Reference

**Data-Driven Research Simulation Variables and Ranges**

This document contains all the scientific data, game mechanics, and simulation parameters that drive Field Station's agricultural research environment.

---

## 🌱 Crop Types

All available research crops with their scientific characteristics and field requirements:

### **🌾 Wheat - *Triticum aestivum* 'Soft Red Winter'**
- **Growth Time:** 90 days
- **Sale Price:** $25
- **Nitrogen Need:** 0.4 (moderate)
- **Water Need:** 0.3 (low)
- **Seasons:** Fall
- *Winter wheat variety common in central Illinois*

### **🌽 Sweet Corn - *Zea mays* var. saccharata**
- **Growth Time:** 120 days
- **Sale Price:** $35
- **Nitrogen Need:** 0.6 (high)
- **Water Need:** 0.5 (moderate)
- **Seasons:** Spring
- *Sweet corn for direct consumption*

### **🌽 Field Corn - *Zea mays* var. indentata**
- **Growth Time:** 140 days
- **Sale Price:** $40
- **Nitrogen Need:** 0.7 (very high)
- **Water Need:** 0.6 (high)
- **Seasons:** Spring
- *Dent corn for livestock feed and ethanol*

### **🥔 Potato - *Solanum tuberosum* 'Russet Burbank'**
- **Growth Time:** 70 days
- **Sale Price:** $20
- **Nitrogen Need:** 0.3 (low)
- **Water Need:** 0.4 (moderate)
- **Seasons:** Spring
- *Popular baking potato variety*

### **🥕 Carrot - *Daucus carota* 'Imperator'**
- **Growth Time:** 60 days
- **Sale Price:** $15
- **Nitrogen Need:** 0.2 (very low)
- **Water Need:** 0.3 (low)
- **Seasons:** Spring, Summer
- *Long, tapered variety for fresh market*

### **🌱 Soybean - *Glycine max***
- **Growth Time:** 95 days
- **Sale Price:** $30
- **Nitrogen Need:** -0.3 (adds nitrogen!)
- **Water Need:** 0.4 (moderate)
- **Seasons:** Spring, Summer
- *Major Illinois crop, nitrogen-fixing legume*

### **🎃 Pumpkin - *Cucurbita pepo* 'Howden'**
- **Growth Time:** 110 days
- **Sale Price:** $28
- **Nitrogen Need:** 0.5 (moderate)
- **Water Need:** 0.7 (high)
- **Seasons:** Spring
- *Classic jack-o'-lantern variety*

### **🍅 Tomato - *Solanum lycopersicum* 'Better Boy'**
- **Growth Time:** 75 days
- **Sale Price:** $45
- **Nitrogen Need:** 0.6 (high)
- **Water Need:** 0.8 (very high)
- **Seasons:** Spring, Summer
- *Popular hybrid variety for home farms*

> **Note:** Soybeans have negative nitrogen need, meaning they actually add nitrogen to the soil through nitrogen fixation. All varieties shown are commonly grown in central Illinois.

---

## 🌍 Soil Properties

| Property | Range | Starting Range | Description |
|----------|-------|----------------|-------------|
| **Soil Quality** | 0.0 - 1.0 | 0.4 - 0.8 | Overall fertility of the soil. Decreases by 0.05 per harvest. |
| **Moisture** | 0.0 - 1.0 | 0.3 - 0.6 | Water content. Affected by weather and crop water needs. |
| **Nitrogen** | 0.0 - 1.0 | 0.3 - 0.7 | Nitrogen content. Consumed by crops, restored naturally over time. |

### **Soil Quality Color Coding:**
- **Green:** > 0.7 (excellent)
- **Yellow:** 0.4 - 0.7 (good)  
- **Red:** < 0.4 (poor)

---

## 🌦️ Weather System

| Weather Type | Moisture Change | Frequency | Effects |
|--------------|-----------------|-----------|---------|
| **☀️ Sunny** | -0.01 | Most common | Slightly dries soil |
| **☁️ Cloudy** | 0.0 | Common | No moisture change |
| **🌧️ Rainy** | +0.02 | Regular | Increases soil moisture |
| **❄️ Snowy** | +0.01 | Winter only | Slight moisture increase |

---

## 📅 Season System

| Season | Duration | Weather Pattern | Plantable Crops |
|--------|----------|----------------|-----------------|
| **🌸 Spring** | Mar - May | Mixed weather, frequent rain | Wheat, Corn, Potato, Carrot, Beans |
| **☀️ Summer** | Jun - Aug | Sunny, occasional storms | Carrot, Beans |
| **🍂 Fall** | Sep - Nov | Cooler, more cloudy | Wheat |
| **❄️ Winter** | Dec - Feb | Cold, snow possible | No crops can be planted |

---

## ⏱️ Game Timing

| Setting | Value | Description |
|---------|-------|-------------|
| **Base Day Length** | 30 seconds | Real-time duration of one game day at 1x speed |
| **Speed Options** | 1x, 2x, 5x | Available game speed multipliers |
| **Days per Year** | 365 | Standard calendar year |

---

## 💰 Economics

| Item | Cost/Value | Notes |
|------|------------|-------|
| **Starting Money** | $500 | Initial player resources |
| **Seed Cost** | $10 | Cost to plant any crop |
| **Harvest Value** | $15 - $45 | Varies by crop type × soil quality multiplier |

---

## 🎮 Game Mechanics

- **Grid Size:** 3x3 tiles (9 total)
- **Zoom Range:** 0.3x to 10x
- **Auto-planting:** Game selects appropriate crops for season (prefers wheat)
- **Growth Factors:**
  - Insufficient water (< 50% need): **0.8x growth speed**
  - Excess water (> 150% need): **0.9x growth speed**  
  - Insufficient nitrogen (< 50% need): **0.7x growth speed**
- **Natural Recovery:** Empty tiles slowly gain nitrogen (+0.001/day)

---

## 🎯 UI Color Codes

| Element | Color | Meaning |
|---------|-------|---------|
| **Soil Quality** | Green / Yellow / Red | Excellent / Good / Poor |
| **Moisture** | Blue / Brown | Adequate / Low |
| **Nitrogen** | Green / Yellow / Red | High / Medium / Low |
| **Money** | Green / Yellow / Red | ≥$100 / $50-99 / <$50 |
| **Crop Growth** | Green / Yellow | Ready for harvest / Still growing |

---

## 🎮 Controls & Interface

### **🖱️ Mouse Controls**
- **Left Click:** Open tile popup
- **Mouse Wheel:** Zoom in/out (0.3x to 10x)
- **Drag:** Pan camera (after 5px movement)
- **Middle Mouse:** Immediate camera dragging
- **Hover:** Show crop tooltips with full names

### **⌨️ Keyboard Shortcuts**
- **Space:** Pause/unpause game
- **P:** Plant crop on selected tile
- **H:** Harvest crop from selected tile
- **A:** Toggle auto-harvest
- **+/-:** Speed up/slow down time
- **Ctrl+S:** Save game
- **Ctrl+L:** Load game
- **F1:** Toggle debug mode
- **ESC:** Return to menu

---

## 💾 Save & Load System

Full field research session persistence with JSON format saves:

| Feature | Description | Usage |
|---------|-------------|--------|
| **Quick Save** | Save current research session state | Ctrl+S or Menu → Save Game |
| **Quick Load** | Load saved research session state | Ctrl+L or Menu → Load Game |
| **Auto Directory** | Creates saves/ folder automatically | All saves stored in saves/savegame.json |
| **Full State** | Saves field station, budget, crops, weather, date | Complete research session restoration |

---

## 💰 Dynamic Market System

Seasonal price fluctuations and daily market variations:

| Season | High-Value Crops | Low-Value Crops | Strategy |
|--------|------------------|-----------------|----------|
| **Spring** | Wheat (+20%), Potato (+10%) | Pumpkin (-30%), Field Corn (-20%) | Plant wheat for quick profit |
| **Summer** | Tomato (+40%), Sweet Corn (+30%) | Wheat (-20%) | Focus on summer crops |
| **Fall** | Pumpkin (+50%), Field Corn (+30%), Soybean (+20%) | Sweet Corn (-30%) | Harvest season - maximum profits |
| **Winter** | Tomato (+10%), Wheat (+10%) | Pumpkin (-40%) | Limited planting options |

> **💡 Market Tips:** Prices fluctuate ±15% daily. Watch the Market Panel for trends: ↗ HIGH (best), ↗ Good, → Fair, ↘ Poor, ↘ Low (worst).

---

## ⚡ Extreme Weather Events

New weather types with real field research consequences:

| Weather Type | Effects | Probability | Seasons |
|--------------|---------|-------------|---------|
| **🌪️ Drought** | Severe moisture loss (-8%), stunts growth | 5% daily | Summer, Fall |
| **🌊 Flood** | Excessive moisture (+15%), can kill crops (15% chance) | 5% daily | Spring, Summer |
| **⛈️ Storm** | Heavy rain (+8%), no crop damage | 5% daily | Summer, Fall |
| **🧊 Hail** | Damages crops (30% chance), light moisture (+3%) | 5% daily | Spring, Summer |

> **⚠️ Weather Strategy:** Extreme weather occurs maximum once per week. Diversify crops to minimize risk. Flood is most dangerous - avoid overwatering!

---

## 🔧 Debug Mode (F1)

Advanced field research troubleshooting and development features:

### **🎯 Click Detection**
- Real-time mouse coordinates
- Grid position conversion
- Click success/failure messages
- Visual tile boundaries (red outlines)

### **📊 System Info**
- Camera position and zoom level
- Selected tile information
- Performance diagnostics
- Tile center markers

---

## ✨ UI Improvements

### **📝 Visual Feedback**
- **Toast Messages:** Success/error notifications
- **Progress Bars:** Crop growth at high zoom (2x+)
- **Tooltips:** Full crop names on hover
- **Color Coding:** Green=success, Red=error, Yellow=warning

### **🎨 Interface Panels**
- **Market Panel:** Real-time prices and trends
- **Tile Info:** Detailed soil and crop data
- **Farm Stats:** Overview of planted/ready crops
- **Research-style Popups:** Click tiles for field actions

---

## 📊 Performance Tips

- **Maximize Research Value:** Plant high-value crops (Field Corn: $40) in high-quality soil
- **Soil Management:** Use soybeans to restore nitrogen, rotate crops
- **Season Planning:** Spring offers most planting options
- **Water Management:** Plant during rainy periods for best growth
- **Research Harvest Timing:** Harvest mature crops quickly for optimal data collection

---

**🌽 Field Station - Game Data Reference v0.1**

*Updated: September 4, 2024 - Major Feature Update*

*Includes: Save/Load System, Dynamic Markets, Extreme Weather, UI Improvements, Debug Mode*