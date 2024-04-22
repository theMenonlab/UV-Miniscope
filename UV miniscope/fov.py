import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
def calculate_average_intensity(image_data):
    # Define the center of the image
    center_y, center_x = np.array(image_data.shape) // 2
    # Define delta_r and scale factor
    delta_r = 5
    scale_factor = 0.618  # pixels per micrometer
    # Create an array where each value is the distance from the center
    Y, X = np.ogrid[:image_data.shape[0], :image_data.shape[1]]
    distances_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
    # Calculate the average pixel intensity for each ring
    average_intensities = []
    num_rings = int(np.max(distances_from_center) // delta_r)
    for i in range(num_rings):
        mask = ((distances_from_center >= i * delta_r) & (distances_from_center < (i+1) * delta_r))
        ring_pixel_values = image_data[mask]
        average_intensity = np.mean(ring_pixel_values) if ring_pixel_values.size > 0 else 0
        average_intensities.append(average_intensity)
    # Find the maximum average intensity and the threshold radius
    max_intensity = max(average_intensities)
    threshold_radius = next(radius * delta_r for radius, intensity in enumerate(average_intensities) if intensity < max_intensity / 2)
    # Convert radius and ring numbers to micrometers
    threshold_radius_micrometers = threshold_radius / scale_factor
    diameters_in_micrometers = np.arange(len(average_intensities)) * delta_r * 2 / scale_factor
    return diameters_in_micrometers, average_intensities, threshold_radius_micrometers
# Image paths and their respective FOVs
image_paths = [
    ('/home/alingold/rdmpy_20231220/output/20240119_single (copy)/averaged_light.png', 'Ave Light Field'),
    ('/home/alingold/rdmpy_20231220/output/20240119_single (copy)/normalized/averaged_light_normalized.png', 'Min Max Normalized'),
    ('/home/alingold/rdmpy_20231220/output/20240119_single (copy)/normalized/corrected_0.2/averaged_light_normalized_corrected.png', 'Field Corrected'),
    ('/home/alingold/rdmpy_20231220/output/20240119_single (copy)/normalized/corrected_0.2/normalized_std/averaged_light_normalized_corrected_normalized.png', 'Field Corrected STD Normalized'),
]
# Plot the data for each image
plt.figure(figsize=(10, 5))
for image_path, label in image_paths:
    image = Image.open(image_path)
    image_data = np.array(image)
    # Calculate average intensity and FOV
    diameters, average_intensities, threshold_radius_micrometers = calculate_average_intensity(image_data)
    # Plot the data
    plt.plot(diameters, average_intensities, marker='o', label=f'{label}, FOV: {threshold_radius_micrometers * 2:.2f} μm')
plt.title('Average Pixel Intensity vs. Diameter in Micrometers')
plt.xlabel('Diameter (μm)')
plt.ylabel('Average Pixel Intensity')
plt.grid(True)
plt.legend()
plt.show()