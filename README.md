# 🌽 Field Station

**A scientifically-accurate farming simulation that bridges entertainment and agricultural education**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

Field Station features real plant varieties with authentic scientific nomenclature and location-specific growing conditions. Unlike typical farming games that use generic crops, this simulation teaches actual agricultural practices while providing engaging gameplay.

## ✨ Key Features

- **🔬 Scientific Accuracy**: Real crop varieties with proper binomial naming (genus and species)
- **🌍 Location-Based**: Authentic Champaign County, Illinois agricultural conditions
- **📚 Educational Value**: Learn soil science, crop rotation, and seasonal farming patterns
- **⚡ Dynamic Systems**: Weather events, market fluctuations, and seasonal challenges
- **🎮 Engaging Gameplay**: Isometric 3x3 grid with zoom, save/load, and progression systems

## 🚀 Quick Start

### Prerequisites
```bash
pip install pygame
```

### Installation & Run
```bash
git clone https://github.com/seheart/field_station.git
cd field_station
python3 field_station.py
```

## 🎯 What Makes It Special

- **Real Science**: Every crop includes authentic cultivars grown in Central Illinois
- **Educational Focus**: Designed for classroom use while remaining fun for casual players
- **Data-Driven**: Game mechanics based on actual agricultural research data
- **Progressive Learning**: Encourages exploration of crop combinations and farming strategies

## 🎮 Gameplay

Manage a 3x3 research farm through four seasons, making decisions about:
- **Crop Selection**: Choose from 8 scientifically-accurate varieties
- **Soil Management**: Monitor quality, moisture, and nitrogen levels  
- **Market Strategy**: Buy and sell based on seasonal price fluctuations
- **Weather Response**: Adapt to realistic Midwest weather patterns

## 🧪 For Educators

Field Station is designed for educational integration:
- **Biology Classes**: Plant taxonomy and growth cycles
- **Environmental Science**: Sustainable farming practices  
- **Geography**: Regional agricultural patterns
- **Economics**: Market dynamics and resource management

## 🛠️ Technical Details

- **Engine**: Pygame for cross-platform compatibility
- **Architecture**: Modular object-oriented design with comprehensive testing
- **Performance**: Optimized for smooth gameplay with zoom capabilities (0.3x-10x)
- **Save System**: JSON-based persistence with versioning support

## 📖 Documentation

- **[Game Strategy](GAME_STRATEGY.md)**: Detailed project vision, design philosophy, and development approach
- **[Development Roadmap](DEVELOPMENT_ROADMAP.md)**: Comprehensive development plan and feature roadmap
- **[Game Data](GAME_DATA.md)**: Complete simulation data and crop information reference

## 🧪 Testing

```bash
./run_tests.sh  # Full test suite
python3 test_field_station.py  # Unit tests only
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests to ensure compatibility
4. Submit a pull request with clear documentation

## 📈 Current Status

**v1.0 Released** - Core gameplay systems complete:
- ✅ Full save/load functionality
- ✅ Dynamic market system with seasonal pricing
- ✅ Extreme weather events (drought, flood, storms)
- ✅ Enhanced UI with tooltips and progress feedback
- ✅ Banished-style tile interaction system

---

**🌱 Where science meets simulation** - *Developed with passion for both gaming and agriculture*

*For detailed information about the project vision, educational philosophy, and long-term development plans, see [GAME_STRATEGY.md](GAME_STRATEGY.md)*