import pandas as pd

# From mb_roulette_v1.txt - Technical Requirements
outcomes = [0, 15, 27, 33, 26, 14, 36, 2, 16, 22, 7, 17, 30, 22, 28, 9, 10, 11, 6, 1, 33, 10, 15, 18, 11, 9, 1, 7, 30, 30, 36, 36]

# A1 consisting of 16 numbers (4 x Corner Bets)
A1 = [2, 3, 5, 6, 17, 18, 20, 21, 25, 26, 28, 29, 31, 32, 34, 35]

# A2 consisting of 30 numbers (5 x Six-Line Bets): 1-6, 13-18, 19-24, 25-30, 31-36
A2 = []
for start in [1, 13, 19, 25, 31]:
    A2.extend(range(start, start + 6))

print("Starting Fresh Roulette System")
print(f"A1 (16 Corner Bets): {A1}")
print(f"A2 (30 Six-Line Bets): {A2}")
print(f"Total Outcomes: {len(outcomes)}")
print()

# Initialize variables
sequence_code = {'a': 3, 'b': 4, 'c': 2}
recording = False
balance = 0
current_bet_type = 1  # 1=Bet1, 2=Bet2, 3=Bet3

# A1 wait rule variables
waiting_for_a1_losses = False
non_a1_count = 0

# Four corner loss rule variables
four_corner_rule_active = False
consecutive_non_a1 = 0
pending_sequence_codes = None

def calculate_new_a(a):
    """Calculate new 'a' value for wins - from mb_roulette_v1.txt"""
    if a > 13:
        return 10
    elif 10 < a < 14:
        return a - 4
    elif 7 < a < 11:
        return a - 3
    elif a < 8:
        return a - 2
    return a

def update_sequence_codes(is_a1_win):
    """Update sequence codes based on A1 win/loss"""
    global sequence_code

    if is_a1_win:
        # Win logic from mb_roulette_v1.txt
        sequence_code['a'] = calculate_new_a(sequence_code['a'])
        sequence_code['b'] = sequence_code['b'] - sequence_code['c']
        sequence_code['c'] = (int(sequence_code['b'] / sequence_code['a'])) * 2
    else:
        # Loss logic from mb_roulette_v1.txt
        sequence_code['a'] = sequence_code['a'] + 1
        sequence_code['b'] = sequence_code['b'] + sequence_code['c']

        # Special rule: If B > 89 then B = (Int(B+1)) / 2
        if sequence_code['b'] > 89:
            sequence_code['b'] = int((sequence_code['b'] + 1) / 2)

        sequence_code['c'] = (int(sequence_code['b'] / sequence_code['a'])) * 2

def place_bet(outcome):
    """Place bet according to Bet1/Bet2/Bet3 progression from mb_roulette_v1.txt"""
    global balance, current_bet_type, waiting_for_a1_losses, non_a1_count
    global four_corner_rule_active, consecutive_non_a1, pending_sequence_codes

    # Check A1 wait rule first
    if waiting_for_a1_losses:
        if outcome in A1:
            # A1 outcome resets the counter
            non_a1_count = 0
            return 0  # No bet during wait period
        else:
            # Non-A1 outcome increments counter
            non_a1_count += 1
            if non_a1_count >= 3:
                waiting_for_a1_losses = False
                non_a1_count = 0
                print(f"A1 wait period ended after 3 non-A1 outcomes")
                return 0  # No bet on the line that ends the wait
            else:
                return 0  # No bet during wait period

    # Four corner rule logic moved to main loop

    # Determine bet parameters based on current bet type
    if current_bet_type == 1:
        # Bet1: Uses A2 list, 5 chips, +1 profit if win, -5 if lose
        bet_amount = 5
        bet_numbers = A2
        win_profit = 1
    elif current_bet_type == 2:
        # Bet2: Uses A1 list, 4 chips, +5 profit if win, -4 if lose
        bet_amount = 4
        bet_numbers = A1
        win_profit = 5
    elif current_bet_type == 3:
        # Bet3: Uses A1 list, 8 chips, +10 profit if win, -8 if lose
        bet_amount = 8
        bet_numbers = A1
        win_profit = 10
    else:
        return 0  # No more bets after Bet3 loss

    # Check if it's a win
    is_win = outcome in bet_numbers

    if is_win:
        balance += win_profit
        current_bet_type = 1  # Reset to Bet1 after any win

        # Check if this was an A1 win (triggers wait rule)
        if outcome in A1:
            waiting_for_a1_losses = True
            non_a1_count = 0
            print(f"A1 win detected - starting wait for 3 consecutive non-A1 outcomes")

    else:
        balance -= bet_amount
        current_bet_type += 1  # Progress to next bet type
        if current_bet_type > 3:
            print(f"Bet3 lost. Stage 1 ends.")
            return bet_amount

    return bet_amount

