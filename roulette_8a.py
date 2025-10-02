
import pandas as pd
import numpy

def outcome_list():
    #number_total = int(input("How many spins have you had?: "))
    number_total = int(input("How many spins do you want?: "))
    number_list = [6,31,11,6,9,34,15,22,26,25,16,6,2,22,12,3,21,29,36,8,9,4,13,31,24,35,
    17,32,35,24,26,29,7,19,19,30,13,32,21,21,20,35,9,6,16,30,22,18,35,14,26,15,13,14,26,16,8,11,20,17,4,16,18,36,4,
    18,4,21,21,2,23,3,15,23,1,10,9,22,35,12,5,25,4,14,3,31,25,9,31,36,36,19,34,5,30,34,13,23]
    number_list_1 = [0,15,27,33,26,14,36,2,16,22,7,17,30,22,28,9,10,11,6,1,33,10,15,18,11,9,1,7,30,30,36,36]
    active_number_list = []
    
    count = 1
    
    while count <= number_total:
        #outcome = input("Enter Number for spin " + str(count) + ": ")
        outcome = number_list_1[count-1]
        active_number_list.append(int(outcome))
        count += 1

    return active_number_list

def calculate_a(a):
    if a > 13:
        a = 10
    elif a in [11, 12, 13]:
        a -= 4
    elif a in [8, 9, 10]:
        a -= 3
    else:  # a is 7 or less
        a -= 2

    return int(a)

def check_three_loss(corner_loss_counter, three_loss_rule):
    if df.at[index-1, 'win'] == 'W':
        three_loss_rule = True
    

    if three_loss_rule:
        
        if corner_loss_counter <3:
            three_loss_rule = True

        else:
            three_loss_rule = False       
            
    return three_loss_rule 


def check_four_loss(corner_loss_counter, four_loss_rule):
    if corner_loss_counter >=4:
        four_loss_rule = True

    else:
        four_loss_rule = False
    return four_loss_rule


    

    


def make_bet(first_bet, three_loss_rule, four_loss_rule, row, balance, df, index, A1, A2, corner_bet):
    if not corner_bet:
        if first_bet:
            if int(row['outcome']) not in A2:
                balance += 1
                df.at[index, 'balance'] = balance
            
            elif int(row['outcome']) in A2:
                balance -= 5
                corner_bet = True
                df.at[index, 'balance'] = balance  


        elif int(row['outcome']) not in A2 and not three_loss_rule:
            balance += 1
            df.at[index, 'balance'] = balance
            
        elif int(row['outcome']) in A2 and not three_loss_rule:
            balance -= 5
            corner_bet = True
            df.at[index, 'negative'] = "-2"
            df.at[index, 'positive'] = "3"


    else:
        if first_bet:
            if int(row['outcome']) not in A1:
                balance -= 4
                df.at[index, 'balance'] = balance
            
            elif int(row['outcome']) in A1:
                balance += 1
                df.at[index, 'balance'] = balance  


        elif int(row['outcome']) not in A1 and not three_loss_rule:
            df.at[index, 'negative'] = "-3"



            
            
        elif int(row['outcome']) in A1 and not three_loss_rule:
            balance += 1
            df.at[index, 'balance'] = balance

        #corner_bet = False
    
    return balance, corner_bet



# Step 1: Create a Pandas DataFrame
columns = ['line', 'outcome', 'win', 'a', 'b', 'c', 'actual bet', 'negative', 'positive', 'balance']
df = pd.DataFrame(columns=columns)
df = df.fillna(0)
df = df.fillna(0).astype({'outcome': 'int'})


# Step 2: Populate the DataFrame with Data
df['outcome'] = outcome_list()

A1 = [2, 3, 5, 6, 17, 18, 20, 21, 25, 26, 28, 29, 31, 32, 34, 35]
A2 = [0, 7, 8, 9, 10, 11, 12]

# Step 3: Check outcomes and assign win/loss
df['win'] = df['outcome'].apply(lambda x: 'W' if x in A1 else 'L')

# Step 4: Initialize sequence_code dictionary
sequence_code = {'a': 3, 'b': 4, 'c': 2}

# Step 5: Start recording sequence_code when the first 'W' occurs
recording = False
init_value = False
balance = 0 
corner_loss_counter = 0
first_bet = True
three_loss_rule = False
four_loss_rule = False
corner_bet = False

for index, row in df.iterrows():
    df.at[index, 'line'] = int(index + 1)

    if row['win'] == 'W' and not recording:
        if index + 1 < len(df):
            df.at[index + 1, 'a'] = sequence_code['a']
            df.at[index + 1, 'b'] = sequence_code['b']
            df.at[index + 1, 'c'] = sequence_code['c']

        recording = True
        init_value = True # initial code of 8 44 10 has been set

    # Step 6: Continue recording sequence_code with values of 'a' dependent on win or loss
    if recording and not init_value:
        if first_bet:
            balance, corner_bet = make_bet(first_bet, three_loss_rule, four_loss_rule, row, balance, df, index, A1, A2, corner_bet)
            first_bet = False

        else:
            three_loss_rule = check_three_loss(corner_loss_counter, three_loss_rule)
            four_loss_rule = check_four_loss(corner_loss_counter, four_loss_rule)
            balance, corner_bet = make_bet(first_bet, three_loss_rule, four_loss_rule, row, balance, df, index, A1, A2, corner_bet)

        
        if not four_loss_rule:

            if int(row['outcome']) in A1:

                corner_loss_counter = 0
                



                answer_a = calculate_a(sequence_code['a'])
                sequence_code['a'] = answer_a
                sequence_code['b'] = sequence_code['b'] - sequence_code['c']
                sequence_code['c'] = int(sequence_code['b'] / sequence_code['a']) * 2
                
                if index + 1 < len(df):
                    df.at[index + 1, 'a'] = sequence_code['a']       
                    df.at[index + 1, 'b'] = sequence_code['b']
                    df.at[index + 1, 'c'] = sequence_code['c']
            else:
                
                corner_loss_counter +=1

                

                sequence_code['a'] += 1
                sequence_code['b'] = sequence_code['b'] + sequence_code['c']
                if sequence_code['b'] > 89:
                    sequence_code['b'] = int((sequence_code['b'] + 1) / 2)
                sequence_code['c'] = int(sequence_code['b'] / sequence_code['a']) * 2

                if index + 1 < len(df):
                    df.at[index + 1, 'a'] = sequence_code['a']
                    df.at[index + 1, 'b'] = sequence_code['b']
                    df.at[index + 1, 'c'] = sequence_code['c']

        else:

            if int(row['outcome']) in A1:

                corner_loss_counter = 0

                if index + 1 < len(df):
                    df.at[index + 1, 'a'] = sequence_code['a']
                    df.at[index + 1, 'b'] = sequence_code['b']
                    df.at[index + 1, 'c'] = sequence_code['c']

            else:

                corner_loss_counter +=1

                if index + 1 < len(df):
                    df.at[index + 1, 'a'] = sequence_code['a']
                    df.at[index + 1, 'b'] = sequence_code['b']
                    df.at[index + 1, 'c'] = sequence_code['c']




            

                

                


        

    

    

    # Stop recording when df['a'] < 4
    if index + 1 < len(df) and 'a' in df.columns and df.at[index + 1, 'a'] < 3:
        recording = False
        first_bet = True
        three_loss_rule = False
        sequence_code = {'a': 3, 'b': 4, 'c': 2}

    init_value = False

print(df)



