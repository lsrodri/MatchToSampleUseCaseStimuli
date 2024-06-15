import os
import cv2
import numpy as np
from skimage import io, feature, color
from skimage.measure import shannon_entropy
from scipy import ndimage

# Function to calculate the fractal dimension of an image
def fractal_dimension(Z, threshold=0.9):
    # Only for 2d image
    assert(len(Z.shape) == 2)

    def boxcount(Z, k):
        S = np.add.reduceat(
            np.add.reduceat(Z, np.arange(0, Z.shape[0], k), axis=0),
                               np.arange(0, Z.shape[1], k), axis=1)

        # We count non-empty (0) and non-full boxes (k*k)
        return len(np.where((S > 0) & (S < k*k))[0])

    # Transform Z into a binary array
    Z = (Z < threshold)

    # Minimal dimension of image
    p = min(Z.shape)

    # Greatest power of 2 less than or equal to p
    n = 2**np.floor(np.log(p)/np.log(2))

    # Extract the exponent
    n = int(np.log(n)/np.log(2))

    # Build successive box sizes (from 2**n down to 2**1)
    sizes = 2**np.arange(n, 1, -1)

    # Actual box counting with decreasing size
    counts = []
    for size in sizes:
        counts.append(boxcount(Z, size))

    # Fit the successive log(sizes) with log (counts)
    coeffs = np.polyfit(np.log(sizes), np.log(counts), 1)
    return -coeffs[0]

# Function to calculate the edge detection score using Canny edge detector
def edge_detection_score(image):
    edges = feature.canny(image)
    return np.sum(edges)

# Path to the folder containing the images
folder_path = './stimuli'

# List to hold the complexity scores
complexity_scores = []

# Process each image in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.png'):
        image_path = os.path.join(folder_path, filename)
        image = io.imread(image_path, as_gray=True)

        # Calculate entropy
        entropy = shannon_entropy(image)

        # Calculate fractal dimension
        fractal_dim = fractal_dimension(image)

        # Calculate edge detection score
        edge_score = edge_detection_score(image)

        # Append the scores to the list
        complexity_scores.append({
            'filename': filename,
            'entropy': entropy,
            'fractal_dimension': fractal_dim,
            'edge_detection_score': edge_score
        })

# Print the complexity scores
for score in complexity_scores:
    print(score)