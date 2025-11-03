# Project Structure

## Active/Production Files

### Main Application
- **roulette.py** (90KB) - Main application file (FINAL VERSION - use this to run the app)
- **roulette_fresh.py** (90KB) - Development version (same as roulette.py, kept for reference)

### HTML Components
- **roulette_wheel_interactive.html** (12KB) - Interactive spinning wheel component (ACTIVE)
  - Accurate European roulette wheel with 37 pockets
  - Smooth spinning animation
  - Visual landing accuracy
  - Gold glow highlighting for winning pocket

### Documentation
- **README.md** (5.1KB) - Complete project documentation and usage guide
- **CHANGELOG.md** (3.7KB) - Version history and change log
- **requirements.txt** (32B) - Python package dependencies
- **HISTORY_FEATURE.md** (4.3KB) - Session history feature documentation
- **BYPASS_RULE_FEATURE.md** (2.4KB) - A10 bypass rule documentation
- **MULTI_DELETE_FEATURE.md** (3.8KB) - Multi-delete feature documentation
- **program_requirements.txt** - Original strategy specification
- **PROJECT_STRUCTURE.md** (this file) - Project organization guide

## Backup/Archive Files

### Old Versions
- **roulette_8a_backup.py** (7.3KB) - Previous main version (backup)
- **roulette_wheel_old.html** (8KB) - Old wheel implementation (superseded)
- **roulette_fresh.html** (111KB) - Old HTML export (not used)
- **program_flowchart.html** (20KB) - Program flowchart visualization

### Reference Files
- **program.txt** - Original program specification
- **program_flowchart.txt** - Flowchart source
- Various other .txt files - Development notes and documentation

## Runtime Directories

### Auto-Generated
- **sessions/** - Session history storage (created automatically)
  - Contains saved session .csv files
  - Managed through the application

## How to Use This Project

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run roulette.py
```

### For Development
- Edit `roulette.py` for main application changes
- Edit `roulette_wheel_interactive.html` for wheel modifications
- Keep `roulette_fresh.py` in sync with `roulette.py` if maintaining both

### File Priority
When running the app, use: **roulette.py**

When modifying the wheel, edit: **roulette_wheel_interactive.html**

## Version Control Notes

### Files to Track in Git
- roulette.py
- roulette_wheel_interactive.html
- README.md
- CHANGELOG.md
- requirements.txt
- All .md documentation files

### Files to Ignore
- sessions/*.csv (user data)
- __pycache__/
- *.pyc
- .streamlit/secrets.toml (if used)

## Current Status

**Version**: 1.0.0 (Final Release)
**Status**: Complete and production-ready
**Last Updated**: November 3, 2025

All features implemented:
- ✅ Complete betting system
- ✅ Interactive spinning wheel
- ✅ Live play mode with dual input methods
- ✅ Session history management
- ✅ A10 bypass rule
- ✅ Multi-session operations
- ✅ Comprehensive documentation

## Support Files

The project also includes various supporting documentation:
- Strategy flowcharts
- Requirement specifications
- Feature-specific documentation
- Development notes

Refer to README.md for complete usage instructions.
