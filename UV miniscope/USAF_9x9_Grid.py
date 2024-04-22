from PIL import Image
import numpy as np

# Load the images
#img_paths = [
#    '/media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_17_54_06.png', '/media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_17_54_13.png', '/media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_17_54_19.png',
#    '/media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_17_54_44.png', '/media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_17_54_38.png', '//media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_17_54_28.png',
#    '/media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_17_54_51.png', '/media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_17_54_59.png', '/media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_17_55_05.png'
#]

img_paths = [
    '/media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_17_55_49.png', '/media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_17_56_06.png', '/media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_17_56_20.png',
    '/media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_17_59_02.png', '/media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_17_58_20.png', '/media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_17_56_44.png',
    '/media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_17_59_30.png', '/media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_18_00_11.png', '/media/alingold/MenonLab/20240331_USAF_grid/miniscopeDeviceName_2024_03_31_18_00_52.png'
]

images = [Image.open(path) for path in img_paths]

# Define the crop coordinates for each image
# Since we want to crop out the corresponding corners of each image,
# we define the crop coordinates accordingly for a 3x3 grid.
# Each image is divided into 9 parts like a tic-tac-toe board.
# We then take the corresponding part from each image.

crop_coords = [
    (0, 0, 203, 203), (203, 0, 405, 203), (405, 0, 608, 203),
    (0, 203, 203, 405), (203, 203, 405, 405), (405, 203, 608, 405),
    (0, 405, 203, 608), (203, 405, 405, 608), (405, 405, 608, 608)
]

# Crop and resize the images accordingly
cropped_images = [img.crop(coords) for img, coords in zip(images, crop_coords)]

# Create an empty image to paste the cropped parts
grid_image = Image.new('RGB', (608, 608))

# Paste the cropped parts into the grid image
for i, img in enumerate(cropped_images):
    # Calculate where to paste the cropped image on the grid
    x = (i % 3) * 203
    y = (i // 3) * 203
    # Paste the cropped image
    grid_image.paste(img, (x, y))

# Save the final image
grid_image_path = '/home/alingold/rdmpy_20231220/output/USAF_9x9_Grid.png'
grid_image.save(grid_image_path)
grid_image.show()

grid_image_path
