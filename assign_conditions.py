import pandas as pd
import numpy as np

# Load the data
file_path = 'match_to_sample_data.csv'
data = pd.read_csv(file_path)

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

# Verify the distribution of sampleNumbers per condition
distribution_balanced = data.groupby(['sampleNumber', 'condition']).size().unstack().fillna(0)
distribution_balanced = distribution_balanced.astype(int)

# Check if the distribution is balanced
is_balanced = (distribution_balanced == 30).all().all()

# Save the balanced data to a new CSV file
output_file_path_balanced = 'trials.csv'
data.to_csv(output_file_path_balanced, index=False)

print("Output file saved at:", output_file_path_balanced)
print("Is balanced:", is_balanced)
print(distribution_balanced)
