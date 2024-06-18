import os

# Get the current working directory
current_directory = os.getcwd()

# Loop through all files in the current directory
for filename in os.listdir(current_directory):
    # Check if "_o" is in the filename
    if "_o" in filename:
        # Replace "_o" with "_s" in the filename
        new_filename = filename.replace("_o", "_s")
        
        # Get the full file paths
        old_file_path = os.path.join(current_directory, filename)
        new_file_path = os.path.join(current_directory, new_filename)
        
        # Rename the file
        os.rename(old_file_path, new_file_path)

print("Renaming complete!")