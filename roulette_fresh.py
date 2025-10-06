import pandas as pd

# From mb_roulette_v1.txt - Technical Requirements
outcomes = [0, 15, 27, 33, 26, 14, 36, 2, 16, 22, 7, 17, 30, 22, 28, 9, 10, 11, 6, 1, 33, 10, 15, 18, 11, 9, 1, 7, 30, 30, 36, 36,4,4,
32,28,6,10,22,24,33,36,15,34,9,0,0,1,18,19,20,8,17,11,27,16,26,4,29,2,2]

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

# Stage tracking
stage = 1  # 1=Stage1, 2=Stage2
stage1_complete = False
stage2_recovery_target = 0  # Will be set when Stage 1 ends

# Stage 2 variables
stage2_divisor = 8  # Initial divisor, user configurable
stage2_betting_active = False

# Mixed numbers tracking
cumulative_negative = {'integer': 0, 'decimal': 0}
cumulative_positive_chips = 0  # Track positive column in chips

# A1 wait rule variables (Stage 1 only)
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

def chips_to_mixed_number(chips):
    """Convert chip loss to mixed number format"""
    if chips == 0:
        return {'integer': 0, 'decimal': 0}

    # For losses, chips will be negative
    abs_chips = abs(chips)
    units_of_4 = abs_chips // 4
    remainder = abs_chips % 4

    if chips < 0:
        # For negative chips, we need to handle the remainder correctly
        if remainder == 0:
            return {'integer': -units_of_4, 'decimal': 0}
        else:
            # Adjust for proper mixed number representation
            # e.g., 5 chips = -2.3 where -2*4 + 3 = -8+3 = -5
            return {'integer': -(units_of_4 + 1), 'decimal': 4 - remainder}
    else:
        return {'integer': units_of_4, 'decimal': remainder}

def add_mixed_numbers(mixed1, mixed2):
    """Add two mixed numbers together"""
    if mixed1['integer'] == 0 and mixed1['decimal'] == 0:
        return mixed2
    if mixed2['integer'] == 0 and mixed2['decimal'] == 0:
        return mixed1

    # Simply add the integer parts (the decimal part is handled separately)
    return {'integer': mixed1['integer'] + mixed2['integer'], 'decimal': mixed1['decimal']}

def add_chips_to_mixed_positive(current_mixed_positive, additional_chips):
    """Add chips to existing mixed number in positive column, return new mixed number"""
    # Convert current mixed positive decimal to chips
    current_chips = current_mixed_positive

    # Add the additional chips
    total_chips = current_chips + additional_chips

    # Convert back to mixed number
    return chips_to_mixed_number(total_chips)

def calculate_recovery_profit(negative_mixed, positive_mixed):
    """Calculate if loss is recovered and return profit in chips"""
    # Convert both to chips and add
    negative_chips = mixed_to_chips_from_dict(negative_mixed)
    positive_chips = positive_mixed  # This is already in chips from decimal part

    total = negative_chips + positive_chips
    return max(0, total)  # Return 0 if still negative, otherwise return profit

def mixed_to_chips_from_dict(mixed_dict):
    """Convert mixed number dict back to chips"""
    if mixed_dict['integer'] < 0:
        # For negative mixed numbers, decimal is already accounted for in the conversion
        return mixed_dict['integer'] * 4
    else:
        return (mixed_dict['integer'] * 4) + mixed_dict['decimal']

def mixed_to_chips(mixed_num):
    """Convert mixed number back to chips"""
    if mixed_num == 0:
        return 0

    if mixed_num < 0:
        # Handle negative mixed numbers
        str_mixed = str(mixed_num)
        if '.' in str_mixed:
            parts = str_mixed.split('.')
            units = int(parts[0])  # Already negative
            decimal = int(parts[1])
            return (units * 4) + decimal  # units*4 is negative, decimal positive
        else:
            return int(mixed_num) * 4
    else:
        # Handle positive mixed numbers
        str_mixed = str(mixed_num)
        if '.' in str_mixed:
            parts = str_mixed.split('.')
            units = int(parts[0])
            decimal = int(parts[1])
            return (units * 4) + decimal
        else:
            return int(mixed_num) * 4

def update_sequence_codes(is_a1_win):
    """Update sequence codes based on A1 win/loss"""
    global sequence_code, stage, stage2_divisor

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
            # In Stage 2, halve the divisor when b > 89 rule applies AND we're actively betting
            if stage == 2 and stage2_divisor > 1 and recording and not four_corner_rule_active:
                stage2_divisor = stage2_divisor // 2
                print(f"b > 89 rule applied in Stage 2 - divisor reduced to {stage2_divisor}")

        sequence_code['c'] = (int(sequence_code['b'] / sequence_code['a'])) * 2

