import os
import csv
import random

NUM_ROWS = 108  # Number of trials per participant
BLOCK_SIZE = 6  # Trial blocks with the same condition
SAMPLE_TIME = 10000  # milliseconds
COMPARISON_TIME = 20000  # milliseconds
SAMPLES = list(range(1, 109))  # 90 samples
PARTICIPANTS = list(range(1, 31))  # 30 participants
CONDITION_TYPES = ['V', 'VH', 'H']  # Conditions: Visual, Visuohaptic, Haptic
TRIAD_RANDOMIZATION = True  # Randomizing condition types every 3 blocks
SAMPLE_ORDER_DIVIDER = NUM_ROWS // 2

# Read the generated_paths.csv file and create a dictionary with ID as key
# This file contains the generated stimuli path coordinates and IDs, the latter is used to retrieve corresponding obj files
path_dict = {}
with open('generated_paths.csv') as pathfile:
    reader = csv.DictReader(pathfile)
    for row in reader:
        path_dict[int(row['ID'])] = {'Path': row['Path'], 'Foil': row['Foil']}

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
        path_info = path_dict[sample_num]
        condition = conditions[i]
        rows.append([participant, i + 1, "", sample_order[i], SAMPLE_TIME, COMPARISON_TIME, condition,"",
                     path_info['Path'], path_info['Foil']])

# After appending all rows, let's balance the "left" and "right" sample_order values
for participant in PARTICIPANTS:
    for condition in CONDITION_TYPES:
        # Get all rows corresponding to the current participant and condition
        participant_condition_rows = [row for row in rows if row[0] == participant and row[6] == condition]

        # Count the occurrences of "left" and "right" in the sample_order for this participant and condition
        left_count = sum(1 for row in participant_condition_rows if row[3] == "left")
        right_count = sum(1 for row in participant_condition_rows if row[3] == "right")

        # Calculate the number of "left" and "right" trials needed to balance
        target_count = SAMPLE_ORDER_DIVIDER // len(CONDITION_TYPES)
        left_needed = target_count - left_count
        right_needed = target_count - right_count

        # Balance the sample_order values if needed
        if left_needed > 0:
            # Randomly select trials with "right" and change them to "left" until the count becomes balanced
            right_trials = [row for row in participant_condition_rows if row[3] == "right"]
            random.shuffle(right_trials)
            for row in right_trials[:left_needed]:
                rows[rows.index(row)][3] = "left"
        elif right_needed > 0:
            # Randomly select trials with "left" and change them to "right" until the count becomes balanced
            left_trials = [row for row in participant_condition_rows if row[3] == "left"]
            random.shuffle(left_trials)
            for row in left_trials[:right_needed]:
                rows[rows.index(row)][3] = "right"


if os.path.exists('match_to_sample_data.csv'):
    os.remove('match_to_sample_data.csv')

# Write the data to a CSV file
with open('match_to_sample_data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(
        ['participantID', 'trialNumber', 'sampleNumber', 'sampleOrder', 'sampleTime', 'comparisonTime',
         'condition', 'template'])
    # Assuming that 'rows' is a list of lists and each inner list represents a row
    # Remove the 'path' and 'foil' column values from each row
    writer.writerows([row[:-2] for row in rows])

# Dictionary to store the counts
count_dict = {}

# Read the CSV file
with open('match_to_sample_data.csv') as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)  # Skip the header row

    # Iterate through each row and count the occurrences
    for row in reader:
        participant = int(row[0])
        condition = row[6]
        sample_order = row[3]

        # Create a key for the participant and condition
        key = (participant, condition, sample_order)

        # Increment the count for this key in the count_dict
        count_dict[key] = count_dict.get(key, 0) + 1

# Print the counts
print("Participant | Condition | Sample Order | Count")
print("---------------------------------------------")
for key, count in count_dict.items():
    participant, condition, sample_order = key
    print(f"{participant:10} | {condition:9} | {sample_order:12} | {count:5}")
