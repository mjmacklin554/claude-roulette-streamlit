import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime

# From mb_roulette_v1.txt - Technical Requirements
outcomes = [0, 15, 27, 33, 26, 14, 36, 2, 16, 22, 7, 17, 30, 22, 28, 9, 10, 11, 6, 1, 33, 10, 15, 18, 11, 9, 1, 7, 30, 30, 36, 36,4,4,
32,28,6,10,22,24,33,36,15,34,9,0,0,1,18,19,20,8,17,11,27,16,26,4,29,2,2]

# A1 consisting of 16 numbers (4 x Corner Bets)
A1 = [2, 3, 5, 6, 17, 18, 20, 21, 25, 26, 28, 29, 31, 32, 34, 35]

# Helper function to get betting recommendation for live play
def get_betting_recommendation(sequence_code, stage, current_bet_type, cumulative_negative, waiting_for_a1_losses=False):
    """Returns the current betting recommendation based on system state"""
    if waiting_for_a1_losses:
        return "Wait (A1 wait period)"

    if stage == 1:
        # Stage 1 betting
        if current_bet_type == 1:
            return "Bet 1: 5 chips on A2 (Six-Line)"
        elif current_bet_type == 2:
            return "Bet 2: 4 chips on A1 (Corners)"
        elif current_bet_type == 3:
            return "Bet 3: 8 chips on A1 (Corners)"
        else:
            return "No bet (wait for A1)"
    elif stage == 2:
        # Stage 2 betting - check if we should bet
        a = sequence_code['a']
        negative_units = abs(cumulative_negative['integer'])

        # This will be filled in when we process
        return f"Stage 2: Check a={a}, negative={negative_units}"
    else:
        return "Session complete"

# A2 consisting of 30 numbers (5 x Six-Line Bets): 1-6, 13-18, 19-24, 25-30, 31-36
A2 = []
for start in [1, 13, 19, 25, 31]:
    A2.extend(range(start, start + 6))

# Session history functions
HISTORY_FOLDER = "session_history"

def ensure_history_folder():
    """Create history folder if it doesn't exist"""
    if not os.path.exists(HISTORY_FOLDER):
        os.makedirs(HISTORY_FOLDER)

def save_session(session_data):
    """Save session to JSON file"""
    ensure_history_folder()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"session_{timestamp}.json"
    filepath = os.path.join(HISTORY_FOLDER, filename)

    with open(filepath, 'w') as f:
        json.dump(session_data, f, indent=2)

    return filename

def load_all_sessions():
    """Load all session files and return as list"""
    ensure_history_folder()
    sessions = []

    if not os.path.exists(HISTORY_FOLDER):
        return sessions

    files = [f for f in os.listdir(HISTORY_FOLDER) if f.endswith('.json')]

    for filename in sorted(files, reverse=True):  # Most recent first
        filepath = os.path.join(HISTORY_FOLDER, filename)
        try:
            with open(filepath, 'r') as f:
                session = json.load(f)
                session['filename'] = filename
                sessions.append(session)
        except Exception as e:
            st.warning(f"Error loading {filename}: {str(e)}")

    return sessions

