# Quick Start Guide

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run roulette.py
```

The app will open automatically in your browser at `http://localhost:8501`

## Using the Application

### Simulation Mode

1. **Configure Settings**:
   - Number of simulations (1-1000)
   - A1 value (initial wait period)
   - A2 value (progression factor)
   - Enable/disable A10 bypass rule
   - Select sequence code option (A, B, C, or D)

2. **Run Simulation**:
   - Click "Run Simulations"
   - View results: profit/loss, win rate, statistics
   - Results shown in expandable table

### Live Play Mode

#### Option 1: Manual Entry
1. **Start Session**: Click "Start New Live Session"
2. **Configure**: Set A1, A2, bypass rule, sequence option
3. **Enter Numbers**: Type roulette numbers (0-36)
4. **Process**: Click "Process Number"
5. **Follow Recommendations**: App shows next bet and amount
6. **Continue**: Repeat steps 3-5

#### Option 2: Spinning Wheel
1. **Select Mode**: Choose "Spinning Wheel" radio button
2. **Spin**: Click "🎰 SPIN WHEEL" in the component
3. **Watch**: Wheel spins for 4 seconds
4. **See Result**: Number displayed with color
5. **Enter Number**: Type the displayed number in field below
6. **Process**: Click "Process Wheel Result"
7. **Repeat**: Continue with next spin

### Session Management

#### Save Current Session
- Click "Save Current Session" in Live Play Mode
- Session stored with timestamp
- Includes all outcomes, bets, and configuration

#### Load Previous Session
1. Go to "View History" tab
2. Find desired session
3. Click "Load This Session"
4. Session restored to Live Play Mode

#### Delete Sessions
1. Go to "View History" tab
2. Check boxes next to sessions to delete
3. Click "Delete Selected Sessions"
4. Confirm deletion

## Tips

### For Best Results
- Use consistent A1 and A2 values for comparison
- Save sessions regularly when playing live
- Review session history to analyze strategy performance
- Try different sequence code options (A, B, C, D) to see variations

### Understanding the Display

**Colors in Live Mode**:
- 🟢 Green: Zero (0)
- 🔴 Red: Red numbers (1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36)
- ⚫ Black: Black numbers (2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35)

**Bet Types**:
- Type 1: Initial betting strategy
- Type 2: Progression after Type 1 patterns
- Type 3: Advanced progression strategy

**Sequence Codes**:
- Displayed as (a,b,c) values
- Track pattern progression
- Used to determine next bet

### Common Workflows

**Quick Test Run**:
```
1. Go to Simulation Mode
2. Set: 10 simulations, A1=3, A2=5
3. Click "Run Simulations"
4. Review results
```

**Live Play Session**:
```
1. Go to Live Play Mode
2. Click "Start New Live Session"
3. Configure settings
4. Choose Manual or Wheel input
5. Process outcomes one by one
6. Save session when done
```

**Analyze Past Performance**:
```
1. Go to View History tab
2. Expand sessions to see details
3. Compare profit/loss across sessions
4. Load successful sessions to continue
```

## Keyboard Shortcuts

When using Manual Entry mode:
- Type number and press Enter to process (if form supports it)
- Use Tab to navigate between fields

## Troubleshooting

**App won't start**:
```bash
# Check Streamlit installation
pip show streamlit

# Reinstall if needed
pip install --upgrade streamlit
```

**Wheel not spinning**:
- Refresh browser page (F5)
- Check browser console for JavaScript errors
- Ensure browser JavaScript is enabled

**Sessions not saving**:
- Check write permissions in project directory
- Ensure sessions/ directory exists (auto-created)

**Port already in use**:
```bash
# Use different port
streamlit run roulette.py --server.port 8502
```

## Next Steps

- Read the full README.md for detailed documentation
- Review CHANGELOG.md for version history
- Check feature-specific .md files for deep dives
- Experiment with different configurations

## Support

For issues or questions:
1. Check README.md for detailed information
2. Review relevant feature documentation (.md files)
3. Check console output for error messages

---

**Ready to start? Run this command:**
```bash
streamlit run roulette.py
```
