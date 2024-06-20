import os
import csv
import random
import pandas as pd
import numpy as np

NUM_ROWS = 90  # Number of trials per participant
BLOCK_SIZE = 5  # Trial blocks with the same condition
SAMPLE_TIME = 10000  # milliseconds
COMPARISON_TIME = 20000  # milliseconds
SAMPLES = list(range(1, 91))  # 90 samples
PARTICIPANTS = list(range(1, 31))  # 30 participants
CONDITION_TYPES = ['V', 'VH', 'H']  # Conditions: Visual, Visuohaptic, Haptic
TRIAD_RANDOMIZATION = True  # Randomizing condition types every 3 blocks
SAMPLE_ORDER_DIVIDER = NUM_ROWS // 2

# Create a list of tuples representing each row of data
rows = []
for participant in PARTICIPANTS:

    # Assign "left" or "right" randomly to half of the rows for each condition
    sample_order = []
    num_trials_per_condition = NUM_ROWS // len(CONDITION_TYPES) // 2
    for condition in CONDITION_TYPES:
        sample_order.extend(["left"] * num_trials_per_condition)
        sample_order.extend(["right"] * num_trials_per_condition)

    # Shuffle the order of the sample_order to mix up the "left" and "right" trials for each condition
    random.shuffle(sample_order)

    # Initialize the list to hold the randomized sequence of conditions
    conditions = []

    # Randomizing every 3 trial blocks to prevent agglomeration of more than 2 blocks of the same condition
    if TRIAD_RANDOMIZATION:
        for _ in range(NUM_ROWS // len(CONDITION_TYPES)):
            # Randomly select the first condition
            condition_1 = random.choice(CONDITION_TYPES)
            conditions.extend([condition_1] * BLOCK_SIZE)

            # Randomly select the second condition excluding the first one
            condition_2 = random.choice([condition for condition in CONDITION_TYPES if condition != condition_1])
            conditions.extend([condition_2] * BLOCK_SIZE)

            # Select the remaining condition
            condition_3 = [condition for condition in CONDITION_TYPES if condition != condition_1 and condition != condition_2][0]
            conditions.extend([condition_3] * BLOCK_SIZE)
    else:
        # Divide the conditions into blocks of 5 trials each, and shuffle the order of the blocks
        condition_blocks = [["V"] * BLOCK_SIZE, ["VH"] * BLOCK_SIZE, ["H"] * BLOCK_SIZE]

        # Checking how many times the condition blocks need to be multiplied to fill the trials per participant
        multiplier = int(NUM_ROWS / len(condition_blocks) / BLOCK_SIZE)

        # Multiply it accordingly
        expanded_condition_blocks = [item for item in condition_blocks for _ in range(multiplier)]

        # Iterating though expanded_condition_blocks until it gets emptied
        while len(expanded_condition_blocks) > 0:

            condition_block = random.choice(expanded_condition_blocks)
            for individual_condition in condition_block:
                conditions.append(individual_condition)
            expanded_condition_blocks.remove(condition_block)

    # Shuffle the samples to ensure a random order for each participant
    random.shuffle(SAMPLES)

    for i in range(NUM_ROWS):
        sample_num = SAMPLES[i]
        condition = conditions[i]
        rows.append([participant, i + 1, "", sample_order[i], SAMPLE_TIME, COMPARISON_TIME, condition])

# Convert rows to DataFrame for easier manipulation
data = pd.DataFrame(rows, columns=['participantID', 'trialNumber', 'sampleNumber', 'sampleOrder', 'sampleTime', 'comparisonTime', 'condition'])

# Define the lists for participants
participant_list_A = [i for i in range(1, 91, 3)]
participant_list_B = [i for i in range(2, 91, 3)]
participant_list_C = [i for i in range(3, 91, 3)]

# Define the lists for stimuli
stimulus_list_A = [i for i in range(1, 91, 3)]
stimulus_list_B = [i for i in range(2, 91, 3)]
stimulus_list_C = [i for i in range(3, 91, 3)]

# Define the scheme
scheme = {
    'A': {'V': stimulus_list_A, 'H': stimulus_list_B, 'VH': stimulus_list_C},
    'B': {'V': stimulus_list_C, 'H': stimulus_list_A, 'VH': stimulus_list_B},
    'C': {'V': stimulus_list_B, 'H': stimulus_list_C, 'VH': stimulus_list_A}
}

# Assign the sample numbers based on the scheme
def assign_sample_numbers(data, scheme):
    participants = data['participantID'].unique()
    condition_order = ['V', 'H', 'VH']
    
    for i, participant_id in enumerate(participants):
        group = chr(65 + i % 3)  # Rotate through 'A', 'B', 'C'
        participant_data = data[data['participantID'] == participant_id].copy()
        
        for condition in condition_order:
            stimulus_list = scheme[group][condition]
            np.random.shuffle(stimulus_list)  # Shuffle for randomness
            
            indices = participant_data[participant_data['condition'] == condition].index
            for idx, sample_number in zip(indices, stimulus_list):
                data.at[idx, 'sampleNumber'] = sample_number
    
    return data

# Apply the function
data['sampleNumber'] = np.nan
data = assign_sample_numbers(data, scheme)

# Balance the sample order to prevent three consecutive trials with the same sampleOrder
def balance_sample_order(data):
    participants = data['participantID'].unique()
    
    for participant in participants:
        participant_data = data[data['participantID'] == participant].copy()
        sample_orders = participant_data['sampleOrder'].tolist()
        
        for i in range(len(sample_orders) - 2):
            # Check for three consecutive trials with the same sampleOrder
            if sample_orders[i] == sample_orders[i+1] == sample_orders[i+2]:
                # Find a later trial with a different sampleOrder
                for j in range(i+3, len(sample_orders)):
                    if sample_orders[j] != sample_orders[i]:
                        # Swap the sampleOrders
                        sample_orders[i+2], sample_orders[j] = sample_orders[j], sample_orders[i+2]
                        break
        
        # Update the sampleOrders in the data
        data.loc[data['participantID'] == participant, 'sampleOrder'] = sample_orders
    
    return data

# Apply the function
data = balance_sample_order(data)

# Verify the distribution of sampleNumbers per condition
distribution_balanced = data.groupby(['sampleNumber', 'condition']).size().unstack().fillna(0)
distribution_balanced = distribution_balanced.astype(int)

# Check if the distribution is balanced
is_balanced = (distribution_balanced == 10).all().all()

# Save the balanced data to a new CSV file
output_file_path_balanced = 'trials_v_h_vh.csv'
data.to_csv(output_file_path_balanced, index=False)

print("Output file saved at:", output_file_path_balanced)
print("Is balanced:", is_balanced)
print(distribution_balanced)