def place_bet(outcome):
    """Place bet according to Bet1/Bet2/Bet3 progression from mb_roulette_v1.txt"""
    global balance, current_bet_type, waiting_for_a1_losses, non_a1_count
    global four_corner_rule_active, consecutive_non_a1, pending_sequence_codes
    global cumulative_negative, cumulative_positive_chips

    # Check A1 wait rule first
    if waiting_for_a1_losses:
        if outcome in A1:
            # A1 outcome resets the counter
            non_a1_count = 0
            return {'bet_amount': 0, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': False}  # No bet during wait period
        else:
            # Non-A1 outcome increments counter
            non_a1_count += 1
            if non_a1_count >= 3:
                waiting_for_a1_losses = False
                non_a1_count = 0
                print(f"A1 wait period ended after 3 non-A1 outcomes")
                return {'bet_amount': 0, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': False}  # No bet on the line that ends the wait
            else:
                return {'bet_amount': 0, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': False}  # No bet during wait period

    # Four corner rule logic moved to main loop

    # Determine bet parameters based on current bet type
    if current_bet_type == 1:
        # Bet1: Uses A2 list, 5 chips, +1 profit if win, -5 if lose
        bet_amount = 5
        bet_numbers = A2
        win_profit = 1
        bet_units = 0  # Bet1 doesn't use mixed number logic
    elif current_bet_type == 2:
        # Bet2: Uses A1 list, 4 chips, +5 profit if win, -4 if lose
        bet_amount = 4
        bet_numbers = A1
        win_profit = 5
        bet_units = 1  # 1 unit bet
    elif current_bet_type == 3:
        # Bet3: Uses A1 list, 8 chips, +10 profit if win, -8 if lose
        bet_amount = 8
        bet_numbers = A1
        win_profit = 10
        bet_units = 2  # 2 unit bet
    else:
        return {'bet_amount': 0, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': False}  # No more bets after Bet3 loss

    # Check if it's a win
    is_win = outcome in bet_numbers

    if is_win:
        # Handle win logic
        if current_bet_type == 1:
            # Bet1 win - normal logic
            balance += win_profit
            current_bet_type = 1  # Reset to Bet1 after any win

            # Check if this was an A1 win (triggers wait rule)
            if outcome in A1:
                waiting_for_a1_losses = True
                non_a1_count = 0
                print(f"A1 win detected - starting wait for 3 consecutive non-A1 outcomes")

            return {'bet_amount': bet_amount, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': False}

        else:
            # Bet2 or Bet3 win on A1 - mixed number logic
            # Reduce negative by bet units
            cumulative_negative['integer'] += bet_units

            # Add Built-in Profit (BIP) to positive
            bip_chips = bet_units  # 1 unit = 1 chip BIP, 2 units = 2 chips BIP
            # Add existing decimal chips from negative mixed number + BIP
            existing_decimal_chips = cumulative_negative['decimal']
            cumulative_positive_chips = existing_decimal_chips + bip_chips

            # Check for recovery - but only add the BIP to balance, not the existing .3
            negative_chips = mixed_to_chips_from_dict(cumulative_negative)
            total_recovery = negative_chips + cumulative_positive_chips

            if total_recovery >= 0:
                # Recovery achieved - add the net profit (total_recovery)
                balance += total_recovery
                # Note: Don't reset mixed numbers here - show them on the line, reset after display

            current_bet_type = 1  # Reset to Bet1 after any win

            # Check if this was an A1 win (triggers wait rule)
            if outcome in A1:
                waiting_for_a1_losses = True
                non_a1_count = 0
                print(f"A1 win detected - starting wait for 3 consecutive non-A1 outcomes")

            return {'bet_amount': bet_amount, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': True}

    else:
        # Handle loss with mixed numbers
        loss_mixed_number = chips_to_mixed_number(-bet_amount)
        cumulative_negative = add_mixed_numbers(cumulative_negative, loss_mixed_number)

        current_bet_type += 1  # Progress to next bet type
        if current_bet_type > 3:
            print(f"Bet3 lost. Stage 1 ends, Stage 2 begins.")
            global stage1_complete, stage, stage2_recovery_target
            stage1_complete = True
            stage = 2
            # Calculate recovery target from current mixed numbers
            negative_chips = mixed_to_chips_from_dict(cumulative_negative)
            stage2_recovery_target = negative_chips  # This will be negative
            # Initialize Stage 2 positive chips with the decimal part from Stage 1
            cumulative_positive_chips = cumulative_negative['decimal']
            return {'bet_amount': bet_amount, 'loss_mixed': loss_mixed_number, 'win_mixed': False}

        return {'bet_amount': bet_amount, 'loss_mixed': loss_mixed_number, 'win_mixed': False}

def place_stage2_bet(outcome, codes_displayed):
    """Place Stage 2 recovery bet based on c value and divisor"""
    global balance, stage2_divisor, cumulative_negative, cumulative_positive_chips
    global stage2_recovery_target, stage, sequence_code

    # In Stage 2, no betting when sequence codes are not displayed
    if not codes_displayed:
        return {'bet_amount': 0, 'units': 0, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': False}

    # Check if a > 10 (no betting if true), UNLESS negative > 20 units
    negative_units = abs(cumulative_negative['integer'])
    if sequence_code['a'] > 10 and negative_units <= 20:
        return {'bet_amount': 0, 'units': 0, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': False}

    # Calculate bet units: c / divisor
    bet_units = int(sequence_code['c'] / stage2_divisor)
    if bet_units == 0:
        bet_units = 1  # Minimum bet

    bet_chips = bet_units * 4  # Convert units to chips

    # Check if it's a win (A1 numbers only in Stage 2)
    is_win = outcome in A1

    if is_win:
        # Stage 2 win - apply mixed number recovery logic
        # Reduce negative by bet units
        cumulative_negative['integer'] += bet_units

        # Add Built-in Profit (BIP) to existing positive
        bip_chips = bet_units  # 1 unit = 1 chip BIP
        cumulative_positive_chips += bip_chips  # Simply add BIP to existing positive

        # Check for complete recovery
        negative_chips = mixed_to_chips_from_dict(cumulative_negative)
        total_recovery = negative_chips + cumulative_positive_chips

        # Check for complete recovery (when total becomes positive)
        if total_recovery >= 0:
            # Full recovery achieved!
            balance += total_recovery  # Add profit to balance
            print(f"Stage 2 recovery successful! Recovered 17 chips plus {total_recovery} profit.")
            print(f"Sequence completed successfully.")
            # Don't reset mixed numbers yet - show them on this line first
            stage = 3  # Mark as completed

        return {'bet_amount': bet_chips, 'units': bet_units, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': True}

    else:
        # Stage 2 loss
        loss_mixed_number = chips_to_mixed_number(-bet_chips)
        cumulative_negative = add_mixed_numbers(cumulative_negative, loss_mixed_number)

        # Check if bank is lost (1000 chips = 250 units)
        total_negative_chips = abs(mixed_to_chips_from_dict(cumulative_negative))
        if total_negative_chips >= 1000:
            print(f"Bank lost! Stage 2 recovery failed.")
            stage = 4  # Mark as failed

        return {'bet_amount': bet_chips, 'units': bet_units, 'loss_mixed': loss_mixed_number, 'win_mixed': False}

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

        # Place bet (stage-dependent logic)
        if stage == 1:
            bet_result = place_bet(outcome)
        elif stage == 2:
            # In Stage 2, check if sequence codes are being displayed
            codes_displayed = not (four_corner_rule_active or (pending_sequence_codes and not four_corner_rule_active))
            if four_corner_rule_active:
                codes_displayed = False
            elif row['a'] != '':  # If sequence codes are shown in this row
                codes_displayed = True
            else:
                codes_displayed = False
            bet_result = place_stage2_bet(outcome, codes_displayed)
        else:
            # Stage completed, no more betting
            bet_result = {'bet_amount': 0, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': False}
            # Show STOP message on line after recovery
            if stage == 3:
                row['actual bet'] = 'STOP'
                print(f"Recovery in Stage 2 has now been successfully completed.")

        if bet_result['bet_amount'] > 0:
            # Display bet type based on stage
            if stage == 1:
                # Stage 1 bet display
                if bet_result['bet_amount'] == 5:
                    row['actual bet'] = 'Bet 1'
                elif bet_result['bet_amount'] == 4:
                    row['actual bet'] = 'Bet 2'
                elif bet_result['bet_amount'] == 8:
                    row['actual bet'] = 'Bet 3'
            elif (stage == 2 or (stage == 3 and 'units' in bet_result)) and 'units' in bet_result:
                # Stage 2 bet display - show units (including recovery line)
                row['actual bet'] = f"{bet_result['units']} units"

            # Handle mixed numbers for losses
            if bet_result['loss_mixed']['integer'] != 0 or bet_result['loss_mixed']['decimal'] != 0:
                # Display cumulative negative mixed number
                row['negative'] = cumulative_negative['integer']

                # Show decimal part in positive column only if there's a remainder AND it's the first loss in sequence
                if cumulative_negative['decimal'] > 0 and cumulative_negative['integer'] == -2:
                    row['positive'] = f".{cumulative_negative['decimal']}"

                # No balance shown for losses during Stage 1
            elif bet_result['win_mixed']:
                # Bet2 or Bet3 win with mixed number logic (Stage 1) or Stage 2 win
                row['negative'] = cumulative_negative['integer']

                # Display positive column with mixed number format
                if cumulative_positive_chips > 0:
                    positive_mixed = chips_to_mixed_number(cumulative_positive_chips)
                    if positive_mixed['integer'] > 0:
                        if positive_mixed['decimal'] > 0:
                            row['positive'] = f"{positive_mixed['integer']}.{positive_mixed['decimal']}"
                        else:
                            row['positive'] = f"{positive_mixed['integer']}"  # Show just integer, not .0
                    else:
                        row['positive'] = f".{positive_mixed['decimal']}"

                # Show balance only if recovery is complete (Stage 3) or normal Stage 1 win
                if stage == 3 or stage == 1:
                    row['balance'] = balance

                # Reset mixed numbers after recovery (if stage is completed)
                if stage == 3:
                    cumulative_negative = {'integer': 0, 'decimal': 0}
                    cumulative_positive_chips = 0
            else:
                # Normal win case (Bet1)
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