# Quick Settings Guide - Roulette Strategy Simulator

## 🎯 Recommended Settings (Start Here!)

### For Your Next Test Run

```
✓ Enable 'Negative > 20' Bypass Rule
  Stage 2 Starting Divisor: 8
  Maximum Bet Units Cap (Stage 2): 25
  Starting Sequence Codes: Standard (3, 4, 2)
  ✓ Enable Debug Output
```

**Why these settings?**
- ✅ Prevents the 52-unit bet that nearly depleted your bank
- ✅ Allows aggressive recovery when deeply negative
- ✅ Lower starting 'a' value (less likely to exceed 10)
- ✅ Shows exactly what's happening in debug output

---

## 📊 Settings Comparison Table

| Setting Type | Conservative | **Recommended** | Aggressive |
|--------------|-------------|-----------------|------------|
| **Bypass Rule** | ✓ Enabled | ✓ **Enabled** | ✓ Enabled |
| **Divisor** | 16 | **8** | 8 |
| **Max Bet Cap** | 20 | **25** | 40 |
| **Sequence Codes** | Standard | **Standard** | Alternative |
| **Bank Size Needed** | 250+ units | 500+ units | 1000+ units |

---

## 🔧 What Each Setting Does

### 1. Bypass Rule (Checkbox)

**✓ ENABLED** (Recommended)
- Allows betting when a > 10 IF negative > 20 units
- Prevents getting stuck unable to bet
- **Use when**: You want aggressive recovery

**Disabled**
- Strict a ≤ 10 rule (NO betting if a > 10)
- More conservative
- **Use when**: Testing original strategy

---

### 2. Stage 2 Starting Divisor

**Divisor = 8** (Recommended)
- Bet size = c / 8
- More aggressive bets
- Faster recovery
- Example: c=40 → 5 units

**Divisor = 16**
- Bet size = c / 16
- More conservative
- Slower recovery
- Example: c=40 → 2.5 units

**Divisor = 32**
- Bet size = c / 32
- Very conservative
- Very slow recovery
- Example: c=40 → 1.25 units

---

### 3. Maximum Bet Units Cap (NEW!)

**0 = No cap** (Original)
- Unlimited bet sizes
- Can exceed 50+ units
- ⚠️ Risk: Bank depletion

**20 units** (Conservative)
- Max loss = 80 chips per bet
- Very safe
- Slow recovery

**25 units** (Recommended)
- Max loss = 100 chips per bet
- Good balance
- Prevents catastrophic losses

**30 units** (Balanced)
- Max loss = 120 chips per bet
- Faster recovery
- Moderate risk

**40 units** (Aggressive)
- Max loss = 160 chips per bet
- Fast recovery
- Higher risk

---

### 4. Starting Sequence Codes

**Standard (3, 4, 2)** (Recommended)
- Starts with a=3, b=4, c=2
- Lower values
- Less likely to exceed a=10
- More forgiving

**Alternative (8, 44, 10)**
- Starts with a=8, b=44, c=10
- Higher values
- Can quickly exceed a=10
- More aggressive

---

## 📈 Real Impact: Your Session Analysis

### Your Original Session (2011-10-12_121.xls)

**Settings Used:**
```
✗ Bypass Rule: DISABLED ← Problem!
  Divisor: 32 ← Too high!
  Max Bet Cap: N/A (didn't exist) ← Problem!
  Sequence Codes: Alternative (8, 44, 10) ← Too aggressive!
```

**Result:** Nearly lost entire bank (-261 chips at worst)

---

### What Would Have Happened With Recommended Settings

**Settings:**
```
✓ Bypass Rule: ENABLED
  Divisor: 8
  Max Bet Cap: 25
  Sequence Codes: Standard (3, 4, 2)
```

**Impact on Critical Lines:**

| Line | Original | With Recommended | Improvement |
|------|----------|------------------|-------------|
| 59   | Skipped (a>10) | Would bet | ✅ More recovery chances |
| 88   | Skipped (a>10) | Would bet | ✅ More recovery chances |
| 101  | 29 units | 25 units | ✅ Saved 4 units |
| **102** | **52 units** | **25 units** | ✅ **Saved 27 units!** |

**Total Savings**: ~31 units = 124 chips

**Estimated Final Result**: -137 units instead of -261 units

---

## 🎮 How to Use

### Tab 1: Run Simulation

1. Load a file or use default outcomes
2. Set the 4 configuration options (see recommended above)
3. ✓ Enable Debug Output
4. Click "Run Simulation"
5. Review debug_output.txt

