# 🌽 Field Station v1.0

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Educational](https://img.shields.io/badge/Use-Educational-purple.svg)](README.md)
[![Field Research](https://img.shields.io/badge/Focus-Field%20Research-brown.svg)](README.md)

A data-driven field research simulation built with Python and Pygame, featuring scientifically accurate crop varieties and location-based research mechanics.

## ✨ Features

### 🌾 Scientific Agriculture
- **8 crop varieties** with scientific names and Illinois-specific strains:
  - Corn - *Zea mays* var. saccharata (Sweet Corn)
  - Field Corn - *Zea mays* var. indentata
  - Wheat - *Triticum aestivum* 'Soft Red Winter'
  - Potato - *Solanum tuberosum* 'Russet Burbank'
  - Carrot - *Daucus carota* 'Imperator'
  - Soybean - *Glycine max* (nitrogen-fixing)
  - Pumpkin - *Cucurbita pepo* 'Howden'
  - Tomato - *Solanum lycopersicum* 'Better Boy'

### 🗺️ Location-Based Field Research
- **Champaign, Illinois, USA** - Default field research location
- Accurate soil properties based on Central Illinois prairie conditions
- Climate-specific weather patterns and seasonal timing
- Expandable system for adding more field research regions

### 🎮 Game Mechanics
- **3x3 isometric tile grid** with zoom (0.3x to 10x)
- **Real-time growth simulation** with seasonal effects
- **Soil management system**: quality, moisture, and nitrogen levels
- **Weather system**: Sunny, cloudy, rainy, snowy conditions
- **Auto-harvest feature** for mature crops
- **Economic system**: Buy seeds, sell harvests, manage finances

### 🎯 Interactive Features
- **Farm setup screen**: Name your farm and choose location
- **Dynamic time controls**: Pause, speed up (1x-8x), or slow down
- **Smart crop selection**: Auto-plants season-appropriate crops
- **Detailed farm statistics** and growth tracking
- **Color-coded UI** for quick status understanding

## 🚀 Getting Started

### Prerequisites
```bash
pip install pygame
```

### Installation
```bash
git clone https://github.com/seheart/field_station.git
cd field_station
python3 field_station.py
```

### Controls
- **ESC**: Main menu / Return to menu
- **Arrow Keys / WASD**: Move camera / Navigate menus
- **Mouse**: Click tiles to open popup, interact with UI
- **Mouse Wheel**: Zoom in/out (0.3x to 10x)
- **Space**: Pause/unpause game
- **P**: Plant crop on selected tile
- **H**: Harvest crop from selected tile
- **A**: Toggle auto-harvest
- **Ctrl+S**: Save game
- **Ctrl+L**: Load game
- **+/-**: Speed up/slow down time
- **F1**: Toggle debug mode (shows click detection info)

## 🧪 Testing

Run the comprehensive test suite:
```bash
./run_tests.sh
```

Or run individual components:
```bash
python3 test_field_station.py  # Unit tests
python3 -m py_compile field_station.py  # Syntax check
```

## 📊 Game Data

View detailed crop information, growth mechanics, and field research tips in [`game_data.html`](game_data.html).

## 🏗️ Architecture

- **field_station.py**: Main game engine with Pygame
- **test_field_station.py**: Comprehensive test suite
- **game_data.html**: Interactive crop and mechanics reference
- **run_tests.sh**: Automated testing script
- **.github/workflows/**: CI/CD pipeline for multiple Python versions

## 🌱 Development

### Project Structure
```
farm-game/
├── field_station.py                # Main game file
├── test_field_station.py           # Unit tests  
├── game_data.html           # Documentation
├── run_tests.sh             # Test runner
├── README.md                # This file
├── ABOUT.md                 # Project details
└── .github/
    └── workflows/
        └── test.yml         # CI/CD pipeline
```

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`./run_tests.sh`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📈 Roadmap

### ✅ **Completed in v1.0**
- [x] **Save/load game functionality** - JSON-based persistence system
- [x] **Market price fluctuations** - Dynamic seasonal pricing with trends
- [x] **Advanced weather patterns** - Extreme weather events (drought, flood, storm, hail)
- [x] **Enhanced UI** - Toast messages, progress bars, tooltips, debug mode
- [x] **Improved controls** - Banished-style tile interaction with drag threshold

### 🔮 **Future Development**
- [ ] Additional field research locations (Iowa, Nebraska, etc.)
- [ ] More crop varieties and seasonal plants
- [ ] Equipment and technology upgrades
- [ ] Multiplayer field research cooperation
- [ ] Achievement and tutorial systems

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with [Pygame](https://www.pygame.org/)
- Agricultural data sourced from University of Illinois Extension
- Crop varieties selected for Central Illinois field research conditions
- Isometric tile rendering inspired by classic field research games

---

**🔬 Happy Researching!** - *Created with scientific accuracy and research passion*