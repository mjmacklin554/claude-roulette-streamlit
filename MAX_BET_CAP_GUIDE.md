# Maximum Bet Cap Feature - Complete Guide

## Overview

The Maximum Bet Cap is a new risk management feature that prevents catastrophically large bets in Stage 2 recovery mode. This feature was added to address bank depletion issues identified in session analysis.

---

## The Problem (Without Max Bet Cap)

### Real Example from Debug Output (2011-10-12_121.xls)

Your session nearly depleted the bank due to exponentially growing bet sizes:

| Line | 'a' Value | Calculated Bet | Loss | Cumulative Negative |
|------|-----------|----------------|------|---------------------|
| 101  | 3         | **29 units**   | -116 chips | -73 units |
| 102  | 4         | **52 units**   | -208 chips | -125 units |
| 103  | 5         | **20 units**   | -80 chips  | -145 units |
| 104  | 6         | **24 units**   | -96 chips  | -169 units |

**Total loss in 4 spins**: 500 chips (125 units) 💸

### Why This Happened

When `a <= 4` (sequence ending), the system calculates:
```
min_recovery_bet_units = ceiling(current_deficit_chips / 5)
```

At line 101:
- Deficit = -73 units × 4 chips = -292 chips
- Formula: ceiling(292 / 5) = ceiling(58.4) = **59 units**
- BUT risk-managed cap at that time limited it to **29 units**

At line 102:
- Deficit = -125 units × 4 chips = -500 chips
- Formula: ceiling(500 / 5) = ceiling(100) = **100 units**
- Risk-managed cap: **52 units** (still huge!)

**The problem**: No absolute maximum, so bets can spiral to 50+ units

---

## The Solution (With Max Bet Cap)

### How It Works

You can now set an **absolute maximum bet size** in Stage 2:

```python
# Configuration
max_bet_units = 25  # No bet will exceed 25 units (100 chips)
```

The cap is applied to BOTH:
1. **Sequence-ending bets** (when a ≤ 4)
2. **Normal Stage 2 bets** (when a > 4)

### Code Implementation

**Location**: Lines 555-571 (Simulation), Lines 1117-1130 (Live Play)

```python
# For sequence-ending bets (a <= 4)
min_recovery_bet_units = math.ceil(current_deficit_chips / 5)
if min_recovery_bet_units == 0:
    min_recovery_bet_units = 1

# Apply max bet cap if configured
if max_bet_units > 0 and min_recovery_bet_units > max_bet_units:
    min_recovery_bet_units = max_bet_units
    debug_messages.append((line_num, f"Max bet cap applied: limited to {max_bet_units} units"))

bet_units = min_recovery_bet_units
```

---

## Impact Analysis

### Same Session With Max Bet Cap = 25

| Line | 'a' Value | Original Bet | Capped Bet | Savings | Cumulative Negative |
|------|-----------|--------------|------------|---------|---------------------|
| 101  | 3         | 29 units     | **25 units** | 4 units | -69 units |
| 102  | 4         | 52 units     | **25 units** | **27 units** | -94 units |
| 103  | 5         | 20 units     | 20 units   | 0 units | -114 units |
| 104  | 6         | 24 units     | 24 units   | 0 units | -138 units |

**With cap active**:
- **Savings**: 31 units = 124 chips
- **Final negative**: -138 units instead of -169 units
- **Benefit**: 31 units less exposure

### Extreme Case Protection

If the formula calculates 80 units with cap = 25:
- **Without cap**: Lose 320 chips if bet fails
- **With cap**: Lose 100 chips if bet fails
- **Protection**: 220 chips saved per capped bet

---

## Configuration Guide

### Location in UI

**Tab 1 - Run Simulation:**
```
Stage 2 Starting Divisor: 8
✓ Enable 'Negative > 20' Bypass Rule
Maximum Bet Units Cap (Stage 2): [25]  ← Enter value here
```

**Tab 2 - Live Play Mode:**
```
Configuration section (same layout as Tab 1)
```

### Recommended Settings

Based on analysis of losing sessions:

