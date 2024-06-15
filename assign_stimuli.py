import pandas as pd
import numpy as np
import random

def create_latin_square(num_conditions):
    # Generates a Latin square for the specified number of conditions
    return np.array([[((j + i) % num_conditions) for i in range(num_conditions)] for j in range(num_conditions)])

def assign_stimuli(data_csv_path, templates_csv_path, num_participants):
    # Load the trials and templates data
    trials_data = pd.read_csv(data_csv_path)
    templates_stimuli = pd.read_csv(templates_csv_path)

    # Create a Latin square for condition assignment
    num_conditions = 3
    conditions = ['V', 'H', 'VH']
    latin_square = create_latin_square(num_conditions)

    # Iterate over each participant
    for participant_id in range(1, num_participants + 1):
        # Get the condition order for this participant using Latin square
        condition_order = latin_square[(participant_id - 1) % num_conditions]

        # Reset and shuffle stimuli for this participant
        shuffled_stimuli = templates_stimuli.sample(frac=1).reset_index(drop=True)
        stimulus_pointer = 0

        # Filter trials for the current participant
        participant_trials = trials_data[trials_data['participantID'] == participant_id]

        # Assign stimuli to the trials
        for index, row in participant_trials.iterrows():
            if stimulus_pointer >= len(shuffled_stimuli):
                stimulus_pointer = 0  # Reset pointer if end of DataFrame is reached
                shuffled_stimuli = templates_stimuli.sample(frac=1).reset_index(drop=True)  # Reshuffle stimuli

            # Get the stimulus and template
            stimulus_row = shuffled_stimuli.iloc[stimulus_pointer]
            condition = conditions[condition_order[index % num_conditions]]

            # Update the trial entry with stimulus and template
            trials_data.at[index, 'condition'] = condition
            trials_data.at[index, 'template'] = stimulus_row['template']
            trials_data.at[index, 'stimulus'] = stimulus_row['stimulus']

            stimulus_pointer += 1  # Move to the next stimulus

    return trials_data

# Path to the CSV files (Update these paths as necessary)
data_csv_path = 'data.csv'
templates_csv_path = 'templates_stimuli.csv'

# Assign stimuli to trials with specific conditions rotation
updated_trials_data = assign_stimuli(data_csv_path, templates_csv_path, 30)
print(updated_trials_data.head(60))

# Save the updated trials data to a CSV file
updated_trials_data.to_csv('trials.csv', index=False)
print("Data has been successfully exported to trials.csv.")

def report_trials_per_condition(trials_data):
    # Group the data by 'stimulusID' and 'condition' and count the occurrences
    trials_count = trials_data.groupby(['stimulus', 'condition']).size().reset_index(name='count')
    return trials_count

# Generate the report
trials_report = report_trials_per_condition(updated_trials_data)
print(trials_report)