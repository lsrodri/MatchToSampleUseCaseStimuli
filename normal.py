import cv2
import numpy as np
from PIL import Image

# Load the image
blended = cv2.imread('blended_watershed.png', cv2.IMREAD_GRAYSCALE)



# Convert the OpenCV image (in BGR format) to a PIL image (in RGB format)
blended_rgb = cv2.cvtColor(blended, cv2.COLOR_BGR2RGB)
blended_pil = Image.fromarray(blended_rgb)

# Convert the image to grayscale
blended_gray = blended_pil.convert('L')

# Convert the grayscale image to a numpy array
blended_array = np.array(blended_gray)

# Compute the x and y gradients
gradient_x = np.gradient(blended_array, axis=1)
gradient_y = np.gradient(blended_array, axis=0)

# Normalize to 0.0 - 1.0
gradient_x = (gradient_x - np.min(gradient_x)) / (np.max(gradient_x) - np.min(gradient_x))
gradient_y = (gradient_y - np.min(gradient_y)) / (np.max(gradient_y) - np.min(gradient_y))

# Compute the simple z gradient
gradient_z = np.ones_like(gradient_x)

# Create the normal map
normal_map = np.dstack((gradient_x, gradient_y, gradient_z))

# Normalize the normal map
norm = np.sqrt(np.power(normal_map[..., 0], 2) + np.power(normal_map[..., 1], 2) + np.power(normal_map[..., 2], 2))
normal_map[..., 0] /= norm
normal_map[..., 1] /= norm
normal_map[..., 2] /= norm

# Scale from 0.0 - 1.0 to 0 - 255
normal_map = (normal_map * 255).astype(np.uint8)

# Convert the normal map to a PIL image
normal_map_pil = Image.fromarray(normal_map, 'RGB')

# Display the normal map
normal_map_pil.show()

# Save the normal map
normal_map_pil.save('normal_map.png')