# Create DataFrame
results = []

for i, outcome in enumerate(outcomes):
    line_num = i + 1

    # Determine win/loss (W if in A1, L otherwise)
    win_status = 'W' if outcome in A1 else 'L'

    # Initialize row
    row = {
        'line': line_num,
        'outcome': outcome,
        'win': win_status,
        'a': '',
        'b': '',
        'c': '',
        'actual bet': '',
        'negative': '',
        'positive': '',
        'balance': ''
    }

    # Check for first A1 win to start recording
    if win_status == 'W' and not recording:
        recording = True
        print(f"First A1 win at line {line_num} - sequence codes will start next line")
        results.append(row)
        continue

    # If recording, process betting and sequence codes
    if recording:
        # Check if we have pending sequence codes to apply (from four corner rule)
        if pending_sequence_codes and not four_corner_rule_active:
            sequence_code.update(pending_sequence_codes)
            print(f"Applying pending sequence codes: {pending_sequence_codes}")
            pending_sequence_codes = None

        # Handle sequence code display with four corner rule
        if four_corner_rule_active:
            # Four corner rule active - don't show sequence codes on this line
            row['a'] = ''
            row['b'] = ''
            row['c'] = ''
            print(f"Four corner rule: suppressing sequence codes on line {line_num}")
        elif pending_sequence_codes:
            # Apply pending codes from four corner rule
            sequence_code.update(pending_sequence_codes)
            row['a'] = sequence_code['a']
            row['b'] = sequence_code['b']
            row['c'] = sequence_code['c']
            print(f"Applying delayed four corner codes: {pending_sequence_codes}")
            pending_sequence_codes = None
        else:
            # Normal sequence code display
            row['a'] = sequence_code['a']
            row['b'] = sequence_code['b']
            row['c'] = sequence_code['c']

        # Place bet (independent of sequence code logic)
        bet_amount = place_bet(outcome)
        if bet_amount > 0:
            row['actual bet'] = bet_amount
            row['balance'] = balance

        # Track consecutive non-A1 outcomes for four corner rule (always track)
        if outcome in A1:
            consecutive_non_a1 = 0  # Reset counter on A1 outcome
            if four_corner_rule_active:
                # A1 outcome ends four corner rule
                print(f"Four corner loss rule ended - A1 outcome detected")
                four_corner_rule_active = False
        else:
            consecutive_non_a1 += 1
            print(f"Consecutive non-A1 count: {consecutive_non_a1}")

        # Update sequence codes for next line (ALWAYS update, even during A1 wait)
        is_a1_win = outcome in A1
        update_sequence_codes(is_a1_win)

        # Check if we just hit 4 consecutive non-A1 (triggers four corner rule)
        if consecutive_non_a1 == 4:
            four_corner_rule_active = True
            pending_sequence_codes = sequence_code.copy()
            print(f"Four corner rule triggered! Calculated codes {pending_sequence_codes} will be delayed")

    results.append(row)

# Create and display DataFrame
df = pd.DataFrame(results)

print("\nBetting Results:")
print(df.to_string(index=False))
print(f"\nFinal Balance: {balance}")