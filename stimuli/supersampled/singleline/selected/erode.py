import os
import cv2
import numpy as np

# Get the current working directory (the folder where the script is running)
image_folder = os.getcwd()
output_folder = os.path.join(image_folder, 'eroded')

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Define the kernel for erosion
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))  # You can adjust the size

# Loop through all files in the image folder
for filename in os.listdir(image_folder):
    if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):  # Add more extensions if needed
        # Read the image
        image_path = os.path.join(image_folder, filename)
        image = cv2.imread(image_path)

        if image is not None:
            # Increase brightness by 20%
            # image = cv2.convertScaleAbs(image, alpha=1, beta=50)  # beta value increases brightness

            # Apply erosion
            eroded_image = cv2.erode(image, kernel, iterations=1)

            # Combine the eroded image with the original using the "darken" blend mode
            combined_image = cv2.min(image, eroded_image)

            # Save the processed image in the output folder
            output_path = os.path.join(output_folder, filename)
            cv2.imwrite(output_path, combined_image)
        else:
            print(f"Failed to read {image_path}")

print("Processing complete!")