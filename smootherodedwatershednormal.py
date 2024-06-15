from PIL import Image
import cv2
import numpy as np

# Load the image
img = cv2.imread('_input.png')

# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply adaptive thresholding
_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# Noise removal
kernel = np.ones((5,5),np.uint8)
opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)

# Sure background area
sure_bg = cv2.dilate(opening,kernel,iterations=3)

# Finding sure foreground area
dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
_, sure_fg = cv2.threshold(dist_transform,0.5*dist_transform.max(),255,0)  # Lowered threshold

# Finding unknown region
sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg,sure_fg)

# Marker labelling
_, markers = cv2.connectedComponents(sure_fg)

# Add one to all labels so that sure background is not 0, but 1
markers = markers+1

# Now, mark the region of unknown with zero
markers[unknown==255] = 0

markers = cv2.watershed(img,markers)

# Create a mask from the markers, only including sure regions
mask = np.ones_like(img, dtype=np.uint8) * 255  # Set all pixels to white
mask[markers == 1] = [0, 0, 0]  # Set sure foreground regions to black

mask = 255 - mask  # Invert the mask

# Add a border to the mask
border_size = 50  # Adjust this value as needed
mask_with_border = cv2.copyMakeBorder(mask, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=0)

# Apply the erosion to the mask with the border
eroded_mask_with_border = cv2.erode(mask_with_border, kernel, iterations=1)

# Remove the border from the eroded mask
# Remove the border from the eroded mask
eroded_mask = mask_with_border[border_size:-border_size or None, border_size:-border_size or None]

# Lucas: Version with more intense erosion, but has a border artifact
# eroded_mask = eroded_mask_with_border[border_size:-border_size or None, border_size:-border_size or None]


# cv2.imshow('Mask', mask)

cv2.imshow('Eroded Watershed', eroded_mask)

# Double the kernel size
kernel_size = 30 * 2

# Make sure the kernel size is odd
if kernel_size % 2 == 0:
    kernel_size += 1

# Apply Gaussian blur to the mask
smooth_mask = cv2.GaussianBlur(eroded_mask, (kernel_size, kernel_size), 0)

# cv2.imshow('Smooth Watershed', smooth_mask)

# Create a more blurred version of smooth_mask
top_layer = cv2.GaussianBlur(smooth_mask, (kernel_size, kernel_size), 0)

# Normalize the images to the range [0, 1] because cv2.multiply expects this range
smooth_mask = smooth_mask.astype(float) / 255
top_layer = top_layer.astype(float) / 255

# Blend the two layers together using the "Multiply" blend mode
blended = cv2.multiply(smooth_mask, top_layer)

# Convert the blended image back to the range [0, 255]
blended = (blended * 255).astype(np.uint8)

# cv2.imshow('Blended Watershed', blended)

# cv2.imwrite('eroded_watershed.png', eroded_mask)
# cv2.imwrite('smooth_watershed.png', smooth_mask)
cv2.imwrite('blended_watershed.png', blended)

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
normal_map_pil.save('2xfossil2d_normal.png')

cv2.waitKey(0)
cv2.destroyAllWindows()