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
streamlit run roulette.py
```

The application will open in your default web browser at `http://localhost:8501`

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

```
claude_roulette_streamlit/
├── roulette.py                      # Main application file
├── roulette_fresh.py                # Development version (same as roulette.py)
├── roulette_wheel_interactive.html  # Interactive spinning wheel component
├── roulette_8a_backup.py            # Previous version backup
├── README.md                        # This file
├── requirements.txt                 # Python dependencies
├── CHANGELOG.md                     # Version history
├── program_requirements.txt         # Original specification document
├── sessions/                        # Session history storage (auto-created)
└── docs/
    ├── HISTORY_FEATURE.md           # History feature documentation
    ├── BYPASS_RULE_FEATURE.md       # A10 bypass rule documentation
    └── MULTI_DELETE_FEATURE.md      # Multi-delete documentation
```

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

Developed using Claude Code (Anthropic).

## License

This is a simulation tool for educational purposes. Roulette involves risk and no betting strategy can guarantee profits.
