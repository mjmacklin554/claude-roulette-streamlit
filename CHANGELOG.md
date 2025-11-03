# Changelog

All notable changes to the Roulette Strategy Simulator project.

## [1.0.0] - 2025-11-03 - Final Release

### Added
- **Interactive Spinning Wheel**: Full HTML5/CSS3/JavaScript roulette wheel with:
  - Accurate European wheel layout (37 pockets)
  - Smooth 4-second spinning animation with cubic-bezier easing
  - Visual landing accuracy - wheel lands on the correct generated number
  - Winning pocket highlight with gold glow and pulse animation
  - Uniform gold border around wheel
  - Proper pocket sizing and positioning
  - Casino-style appearance with gradient effects

- **Live Play Mode Enhancements**:
  - Two input methods: Manual Entry and Spinning Wheel
  - Full betting system integration in live mode
  - Real-time betting recommendations
  - Complete session state tracking
  - All betting rules implemented (A1 wait, four corner loss, Stage 2, etc.)

- **Documentation**:
  - Comprehensive README.md
  - requirements.txt for dependencies
  - CHANGELOG.md (this file)

### Fixed
- **Wheel Landing Accuracy**: Corrected rotation calculation to ensure visual landing matches RNG selection
  - Fixed rotation direction (clockwise vs counter-clockwise confusion)
  - Fixed fractional spin issues by using integer spins only
  - Simplified rotation formula: `rotation = 360*n - pocket_angle`
  - Removed accumulated rotation tracking between spins

- **Wheel Visual Issues**:
  - Fixed overlapping pockets by adjusting dimensions (28px x 40px)
  - Fixed uneven gold border using flexbox centering
  - Fixed pocket visibility by using positioned boxes instead of triangular segments
  - Increased iframe height from 700px to 800px to prevent button cutoff

- **User Experience**:
  - Removed non-functional "Process This Number" button
  - Clarified instructions for wheel usage
  - Simplified workflow: spin → see result → enter number → process

### Changed
- Renamed `roulette_fresh.py` to `roulette.py` as main application file
- Backed up previous version as `roulette_8a_backup.py`
- Updated `roulette_wheel_interactive.html` with final wheel implementation

## [0.9.0] - Stage 2: Session History & Management

### Added
- Session history feature with save/load/delete functionality
- Multi-session delete with checkbox selection
- Session statistics display (profit/loss, win rate, outcomes)
- Persistent storage using Pandas DataFrames
- Session browser with expandable details

### Documentation
- HISTORY_FEATURE.md
- MULTI_DELETE_FEATURE.md

## [0.8.0] - Stage 1: A10 Bypass Rule

### Added
- A10 bypass rule implementation
- Configurable bypass option in simulation and live modes
- Comprehensive rule testing and validation

### Documentation
- BYPASS_RULE_FEATURE.md
- program_requirements.txt (original specification)

## [0.7.0] - Core Betting System

### Added
- Complete betting system with all rules:
  - Bet type progression (1→2→3)
  - Sequence code tracking (a, b, c values)
  - Mixed number system
  - Four corner loss handling
  - Stage 2 progression logic
  - Dynamic bet amount calculation

- Simulation mode with batch processing
- Live play mode with manual entry
- Real-time statistics and tracking

## [0.1.0] - Initial Development

### Added
- Basic Streamlit application structure
- European roulette number generation
- Simple betting logic
- Basic UI layout

---

## Version Numbering

Format: MAJOR.MINOR.PATCH
- MAJOR: Significant feature additions or breaking changes
- MINOR: New features, non-breaking changes
- PATCH: Bug fixes and minor improvements

## Notes

This project evolved through multiple stages, culminating in a complete betting strategy simulator with an interactive visual component. The final version (1.0.0) represents a fully functional application with comprehensive features for both automated simulation and live play.