def delete_session(filename):
    """Delete a session file"""
    filepath = os.path.join(HISTORY_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

# Streamlit user inputs - Create tabs for main app, live play, and history
tab1, tab2, tab3, tab4 = st.tabs(["Run Simulation", "Live Play Mode", "View History", "Batch Processing"])

with tab1:
    st.title("Michael's Roulette System Configuration")

    # File input for outcomes
    numbers_folder = "numbers"
    available_files = []
    if os.path.exists(numbers_folder):
        files = [f for f in os.listdir(numbers_folder) if f.endswith(('.xls', '.xlsx', '.csv', '.txt'))]
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

    # Bypass rule checkbox
    bypass_a10_rule = st.checkbox("Enable 'Negative > 20' Bypass Rule", value=True,
                                  help="When enabled, allows betting even when a > 10 if negative exceeds 20 units. When disabled, ALWAYS enforces a ≤ 10 rule.")

    # Only bet when c > 7 checkbox
    only_bet_c_gt_7 = st.checkbox("Only bet when c > 7", value=False,
                                  help="When enabled, skips betting when sequence code 'c' is 7 or less (works like A1 wait rule).")

    # A1 Wait Rule checkbox
    enable_a1_wait_rule = st.checkbox("Enable A1 Wait Rule", value=False,
                                      help="When enabled, waits for 3 consecutive non-A1 outcomes after an A1 win before resuming betting.")

    # Always bet when a > 10 checkbox
    always_bet_a_gt_10 = st.checkbox("Always bet when a > 10", value=False,
                                     help="When enabled, ALWAYS bets when a > 10 regardless of negative units (overrides bypass rule).")

    # Enable divisor below 1 checkbox
    enable_divisor_below_1 = st.checkbox("Enable divisor below 1 (aggressive betting)", value=False,
                                        help="When enabled, allows divisor to continue halving below 1 (0.5, 0.25, etc.), resulting in multiplied bets (c*2, c*4, etc.).")

    # Max bet cap
    max_bet_cap = st.number_input("Max Bet Cap (Stage 2 units, 0 = no cap)",
                                  min_value=0,
                                  max_value=100,
                                  value=0,
                                  step=5,
                                  help="Sets an absolute maximum bet size in Stage 2. Set to 0 for no cap. Recommended: 25-30 units for safety.")

    # Debug checkbox
    debug_mode = st.checkbox("Enable Debug Output", value=False,
                            help="When enabled, outputs DataFrame and system messages to debug_output.txt")

    # Save session checkbox
    save_session_enabled = st.checkbox("Save session to history", value=True,
                                       help="When enabled, saves session results for later review")

    # Add a run button
    if st.button("Run Simulation"):
        st.title("Michael's Roulette Results")

        # Load outcomes from file or use default
        if use_file and selected_file and selected_file != "":
            try:
                file_path = os.path.join(numbers_folder, selected_file)
                if selected_file.endswith('.txt'):
                    # Load TXT file (one number per line)
                    with open(file_path, 'r') as f:
                        file_outcomes = [int(line.strip()) for line in f if line.strip().isdigit()]
                    outcomes = file_outcomes
                elif selected_file.endswith('.csv'):
                    # Load CSV file with no header
                    df = pd.read_csv(file_path, header=None)
                    file_outcomes = df.iloc[:, 0].dropna().astype(int).tolist()
                    outcomes = file_outcomes
                else:
                    # Load Excel file (.xls or .xlsx) with no header
                    df = pd.read_excel(file_path, header=None)
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
        stage = 1  # 1=Stage1, 2=Stage2, 3=Stage2 recovered
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

        # Turnover tracking
        total_turnover = 0  # Track total dollar value of all bets made

        # Track worst drawdown point
        worst_drawdown_state = {
            'line': 0,
            'bet': '',
            'negative': 0,
            'positive': '0',
            'positive_chips': 0,
            'chip_loss': 0,
            'balance': 0,
            'total_loss': 0
        }

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

                    # Check A1 wait rule first (only if enabled)
                    if enable_a1_wait_rule and waiting_for_a1_losses:
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
                    elif only_bet_c_gt_7 and sequence_code['c'] <= 7:
                        # c <= 7 rule: skip betting (like A1 wait rule)
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
                                    if outcome in A1 and enable_a1_wait_rule:
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
                                    if outcome in A1 and enable_a1_wait_rule:
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
                        # Check if a > 10 (no betting if true)
                        # If bypass_a10_rule is enabled, allow betting when negative > 20 units
                        negative_units = abs(cumulative_negative['integer'])
                        should_bet = False

                        # Always bet when a > 10 overrides everything
                        if always_bet_a_gt_10 and sequence_code['a'] > 10:
                            should_bet = True
                            debug_messages.append((line_num, f"Always bet a>10 rule: a={sequence_code['a']} > 10, forcing bet"))
                        elif bypass_a10_rule:
                            # Original rule: bet if (a ≤ 10) OR (negative > 20)
                            should_bet = not (sequence_code['a'] > 10 and negative_units <= 20)
                            if sequence_code['a'] > 10 and negative_units > 20:
                                debug_messages.append((line_num, f"Bypass rule activated: a={sequence_code['a']} > 10 but negative={negative_units} > 20, continuing to bet"))
                        else:
                            # Strict rule: bet ONLY if a ≤ 10
                            should_bet = sequence_code['a'] <= 10
                            if sequence_code['a'] > 10:
                                debug_messages.append((line_num, f"Bypass rule disabled: a={sequence_code['a']} > 10, skipping bet"))

                        # Check c <= 7 rule (like A1 wait rule)
                        if should_bet and only_bet_c_gt_7 and sequence_code['c'] <= 7:
                            should_bet = False

                        if should_bet:
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
                                # When a > 4, no risk management - just use normal bet
                                bet_units = normal_bet_units
                                risk_managed_bet_units = normal_bet_units  # For debug display

                            # Apply max bet cap if set
                            if max_bet_cap > 0 and bet_units > max_bet_cap:
                                debug_messages.append((line_num, f"Max bet cap applied: reducing bet from {bet_units} to {max_bet_cap} units"))
                                bet_units = max_bet_cap

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
                                    stage = 3  # Mark as completed (recovered from Stage 2)

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
                    # Accumulate turnover (total dollar value of bets)
                    total_turnover += bet_result['bet_amount']

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
                        if stage == 2 and recording and not four_corner_rule_active:
                            # Check if divisor can be reduced
                            if enable_divisor_below_1:
                                # Allow divisor to go below 1 (using float division)
                                stage2_divisor = stage2_divisor / 2
                                debug_messages.append((line_num, f"b > 89 rule applied in Stage 2 - divisor reduced to {stage2_divisor}"))
                            elif stage2_divisor > 1:
                                # Normal mode: stop at 1
                                stage2_divisor = stage2_divisor // 2
                                debug_messages.append((line_num, f"b > 89 rule applied in Stage 2 - divisor reduced to {stage2_divisor}"))

                    # Prevent division by zero
                    if sequence_code['a'] == 0:
                        sequence_code['a'] = 1
                        debug_messages.append((line_num, f"Warning: sequence_code['a'] was 0, reset to 1"))
                    sequence_code['c'] = (int(sequence_code['b'] / sequence_code['a'])) * 2

                # Check for sequence completion (a < 3 while recording OR stage 3 after Stage 2 recovery)
                # Note: Uses 'recording' instead of 'first_bet_placed' so c <= 7 rule doesn't prevent sequence ending
                if (recording and sequence_code['a'] < 3) or stage == 3:
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

            # Track worst drawdown state after bet is placed
            if row['actual bet'] != '' and row['actual bet'] != 'STOP':
                # Calculate current chip loss from mixed numbers
                current_negative_chips = cumulative_negative['integer'] * 4
                current_positive_chips = cumulative_positive_chips
                current_chip_loss = current_negative_chips + current_positive_chips
                current_total_loss = current_chip_loss + balance

                # Update worst drawdown if this is worse
                if current_total_loss < worst_drawdown_state['total_loss']:
                    # Get positive display value (always show actual value even if not displayed in table)
                    positive_display = '0'
                    if cumulative_positive_chips > 0:
                        positive_mixed = chips_to_mixed_number(cumulative_positive_chips)
                        if positive_mixed['integer'] > 0:
                            if positive_mixed['decimal'] > 0:
                                positive_display = f"{positive_mixed['integer']}.{positive_mixed['decimal']}"
                            else:
                                positive_display = f"{positive_mixed['integer']}.0"
                        else:
                            positive_display = f".{positive_mixed['decimal']}"

                    worst_drawdown_state = {
                        'line': line_num,
                        'bet': row['actual bet'],
                        'negative': cumulative_negative['integer'],
                        'positive': positive_display,
                        'positive_chips': current_positive_chips,
                        'chip_loss': current_chip_loss,
                        'balance': balance,
                        'total_loss': current_total_loss
                    }

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
                    f.write(f"- Stage 2 Divisor: {initial_stage2_divisor}\n")
                    f.write(f"- Bypass a>10 Rule (negative>20): {'Enabled' if bypass_a10_rule else 'Disabled'}\n")
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

        # Save session to history if enabled
        if save_session_enabled:
            try:
                # Determine if session ended successfully (not stuck in Stage 2)
                # Success = we're not in Stage 2 when outcomes run out
                session_successful = stage != 2  # True if we're in Stage 1 or Stage 3, False if stuck in Stage 2

                # Prepare session data
                session_data = {
                    'timestamp': datetime.now().isoformat(),
                    'configuration': {
                        'file': selected_file if use_file and selected_file else 'Default outcomes',
                        'sequence_codes': selected_sequence_option,
                        'stage2_divisor': initial_stage2_divisor,
                        'bypass_a10_rule': bypass_a10_rule,
                        'total_outcomes': len(outcomes)
                    },
                    'results': {
                        'sequences_completed': sequence_number,
                        'final_balance_chips': balance,
                        'starting_bank_units': starting_bank,
                        'final_bank_units': final_bank_units,
                        'session_status': 'ENDED' if not session_active else 'ACTIVE',
                        'outcomes_processed': len(results),
                        'profit_loss_chips': balance,
                        'profit_loss_units': (final_bank_units - starting_bank),
                        'worst_drawdown': worst_drawdown_state,
                        'session_successful': session_successful,
                        'final_stage': stage,  # Track what stage we ended in
                        'total_turnover': total_turnover  # Total dollar value of all bets made
                    },
                    'dataframe': df.to_dict(orient='records'),
                    'balance_history': balance_history,
                    'debug_messages': [[line_num, msg] for line_num, msg in debug_messages]
                }

                saved_filename = save_session(session_data)
                st.success(f"Session saved to history: {saved_filename}")
            except Exception as e:
                st.error(f"Error saving session: {str(e)}")

# Helper function to process an outcome in live mode (used by both manual and wheel modes)
def process_outcome_live(outcome, st, A1, A2, live_bypass_a10, sequence_code_options, live_sequence_option):
    """Process a roulette outcome through the full betting system in live mode"""
    import math

    # Add number to outcomes
    st.session_state.live_outcomes.append(outcome)

    # Process the outcome with FULL betting system logic
    win_status = 'W' if outcome in A1 else 'L'
    line_num = len(st.session_state.live_outcomes)

    # Check for first A1 win to start recording
    if win_status == 'W' and not st.session_state.live_recording:
        st.session_state.live_recording = True
        st.session_state.live_sequence_number += 1
        st.session_state.live_debug_messages.append((line_num, f"Sequence {st.session_state.live_sequence_number} started! First A1 win"))
        st.session_state.live_current_bet = "Bet 1: 5 chips on A2 (Six-Line)"
        st.success(f"✓ Number {outcome} - First A1 win! Betting starts next spin.")
        st.rerun()

    # If recording, process full betting logic
    if st.session_state.live_recording:
        # Get shorthand references to session state
        seq_code = st.session_state.live_sequence_codes
        stage = st.session_state.live_stage
        bet_type = st.session_state.live_current_bet_type
        balance = st.session_state.live_balance
        cum_neg = st.session_state.live_cumulative_negative
        cum_pos = st.session_state.live_cumulative_positive_chips

        # Helper functions (same as Tab 1)
        def calculate_new_a_live(a):
            if a > 13:
                return 10
            elif 10 < a < 14:
                return a - 4
            elif 7 < a < 11:
                return a - 3
            elif a < 8:
                return a - 2
            return a

        def chips_to_mixed_number_live(chips):
            if chips == 0:
                return {'integer': 0, 'decimal': 0}
            abs_chips = abs(chips)
            units_of_4 = abs_chips // 4
            remainder = abs_chips % 4
            if chips < 0:
                if remainder == 0:
                    return {'integer': -units_of_4, 'decimal': 0}
                else:
                    return {'integer': -(units_of_4 + 1), 'decimal': 4 - remainder}
            else:
                return {'integer': units_of_4, 'decimal': remainder}

        def add_mixed_numbers_live(mixed1, mixed2):
            if mixed1['integer'] == 0 and mixed1['decimal'] == 0:
                return mixed2
            if mixed2['integer'] == 0 and mixed2['decimal'] == 0:
                return mixed1
            return {'integer': mixed1['integer'] + mixed2['integer'], 'decimal': mixed1['decimal']}

        def mixed_to_chips_from_dict_live(mixed_dict):
            if mixed_dict['integer'] < 0:
                return mixed_dict['integer'] * 4
            else:
                return (mixed_dict['integer'] * 4) + mixed_dict['decimal']

        # Apply pending sequence codes if any
        if st.session_state.live_pending_sequence_codes and not st.session_state.live_four_corner_rule_active:
            seq_code.update(st.session_state.live_pending_sequence_codes)
            st.session_state.live_debug_messages.append((line_num, f"Applying pending sequence codes"))
            st.session_state.live_pending_sequence_codes = None

        # Place bet based on current stage
        bet_result = {'bet_amount': 0, 'loss_mixed': {'integer': 0, 'decimal': 0}, 'win_mixed': False}

        if stage == 1:
            # Stage 1 betting logic
            if st.session_state.live_waiting_for_a1_losses:
                if outcome in A1:
                    st.session_state.live_non_a1_count = 0
                else:
                    st.session_state.live_non_a1_count += 1
                    if st.session_state.live_non_a1_count >= 3:
                        st.session_state.live_waiting_for_a1_losses = False
                        st.session_state.live_non_a1_count = 0
                        st.session_state.live_debug_messages.append((line_num, "A1 wait period ended"))
            else:
                # Determine bet parameters
                if bet_type == 1:
                    bet_amount = 5
                    bet_numbers = A2
                    win_profit = 1
                    bet_units = 0
                elif bet_type == 2:
                    bet_amount = 4
                    bet_numbers = A1
                    win_profit = 5
                    bet_units = 1
                elif bet_type == 3:
                    bet_amount = 8
                    bet_numbers = A1
                    win_profit = 10
                    bet_units = 2
                else:
                    bet_amount = 0
                    bet_numbers = []

                if bet_type <= 3 and bet_amount > 0:
                    is_win = outcome in bet_numbers

                    if is_win:
                        # Handle win
                        if bet_type == 1:
                            balance += win_profit
                            st.session_state.live_current_bet_type = 1
                            if outcome in A1:
                                st.session_state.live_waiting_for_a1_losses = True
                                st.session_state.live_non_a1_count = 0
                        else:
                            # Bet2/Bet3 win - mixed number logic
                            cum_neg['integer'] += bet_units
                            bip_chips = bet_units
                            existing_decimal_chips = cum_neg['decimal']
                            cum_pos = existing_decimal_chips + bip_chips
                            negative_chips = mixed_to_chips_from_dict_live(cum_neg)
                            total_recovery = negative_chips + cum_pos
                            recovery_achieved = False
                            if total_recovery >= 0:
                                balance += total_recovery
                                recovery_achieved = True
                                cum_neg = {'integer': 0, 'decimal': 0}
                                cum_pos = 0
                            st.session_state.live_current_bet_type = 1
                            if outcome in A1:
                                st.session_state.live_waiting_for_a1_losses = True
                                st.session_state.live_non_a1_count = 0
                            bet_result['recovery_achieved'] = recovery_achieved
                            st.session_state.live_cumulative_negative = cum_neg
                            st.session_state.live_cumulative_positive_chips = cum_pos
                        bet_result = {'bet_amount': bet_amount, 'win_mixed': (bet_type > 1)}
                        st.session_state.live_balance = balance
                    else:
                        # Handle loss
                        loss_mixed_number = chips_to_mixed_number_live(-bet_amount)
                        cum_neg = add_mixed_numbers_live(cum_neg, loss_mixed_number)
                        st.session_state.live_cumulative_negative = cum_neg
                        st.session_state.live_current_bet_type += 1
                        if st.session_state.live_current_bet_type > 3:
                            st.session_state.live_debug_messages.append((line_num, "Bet3 lost. Stage 2 begins."))
                            st.session_state.live_stage = 2
                            stage = 2
                            st.session_state.live_cumulative_positive_chips = cum_neg['decimal']
                        bet_result = {'bet_amount': bet_amount, 'loss_mixed': loss_mixed_number}

                    if not st.session_state.live_first_bet_placed:
                        st.session_state.live_first_bet_placed = True

        elif stage == 2:
            # Stage 2 betting logic
            codes_displayed = not st.session_state.live_four_corner_rule_active

            if codes_displayed:
                negative_units = abs(cum_neg['integer'])
                should_bet = False

                if live_bypass_a10:
                    should_bet = not (seq_code['a'] > 10 and negative_units <= 20)
                    if seq_code['a'] > 10 and negative_units > 20:
                        st.session_state.live_debug_messages.append((line_num, f"Bypass rule activated"))
                else:
                    should_bet = seq_code['a'] <= 10

                if should_bet:
                    normal_bet_units = int(seq_code['c'] / st.session_state.live_stage2_divisor)
                    if normal_bet_units == 0:
                        normal_bet_units = 1

                    # Risk management
                    negative_integer = abs(cum_neg['integer'])
                    positive_integer = 0
                    if cum_pos > 0:
                        positive_mixed = chips_to_mixed_number_live(cum_pos)
                        positive_integer = positive_mixed['integer']

                    recovery_shortfall = negative_integer - positive_integer

                    if seq_code['a'] <= 4:
                        negative_chips = mixed_to_chips_from_dict_live(cum_neg)
                        current_deficit_chips = -(negative_chips + cum_pos)
                        min_recovery_bet_units = math.ceil(current_deficit_chips / 5)
                        if min_recovery_bet_units == 0:
                            min_recovery_bet_units = 1
                        bet_units = min_recovery_bet_units
                    else:
                        risk_managed_bet_units = int(abs(recovery_shortfall) * 0.8)
                        if risk_managed_bet_units == 0:
                            risk_managed_bet_units = 1
                        bet_units = min(normal_bet_units, risk_managed_bet_units)

                    bet_chips = bet_units * 4
                    is_win = outcome in A1

                    if is_win:
                        cum_neg['integer'] += bet_units
                        bip_chips = bet_units
                        cum_pos += bip_chips
                        negative_chips = mixed_to_chips_from_dict_live(cum_neg)
                        total_recovery = negative_chips + cum_pos

                        if total_recovery >= 0:
                            balance += total_recovery
                            st.session_state.live_debug_messages.append((line_num, "Stage 2 recovery successful!"))
                            st.session_state.live_stage = 3
                            stage = 3

                        st.session_state.live_balance = balance
                        st.session_state.live_cumulative_negative = cum_neg
                        st.session_state.live_cumulative_positive_chips = cum_pos
                        bet_result = {'bet_amount': bet_chips, 'units': bet_units, 'win_mixed': True}
                    else:
                        loss_mixed_number = chips_to_mixed_number_live(-bet_chips)
                        cum_neg = add_mixed_numbers_live(cum_neg, loss_mixed_number)
                        st.session_state.live_cumulative_negative = cum_neg
                        bet_result = {'bet_amount': bet_chips, 'units': bet_units, 'loss_mixed': loss_mixed_number}

        # Track consecutive non-A1 for four corner rule
        if outcome in A1:
            st.session_state.live_consecutive_non_a1 = 0
            if st.session_state.live_four_corner_rule_active:
                st.session_state.live_four_corner_rule_active = False
        else:
            st.session_state.live_consecutive_non_a1 += 1

        # Update sequence codes
        is_a1_win = outcome in A1
        if is_a1_win:
            seq_code['a'] = calculate_new_a_live(seq_code['a'])
            seq_code['b'] = seq_code['b'] - seq_code['c']
            if seq_code['a'] == 0:
                seq_code['a'] = 1
            seq_code['c'] = (int(seq_code['b'] / seq_code['a'])) * 2
        else:
            seq_code['a'] = seq_code['a'] + 1
            seq_code['b'] = seq_code['b'] + seq_code['c']
            if seq_code['b'] > 89:
                seq_code['b'] = int((seq_code['b'] + 1) / 2)
                if stage == 2 and st.session_state.live_stage2_divisor > 1:
                    st.session_state.live_stage2_divisor = st.session_state.live_stage2_divisor // 2
            if seq_code['a'] == 0:
                seq_code['a'] = 1
            seq_code['c'] = (int(seq_code['b'] / seq_code['a'])) * 2

        # Check for sequence completion
        if (st.session_state.live_first_bet_placed and seq_code['a'] < 3) or stage == 3:
            st.session_state.live_debug_messages.append((line_num, f"Sequence {st.session_state.live_sequence_number} completed!"))
            # Reset for new sequence
            st.session_state.live_sequence_codes = sequence_code_options[live_sequence_option].copy()
            st.session_state.live_recording = False
            st.session_state.live_current_bet_type = 1
            st.session_state.live_stage = 1
            st.session_state.live_stage2_divisor = st.session_state.live_initial_stage2_divisor
            st.session_state.live_waiting_for_a1_losses = False
            st.session_state.live_non_a1_count = 0
            st.session_state.live_four_corner_rule_active = False
            st.session_state.live_consecutive_non_a1 = 0
            st.session_state.live_pending_sequence_codes = None
            st.session_state.live_cumulative_negative = {'integer': 0, 'decimal': 0}
            st.session_state.live_cumulative_positive_chips = 0
            st.session_state.live_first_bet_placed = False

        # Check for four corner rule trigger
        if st.session_state.live_consecutive_non_a1 == 4:
            st.session_state.live_four_corner_rule_active = True
            st.session_state.live_pending_sequence_codes = seq_code.copy()

        # Update next bet recommendation
        if not st.session_state.live_recording:
            st.session_state.live_current_bet = "Wait for first A1 win"
        elif st.session_state.live_waiting_for_a1_losses:
            st.session_state.live_current_bet = "Wait (A1 wait period)"
        elif st.session_state.live_stage == 1:
            bet_type = st.session_state.live_current_bet_type
            if bet_type == 1:
                st.session_state.live_current_bet = "Bet 1: 5 chips on A2 (Six-Line)"
            elif bet_type == 2:
                st.session_state.live_current_bet = "Bet 2: 4 chips on A1 (Corners)"
            elif bet_type == 3:
                st.session_state.live_current_bet = "Bet 3: 8 chips on A1 (Corners)"
        elif st.session_state.live_stage == 2:
            if st.session_state.live_four_corner_rule_active:
                st.session_state.live_current_bet = "Wait (Four corner rule - wait for A1)"
            else:
                # Calculate next bet units
                a_val = st.session_state.live_sequence_codes['a']
                c_val = st.session_state.live_sequence_codes['c']
                div_val = st.session_state.live_stage2_divisor
                units = max(1, int(c_val / div_val))
                st.session_state.live_current_bet = f"Stage 2: {units} units on A1 (Corners)"
        elif st.session_state.live_stage == 3:
            st.session_state.live_current_bet = "Sequence completed - wait for next A1"

        st.success(f"✓ Number {outcome} processed - {'WIN' if outcome in A1 else 'LOSS'}")

    st.rerun()

# Live Play Mode Tab
with tab2:
    st.title("Live Play Mode")
    st.write("Enter roulette numbers one at a time as they come up at the wheel.")

    # Initialize live session state with full betting system variables
    if 'live_session_active' not in st.session_state:
        st.session_state.live_session_active = False
    if 'live_outcomes' not in st.session_state:
        st.session_state.live_outcomes = []
    if 'live_current_bet' not in st.session_state:
        st.session_state.live_current_bet = "Wait for first A1 win to start betting"
    if 'live_balance' not in st.session_state:
        st.session_state.live_balance = 0
    if 'live_sequence_codes' not in st.session_state:
        st.session_state.live_sequence_codes = None
    if 'live_stage' not in st.session_state:
        st.session_state.live_stage = 1
    if 'live_recording' not in st.session_state:
        st.session_state.live_recording = False

    # Additional state variables for full betting system
    if 'live_current_bet_type' not in st.session_state:
        st.session_state.live_current_bet_type = 1
    if 'live_cumulative_negative' not in st.session_state:
        st.session_state.live_cumulative_negative = {'integer': 0, 'decimal': 0}
    if 'live_cumulative_positive_chips' not in st.session_state:
        st.session_state.live_cumulative_positive_chips = 0
    if 'live_waiting_for_a1_losses' not in st.session_state:
        st.session_state.live_waiting_for_a1_losses = False
    if 'live_non_a1_count' not in st.session_state:
        st.session_state.live_non_a1_count = 0
    if 'live_four_corner_rule_active' not in st.session_state:
        st.session_state.live_four_corner_rule_active = False
    if 'live_consecutive_non_a1' not in st.session_state:
        st.session_state.live_consecutive_non_a1 = 0
    if 'live_pending_sequence_codes' not in st.session_state:
        st.session_state.live_pending_sequence_codes = None
    if 'live_stage2_divisor' not in st.session_state:
        st.session_state.live_stage2_divisor = 8
    if 'live_initial_stage2_divisor' not in st.session_state:
        st.session_state.live_initial_stage2_divisor = 8
    if 'live_sequence_number' not in st.session_state:
        st.session_state.live_sequence_number = 0
    if 'live_first_bet_placed' not in st.session_state:
        st.session_state.live_first_bet_placed = False
    if 'live_results' not in st.session_state:
        st.session_state.live_results = []
    if 'live_debug_messages' not in st.session_state:
        st.session_state.live_debug_messages = []
    if 'live_input_mode' not in st.session_state:
        st.session_state.live_input_mode = "Manual Entry"
    if 'live_wheel_result' not in st.session_state:
        st.session_state.live_wheel_result = None

    # Configuration section
    st.subheader("Configuration")
    col1, col2 = st.columns(2)
    with col1:
        live_sequence_option = st.selectbox("Starting Sequence Codes:",
                                           list(sequence_code_options.keys()),
                                           help="Choose the initial sequence codes (a, b, c) for the system",
                                           key="live_sequence")
        live_stage2_divisor = st.selectbox("Stage 2 Starting Divisor",
                                         options=[8, 16, 32],
                                         index=0,
                                         help="Initial divisor for Stage 2 betting calculations",
                                         key="live_divisor")
    with col2:
        live_bypass_a10 = st.checkbox("Enable 'Negative > 20' Bypass Rule", value=True,
                                      help="When enabled, allows betting even when a > 10 if negative exceeds 20 units.",
                                      key="live_bypass")

    st.divider()

    # Input mode selection
    st.subheader("Number Input Mode")
    input_mode = st.radio(
        "Choose input method:",
        ["Manual Entry", "Spinning Wheel"],
        horizontal=True,
        key="input_mode_selector"
    )
    st.session_state.live_input_mode = input_mode

    st.divider()

    # Session controls
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        if not st.session_state.live_session_active:
            if st.button("Start New Session", type="primary"):
                # Initialize all session variables
                st.session_state.live_session_active = True
                st.session_state.live_outcomes = []
                st.session_state.live_current_bet = "Wait for first A1 win to start betting"
                st.session_state.live_balance = 0
                st.session_state.live_sequence_codes = sequence_code_options[live_sequence_option].copy()
                st.session_state.live_stage = 1
                st.session_state.live_recording = False
                st.session_state.live_current_bet_type = 1
                st.session_state.live_cumulative_negative = {'integer': 0, 'decimal': 0}
                st.session_state.live_cumulative_positive_chips = 0
                st.session_state.live_waiting_for_a1_losses = False
                st.session_state.live_non_a1_count = 0
                st.session_state.live_four_corner_rule_active = False
                st.session_state.live_consecutive_non_a1 = 0
                st.session_state.live_pending_sequence_codes = None
                st.session_state.live_stage2_divisor = live_stage2_divisor
                st.session_state.live_initial_stage2_divisor = live_stage2_divisor
                st.session_state.live_sequence_number = 0
                st.session_state.live_first_bet_placed = False
                st.session_state.live_results = []
                st.session_state.live_debug_messages = []
                st.success("Session started! Enter your first number below.")
                st.rerun()
        else:
            if st.button("Stop Session", type="secondary"):
                st.session_state.live_session_active = False
                st.info("Session stopped. You can save the numbers or start a new session.")
                st.rerun()

    with col2:
        if st.session_state.live_session_active and len(st.session_state.live_outcomes) > 0:
            if st.button("Save Numbers to File"):
                # Save to numbers folder
                ensure_history_folder()
                numbers_folder = "numbers"
                if not os.path.exists(numbers_folder):
                    os.makedirs(numbers_folder)

                timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                filename = f"live_play_{timestamp}.txt"
                filepath = os.path.join(numbers_folder, filename)

                with open(filepath, 'w') as f:
                    for num in st.session_state.live_outcomes:
                        f.write(f"{num}\n")

                st.success(f"Saved {len(st.session_state.live_outcomes)} numbers to {filename}")

    with col3:
        if len(st.session_state.live_outcomes) > 0:
            if st.button("Clear All Numbers"):
                st.session_state.live_outcomes = []
                st.session_state.live_results = []
                st.info("All numbers cleared.")
                st.rerun()

    st.divider()

    # Number input section - different based on mode
    if st.session_state.live_session_active:
        if st.session_state.live_input_mode == "Manual Entry":
            # Manual entry mode
            st.subheader("Enter Number")

            col1, col2 = st.columns([1, 3])
            with col1:
                number_input = st.number_input("Roulette Number (0-36):",
                                              min_value=0,
                                              max_value=36,
                                              value=0,
                                              step=1,
                                              key="live_number_input")
            with col2:
                st.write("")  # Spacing
                st.write("")  # Spacing
                process_manual = st.button("Process Number", type="primary")

            if process_manual:
                # Process the number using the shared function
                process_outcome_live(number_input, st, A1, A2, live_bypass_a10, sequence_code_options, live_sequence_option)
        else:
            # Spinning Wheel mode
            st.subheader("🎰 Interactive Spinning Wheel")

            # Display the wheel using components
            import streamlit.components.v1 as components

            st.info("👇 Click 'SPIN WHEEL' to generate a random number, then enter the result in the field below")

            # Load the interactive HTML
            with open('roulette_wheel_interactive.html', 'r') as f:
                wheel_html = f.read()

            # Display the interactive wheel
            components.html(wheel_html, height=800, scrolling=False)

            st.write("---")

            # Manual entry after seeing wheel result
            st.subheader("Enter the Wheel Result")
            col1, col2 = st.columns([1, 3])
            with col1:
                wheel_number_input = st.number_input("Number from wheel:",
                                                      min_value=0,
                                                      max_value=36,
                                                      value=0,
                                                      step=1,
                                                      key="wheel_number_input")
            with col2:
                st.write("")
                st.write("")
                if st.button("Process Wheel Result", type="primary", key="process_wheel_number"):
                    process_outcome_live(wheel_number_input, st, A1, A2, live_bypass_a10, sequence_code_options, live_sequence_option)

    # Display current betting recommendation (always show if session active)
    if st.session_state.live_session_active:
        st.divider()
        st.subheader("Next Bet")

        # Show what to bet on the NEXT spin
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info(f"**{st.session_state.live_current_bet}**")
        with col2:
            st.metric("Balance", f"{st.session_state.live_balance} chips")

        # Show detailed system state if recording
        if st.session_state.live_recording and st.session_state.live_sequence_codes:
            st.divider()
            st.subheader("Current System State")

            # Display in columns for better layout
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write("**Sequence Codes:**")
                codes = st.session_state.live_sequence_codes
                if not st.session_state.live_four_corner_rule_active:
                    st.write(f"- a = {codes['a']}")
                    st.write(f"- b = {codes['b']}")
                    st.write(f"- c = {codes['c']}")
                else:
                    st.write("- (Hidden - Four Corner Rule)")
                st.write(f"**Stage:** {st.session_state.live_stage}")
                if st.session_state.live_stage == 2:
                    st.write(f"**Divisor:** {st.session_state.live_stage2_divisor}")

            with col2:
                st.write("**Mixed Numbers:**")
                neg = st.session_state.live_cumulative_negative
                st.write(f"- Negative: {neg['integer']}.{neg['decimal']}")

                pos_chips = st.session_state.live_cumulative_positive_chips
                if pos_chips > 0:
                    # Convert to mixed number for display
                    pos_units = pos_chips // 4
                    pos_dec = pos_chips % 4
                    if pos_units > 0:
                        st.write(f"- Positive: {pos_units}.{pos_dec} ({pos_chips} chips)")
                    else:
                        st.write(f"- Positive: .{pos_dec} ({pos_chips} chips)")
                else:
                    st.write(f"- Positive: 0")

                # Show total deficit/surplus
                neg_chips = neg['integer'] * 4
                total = neg_chips + pos_chips
                st.write(f"- Net: {total} chips")

            with col3:
                st.write("**Status Flags:**")
                st.write(f"- Sequence #{st.session_state.live_sequence_number}")
                if st.session_state.live_waiting_for_a1_losses:
                    st.write(f"- A1 Wait: Active ({st.session_state.live_non_a1_count}/3)")
                if st.session_state.live_four_corner_rule_active:
                    st.write(f"- Four Corner: Active")
                if st.session_state.live_consecutive_non_a1 > 0 and not st.session_state.live_four_corner_rule_active:
                    st.write(f"- Non-A1 Count: {st.session_state.live_consecutive_non_a1}/4")

        # Show debug messages if any
        if st.session_state.live_debug_messages and len(st.session_state.live_debug_messages) > 0:
            with st.expander("System Messages"):
                for line_num, message in st.session_state.live_debug_messages[-10:]:  # Show last 10 messages
                    st.write(f"Line {line_num}: {message}")

    # Display current session history
    if len(st.session_state.live_outcomes) > 0:
        st.divider()
        st.subheader("Session History")

        # Display outcomes
        st.write(f"**Numbers entered ({len(st.session_state.live_outcomes)}):**")
        # Display in rows of 20
        outcomes_display = []
        for i, num in enumerate(st.session_state.live_outcomes):
            marker = "✓" if num in A1 else "✗"
            outcomes_display.append(f"{num}{marker}")

        outcomes_str = " | ".join(outcomes_display)
        st.code(outcomes_str)
        st.caption("✓ = A1 win, ✗ = Loss")

    else:
        if not st.session_state.live_session_active:
            st.info("Start a new session and enter numbers to begin.")

# View History Tab
with tab3:
    st.title("Session History")

    # Load all sessions
    all_sessions = load_all_sessions()

    if not all_sessions:
        st.info("No session history found. Run a simulation with 'Save session to history' enabled to create history.")
    else:
        st.write(f"**Total Sessions: {len(all_sessions)}**")

        # Calculate overall statistics
        total_profit_chips = sum(s['results']['profit_loss_chips'] for s in all_sessions)
        total_profit_units = sum(s['results']['profit_loss_units'] for s in all_sessions)
        total_turnover = sum(s['results'].get('total_turnover', 0) for s in all_sessions)
        profitable_sessions = len([s for s in all_sessions if s['results']['profit_loss_chips'] > 0])
        win_rate = (profitable_sessions / len(all_sessions)) * 100 if all_sessions else 0

        # Calculate worst losses
        worst_losses = []
        for s in all_sessions:
            worst_dd = s['results'].get('worst_drawdown', {})
            if 'total_loss' in worst_dd:
                worst_losses.append(worst_dd['total_loss'])
            else:
                # Old format fallback
                old_dd = s['results'].get('max_drawdown_chips', 0)
                worst_losses.append(-old_dd)

        avg_worst_loss = sum(worst_losses) / len(worst_losses) if worst_losses else 0
        absolute_worst = min(worst_losses) if worst_losses else 0

        # Display overall statistics
        st.subheader("Overall Statistics")

        # First row of metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Sessions", len(all_sessions))
        with col2:
            st.metric("Win Rate", f"{win_rate:.1f}%")
        with col3:
            st.metric("Total Profit (Chips)", total_profit_chips)

        # Second row of metrics
        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("Total Turnover", f"{total_turnover:,} chips")
        with col5:
            st.metric("Avg Worst Loss", f"{avg_worst_loss:.1f}")
        with col6:
            st.metric("Absolute Worst", f"{absolute_worst}")

        # Create summary table
        st.subheader("Session List")

        # Prepare data for table
        session_summary = []
        for session in all_sessions:
            timestamp_str = session['timestamp']
            # Parse ISO timestamp
            try:
                dt = datetime.fromisoformat(timestamp_str)
                date_display = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                date_display = timestamp_str

            # Get worst drawdown info
            worst_dd = session['results'].get('worst_drawdown', {})
            # For backward compatibility with old format
            if 'total_loss' in worst_dd:
                drawdown_display = f"{worst_dd['total_loss']} chips"
            else:
                # Old format - just show max_drawdown_chips if it exists
                old_dd = session['results'].get('max_drawdown_chips', 0)
                drawdown_display = f"{old_dd} chips" if old_dd else "N/A"

            bypass_setting = session['configuration'].get('bypass_a10_rule', True)  # Default True for backward compatibility

            # Check if session was successful (not stuck in Stage 2)
            # For backward compatibility, check if session_successful exists, otherwise infer from final_stage
            if 'session_successful' in session['results']:
                session_successful = session['results']['session_successful']
            elif 'final_stage' in session['results']:
                session_successful = session['results']['final_stage'] != 2
            else:
                # Old sessions - assume successful if there's positive balance
                session_successful = session['results']['profit_loss_chips'] >= 0

            # Get turnover (default to 0 for old sessions)
            turnover = session['results'].get('total_turnover', 0)

            session_summary.append({
                'Date': date_display,
                'File': session['configuration']['file'],
                'Seq Codes': session['configuration']['sequence_codes'],
                'Divisor': session['configuration']['stage2_divisor'],
                'Bypass': 'Yes' if bypass_setting else 'No',
                'Sequences': session['results']['sequences_completed'],
                'Success': '✓' if session_successful else '✗',
                'Turnover': turnover,
                'Profit (Chips)': session['results']['profit_loss_chips'],
                'Profit (Units)': session['results']['profit_loss_units'],
                'Worst Loss': drawdown_display,
                'Status': session['results']['session_status'],
                'Filename': session['filename']
            })

        summary_df = pd.DataFrame(session_summary)

        # Session deletion section
        st.subheader("Session Management")

        # Initialize session state for checkboxes
        if 'selected_sessions' not in st.session_state:
            st.session_state.selected_sessions = set()

        # Initialize delete all confirmation state
        if 'confirm_delete_all' not in st.session_state:
            st.session_state.confirm_delete_all = False

        # Track if delete button was clicked
        delete_selected_clicked = False

        # Select All / Deselect All / Delete buttons
        col1, col2, col3, col4 = st.columns([1, 1, 1.5, 2.5])
        with col1:
            if st.button("Select All"):
                st.session_state.selected_sessions = set([s['Filename'] for s in session_summary])
                st.rerun()
        with col2:
            if st.button("Deselect All"):
                st.session_state.selected_sessions = set()
                st.rerun()
        with col3:
            # Show button without count - it will delete whatever is checked in the table
            if st.button("Delete Selected", type="primary"):
                delete_selected_clicked = True
        with col4:
            if not st.session_state.confirm_delete_all:
                if st.button(f"Delete All ({len(all_sessions)})", type="secondary"):
                    st.session_state.confirm_delete_all = True
                    st.rerun()
            else:
                st.warning("⚠️ Confirm: Delete ALL sessions?")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("Yes, Delete All", type="primary"):
                        deleted_count = 0
                        for session in all_sessions:
                            if delete_session(session['filename']):
                                deleted_count += 1
                        st.session_state.selected_sessions = set()
                        st.session_state.confirm_delete_all = False
                        st.success(f"Deleted all {deleted_count} session(s) successfully!")
                        st.rerun()
                with col_no:
                    if st.button("Cancel"):
                        st.session_state.confirm_delete_all = False
                        st.rerun()

        # Display dataframe with checkbox column using st.data_editor
        st.write("**Session List:**")

        # Add a Select column to the dataframe
        display_df = summary_df.copy()
        display_df.insert(0, 'Select', False)  # Add Select column at the beginning

        # Set existing selections
        for idx, row in display_df.iterrows():
            if row['Filename'] in st.session_state.selected_sessions:
                display_df.at[idx, 'Select'] = True

        # Display editable dataframe with checkboxes
        edited_df = st.data_editor(
            display_df.drop(columns=['Filename']),
            hide_index=True,
            use_container_width=True,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    help="Select sessions to delete",
                    default=False,
                )
            },
            disabled=[col for col in display_df.columns if col not in ['Select', 'Filename']],
            key="session_table"
        )

        # Update selected sessions based on edited dataframe
        st.session_state.selected_sessions = set()
        for idx, row in edited_df.iterrows():
            if row['Select']:
                st.session_state.selected_sessions.add(summary_df.iloc[idx]['Filename'])

        # Process delete if button was clicked
        if delete_selected_clicked:
            if len(st.session_state.selected_sessions) > 0:
                deleted_count = 0
                for filename in list(st.session_state.selected_sessions):
                    if delete_session(filename):
                        deleted_count += 1
                st.session_state.selected_sessions = set()
                st.success(f"Deleted {deleted_count} session(s) successfully!")
                st.rerun()
            else:
                st.warning("No sessions selected. Please check the boxes next to sessions you want to delete.")

        st.write("---")

        # Session detail viewer
        st.subheader("View Session Details")

        # Create dropdown for session selection
        session_options = {f"{s['Date']} - {s['Profit (Chips)']} chips": s['Filename']
                          for s in session_summary}

        if session_options:
            selected_display = st.selectbox("Select session to view:", [""] + list(session_options.keys()))

            if selected_display and selected_display != "":
                selected_filename = session_options[selected_display]
                selected_session = next(s for s in all_sessions if s['filename'] == selected_filename)

                # Display session details
                st.write("---")
                st.write("**Configuration:**")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"- File: {selected_session['configuration']['file']}")
                    st.write(f"- Sequence Codes: {selected_session['configuration']['sequence_codes']}")
                with col2:
                    st.write(f"- Stage 2 Divisor: {selected_session['configuration']['stage2_divisor']}")
                    bypass_val = selected_session['configuration'].get('bypass_a10_rule', True)
                    st.write(f"- Bypass a>10 Rule: {'Enabled' if bypass_val else 'Disabled'}")
                    st.write(f"- Total Outcomes: {selected_session['configuration']['total_outcomes']}")

                st.write("**Results:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"- Sequences Completed: {selected_session['results']['sequences_completed']}")
                    st.write(f"- Final Balance: {selected_session['results']['final_balance_chips']} chips")

                    # Display final stage and success status
                    final_stage = selected_session['results'].get('final_stage', 1)
                    stage_name = {1: "Stage 1", 2: "Stage 2 (Unfinished)", 3: "Stage 2 (Recovered)", 4: "Failed"}
                    st.write(f"- Final Stage: {stage_name.get(final_stage, 'Unknown')}")

                    session_successful = selected_session['results'].get('session_successful', True)
                    st.write(f"- Success: {'✓ Clean finish' if session_successful else '✗ Stuck in Stage 2'}")

                with col2:
                    st.write(f"- Final Bank: {selected_session['results']['final_bank_units']} units")
                    st.write(f"- Profit/Loss: {selected_session['results']['profit_loss_chips']} chips")
                    turnover = selected_session['results'].get('total_turnover', 0)
                    st.write(f"- Turnover: {turnover:,} chips")
                with col3:
                    st.write(f"- Status: {selected_session['results']['session_status']}")
                    st.write(f"- Outcomes Processed: {selected_session['results']['outcomes_processed']}")

                # Display worst drawdown details
                worst_dd = selected_session['results'].get('worst_drawdown', {})
                if worst_dd and 'line' in worst_dd and worst_dd['line'] > 0:
                    st.write("**Worst Drawdown Point:**")
                    st.write(f"- Line: {worst_dd['line']}")
                    st.write(f"- Bet: {worst_dd['bet']}")
                    st.write(f"- Negative: {worst_dd['negative']}")
                    positive_val = worst_dd.get('positive', '0')
                    positive_chips_val = worst_dd.get('positive_chips', 0)
                    st.write(f"- Positive: {positive_val} ({positive_chips_val} chips)")
                    st.write(f"- Chip Loss Calculation: ({worst_dd['negative']} × 4) + {positive_chips_val} = {worst_dd['chip_loss']} chips")
                    st.write(f"- Balance: {worst_dd['balance']} chips")
                    st.write(f"- Total Loss: {worst_dd['chip_loss']} + {worst_dd['balance']} = {worst_dd['total_loss']} chips")
                else:
                    st.write("**Worst Drawdown:** No significant drawdown recorded")

                # Display balance chart
                if 'balance_history' in selected_session and selected_session['balance_history']:
                    st.subheader("Balance Progression")
                    fig, ax = plt.subplots(figsize=(12, 6))
                    balance_hist = selected_session['balance_history']
                    spins = range(1, len(balance_hist) + 1)
                    ax.plot(spins, balance_hist, linewidth=2, color='blue')
                    ax.set_xlabel('Spin Number')
                    ax.set_ylabel('Balance')
                    ax.set_title('Balance vs Number of Spins')
                    ax.grid(True, alpha=0.3)
                    ax.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='Break-even line')
                    ax.legend()
                    st.pyplot(fig)

                # Display dataframe
                st.subheader("Betting Details")
                session_df = pd.DataFrame(selected_session['dataframe'])
                st.dataframe(session_df, use_container_width=True)

                # Display debug messages if available
                if 'debug_messages' in selected_session and selected_session['debug_messages']:
                    with st.expander("System Messages"):
                        for line_num, message in selected_session['debug_messages']:
                            st.write(f"Line {line_num}: {message}")


        # Comparison feature
        st.subheader("Session Comparison")
        st.write("Compare performance across different configurations:")

        # Group by sequence codes
        if len(all_sessions) > 1:
            seq_code_performance = {}
            for session in all_sessions:
                seq_code = session['configuration']['sequence_codes']
                if seq_code not in seq_code_performance:
                    seq_code_performance[seq_code] = {'count': 0, 'total_profit': 0, 'wins': 0}

                seq_code_performance[seq_code]['count'] += 1
                seq_code_performance[seq_code]['total_profit'] += session['results']['profit_loss_chips']
                if session['results']['profit_loss_chips'] > 0:
                    seq_code_performance[seq_code]['wins'] += 1

            # Display comparison
            comparison_data = []
            for seq_code, stats in seq_code_performance.items():
                avg_profit = stats['total_profit'] / stats['count']
                win_rate = (stats['wins'] / stats['count']) * 100
                comparison_data.append({
                    'Sequence Codes': seq_code,
                    'Sessions': stats['count'],
                    'Win Rate': f"{win_rate:.1f}%",
                    'Total Profit': stats['total_profit'],
                    'Avg Profit': f"{avg_profit:.1f}"
                })

            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True)

        # Export functionality
        st.subheader("Export History")
        if st.button("Export All Sessions to CSV"):
            try:
                export_df = summary_df.drop(columns=['Filename'])
                csv = export_df.to_csv(index=False)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"roulette_history_{timestamp}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error exporting: {str(e)}")