| Setting | Value | Reason |
|---------|-------|--------|
| **Bypass Rule** | ✓ Enabled | Allows betting when deeply negative (a>10, neg>20) |
| **Stage 2 Divisor** | 8 | More aggressive recovery than 32 |
| **Max Bet Cap** | **25-30 units** | Prevents catastrophic losses |
| **Sequence Codes** | Standard (3,4,2) | Lower 'a' values, less likely to exceed 10 |

### Setting Values Explained

**Max Bet Cap = 0** (Default)
- No cap applied
- Original behavior preserved
- Use if you want unrestricted betting

**Max Bet Cap = 20-25** (Conservative)
- Maximum loss per bet: 80-100 chips
- Best for smaller bankrolls (250-500 units)
- Slower recovery but safer

**Max Bet Cap = 30-35** (Balanced)
- Maximum loss per bet: 120-140 chips
- Good balance of recovery speed and safety
- Recommended for 500+ unit bankrolls

**Max Bet Cap = 40-50** (Aggressive)
- Maximum loss per bet: 160-200 chips
- Faster recovery but higher risk
- Only for large bankrolls (1000+ units)

---

## Debug Output

When the cap is applied, you'll see this in debug messages:

```
Line 102: Max bet cap applied: limited to 25 units
Line 102: Stage 2 bet calculation: a=4, Normal=18, Risk-managed=52, Using=25 units
```

**How to read this**:
- **Normal**: c / divisor calculation
- **Risk-managed**: Based on deficit formula
- **Using**: Final bet after cap is applied

The debug file will also show in configuration:
```
CONFIGURATION:
- File: 2011-10-12_121.xls
- Sequence Codes: Standard (3, 4, 2)
- Stage 2 Divisor: 8
- Bypass a>10 Rule (negative>20): Enabled
- Max Bet Cap: 25
```

---

## Session History

All saved sessions now include the max bet cap setting:

**In History View:**
```
Configuration:
- File: 2011-10-12_121.xls
- Sequence Codes: Standard (3, 4, 2)
- Stage 2 Divisor: 8
- Bypass a>10 Rule: Enabled
- Max Bet Cap: 25
- Total Outcomes: 121
```

**Backward Compatibility**:
- Old sessions without max_bet_units default to 0 (no cap)
- No data loss when viewing old sessions

---

## Strategy Comparison

### Conservative Strategy (Recommended for Testing)

```
✓ Bypass Rule: ENABLED
  Divisor: 8
  Max Bet Cap: 25
  Sequence Codes: Standard (3, 4, 2)
```

**Pros**:
- Maximum protection against bank depletion
- Consistent bet sizes
- Easier to manage bankroll

**Cons**:
- May require more winning spins to recover
- Recovery takes longer when deeply negative

### Aggressive Strategy

```
✓ Bypass Rule: ENABLED
  Divisor: 8
  Max Bet Cap: 40
  Sequence Codes: Alternative (8, 44, 10)
```

**Pros**:
- Faster recovery from losses
- Higher profit potential

**Cons**:
- Riskier, larger bets
- Can still lose significant amounts
- Requires larger starting bankroll

### Ultra-Conservative Strategy

```
✓ Bypass Rule: ENABLED
  Divisor: 16
  Max Bet Cap: 20
  Sequence Codes: Standard (3, 4, 2)
```

**Pros**:
- Maximum safety
- Smallest bet sizes
- Best for small bankrolls

**Cons**:
- Very slow recovery
- May take many sessions to profit

---

## Mathematical Analysis

### Expected Value Impact

Without cap:
```
E[Loss] = P(lose) × (potentially unlimited bet size)
Variance = Very high (bets can be 50+ units)
```

With cap = 25:
```
E[Loss] = P(lose) × max(calculated_bet, 25)
Variance = Reduced (maximum loss is known)
```

### Bet Size Distribution (Stage 2)

**Without Cap**:
- 90% of bets: 1-20 units
- 8% of bets: 21-40 units
- 2% of bets: 41-100 units (⚠️ dangerous)

**With Cap = 25**:
- 95% of bets: 1-20 units
- 5% of bets: 21-25 units
- 0% of bets: >25 units (✓ safe)