**Look for:**
- "Max bet cap applied" messages
- Final balance
- Session successful (✓ or ✗)

---

### Tab 2: Live Play Mode

1. Set the 4 configuration options
2. Click "Start New Live Session"
3. Choose input mode:
   - **Manual Entry**: Type numbers
   - **Spinning Wheel**: Click wheel, enter result
4. Follow betting recommendations
5. Click "Save Current Session" when done

**Watch for:**
- Current betting recommendation
- Sequence codes (a, b, c)
- Mixed numbers (negative/positive)
- Balance

---

## 🚨 Warning Signs

### Change Settings If You See:

**Frequent "a > 10" skipping**
→ Make sure Bypass Rule is ✓ ENABLED

**Bets exceeding 30 units**
→ Lower Max Bet Cap to 25 or 20

**Negative exceeding -100 units**
→ More conservative settings needed

**Bank below 100 units**
→ STOP and reconsider strategy

**Multiple 4-corner rules in Stage 2**
→ Consider modifying 4-corner behavior

---

## 📝 Quick Checklist

Before running a simulation:

- [ ] Bypass Rule = ✓ ENABLED
- [ ] Divisor = 8
- [ ] Max Bet Cap = 25
- [ ] Sequence Codes = Standard (3, 4, 2)
- [ ] Debug Output = ✓ ENABLED (for testing)
- [ ] File loaded or using defaults
- [ ] Reviewed last session's debug output

---

## 💡 Pro Tips

### Tip 1: Always Enable Debug Output (When Testing)
You can see exactly what's happening and why.

### Tip 2: Start Conservative, Then Adjust
Begin with cap=25, divisor=8. If you're winning consistently, you can increase cap to 30.

### Tip 3: Compare Sessions
Save sessions with different settings and compare in Tab 3 (View History).

### Tip 4: Watch for Cap Triggers
If you see "Max bet cap applied" frequently, you might be too aggressive.

### Tip 5: Use Standard Sequence Codes
Unless you have a specific reason, stick with Standard (3, 4, 2).

---

## 🔄 Common Scenarios

### Scenario 1: Testing New Settings
```
Conservative settings + Debug Output ON
Run 10 simulations
Review all debug files
Compare results
```

### Scenario 2: Live Play at Casino
```
Recommended settings
Spinning Wheel mode OR Manual Entry
Save session frequently
Don't chase losses
```

### Scenario 3: Maximum Safety
```
Bypass: Enabled
Divisor: 16
Max Bet Cap: 20
Sequence: Standard
```

### Scenario 4: Aggressive Recovery Test
```
Bypass: Enabled
Divisor: 8
Max Bet Cap: 30
Sequence: Standard
```

---

## 📁 File Reference

**Configuration Files:**
- `roulette.py` - Main application
- `MAX_BET_CAP_GUIDE.md` - Detailed feature guide
- `QUICK_SETTINGS_GUIDE.md` - This file

**Data Files:**
- `numbers/` - Input data files
- `session_history/` - Saved sessions
- `debug_output.txt` - Debug information

**Documentation:**
- `README.md` - Full documentation
- `QUICKSTART.md` - Getting started guide
- `CHANGELOG.md` - Version history

---

## ❓ FAQ

**Q: What if I set Max Bet Cap to 0?**
A: No cap is applied. Original behavior (bets can be unlimited).

**Q: Can I change settings mid-session in Live Play?**
A: No. Start a new session to change settings.

**Q: Which is more important: Bypass Rule or Max Bet Cap?**
A: Both are critical. Bypass Rule lets you bet when deeply negative. Max Bet Cap prevents huge losses.

**Q: What's the safest possible configuration?**
A: Bypass ON, Divisor=16, Cap=15, Sequence=Standard

**Q: What if I'm still losing with recommended settings?**
A: The strategy doesn't guarantee wins. No roulette strategy can overcome house edge long-term. Use for testing/analysis only.

---

## 🎯 Bottom Line

### Start Here:
```
✓ Bypass Rule: ON
  Divisor: 8
  Max Bet Cap: 25
  Sequence Codes: Standard (3, 4, 2)
```

### If Losing Too Much:
```
Cap: 20 (or 15)
Divisor: 16
```

### If Recovery Too Slow:
```
Cap: 30
Divisor: 8
```

### To Test Original Strategy:
```
Cap: 0
Everything else same
```

---

**Last Updated**: 2025-11-05
**Version**: With Max Bet Cap Feature
**Status**: ✅ Ready to Use
