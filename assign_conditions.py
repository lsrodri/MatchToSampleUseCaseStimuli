import pandas as pd
import numpy as np

def assign_stimuli_across_conditions(data_csv_path, templates_csv_path):
    trials_data = pd.read_csv(data_csv_path)
    stimuli_data = pd.read_csv(templates_csv_path)

    trials_data['assigned'] = False

    participants = trials_data['participantID'].unique()
    num_participants = len(participants) - len(participants) % 3

    conditions = ['H', 'V', 'VH']

    for idx, stimulus_row in stimuli_data.iterrows():
        stimulus = stimulus_row['stimulus']
        template = stimulus_row['template']

        for i in range(0, num_participants, 3):
            for j, condition in enumerate(conditions):
                participant_id = participants[i + j]

                available_trials = trials_data[(trials_data['participantID'] == participant_id) &
                                               (trials_data['condition'] == condition) &
                                               (trials_data['assigned'] == False)]

                if not available_trials.empty:
                    trial_index = available_trials.sample(n=1).index.item()
                    trials_data.at[trial_index, 'stimulus'] = stimulus
                    trials_data.at[trial_index, 'template'] = template
                    trials_data.at[trial_index, 'assigned'] = True

                    print(f"Assigned stimulus {stimulus} to participant {participant_id}, condition {condition}, trial index {trial_index}")
                else:
                    print(f"No available trials for stimulus {stimulus} with participant {participant_id} under condition {condition}")

    trials_data.drop(columns=['assigned'], inplace=True)
    return trials_data

# File paths
data_csv_path = 'data.csv'
templates_csv_path = 'templates_stimuli.csv'

# Process the data
assigned_data = assign_stimuli_across_conditions(data_csv_path, templates_csv_path)
assigned_data.to_csv('assigned_conditions.csv', index=False)
print("Assigned data saved to 'assigned_conditions.csv'.")

def report_stimulus_condition_combinations(assigned_data):
    # Report on unique combinations of stimulus and condition
    count_report = assigned_data.groupby(['stimulus', 'condition']).size().reset_index(name='count')
    return count_report

# Generate the report
distribution_report = report_stimulus_condition_combinations(assigned_data)
print(distribution_report)
