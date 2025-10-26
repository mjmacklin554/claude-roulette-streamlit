import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# From mb_roulette_v1.txt - Technical Requirements
outcomes = [0, 15, 27, 33, 26, 14, 36, 2, 16, 22, 7, 17, 30, 22, 28, 9, 10, 11, 6, 1, 33, 10, 15, 18, 11, 9, 1, 7, 30, 30, 36, 36,4,4,
32,28,6,10,22,24,33,36,15,34,9,0,0,1,18,19,20,8,17,11,27,16,26,4,29,2,2]

# A1 consisting of 16 numbers (4 x Corner Bets)
A1 = [2, 3, 5, 6, 17, 18, 20, 21, 25, 26, 28, 29, 31, 32, 34, 35]

# A2 consisting of 30 numbers (5 x Six-Line Bets): 1-6, 13-18, 19-24, 25-30, 31-36
A2 = []
for start in [1, 13, 19, 25, 31]:
    A2.extend(range(start, start + 6))

# Streamlit user inputs
st.title("Michael's Roulette System Configuration")

# File input for outcomes
import os
numbers_folder = "numbers"
available_files = []
if os.path.exists(numbers_folder):
    files = [f for f in os.listdir(numbers_folder) if f.endswith(('.xls', '.xlsx', '.csv'))]
    # Sort files by date (format: YYYY-MM-DD_nnn)
    # Extract date portion before underscore for sorting
    available_files = sorted(files, key=lambda x: x.split('_')[0] if '_' in x else x)

use_file = st.checkbox("Load outcomes from file", value=False)
selected_file = None
if use_file:
    if available_files:
        selected_file = st.selectbox("Select file:", [""] + available_files,
                                   help="Choose an Excel (.xls/.xlsx) or CSV file from the numbers folder")
    else:
        st.warning("No Excel or CSV files found in the 'numbers' folder")
        use_file = False

# Starting sequence codes selection
sequence_code_options = {
    "Standard (3, 4, 2)": {'a': 3, 'b': 4, 'c': 2},
    "Alternative (8, 44, 10)": {'a': 8, 'b': 44, 'c': 10}
}

selected_sequence_option = st.selectbox("Starting Sequence Codes:",
                                       list(sequence_code_options.keys()),
                                       help="Choose the initial sequence codes (a, b, c) for the system")

stage2_divisor = st.selectbox("Stage 2 Starting Divisor",
                             options=[8, 16, 32],
                             index=0,
                             help="Initial divisor for Stage 2 betting calculations (halves when b > 89 rule applies)")

# Debug checkbox
debug_mode = st.checkbox("Enable Debug Output", value=False,
                        help="When enabled, outputs DataFrame and system messages to debug_output.txt")

