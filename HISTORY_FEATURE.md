# Historical Session Tracking Feature

## Overview
Added comprehensive session history tracking to the roulette system, allowing you to save, view, analyze, and compare past sessions.

## New Features

### 1. Session Storage
- **Location**: `session_history/` folder (auto-created)
- **Format**: JSON files named `session_YYYY-MM-DD_HHMMSS.json`
- **Data Saved**:
  - Timestamp and configuration (file used, sequence codes, divisor)
  - Complete results (balance, sequences, profit/loss)
  - Full DataFrame with all betting details
  - Balance progression history
  - System debug messages

### 2. Run Simulation Tab
- **New Checkbox**: "Save session to history" (enabled by default)
- Automatically saves session after each simulation
- Success message confirms save with filename

### 3. View History Tab
Complete session history management interface:

#### Overall Statistics Dashboard
- Total number of sessions
- Overall win rate percentage
- Total profit/loss in chips and units
- Displayed in 4 metric cards

#### Session List Table
Displays all sessions with:
- Date/Time
- File used
- Sequence codes
- Stage 2 divisor
- Sequences completed
- Profit/Loss (chips and units)
- Session status

#### Session Detail Viewer
Select any session to view:
- **Configuration Details**: File, sequence codes, divisor, outcomes
- **Results Summary**: Sequences, balance, profit/loss, status
- **Balance Progression Chart**: Visual graph of balance over time
- **Complete Betting Details**: Full DataFrame from the session
- **System Messages**: Expandable section with debug messages
- **Delete Option**: Remove unwanted sessions

#### Session Comparison
- Compares performance by sequence code configuration
- Shows sessions count, win rate, total profit, and average profit
- Helps identify best performing configurations

#### Export Functionality
- Export all session history to CSV
- Downloadable file with timestamp
- Useful for external analysis in Excel or other tools

## Usage

### Running a Session
1. Configure your simulation in the "Run Simulation" tab
2. Ensure "Save session to history" is checked
3. Click "Run Simulation"
4. Session automatically saved after completion

### Viewing History
1. Switch to "View History" tab
2. Browse overall statistics and session list
3. Select a session from dropdown to view details
4. Use comparison section to analyze performance trends

### Managing History
- **Delete Sessions**: Click "Delete this session" button in detail view
- **Export Data**: Click "Export All Sessions to CSV" for backup/analysis
- **Session Files**: Located in `session_history/` folder

## Technical Details

### File Structure
```json
{
  "timestamp": "ISO 8601 format",
  "configuration": {
    "file": "filename or 'Default outcomes'",
    "sequence_codes": "Standard (3, 4, 2) or Alternative (8, 44, 10)",
    "stage2_divisor": 8,
    "total_outcomes": 61
  },
  "results": {
    "sequences_completed": 1,
    "final_balance_chips": 12,
    "starting_bank_units": 250,
    "final_bank_units": 253,
    "session_status": "ACTIVE or ENDED",
    "outcomes_processed": 61,
    "profit_loss_chips": 12,
    "profit_loss_units": 3
  },
  "dataframe": [...],
  "balance_history": [...],
  "debug_messages": [...]
}
```

### Functions Added
- `ensure_history_folder()`: Creates session_history folder
- `save_session(session_data)`: Saves session to JSON file
- `load_all_sessions()`: Loads all sessions from folder
- `delete_session(filename)`: Deletes a session file

## Benefits

1. **Track Performance**: Monitor your results over time
2. **Compare Strategies**: See which sequence codes work best
3. **Learn Patterns**: Review successful sessions to understand what works
4. **Data Analysis**: Export to CSV for advanced analysis
5. **Record Keeping**: Maintain complete history of all simulations
6. **Easy Review**: Quickly access past sessions with all details

## Testing

The feature has been tested and verified:
- ✅ Syntax validation passed
- ✅ Streamlit app starts successfully
- ✅ All tabs render correctly
- ✅ Session save/load functionality implemented
- ✅ No Python errors or warnings

## Next Steps (Optional Enhancements)

Potential future improvements:
- Add session notes/comments
- Date range filtering
- Advanced charts (profit trend over time)
- Session tagging/categorization
- Automatic backup of history folder
- Performance analytics (max drawdown, recovery rate, etc.)
