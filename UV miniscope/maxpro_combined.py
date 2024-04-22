import os
import shutil
import cv2
import numpy as np

# Base directory where your timelapse images are stored
base_dir = '/media/alingold/MenonLab/20240402_white_rot_timelapse'

# Directory containing manually selected in-focus images
best_focus_dir = os.path.join(base_dir, 'in_focus')

# Directory to save the new folders with the selected images
output_base_dir = os.path.join(base_dir, 'surrounding_images')

# List and sort all images in the base directory
all_images = sorted(os.listdir(base_dir))

# List and sort all in-focus images
in_focus_images = sorted(os.listdir(best_focus_dir))

# Process each in-focus image
for in_focus_image in in_focus_images:
    # Find the index of the in-focus image in the list of all images
    if in_focus_image in all_images:
        index = all_images.index(in_focus_image)
        
        # Calculate the indices for the 3 preceding and 3 succeeding images
        surrounding_indices = range(max(0, index - 3), min(index + 4, len(all_images)))

        for idx in surrounding_indices:
            if idx == index:
                continue  # Skip the in-focus image itself

            # Get the filename of the surrounding image
            surrounding_image = all_images[idx]

            # Determine the output folder based on the index difference
            output_folder_name = f'{idx - index:+d}'  # Naming folders as +1, +2, -1, -2, etc.
            output_folder_path = os.path.join(output_base_dir, output_folder_name)

            # Create the output folder if it doesn't exist
            if not os.path.exists(output_folder_path):
                os.makedirs(output_folder_path)

            # Source path of the image to be copied
            source_path = os.path.join(base_dir, surrounding_image)

            # Copy the image to the respective folder
            shutil.copy(source_path, output_folder_path)
    else:
        print(f"In-focus image {in_focus_image} not found in base directory.")



# Paths to the directories containing the images
directories = [
    os.path.join(output_base_dir, "+3"),
    os.path.join(output_base_dir, "+2"),
    os.path.join(output_base_dir, "+1"),
    best_focus_dir,
    os.path.join(output_base_dir, "-1"),
    os.path.join(output_base_dir, "-2"),
    os.path.join(output_base_dir, "-3"),
]

# Ensure all directories have the same number of images
num_images = len(os.listdir(directories[0]))
for directory in directories[1:]:
    if len(os.listdir(directory)) != num_images:
        raise ValueError("Directories do not contain the same number of images")

# Directory to save the maximum projection image
output_directory = os.path.join(base_dir, 'maxpro')
os.makedirs(output_directory, exist_ok=True)

# Loop through each set of images and create the maximal projection
for i in range(num_images):  # Start from 0 to include all images
    # Initialize the maximum intensity image with zeros
    first_image_path = os.path.join(directories[0], sorted(os.listdir(directories[0]))[i])
    first_image = cv2.imread(first_image_path)
    if first_image is None:
        raise ValueError(f"Image {first_image_path} could not be loaded")
    max_intensity_image = np.zeros_like(first_image)
    
    for directory in directories:
        image_path = os.path.join(directory, sorted(os.listdir(directory))[i])
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Image {image_path} could not be loaded")

        # Update the maximum intensity image
        max_intensity_image = np.maximum(max_intensity_image, image)

    # Save the maximum intensity image
    filename = f"max_projection_{i+1}.png"  # Use i+1 for naming to match your original code
    max_intensity_image_path = os.path.join(output_directory, filename)
    cv2.imwrite(max_intensity_image_path, max_intensity_image)

print("Maximum intensity projection is completed.")