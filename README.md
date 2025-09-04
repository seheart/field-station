# 🚜 Farm Game v0.1

A data-driven farming simulation game built with Python and Pygame, featuring scientifically accurate crop varieties and location-based farming mechanics.

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

### 🗺️ Location-Based Farming
- **Champaign, Illinois, USA** - Default farming location
- Accurate soil properties based on Central Illinois prairie conditions
- Climate-specific weather patterns and seasonal timing
- Expandable system for adding more farming regions

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
git clone https://github.com/seheart/farm-game.git
cd farm-game
python3 farming_game.py
```

### Controls
- **ESC**: Main menu / Pause
- **Arrow Keys / WASD**: Navigate menus
- **Mouse**: Click tiles to select, interact with UI
- **P**: Pause/unpause game
- **A**: Toggle auto-harvest
- **+/-**: Zoom in/out
- **Space**: Speed up time
- **Tab**: Cycle through tile information

## 🧪 Testing

Run the comprehensive test suite:
```bash
./run_tests.sh
```

Or run individual components:
```bash
python3 test_farming_game.py  # Unit tests
python3 -m py_compile farming_game.py  # Syntax check
```

## 📊 Game Data

View detailed crop information, growth mechanics, and farming tips in [`game_data.html`](game_data.html).

## 🏗️ Architecture

- **farming_game.py**: Main game engine with Pygame
- **test_farming_game.py**: Comprehensive test suite
- **game_data.html**: Interactive crop and mechanics reference
- **run_tests.sh**: Automated testing script
- **.github/workflows/**: CI/CD pipeline for multiple Python versions

## 🌱 Development

### Project Structure
```
farm-game/
├── farming_game.py          # Main game file
├── test_farming_game.py     # Unit tests  
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

- [ ] Additional farming locations (Iowa, Nebraska, etc.)
- [ ] More crop varieties and seasonal plants
- [ ] Advanced weather patterns and climate events
- [ ] Equipment and technology upgrades
- [ ] Market price fluctuations
- [ ] Multiplayer farming cooperation
- [ ] Save/load game functionality

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with [Pygame](https://www.pygame.org/)
- Agricultural data sourced from University of Illinois Extension
- Crop varieties selected for Central Illinois farming conditions
- Isometric tile rendering inspired by classic farming games

---

**🚜 Happy Farming!** - *Created with scientific accuracy and farming passion*