with tab4:
    st.title("Batch Processing")
    st.write("Process multiple files from the `numbers_for_autorun` folder. Select which settings to vary - unchecked settings will use default values.")

    # Batch processing settings
    st.subheader("Variable Settings")
    st.write("**Check** the settings you want to customize. **Unchecked** settings will use default values shown below.")

    # Starting Sequence Codes with multiselect
    use_custom_sequences = st.checkbox("Customize Starting Sequence Codes", value=False, key="batch_use_seq")
    if use_custom_sequences:
        batch_sequence_options = st.multiselect(
            "Select sequence codes to test:",
            list(sequence_code_options.keys()),
            default=["Standard (3, 4, 2)"],
            key="batch_seq",
            help="Choose one or more sequence codes. Each will be tested with all files."
        )
    else:
        batch_sequence_options = ["Standard (3, 4, 2)"]
        st.info("📌 Default: Standard (3, 4, 2)")

    # Stage 2 Divisor with multiselect
    use_custom_divisor = st.checkbox("Customize Stage 2 Divisor", value=False, key="batch_use_div")
    if use_custom_divisor:
        batch_stage2_divisors = st.multiselect(
            "Select divisors to test:",
            [8, 16, 32],
            default=[8],
            key="batch_div",
            help="Choose one or more divisors. Each will be tested."
        )
    else:
        batch_stage2_divisors = [8]
        st.info("📌 Default: 8")

    st.divider()
    st.subheader("Optional Rules")

    col1, col2 = st.columns(2)
    with col1:
        use_bypass_rule = st.checkbox("Test Bypass Rule variations", value=False, key="batch_use_bypass")
        if use_bypass_rule:
            batch_bypass_options = st.multiselect(
                "Bypass Rule settings:",
                ["Enabled", "Disabled"],
                default=["Enabled"],
                key="batch_bypass",
                help="Test with bypass rule on/off"
            )
        else:
            batch_bypass_options = ["Enabled"]
            st.info("📌 Default: Enabled")

        use_c_gt_7 = st.checkbox("Test 'Only bet when c > 7' variations", value=False, key="batch_use_c_gt_7")
        if use_c_gt_7:
            batch_c_gt_7_options = st.multiselect(
                "c > 7 Rule settings:",
                ["Enabled", "Disabled"],
                default=["Disabled"],
                key="batch_c_gt_7",
                help="Test with c > 7 rule on/off"
            )
        else:
            batch_c_gt_7_options = ["Disabled"]
            st.info("📌 Default: Disabled")

        use_a1_wait = st.checkbox("Test 'A1 Wait Rule' variations", value=False, key="batch_use_a1_wait")
        if use_a1_wait:
            batch_a1_wait_options = st.multiselect(
                "A1 Wait Rule settings:",
                ["Enabled", "Disabled"],
                default=["Disabled"],
                key="batch_a1_wait",
                help="Test with A1 wait rule on/off"
            )
        else:
            batch_a1_wait_options = ["Disabled"]
            st.info("📌 Default: Disabled")

    with col2:
        use_always_bet = st.checkbox("Test 'Always bet when a > 10' variations", value=False, key="batch_use_always_bet")
        if use_always_bet:
            batch_always_bet_options = st.multiselect(
                "Always bet a>10 settings:",
                ["Enabled", "Disabled"],
                default=["Disabled"],
                key="batch_always_bet",
                help="Test with always bet rule on/off"
            )
        else:
            batch_always_bet_options = ["Disabled"]
            st.info("📌 Default: Disabled")

        use_divisor_below_1 = st.checkbox("Test 'Divisor below 1' variations", value=False, key="batch_use_div_below_1")
        if use_divisor_below_1:
            batch_divisor_below_1_options = st.multiselect(
                "Divisor below 1 settings:",
                ["Enabled", "Disabled"],
                default=["Disabled"],
                key="batch_div_below_1",
                help="Test with divisor below 1 on/off"
            )
        else:
            batch_divisor_below_1_options = ["Disabled"]
            st.info("📌 Default: Disabled")

        use_max_bet_cap = st.checkbox("Test 'Max Bet Cap' variations", value=False, key="batch_use_max_cap")
        if use_max_bet_cap:
            batch_max_bet_caps = st.multiselect(
                "Max bet cap values:",
                [0, 10, 15, 20, 25, 30],
                default=[0],
                key="batch_max_cap",
                help="Test with different max bet caps (0 = no cap)"
            )
        else:
            batch_max_bet_caps = [0]
            st.info("📌 Default: 0 (no cap)")

    # Check for files in batch folder
    batch_folder = "numbers_for_autorun"
    batch_files_available = []
    if os.path.exists(batch_folder):
        batch_files_available = sorted([f for f in os.listdir(batch_folder)
                                       if f.endswith(('.xls', '.xlsx', '.csv', '.txt'))])

    # Calculate total combinations
    import itertools
    total_combinations = (
        len(batch_sequence_options) *
        len(batch_stage2_divisors) *
        len(batch_bypass_options) *
        len(batch_c_gt_7_options) *
        len(batch_a1_wait_options) *
        len(batch_always_bet_options) *
        len(batch_divisor_below_1_options) *
        len(batch_max_bet_caps)
    )
    total_tests = len(batch_files_available) * total_combinations

    st.divider()
    st.subheader("Batch Summary")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Files", len(batch_files_available))
    with col_b:
        st.metric("Setting Combinations", total_combinations)
    with col_c:
        st.metric("Total Tests", total_tests)

    if batch_files_available:
        # Show preview of files
        with st.expander(f"Preview files ({len(batch_files_available)} total)"):
            preview_df = pd.DataFrame({'Filename': batch_files_available[:20]})
            st.dataframe(preview_df, use_container_width=True)
            if len(batch_files_available) > 20:
                st.write(f"... and {len(batch_files_available) - 20} more files")
    else:
        st.warning(f"No files found in `{batch_folder}` folder. Please add .xls, .xlsx, .csv, or .txt files to process.")

    # Run batch processing
    if st.button("Run Batch Processing", disabled=not batch_files_available):
        st.title("Batch Processing Results")

        st.info(f"Running {total_tests} total tests ({len(batch_files_available)} files × {total_combinations} combinations)")
        st.write("Processing all files with selected setting combinations...")

        batch_results = []
        batch_progress = st.progress(0)
        batch_status = st.empty()

        # Generate all combinations
        all_combinations = list(itertools.product(
            batch_sequence_options,
            batch_stage2_divisors,
            batch_bypass_options,
            batch_c_gt_7_options,
            batch_a1_wait_options,
            batch_always_bet_options,
            batch_divisor_below_1_options,
            batch_max_bet_caps
        ))

        test_num = 0
        for batch_file in batch_files_available:
            file_path = os.path.join(batch_folder, batch_file)

            try:
                # Load file outcomes
                if batch_file.endswith('.txt'):
                    with open(file_path, 'r') as f:
                        file_outcomes = [int(line.strip()) for line in f if line.strip().isdigit()]
                elif batch_file.endswith('.csv'):
                    df = pd.read_csv(file_path, header=None)
                    file_outcomes = df.iloc[:, 0].dropna().astype(int).tolist()
                else:
                    df = pd.read_excel(file_path, header=None)
                    file_outcomes = df.iloc[:, 0].dropna().astype(int).tolist()

                # Run simulation for each combination
                for combo in all_combinations:
                    test_num += 1
                    seq_code_name, divisor, bypass, c_gt_7, a1_wait, always_bet, div_below_1, max_cap = combo

                    batch_status.text(f"Test {test_num}/{total_tests}: {batch_file[:20]}... | {seq_code_name[:15]} | Div:{divisor}")

                    # Convert string options to boolean
                    bypass_enabled = (bypass == "Enabled")
                    c_gt_7_enabled = (c_gt_7 == "Enabled")
                    a1_wait_enabled = (a1_wait == "Enabled")
                    always_bet_enabled = (always_bet == "Enabled")
                    div_below_1_enabled = (div_below_1 == "Enabled")

                    # Get sequence codes
                    init_seq_codes = sequence_code_options[seq_code_name].copy()

                    # Run streamlined simulation (no UI, just core logic and results)
                    try:
                        # === SIMULATION START ===
                        # Initialize all variables
                        seq_code = init_seq_codes.copy()
                        recording = False
                        balance = 0
                        current_bet_type = 1
                        session_active = True
                        sequence_number = 0
                        first_bet_placed = False
                        stage = 1
                        waiting_for_a1_losses = False
                        non_a1_count = 0
                        cumulative_negative = {'integer': 0, 'decimal': 0}
                        cumulative_positive_chips = 0
                        consecutive_non_a1 = 0
                        four_corner_rule_active = False
                        pending_sequence_codes = None
                        codes_displayed = False
                        current_divisor = divisor
                        initial_divisor = divisor
                        starting_bank = 250

                        # Helper functions (inline for batch)
                        def calc_new_a(a):
                            if a > 13: return 10
                            elif 10 < a < 14: return a - 4
                            elif 7 < a < 11: return a - 3
                            elif a < 8: return a - 2
                            return a

                        def chips_to_mixed(chips):
                            if chips == 0: return {'integer': 0, 'decimal': 0}
                            abs_chips = abs(chips)
                            units_of_4 = abs_chips // 4
                            remainder = abs_chips % 4
                            if chips < 0:
                                if remainder == 0: return {'integer': -units_of_4, 'decimal': 0}
                                else: return {'integer': -(units_of_4 + 1), 'decimal': 4 - remainder}
                            else:return {'integer': units_of_4, 'decimal': remainder}

                        def mixed_to_chips(mixed_dict):
                            if mixed_dict['integer'] < 0: return mixed_dict['integer'] * 4
                            else: return (mixed_dict['integer'] * 4) + mixed_dict['decimal']

                        # Process outcomes
                        for i, outcome in enumerate(file_outcomes):
                            if not session_active:
                                break

                            win_status = 'W' if outcome in A1 else 'L'

                            # Start recording on first A1 win
                            if win_status == 'W' and not recording and session_active:
                                recording = True
                                sequence_number += 1
                                continue

                            # Main betting and sequence logic
                            if recording and session_active:
                                # Apply pending codes
                                if pending_sequence_codes and not four_corner_rule_active:
                                    seq_code.update(pending_sequence_codes)
                                    pending_sequence_codes = None

                                # Display codes
                                if not four_corner_rule_active and not pending_sequence_codes:
                                    codes_displayed = True
                                else:
                                    codes_displayed = False

                                # === STAGE 1 BETTING ===
                                if stage == 1:
                                    # Check c > 7 rule
                                    if c_gt_7_enabled and seq_code['c'] <= 7:
                                        pass  # Skip betting
                                    # Check A1 wait rule
                                    elif a1_wait_enabled and waiting_for_a1_losses:
                                        # Update non-A1 count
                                        if outcome not in A1:
                                            non_a1_count += 1
                                            if non_a1_count >= 3:
                                                waiting_for_a1_losses = False
                                                non_a1_count = 0
                                    else:
                                        # Place bet based on bet type
                                        if current_bet_type == 1:
                                            bet_numbers = A2
                                            bet_amount = 5
                                        elif current_bet_type == 2:
                                            bet_numbers = A1
                                            bet_amount = 4
                                        else:  # Bet3
                                            bet_numbers = A1
                                            bet_amount = 8

                                        first_bet_placed = True
                                        is_win = outcome in bet_numbers

                                        if is_win:
                                            # Handle wins
                                            if current_bet_type == 1:
                                                balance += bet_amount
                                                current_bet_type = 1
                                                if outcome in A1 and a1_wait_enabled:
                                                    waiting_for_a1_losses = True
                                                    non_a1_count = 0
                                            else:
                                                # Bet2/Bet3 win - mixed number logic
                                                cumulative_negative['integer'] += (bet_amount // 4)
                                                bip_chips = (bet_amount // 4)
                                                cumulative_positive_chips += cumulative_negative['decimal'] + bip_chips
                                                negative_chips = mixed_to_chips(cumulative_negative)
                                                total_recovery = negative_chips + cumulative_positive_chips
                                                if total_recovery >= 0:
                                                    balance += total_recovery
                                                current_bet_type = 1
                                                if outcome in A1 and a1_wait_enabled:
                                                    waiting_for_a1_losses = True
                                                    non_a1_count = 0
                                        else:
                                            # Handle losses
                                            loss_mixed = chips_to_mixed(-bet_amount)
                                            cumulative_negative['integer'] += loss_mixed['integer']
                                            cumulative_negative['decimal'] += loss_mixed['decimal']
                                            if cumulative_negative['decimal'] >= 4:
                                                carry = cumulative_negative['decimal'] // 4
                                                cumulative_negative['integer'] += carry
                                                cumulative_negative['decimal'] = cumulative_negative['decimal'] % 4

                                            # Progress bet type
                                            if current_bet_type == 1:
                                                current_bet_type = 2
                                            elif current_bet_type == 2:
                                                current_bet_type = 3
                                            else:
                                                # Bet3 lost - move to Stage 2
                                                stage = 2
                                                current_bet_type = 1

                                # === STAGE 2 BETTING ===
                                elif stage == 2:
                                    if codes_displayed:
                                        negative_units = abs(cumulative_negative['integer'])
                                        should_bet = False

                                        # Check always bet a>10 rule (overrides everything)
                                        if always_bet_enabled and seq_code['a'] > 10:
                                            should_bet = True
                                        elif bypass_enabled:
                                            should_bet = not (seq_code['a'] > 10 and negative_units <= 20)
                                        else:
                                            should_bet = seq_code['a'] <= 10

                                        # Check c > 7 rule
                                        if should_bet and c_gt_7_enabled and seq_code['c'] <= 7:
                                            should_bet = False

                                        if should_bet:
                                            # Calculate bet units
                                            if current_divisor == 0: current_divisor = 1
                                            normal_bet_units = int(seq_code['c'] / current_divisor)
                                            if normal_bet_units == 0: normal_bet_units = 1

                                            # Risk management
                                            if seq_code['a'] <= 4:
                                                negative_chips = mixed_to_chips(cumulative_negative)
                                                current_deficit_chips = -(negative_chips + cumulative_positive_chips)
                                                import math
                                                min_recovery_bet_units = math.ceil(current_deficit_chips / 5)
                                                if min_recovery_bet_units == 0: min_recovery_bet_units = 1
                                                bet_units = min_recovery_bet_units
                                            else:
                                                bet_units = normal_bet_units

                                            # Apply max bet cap
                                            if max_cap > 0 and bet_units > max_cap:
                                                bet_units = max_cap

                                            bet_chips = bet_units * 4
                                            is_win = outcome in A1

                                            if is_win:
                                                # Stage 2 win
                                                cumulative_negative['integer'] += bet_units
                                                bip_chips = bet_units
                                                cumulative_positive_chips += cumulative_negative['decimal'] + bip_chips
                                                negative_chips = mixed_to_chips(cumulative_negative)
                                                total_recovery = negative_chips + cumulative_positive_chips

                                                if total_recovery >= 0:
                                                    balance += total_recovery
                                                    # Recovery complete
                                                    stage = 3
                                                    cumulative_negative = {'integer': 0, 'decimal': 0}
                                                    cumulative_positive_chips = 0
                                            else:
                                                # Stage 2 loss
                                                loss_mixed = chips_to_mixed(-bet_chips)
                                                cumulative_negative['integer'] += loss_mixed['integer']
                                                cumulative_negative['decimal'] += loss_mixed['decimal']
                                                if cumulative_negative['decimal'] >= 4:
                                                    carry = cumulative_negative['decimal'] // 4
                                                    cumulative_negative['integer'] += carry
                                                    cumulative_negative['decimal'] = cumulative_negative['decimal'] % 4

                                                # Check bank depletion
                                                if abs(mixed_to_chips(cumulative_negative)) >= 1000:
                                                    stage = 4
                                                    session_active = False

                                # Track consecutive non-A1 for four corner rule
                                if outcome in A1:
                                    consecutive_non_a1 = 0
                                    if four_corner_rule_active:
                                        four_corner_rule_active = False
                                else:
                                    consecutive_non_a1 += 1

                                # Update sequence codes
                                is_a1_win = outcome in A1
                                if is_a1_win:
                                    seq_code['a'] = calc_new_a(seq_code['a'])
                                    seq_code['b'] = seq_code['b'] - seq_code['c']
                                    if seq_code['a'] == 0: seq_code['a'] = 1
                                    seq_code['c'] = (int(seq_code['b'] / seq_code['a'])) * 2
                                else:
                                    seq_code['a'] = seq_code['a'] + 1
                                    seq_code['b'] = seq_code['b'] + seq_code['c']

                                    # B > 89 rule
                                    if seq_code['b'] > 89:
                                        seq_code['b'] = int((seq_code['b'] + 1) / 2)
                                        if stage == 2 and recording and not four_corner_rule_active:
                                            if div_below_1_enabled:
                                                current_divisor = current_divisor / 2
                                            elif current_divisor > 1:
                                                current_divisor = current_divisor // 2

                                    if seq_code['a'] == 0: seq_code['a'] = 1
                                    seq_code['c'] = (int(seq_code['b'] / seq_code['a'])) * 2

                                # Check sequence completion
                                if (recording and seq_code['a'] < 3) or stage == 3:
                                    # Sequence complete
                                    recording = False
                                    first_bet_placed = False
                                    stage = 1
                                    current_bet_type = 1
                                    seq_code = init_seq_codes.copy()
                                    cumulative_negative = {'integer': 0, 'decimal': 0}
                                    cumulative_positive_chips = 0
                                    waiting_for_a1_losses = False
                                    non_a1_count = 0
                                    consecutive_non_a1 = 0
                                    four_corner_rule_active = False
                                    pending_sequence_codes = None
                                    codes_displayed = False
                                    current_divisor = initial_divisor

                        # Calculate final results
                        final_bank_units = starting_bank + (balance // 4)
                        profit_loss = final_bank_units - starting_bank

                        # Determine success (not stuck in Stage 2)
                        session_successful = stage != 2

                        batch_results.append({
                            'Test #': test_num,
                            'File': batch_file,
                            'Seq Codes': seq_code_name,
                            'Divisor': divisor,
                            'Bypass': bypass[:3],
                            'c>7': c_gt_7[:3],
                            'A1 Wait': a1_wait[:3],
                            'Always Bet': always_bet[:3],
                            'Div<1': div_below_1[:3],
                            'Max Cap': max_cap,
                            'Sequences': sequence_number,
                            'Final Balance': balance,
                            'Final Bank': final_bank_units,
                            'Profit/Loss': profit_loss,
                            'Status': 'ENDED' if not session_active else 'ACTIVE',
                            'Success': 'Yes' if session_successful else 'No'
                        })
                        # === SIMULATION END ===

                    except Exception as e:
                        batch_results.append({
                            'Test #': test_num,
                            'File': batch_file,
                            'Seq Codes': seq_code_name,
                            'Divisor': divisor,
                            'Bypass': '-',
                            'c>7': '-',
                            'A1 Wait': '-',
                            'Always Bet': '-',
                            'Div<1': '-',
                            'Max Cap': '-',
                            'Sequences': '-',
                            'Final Balance': '-',
                            'Final Bank': '-',
                            'Profit/Loss': '-',
                            'Status': f'ERROR: {str(e)[:20]}',
                            'Success': '-'
                        })

                    batch_progress.progress(test_num / total_tests)

            except Exception as e:
                test_num += 1
                batch_results.append({
                    'Test #': test_num,
                    'File': batch_file,
                    'Seq Codes': '-',
                    'Divisor': '-',
                    'Bypass': '-',
                    'c>7': '-',
                    'A1 Wait': '-',
                    'Always Bet a>10': '-',
                    'Div<1': '-',
                    'Max Cap': '-',
                    'Outcomes': 'ERROR',
                    'Status': f'✗ {str(e)[:30]}'
                })
                batch_progress.progress(test_num / total_tests)
                continue

        batch_status.text("✓ Batch configuration complete!")

        # Display results
        results_df = pd.DataFrame(batch_results)

        # Calculate summary statistics
        successful_tests = len([r for r in batch_results if r['Status'] == 'ACTIVE' or r['Status'] == 'ENDED'])
        active_sessions = len([r for r in batch_results if r['Status'] == 'ACTIVE'])
        ended_sessions = len([r for r in batch_results if r['Status'] == 'ENDED'])
        error_tests = len([r for r in batch_results if 'ERROR' in r['Status']])

        # Calculate success rate (not stuck in Stage 2)
        success_count = len([r for r in batch_results if r.get('Success') == 'Yes'])
        success_rate = (success_count / successful_tests * 100) if successful_tests > 0 else 0

        # Calculate profit statistics (only for successful tests)
        successful_results = [r for r in batch_results if isinstance(r['Profit/Loss'], int)]
        if successful_results:
            total_profit = sum(r['Profit/Loss'] for r in successful_results)
            avg_profit = total_profit / len(successful_results)
            profitable_tests = len([r for r in successful_results if r['Profit/Loss'] > 0])
            win_rate = (profitable_tests / len(successful_results)) * 100
        else:
            total_profit = 0
            avg_profit = 0
            profitable_tests = 0
            win_rate = 0

        st.success(f"✓ Batch processing complete! {successful_tests}/{total_tests} tests ran successfully")

        # Show summary statistics
        st.subheader("Batch Results Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tests", total_tests)
            st.metric("Completed", successful_tests)
        with col2:
            st.metric("Success Rate", f"{success_rate:.1f}%")
            st.metric("Successful Tests", success_count)
        with col3:
            st.metric("Win Rate", f"{win_rate:.1f}%")
            st.metric("Profitable Tests", profitable_tests)
        with col4:
            st.metric("Avg Profit/Loss", f"{avg_profit:+.1f} units")
            st.metric("Total Profit", f"{total_profit:+d} units")

        # Show detailed results
        st.subheader("Detailed Results")
        st.write(f"Showing all {len(results_df)} test results:")
        st.dataframe(results_df, use_container_width=True, height=600)

        # Download results as CSV
        csv = results_df.to_csv(index=False)
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name=f"batch_results_{timestamp}.csv",
            mime="text/csv"
        )