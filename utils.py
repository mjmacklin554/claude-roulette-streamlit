"""
Utility functions for Michael's Roulette System
Contains helper functions for mixed numbers, betting calculations, and data processing
"""

# A1 consisting of 16 numbers (4 x Corner Bets)
A1 = [2, 3, 5, 6, 17, 18, 20, 21, 25, 26, 28, 29, 31, 32, 34, 35]

# A2 consisting of 30 numbers (5 x Six-Line Bets): 1-6, 13-18, 19-24, 25-30, 31-36
A2 = []
for start in [1, 13, 19, 25, 31]:
    A2.extend(range(start, start + 6))


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
        return f"Stage 2: Check a={a}, negative={negative_units}"
    else:
        return "Session complete"


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


class NoOpList:
    """A no-op list class that ignores all append operations for performance"""
    def append(self, item):
        pass
    def __iter__(self):
        return iter([])
    def __bool__(self):
        return False
    def __len__(self):
        return 0
