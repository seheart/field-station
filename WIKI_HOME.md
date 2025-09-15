# Field Station - Project Wiki

Welcome to the Field Station project documentation hub. This wiki organizes all project knowledge in one place.

## 📚 Documentation Index

### 🎮 **Game Design & Strategy**
- [**Game Strategy Guide**](GAME_STRATEGY.md) - Core game mechanics and strategy
- [**Game Data Structures**](GAME_DATA.md) - Data models and game state management  
- [**AI Ideas & Features**](AI_IDEAS.md) - AI-powered game features and concepts

### 🎨 **User Interface & Design**
- [**UI Design Plan**](UI_DESIGN_PLAN.md) - Complete UI/UX design specifications
- [**Design System**](DESIGN_SYSTEM.md) - Colors, fonts, and visual guidelines
- [**UI Framework Guide**](UI_FRAMEWORK_GUIDE.md) - Technical UI implementation guide

### 🧪 **Quality Assurance & Testing**
- [**QA Framework Guide**](QA_README.md) - Automated testing framework
- [**SDLC QA Integration**](SDLC_QA_README.md) - User story-driven QA for development lifecycle
- [**User Stories**](USER_STORIES.md) - Complete user story definitions and acceptance criteria
- [**Menu UI Validation Report**](MENU_UI_VALIDATION_REPORT.md) - Comprehensive menu system audit
- [**Menu System Validation**](MENU_SYSTEM_VALIDATION_SUMMARY.md) - Menu functionality validation
- [**Layout Fixes Summary**](LAYOUT_FIXES_SUMMARY.md) - UI layout improvements and fixes

### 🚀 **Development & Project Management**
- [**Development Roadmap**](DEVELOPMENT_ROADMAP.md) - Project milestones and feature timeline
- [**Project README**](README.md) - Getting started and project overview
- [**Versioning Strategy**](VERSIONING.md) - Version control and release process

## 🔧 **Quick Reference**

### Development Commands
```bash
# Start the game
./field_station_launcher.sh

# Run QA tests
./run_qa.sh                # Technical QA
./run_full_qa.sh           # Complete SDLC QA
python3 user_flow_qa.py    # User flow testing

# View user stories
python3 user_stories.py

# Create issue tickets
python3 issue_tracker_integration.py
```

### Project Structure
```
field_station/
├── 📁 Core Game Files
│   ├── field_station.py      # Main game engine
│   ├── ui_framework.py       # UI rendering system
│   └── menu_icons.py         # Icon definitions
├── 📁 QA & Testing
│   ├── test_framework.py     # Technical QA tests
│   ├── user_flow_qa.py       # User workflow testing
│   ├── user_stories.py       # User story definitions
│   └── issue_tracker_integration.py  # Issue tracking
├── 📁 Documentation
│   ├── *.md files            # All project documentation
│   └── qa_screenshots/       # QA test screenshots
└── 📁 Configuration
    ├── *_config.json         # Issue tracker configs
    └── qa_issues.json        # Local issue tracking
```

## 📊 **Current Status**

### QA Health Check
- ✅ **Technical QA**: 100% pass rate (7/7 tests)
- ❌ **User Flow QA**: 20% pass rate (1/5 stories) 
- 📋 **User Stories**: 10 stories across 7 pages
- 🎯 **Active Issues**: 2 high-priority bugs tracked

### Key Metrics
- **Lines of Code**: ~2,000+ (Python)
- **Documentation**: 14 comprehensive guides
- **Test Coverage**: 7 technical tests + 10 user stories
- **UI Pages**: 7 fully documented pages

## 🤝 **Contributing**

### Before Making Changes
1. **Run QA**: `./run_full_qa.sh` to ensure no regressions
2. **Update User Stories**: Add/modify user stories for new features
3. **Document Changes**: Update relevant wiki pages

### Development Workflow
1. **Plan**: Check [Development Roadmap](DEVELOPMENT_ROADMAP.md)
2. **Design**: Follow [UI Design Plan](UI_DESIGN_PLAN.md) 
3. **Develop**: Use [UI Framework Guide](UI_FRAMEWORK_GUIDE.md)
4. **Test**: Run [QA Framework](QA_README.md)
5. **Deploy**: Follow [SDLC QA process](SDLC_QA_README.md)

## 🆘 **Getting Help**

### Common Tasks
- **Understanding the codebase**: Start with [README.md](README.md)
- **Making UI changes**: Read [UI Framework Guide](UI_FRAMEWORK_GUIDE.md)
- **Adding features**: Check [Development Roadmap](DEVELOPMENT_ROADMAP.md)
- **Fixing bugs**: Use [QA Framework](QA_README.md) to identify issues
- **User experience issues**: Review [User Stories](user_stories.py)

### Troubleshooting
- **Game won't start**: Check [README.md](README.md) setup instructions
- **UI looks wrong**: Verify [Design System](DESIGN_SYSTEM.md) compliance
- **Tests failing**: Run `./run_qa.sh` for detailed error reports
- **Menu not working**: Check [Menu System Validation](MENU_SYSTEM_VALIDATION_SUMMARY.md)

---

**📝 Wiki Maintenance**: This wiki is automatically updated as documentation changes. Last updated: $(date)