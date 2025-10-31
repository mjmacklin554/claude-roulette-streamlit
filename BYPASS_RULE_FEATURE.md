# Bypass a>10 Rule Feature

## Summary
Added a configurable option to control whether the system allows betting in Stage 2 when `a > 10` and negative units exceed 20.

## Changes Made

### 1. UI Configuration (Line 110-112)
Added a new checkbox in the Streamlit interface:
```python
bypass_a10_rule = st.checkbox("Enable 'Negative > 20' Bypass Rule", value=True,
                              help="When enabled, allows betting even when a > 10 if negative exceeds 20 units. When disabled, ALWAYS enforces a ≤ 10 rule.")
```

**Default**: Enabled (maintains original behavior)

### 2. Stage 2 Betting Logic (Lines 465-482)
Updated the betting decision logic to respect the bypass rule setting:

**When Bypass Rule is ENABLED (default):**
- Bets when `a ≤ 10` OR when `negative > 20` units
- This is the original behavior
- Debug message: "Bypass rule activated: a=X > 10 but negative=Y > 20, continuing to bet"

**When Bypass Rule is DISABLED:**
- Bets ONLY when `a ≤ 10`
- Strictly enforces the a ≤ 10 rule regardless of negative units
- Debug message: "Bypass rule disabled: a=X > 10, skipping bet"

### 3. Session History (Lines 833, 928, 971)
- Configuration is saved with each session
- History table shows "Bypass" column (Yes/No)
- Session details display the bypass rule setting
- Backward compatible: defaults to "Yes" for old sessions

### 4. Debug Output (Line 773)
Added bypass rule setting to debug output configuration section:
```
- Bypass a>10 Rule (negative>20): Enabled/Disabled
```

## Testing Example

Looking at line 78 in your debug_output.txt:
```
Line 78: a=11, negative=32 units
```

**With Bypass Rule ENABLED (default):**
- Will place bet because negative (32) > 20

**With Bypass Rule DISABLED:**
- Will NOT place bet because a (11) > 10
- System will wait until `a` decreases to 10 or less before betting

## How to Use

1. Run the Streamlit app
2. Check or uncheck "Enable 'Negative > 20' Bypass Rule"
3. Run simulation
4. Compare results between the two settings

## Impact on Strategy

**Enabling the bypass rule (original behavior):**
- More aggressive recovery attempts when deeply negative
- May increase bet frequency during difficult sequences
- Can potentially recover from larger drawdowns

**Disabling the bypass rule (new option):**
- More conservative approach
- Strictly enforces the a ≤ 10 betting condition
- May reduce risk but potentially leave larger unrecovered losses
- Useful for testing the system's behavior without the special exception
