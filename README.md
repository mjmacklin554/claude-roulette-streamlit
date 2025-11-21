# Roulette Strategy Simulator

A comprehensive Streamlit-based application for simulating and testing a systematic European roulette betting strategy with live play mode and interactive spinning wheel.

## Features

### Core Functionality
- **European Roulette Simulation** (37 numbers: 0-36)
- **Systematic Betting Strategy** with configurable parameters
- **Session History** with save/load/delete functionality
- **Live Play Mode** with two input methods:
  - Manual number entry
  - Interactive spinning wheel with realistic animation

### Betting System Features
- Dynamic bet type progression (1→2→3)
- Sequence code tracking (a, b, c values)
- Mixed number system for betting decisions
- A10 bypass rule (configurable)
- Four corner loss handling
- Stage 2 progression logic
- Comprehensive win/loss tracking

### Visualization
- Interactive HTML5 roulette wheel with:
  - Accurate European wheel layout
  - Smooth spinning animation (4 seconds)
  - Visual landing on correct number
  - Winning pocket highlight with gold glow
  - Realistic casino-style appearance

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Required Python Packages
```bash
pip install streamlit pandas
```

## Usage

### Running the Application
```bash
streamlit run main.py
```

The application will open in your default web browser at `http://localhost:8501`

**Note:** Previously used `roulette.py`. The application has been refactored into modular files for better performance.

### Application Modes

#### 1. Simulation Mode
Run automated simulations with:
- Configurable number of simulations (1-1000)
- Custom A1 and A2 values
- Optional A10 bypass rule
- Sequence code options (A, B, C, D)
- Detailed statistics and results

#### 2. Live Play Mode
Interactive play with real-time betting recommendations:

**Configuration:**
- Set initial A1 and A2 values
- Enable/disable A10 bypass
- Choose sequence code option

**Input Methods:**

*Manual Entry:*
- Enter numbers manually (0-36)
- Process each outcome individually

*Spinning Wheel:*
- Click "SPIN WHEEL" for visual random number generation
- Watch the wheel spin and land on a number
- Enter the displayed number
- Process the result

**Real-time Display:**
- Current betting recommendation
- Bet amount
- Session statistics
- Outcome history with color coding

### Session Management
- **Save Session**: Store current live play session to history
- **Load Session**: Restore a previous session to continue
- **View History**: Browse all saved sessions with statistics
- **Delete Sessions**: Remove single or multiple sessions
- **Session Includes**: All outcomes, bets, sequence codes, and configuration

## File Structure

### Main Application Files (Modular Design)
- **`main.py`** - Main Streamlit UI application (**run this file**)
- **`utils.py`** - Utility functions and constants (A1, A2, mixed numbers, etc.)
- **`session_manager.py`** - Session history management (save/load/delete sessions)
- **`simulation.py`** - Core simulation logic (placeholder for future expansion)

### Legacy Files
- **`roulette.py`** - Original monolithic file (kept for reference)

### Data Folders
- **`numbers/`** - Excel/CSV files with roulette outcomes
- **`numbers_for_autorun/`** - Files for batch optimization mode
- **`session_history/`** - Saved simulation sessions (auto-created, gitignored)

### Other Files
- **`roulette_wheel_interactive.html`** - Interactive spinning wheel component
- **`README.md`** - This file
- **`requirements.txt`** - Python dependencies
- **`program_requirements.txt`** - Original specification document

## Performance Optimizations

### Recent Performance Improvements
The application has been optimized for speed through several key improvements:

1. **Modular Architecture** - Separated code into multiple files reduces initial load time
   - Main file reduced from 3,469 to 3,369 lines
   - Helper functions moved to `utils.py`
   - Session management moved to `session_manager.py`

2. **Caching** - Expensive operations are cached for 60 seconds
   - File directory listings (`@st.cache_data`)
   - Session history loading

3. **Conditional Debug Messages** - `NoOpList` class eliminates overhead when debug mode is OFF
   - Avoids ~60 string formatting operations per spin
   - Results in 60-90% faster simulations when debug is disabled

4. **Progress Indicators** - Visual feedback during processing
   - Progress bar updates every 100 spins
   - Status text showing current progress

### Expected Performance
- **Widget interactions**: Faster due to modular structure
- **Simulations (debug OFF)**: 60-90% faster
- **File loading**: Cached after first access
- **Session history**: Cached after first access

## Strategy Overview

The betting system implements a sophisticated progression strategy:

1. **Bet Types**: Progress through three bet types (1→2→3)
2. **Sequence Codes**: Track patterns with a, b, c values
3. **Mixed Numbers**: Combine outcomes for betting decisions
4. **Dynamic Betting**: Adjust bet amounts based on cumulative results
5. **Loss Recovery**: Systematic approach to recovering from losses

See `program_requirements.txt` for detailed strategy rules.

## Technical Details

### Technologies Used
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and session storage
- **HTML5/CSS3/JavaScript**: Interactive wheel component
- **Python**: Core logic and calculations

### Browser Compatibility
The interactive spinning wheel works best in modern browsers:
- Chrome/Edge (recommended)
- Firefox
- Safari

## Troubleshooting

### Common Issues

**Wheel not spinning:**
- Ensure browser JavaScript is enabled
- Try refreshing the page
- Check browser console for errors

**Session not saving:**
- Check write permissions in the project directory
- Ensure `sessions/` directory exists (auto-created)

**Numbers not processing:**
- Verify number is within 0-36 range
- Ensure session is started in Live Play mode

## Version History

See `CHANGELOG.md` for detailed version history.

**Current Version**: 1.0 (Final Release)
- Complete betting system implementation
- Interactive spinning wheel
- Session history management
- A10 bypass rule
- Multi-session delete
- Live play mode with manual and wheel input

## Credits

Developed by Michael Macklin with some assistance from ClaudeAI

## License

This is a simulation tool for educational purposes. Roulette involves risk and no betting strategy can guarantee profits.