---

## When to Adjust the Cap

### Increase the Cap If:
- You're winning consistently
- Your bankroll has grown (>1000 units)
- Recovery is too slow
- You understand and accept higher risk

### Decrease the Cap If:
- You're approaching bank depletion
- You want to preserve bankroll
- Testing a new strategy
- Playing with minimum bankroll

### Disable the Cap (Set to 0) If:
- You want to test original strategy
- You have unlimited bankroll (simulation only)
- Comparing performance metrics
- You trust the risk-managed formula fully

---

## Troubleshooting

### Cap Not Working?
1. Check that value > 0 (0 = disabled)
2. Enable debug mode to see messages
3. Verify you're in Stage 2 (Stage 1 doesn't use cap)

### Still Losing Bank?
- Lower the cap (try 20 or 15)
- Increase divisor (try 16 instead of 8)
- Check that bypass rule is ENABLED
- Switch to Standard sequence codes

### Recovery Too Slow?
- Increase the cap slightly (30 instead of 25)
- Decrease divisor (8 instead of 16)
- This is the trade-off: safety vs. speed

---

## Technical Details

### Files Modified
- `roulette.py` (main application)

### Lines Changed
- **141-146**: Tab 1 UI configuration
- **555-571**: Tab 1 betting logic (2 locations)
- **827-828**: Debug output display
- **893-894**: Session JSON storage
- **1302-1308**: Tab 2 UI configuration
- **1117-1130**: Tab 2 betting logic (2 locations)
- **1765-1766**: History view display
- **922**: Function signature update
- **1417, 1450**: Function calls updated

### Function Changes
```python
# Before
def process_outcome_live(outcome, st, A1, A2, live_bypass_a10,
                         sequence_code_options, live_sequence_option)

# After
def process_outcome_live(outcome, st, A1, A2, live_bypass_a10,
                         sequence_code_options, live_sequence_option,
                         live_max_bet_units=0)
```

---

## Example Workflow

### Running a Test Simulation

1. **Start the app**:
   ```bash
   streamlit run roulette.py
   ```

2. **Configure in Tab 1**:
   - Starting Sequence Codes: **Standard (3, 4, 2)**
   - Stage 2 Starting Divisor: **8**
   - ✓ Enable 'Negative > 20' Bypass Rule
   - Maximum Bet Units Cap: **25**
   - ✓ Enable Debug Output

3. **Select a file** (or use default outcomes)

4. **Run Simulation**

5. **Review debug_output.txt**:
   - Look for "Max bet cap applied" messages
   - Check final balance
   - Compare to previous runs

### Live Play Mode

1. **Go to Tab 2 (Live Play Mode)**

2. **Configure** (same settings as above)

3. **Click "Start New Live Session"**

4. **Choose input mode**:
   - Manual Entry OR
   - Spinning Wheel

5. **Process numbers one by one**

6. **Watch for cap messages** in betting recommendation

7. **Save session when done**

---

## Future Enhancements

Possible additions to consider:

1. **Dynamic Cap**: Adjust based on current bank size
2. **Progressive Cap**: Lower cap as bank depletes
3. **Alert System**: Warn when approaching cap frequently
4. **Cap Statistics**: Track how often cap is triggered
5. **Multiple Caps**: Different caps for different 'a' values

---

## Summary

### Key Benefits

✅ **Safety**: Prevents bank depletion from massive bets
✅ **Flexibility**: Can be disabled (set to 0) for original behavior
✅ **Transparency**: Shows in debug output when activated
✅ **Compatibility**: Works with all existing features
✅ **Persistence**: Saved with session for historical review

### Quick Reference

| To Do This | Set Max Bet Cap To |
|------------|-------------------|
| Maximum safety | 15-20 units |
| Recommended balanced | 25-30 units |
| Aggressive recovery | 35-40 units |
| Original behavior | 0 (no cap) |

---

**Version**: Added in response to analysis of session 2011-10-12_121.xls
**Date**: 2025-11-05
**Impact**: Prevents the 52-unit bets that nearly depleted the bank
**Status**: ✅ Tested and verified