# Add a run button
if st.button("Run Simulation"):
    st.title("Michael's Roulette Results")

    # Load outcomes from file or use default
    if use_file and selected_file and selected_file != "":
        try:
            file_path = os.path.join(numbers_folder, selected_file)
            if selected_file.endswith('.csv'):
                # Load CSV file with no header
                df = pd.read_csv(file_path, header=None)
            else:
                # Load Excel file (.xls or .xlsx) with no header
                df = pd.read_excel(file_path, header=None)

            # Since we're loading with no header, use the first column which contains all the data
            file_outcomes = df.iloc[:, 0].dropna().astype(int).tolist()
            outcomes = file_outcomes
            st.success(f"Loaded {len(outcomes)} outcomes from {selected_file} (first outcome: {outcomes[0]})")

        except Exception as e:
            st.error(f"Error loading file {selected_file}: {str(e)}")
            st.info("Using default outcomes instead")
            # Keep the original default outcomes
    else:
        st.info("Using default test outcomes")

    print("Starting Fresh Roulette System")
    print(f"A1 (16 Corner Bets): {A1}")
    print(f"A2 (30 Six-Line Bets): {A2}")
    print(f"Total Outcomes: {len(outcomes)}")
    print()

    # Initialize variables - must be declared before functions that use nonlocal
    initial_sequence_codes = sequence_code_options[selected_sequence_option].copy()
    sequence_code = initial_sequence_codes.copy()
    recording = False
    balance = 0
    current_bet_type = 1  # 1=Bet1, 2=Bet2, 3=Bet3

    # Session and sequence tracking
    session_active = True
    sequence_number = 0
    first_bet_placed = False  # Track if we've placed the first bet in current sequence

    # Stage tracking
    stage = 1  # 1=Stage1, 2=Stage2
    stage1_complete = False
    stage2_recovery_target = 0  # Will be set when Stage 1 ends

    # Stage 2 variables - save initial divisor for reset
    initial_stage2_divisor = stage2_divisor  # Save user's initial choice
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

    # Create DataFrame and collect debug messages - must be before functions
    results = []
    debug_messages = []
    balance_history = []  # Track balance at each spin

    # Bank limits
    starting_bank = 250  # units
    current_bank_units = starting_bank

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

    # Remove the nested functions and put logic inline in the main loop

    for i, outcome in enumerate(outcomes):
        if not session_active:
            break  # Stop processing if session ended
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
        if win_status == 'W' and not recording and session_active:
            recording = True
            sequence_number += 1
            debug_messages.append((line_num, f"Sequence {sequence_number} started! First A1 win - sequence codes will start next line"))
            results.append(row)
            balance_history.append(balance)  # Track balance
            continue

        # If recording and session is active, process betting and sequence codes
        if recording and session_active:
            # Check if we have pending sequence codes to apply (from four corner rule)
            if pending_sequence_codes and not four_corner_rule_active:
                sequence_code.update(pending_sequence_codes)
                debug_messages.append((line_num, f"Applying pending sequence codes: {pending_sequence_codes}"))
                pending_sequence_codes = None

            # Handle sequence code display with four corner rule
            if four_corner_rule_active:
                # Four corner rule active - don't show sequence codes on this line
                row['a'] = ''
                row['b'] = ''
                row['c'] = ''
                debug_messages.append((line_num, f"Four corner rule: suppressing sequence codes"))
            elif pending_sequence_codes:
                # Apply pending codes from four corner rule
                sequence_code.update(pending_sequence_codes)
                row['a'] = sequence_code['a']
                row['b'] = sequence_code['b']
                row['c'] = sequence_code['c']
                debug_messages.append((line_num, f"Applying delayed four corner codes: {pending_sequence_codes}"))
                pending_sequence_codes = None
            else:
                # Normal sequence code display
                row['a'] = sequence_code['a']
                row['b'] = sequence_code['b']
                row['c'] = sequence_code['c']

            # Place bet (stage-dependent logic)
            if stage == 1:
                # Stage 1 betting logic (inline)
                bet_result = {'bet_amount': 0, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': False}

                # Check A1 wait rule first
                if waiting_for_a1_losses:
                    if outcome in A1:
                        # A1 outcome resets the counter
                        non_a1_count = 0
                        bet_result = {'bet_amount': 0, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': False}
                    else:
                        # Non-A1 outcome increments counter
                        non_a1_count += 1
                        if non_a1_count >= 3:
                            waiting_for_a1_losses = False
                            non_a1_count = 0
                            debug_messages.append((line_num, f"A1 wait period ended after 3 non-A1 outcomes"))
                        bet_result = {'bet_amount': 0, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': False}
                else:
                    # Determine bet parameters based on current bet type
                    if current_bet_type == 1:
                        bet_amount = 5
                        bet_numbers = A2
                        win_profit = 1
                        bet_units = 0
                    elif current_bet_type == 2:
                        bet_amount = 4
                        bet_numbers = A1
                        win_profit = 5
                        bet_units = 1
                    elif current_bet_type == 3:
                        bet_amount = 8
                        bet_numbers = A1
                        win_profit = 10
                        bet_units = 2
                    else:
                        bet_result = {'bet_amount': 0, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': False}

                    if current_bet_type <= 3:
                        # Check if it's a win
                        is_win = outcome in bet_numbers

                        if is_win:
                            # Handle win logic
                            if current_bet_type == 1:
                                balance += win_profit
                                current_bet_type = 1
                                if outcome in A1:
                                    waiting_for_a1_losses = True
                                    non_a1_count = 0
                                    debug_messages.append((line_num, f"A1 win detected - starting wait for 3 consecutive non-A1 outcomes"))
                                bet_result = {'bet_amount': bet_amount, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': False}
                            else:
                                # Bet2 or Bet3 win on A1 - mixed number logic
                                cumulative_negative['integer'] += bet_units
                                bip_chips = bet_units
                                existing_decimal_chips = cumulative_negative['decimal']
                                cumulative_positive_chips = existing_decimal_chips + bip_chips
                                negative_chips = mixed_to_chips_from_dict(cumulative_negative)
                                total_recovery = negative_chips + cumulative_positive_chips
                                recovery_achieved = False
                                if total_recovery >= 0:
                                    balance += total_recovery
                                    recovery_achieved = True
                                current_bet_type = 1
                                if outcome in A1:
                                    waiting_for_a1_losses = True
                                    non_a1_count = 0
                                    debug_messages.append((line_num, f"A1 win detected - starting wait for 3 consecutive non-A1 outcomes"))
                                bet_result = {'bet_amount': bet_amount, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': True, 'recovery_achieved': recovery_achieved}
                        else:
                            # Handle loss with mixed numbers
                            loss_mixed_number = chips_to_mixed_number(-bet_amount)
                            cumulative_negative = add_mixed_numbers(cumulative_negative, loss_mixed_number)
                            current_bet_type += 1
                            if current_bet_type > 3:
                                debug_messages.append((line_num, f"Bet3 lost. Stage 1 ends, Stage 2 begins."))
                                stage1_complete = True
                                stage = 2
                                negative_chips = mixed_to_chips_from_dict(cumulative_negative)
                                stage2_recovery_target = negative_chips
                                cumulative_positive_chips = cumulative_negative['decimal']
                            bet_result = {'bet_amount': bet_amount, 'loss_mixed': loss_mixed_number, 'win_mixed': False}
            elif stage == 2:
                # In Stage 2, check if sequence codes are being displayed
                codes_displayed = not (four_corner_rule_active or (pending_sequence_codes and not four_corner_rule_active))
                if four_corner_rule_active:
                    codes_displayed = False
                elif row['a'] != '':  # If sequence codes are shown in this row
                    codes_displayed = True
                else:
                    codes_displayed = False
                # Stage 2 betting logic (inline)
                bet_result = {'bet_amount': 0, 'units': 0, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': False}

                if codes_displayed:
                    # Check if a > 10 (no betting if true), UNLESS negative > 20 units
                    negative_units = abs(cumulative_negative['integer'])
                    if not (sequence_code['a'] > 10 and negative_units <= 20):
                        # Calculate bet units: c / divisor
                        if stage2_divisor == 0:
                            stage2_divisor = 1
                            debug_messages.append((line_num, f"Warning: stage2_divisor was 0, reset to 1"))
                        normal_bet_units = int(sequence_code['c'] / stage2_divisor)
                        if normal_bet_units == 0:
                            normal_bet_units = 1  # Minimum bet

                        # Risk management: Calculate risk-managed bet to avoid over-betting
                        negative_integer = abs(cumulative_negative['integer'])
                        positive_integer = 0
                        if cumulative_positive_chips > 0:
                            positive_mixed = chips_to_mixed_number(cumulative_positive_chips)
                            positive_integer = positive_mixed['integer']

                        recovery_shortfall = negative_integer - positive_integer

                        # Check if sequence is close to ending (a <= 4)
                        # If so, calculate based on actual chip deficit to ensure full recovery
                        if sequence_code['a'] <= 4:
                            # Calculate actual deficit in chips
                            negative_chips = mixed_to_chips_from_dict(cumulative_negative)
                            current_deficit_chips = -(negative_chips + cumulative_positive_chips)
                            # Each unit recovers 5 chips (4 to negative + 1 BIP)
                            # Need to round up to ensure full recovery
                            import math
                            min_recovery_bet_units = math.ceil(current_deficit_chips / 5)
                            if min_recovery_bet_units == 0:
                                min_recovery_bet_units = 1  # Minimum bet
                            # When a <= 4, bet exactly the minimum needed for recovery
                            bet_units = min_recovery_bet_units
                            risk_managed_bet_units = min_recovery_bet_units  # For debug display
                        else:
                            risk_managed_bet_units = int(abs(recovery_shortfall) * 0.8)
                            if risk_managed_bet_units == 0:
                                risk_managed_bet_units = 1  # Minimum bet
                            # Normal betting: use the smaller of normal bet or risk-managed bet
                            bet_units = min(normal_bet_units, risk_managed_bet_units)

                        debug_messages.append((line_num, f"Stage 2 bet calculation: a={sequence_code['a']}, Normal={normal_bet_units}, Risk-managed={risk_managed_bet_units}, Using={bet_units} units"))
                        bet_chips = bet_units * 4  # Convert units to chips

                        # Check if it's a win (A1 numbers only in Stage 2)
                        is_win = outcome in A1

                        if is_win:
                            # Stage 2 win - apply mixed number recovery logic
                            cumulative_negative['integer'] += bet_units
                            bip_chips = bet_units  # 1 unit = 1 chip BIP
                            cumulative_positive_chips += bip_chips

                            # Check for complete recovery
                            negative_chips = mixed_to_chips_from_dict(cumulative_negative)
                            total_recovery = negative_chips + cumulative_positive_chips

                            if total_recovery >= 0:
                                # Full recovery achieved!
                                balance += total_recovery
                                debug_messages.append((line_num, f"Stage 2 recovery successful! Recovered 17 chips plus {total_recovery} profit."))
                                debug_messages.append((line_num, f"Sequence completed successfully."))
                                stage = 3  # Mark as completed

                            bet_result = {'bet_amount': bet_chips, 'units': bet_units, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': True}
                        else:
                            # Stage 2 loss
                            loss_mixed_number = chips_to_mixed_number(-bet_chips)
                            cumulative_negative = add_mixed_numbers(cumulative_negative, loss_mixed_number)

                            # Check if bank is lost (1000 chips = 250 units)
                            total_negative_chips = abs(mixed_to_chips_from_dict(cumulative_negative))
                            if total_negative_chips >= 1000:
                                debug_messages.append((line_num, f"Bank lost! Stage 2 recovery failed."))
                                stage = 4  # Mark as failed

                            bet_result = {'bet_amount': bet_chips, 'units': bet_units, 'loss_mixed': loss_mixed_number, 'win_mixed': False}
            else:
                # Stage completed, no more betting
                bet_result = {'bet_amount': 0, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': False}
                # Show STOP message on line after recovery
                if stage == 3:
                    row['actual bet'] = 'STOP'
                    debug_messages.append((line_num, f"Recovery in Stage 2 has now been successfully completed."))

            if bet_result['bet_amount'] > 0:
                # Mark that first bet has been placed
                if not first_bet_placed:
                    first_bet_placed = True
                # Display bet type - check if it's a Stage 2 bet first (has 'units' key)
                if 'units' in bet_result and bet_result['units'] > 0:
                    # Stage 2 bet display - show units
                    row['actual bet'] = f"{bet_result['units']} units"
                elif bet_result['bet_amount'] == 5:
                    row['actual bet'] = 'Bet 1'
                elif bet_result['bet_amount'] == 4:
                    row['actual bet'] = 'Bet 2'
                elif bet_result['bet_amount'] == 8:
                    row['actual bet'] = 'Bet 3'

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

                    # Reset mixed numbers after recovery
                    if stage == 3:
                        # Stage 2/3 recovery complete
                        cumulative_negative = {'integer': 0, 'decimal': 0}
                        cumulative_positive_chips = 0
                    elif stage == 1 and 'recovery_achieved' in bet_result and bet_result['recovery_achieved']:
                        # Stage 1 Bet2/Bet3 recovery complete
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
                    debug_messages.append((line_num, f"Four corner loss rule ended - A1 outcome detected"))
                    four_corner_rule_active = False
            else:
                consecutive_non_a1 += 1
                debug_messages.append((line_num, f"Consecutive non-A1 count: {consecutive_non_a1}"))

            # Update sequence codes for next line (ALWAYS update, even during A1 wait)
            is_a1_win = outcome in A1

            # Sequence code update logic (inline)
            if is_a1_win:
                # Win logic from mb_roulette_v1.txt
                sequence_code['a'] = calculate_new_a(sequence_code['a'])
                sequence_code['b'] = sequence_code['b'] - sequence_code['c']
                # Prevent division by zero
                if sequence_code['a'] == 0:
                    sequence_code['a'] = 1
                    debug_messages.append((line_num, f"Warning: sequence_code['a'] was 0, reset to 1"))
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
                        debug_messages.append((line_num, f"b > 89 rule applied in Stage 2 - divisor reduced to {stage2_divisor}"))

                # Prevent division by zero
                if sequence_code['a'] == 0:
                    sequence_code['a'] = 1
                    debug_messages.append((line_num, f"Warning: sequence_code['a'] was 0, reset to 1"))
                sequence_code['c'] = (int(sequence_code['b'] / sequence_code['a'])) * 2

            # Check for sequence completion (a < 3 after first bet OR stage 3 after Stage 2 recovery)
            if (first_bet_placed and sequence_code['a'] < 3) or stage == 3:
                debug_messages.append((line_num, f"Sequence {sequence_number} completed! (a={sequence_code['a']} < 3)"))
                # Reset for new sequence
                sequence_code = initial_sequence_codes.copy()
                recording = False  # Will restart on next A1 win
                current_bet_type = 1
                stage = 1
                stage1_complete = False
                stage2_divisor = initial_stage2_divisor  # Reset divisor to initial value
                waiting_for_a1_losses = False
                non_a1_count = 0
                four_corner_rule_active = False
                consecutive_non_a1 = 0
                pending_sequence_codes = None
                cumulative_negative = {'integer': 0, 'decimal': 0}
                cumulative_positive_chips = 0
                first_bet_placed = False
                # Check bank status
                current_bank_units = starting_bank + (balance // 4)  # Convert balance back to units
                if current_bank_units <= 0:
                    debug_messages.append((line_num, f"Bank depleted! Session ends."))
                    session_active = False

            # Check if we just hit 4 consecutive non-A1 (triggers four corner rule)
            if consecutive_non_a1 == 4:
                four_corner_rule_active = True
                pending_sequence_codes = sequence_code.copy()
                debug_messages.append((line_num, f"Four corner rule triggered! Calculated codes {pending_sequence_codes} will be delayed"))

        results.append(row)
        balance_history.append(balance)  # Track balance after each spin

    # Create and display DataFrame
    df = pd.DataFrame(results)
    st.dataframe(df)

    # Create balance progression graph
    st.subheader("Balance Progression")
    if balance_history:
        fig, ax = plt.subplots(figsize=(12, 6))
        spins = range(1, len(balance_history) + 1)
        ax.plot(spins, balance_history, linewidth=2, color='blue')
        ax.set_xlabel('Spin Number')
        ax.set_ylabel('Balance')
        ax.set_title('Balance vs Number of Spins')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='Break-even line')
        ax.legend()
        st.pyplot(fig)
    else:
        st.write("No balance data to display")

    # Display debug messages
    st.subheader("System Messages")
    if debug_messages:
        for line_num, message in debug_messages:
            st.write(f"Line {line_num}: {message}")
    else:
        st.write("No system messages generated")

    # Write debug output to file if enabled
    if debug_mode:
        try:
            with open('debug_output.txt', 'w') as f:
                f.write("="*80 + "\n")
                f.write("ROULETTE SYSTEM DEBUG OUTPUT\n")
                f.write("="*80 + "\n\n")

                # Write configuration
                f.write("CONFIGURATION:\n")
                f.write(f"- File: {selected_file if use_file and selected_file else 'Default outcomes'}\n")
                f.write(f"- Sequence Codes: {selected_sequence_option}\n")
                f.write(f"- Stage 2 Divisor: {stage2_divisor}\n")
                f.write(f"- Total Outcomes: {len(outcomes)}\n\n")

                # Write DataFrame
                f.write("="*80 + "\n")
                f.write("BETTING RESULTS:\n")
                f.write("="*80 + "\n\n")
                f.write(df.to_string(index=False))
                f.write("\n\n")

                # Write system messages
                f.write("="*80 + "\n")
                f.write("SYSTEM MESSAGES:\n")
                f.write("="*80 + "\n\n")
                for line_num, message in debug_messages:
                    f.write(f"Line {line_num}: {message}\n")
                f.write("\n")

                # Write final summary
                f.write("="*80 + "\n")
                f.write("FINAL SUMMARY:\n")
                f.write("="*80 + "\n\n")
                f.write(f"Total Sequences Completed: {sequence_number}\n")
                f.write(f"Final Balance: {balance} chips\n")
                final_bank_units = starting_bank + (balance // 4)
                f.write(f"Final Bank: {final_bank_units} units (started with {starting_bank} units)\n")
                f.write(f"Session Status: {'ENDED' if not session_active else 'ACTIVE'}\n")
                f.write(f"Outcomes Processed: {len(results)}/{len(outcomes)}\n")

            st.success("Debug output written to debug_output.txt")
        except Exception as e:
            st.error(f"Error writing debug output: {str(e)}")

    # Display final balance and session summary
    st.subheader("Final Results")
    st.write(f"**Session Summary:**")
    st.write(f"- Starting Sequence Codes: {selected_sequence_option}")
    st.write(f"- Total Sequences Completed: {sequence_number}")
    st.write(f"- Final Balance: {balance} chips")
    final_bank_units = starting_bank + (balance // 4)
    st.write(f"- Final Bank: {final_bank_units} units (started with {starting_bank} units)")
    if not session_active:
        st.write(f"- Session Status: **ENDED** (Bank depleted or sequence completion)")
    else:
        st.write(f"- Session Status: **ACTIVE** (All outcomes processed)")
    st.write(f"- Outcomes Processed: {len(results)}/{len(outcomes)}")

    print("\nBetting Results:")
    print(df.to_string(index=False))
    print(f"\nFinal Balance: {balance}")