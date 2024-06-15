import pandas as pd
import numpy as np

def assign_stimuli_evenly(data_csv_path, templates_csv_path):
    # Load data
    trials_data = pd.read_csv(data_csv_path)
    stimuli_data = pd.read_csv(templates_csv_path)

    # Prepare the stimuli distribution map
    num_conditions = trials_data['condition'].nunique()
    num_trials_per_condition = len(trials_data) // num_conditions
    stimuli_per_condition = {stimulus: {cond: num_trials_per_condition // num_conditions 
                                        for cond in trials_data['condition'].unique()} 
                             for stimulus in stimuli_data['stimulus']}

    # List to hold updated trial information
    updated_trials = []

    # Shuffle trials to avoid any order bias
    trials_data = trials_data.sample(frac=1).reset_index(drop=True)

    # Assign stimuli
    for _, trial in trials_data.iterrows():
        condition = trial['condition']
        available_stimuli = [s for s in stimuli_data['stimulus'] if stimuli_per_condition[s][condition] > 0]

        if not available_stimuli:
            print(f"Ran out of stimuli for condition {condition}. Check data balance.")
            trial['stimulus'] = None
            trial['template'] = None
        else:
            chosen_stimulus = np.random.choice(available_stimuli)
            trial['stimulus'] = chosen_stimulus
            trial['template'] = stimuli_data.loc[stimuli_data['stimulus'] == chosen_stimulus, 'template'].values[0]
            # Decrement the count
            stimuli_per_condition[chosen_stimulus][condition] -= 1

        updated_trials.append(trial)

    # Return updated DataFrame
    return pd.DataFrame(updated_trials)

# Paths to your data files
data_csv_path = 'data.csv'
templates_csv_path = 'templates_stimuli.csv'

# Execute the function
assigned_data = assign_stimuli_evenly(data_csv_path, templates_csv_path)
assigned_data.to_csv('assigned_trials_balanced.csv', index=False)
print("Balanced assigned data saved to 'assigned_trials_balanced.csv'.")

# Function to report trials per condition
def report_trials_per_condition(trials_data):
    return trials_data.groupby(['stimulus', 'condition']).size().reset_index(name='count')

# Report the distribution
distribution_report = report_trials_per_condition(assigned_data)
print(distribution_report)
