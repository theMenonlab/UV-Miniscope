import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from skimage.measure import profile_line
from scipy.interpolate import make_interp_spline


horizontal = True

'''
# Single USAF plant beads on axis vertical bars
line_coords = [357, 225, 377, 225]  # vertical bars G7E1, x + 58, y - 46
line_coords = [357, 244, 379, 244]  # vertical bars G7E2
line_coords = [359, 263, 381, 263]  # vertical bars G7E3
line_coords = [360, 279, 384, 279]  # vertical bars G7E4
line_coords = [361, 293, 384, 293]  # vertical bars G7E5
line_coords = [363, 305, 386, 305]  # vertical bars G7E6

# Grid USAF plant beads on axis horizontal bars
line_coords = [380, 219, 380, 239]  # horizontal bars G7E1
line_coords = [381, 240, 381, 260]  # horizontal bars G7E2
line_coords = [381, 257, 381, 274]  # horizontal bars G7E3
line_coords = [382, 274, 382, 289]  # horizontal bars G7E4
line_coords = [383, 289, 383, 302]  # horizontal bars G7E5
line_coords = [383, 302, 383, 322]  # horizontal bars G7E6


# Single USAF plant beads on axis vertical bars
line_coords = [300, 271, 322, 271]  # vertical bars G7E1
line_coords = [300, 290, 322, 290]  # vertical bars G7E2
line_coords = [302, 308, 324, 308]  # vertical bars G7E3
line_coords = [303, 324, 327, 324]  # vertical bars G7E4
line_coords = [304, 338, 327, 338]  # vertical bars G7E5
line_coords = [306, 350, 329, 350]  # vertical bars G7E6

# Single USAF plant beads on axis horizontal bars
line_coords = [324, 265, 324, 285]  # horizontal bars G7E1
line_coords = [325, 286, 325, 306]  # horizontal bars G7E2
line_coords = [326, 303, 326, 320]  # horizontal bars G7E3
line_coords = [327, 320, 327, 335]  # horizontal bars G7E4
line_coords = [328, 335, 328, 348]  # horizontal bars G7E5
line_coords = [329, 348, 329, 360]  # horizontal bars G7E6

#grid focus plant beads off axis horrizontal bars
line_coords = [551, 215, 551, 235]  # horizontal bars G7E1 grid focus plant beads
line_coords = [551, 237, 551, 255]  # horizontal bars G7E2 grid focus plant beads
line_coords = [552, 255, 552, 273]  # horizontal bars G7E3 grid focus plant beads
line_coords = [553, 273, 553, 288]  # horizontal bars G7E4 grid focus plant beads
line_coords = [553, 288, 553, 302]  # horizontal bars G7E5 grid focus plant beads
line_coords = [553, 302, 553, 314]  # horizontal bars G7E6 grid focus plant beads

#grid focus plant beads off axis vertical bars
line_coords = [525, 221, 547, 221]  # vertical bars G7E1 grid focus plant beads
line_coords = [528, 241, 548, 241]  # vertical bars G7E2 grid focus plant beads
line_coords = [530, 260, 550, 260]  # vertical bars G7E3 grid focus plant beads
line_coords = [532, 276, 552, 276]  # vertical bars G7E4 grid focus plant beads
line_coords = [532, 291, 552, 291]  # vertical bars G7E5 grid focus plant beads
line_coords = [535, 304, 555, 304]  # vertical bars G7E6 grid focus plant beads
'''
line_coords = [553, 302, 553, 314]  # horizontal bars G7E6 grid focus plant beads
line_coords = [380, 219, 380, 239]  # horizontal bars G7E1  # horizontal bars G7E1
line_coords = [551, 215, 551, 235]  # horizontal bars G7E1 grid focus plant beads


# Paths to your image files
img_paths = [ #Single USAF plant beads
    '/home/alingold/rdmpy_20231220/output/20240109_SingleUSAF_20231228_singleBeads (copy)/measurement.png',
    '/home/alingold/rdmpy_20231220/output/20240109_SingleUSAF_20231228_singleBeads (copy)/normalized/corrected_0.2/normalized_std/2_ring_deconvolve_normalized_corrected_normalized.png',
    '/home/alingold/rdmpy_20231220/output/20240109_SingleUSAF_20231228_singleBeads (copy)/normalized/corrected_0.2/normalized_std/3_space_invariant_normalized_corrected_normalized.png',
    '/home/alingold/rdmpy_20231220/output/20240109_SingleUSAF_20231228_singleBeads (copy)/normalized/corrected_0.2/normalized_std/4_blind_1e-3_normalized_corrected_normalized.png'
]


img_paths = [ #USAF grid no focus plant beads
    '/home/alingold/rdmpy_20231220/output/USAF_grid_no_focus_plant_beads/measurement.png',
    '/home/alingold/rdmpy_20231220/output/USAF_grid_no_focus_plant_beads/normalized/corrected_0.2/normalized_std/ring_deconvolve_normalized_corrected_normalized.png',
    '/home/alingold/rdmpy_20231220/output/USAF_grid_no_focus_plant_beads/normalized/corrected_0.2/normalized_std/space_invariant_normalized_corrected_normalized.png',
    '/home/alingold/rdmpy_20231220/output/USAF_grid_no_focus_plant_beads/normalized/corrected_0.2/normalized_std/blind_1e-3_normalized_corrected_normalized.png'
]

# Custom legend labels
legend_labels = [
    'Measurement',
    'Ring DC',
    'Wiener DC',
    'Blind DC'
]

# Initialize Figure 1 for plotting all the intensity profiles later
plt.figure(0)
plt.xlabel('Distance along the line (μm)')
plt.ylabel('Normalized Mean Pixel Intensity')

# For storing smoothed lines and their labels for later plotting
y_smooth_lines = []
line_labels = []
original_profiles = []
x_values = []

# Loop through each image file
for img_path, label in zip(img_paths, legend_labels):
    # Read and display the image with lines
    img = Image.open(img_path)
    img_array = np.array(img)

    # Initialize a new figure for each image to draw lines on it
    plt.figure(0)

    sum_intensity_profiles = None

    # Drawing lines and accumulating intensity profiles
    for i in range(10):
        if horizontal:
            current_line_coords = (line_coords[0] + i, line_coords[1], line_coords[2] + i, line_coords[3])
            intensity_profile = profile_line(img_array, (current_line_coords[1], current_line_coords[0]), (current_line_coords[3], current_line_coords[2]))
        else:
            current_line_coords = (line_coords[0], line_coords[1] + i, line_coords[2], line_coords[3] + i)
            intensity_profile = profile_line(img_array, (current_line_coords[1], current_line_coords[0]), (current_line_coords[3], current_line_coords[2]))
        if sum_intensity_profiles is None:
            sum_intensity_profiles = intensity_profile
        else:
            sum_intensity_profiles += intensity_profile

        # Draw line on the image
        plt.plot([current_line_coords[0], current_line_coords[2]], [current_line_coords[1], current_line_coords[3]], 'r-')
    
    

    # Calculate and smooth the average intensity profile
    avg_intensity_profiles = sum_intensity_profiles / 10 / 255  # Normalize

    print(f"Average pixel values for {label}: {avg_intensity_profiles}")
    '''
    profile = avg_intensity_profiles
    max_1 = np.nanmax(profile)
    max_1_index = np.nanargmax(profile)
    profile[[max_1_index, max_1_index + 1, max_1_index - 1]] = np.nan
    max_2 = np.nanmax(profile)
    max_2_index = np.nanargmax(profile)
    profile[[max_2_index, max_2_index + 1, max_2_index - 1]] = np.nan
    max_3 = np.nanmax(profile)
    max_3_index = np.nanargmax(profile)
    profile[[max_3_index, max_3_index + 1, max_3_index - 1]] = np.nan

    profile_min_1 = avg_intensity_profiles[max_1_index:max_2_index]
    profile_min_2 = avg_intensity_profiles[max_2_index:max_3_index]
    print(f'profile_min_1: {profile_min_1}')
    print(f'profile_min_2: {profile_min_2}')
    min_1 = np.min(profile_min_1)
    min_2 = np.min(profile_min_2)

    max_all = [max_1, max_2, max_3]
    min_all = [min_1, min_2]
    print(f'label: {label}')
    print(f"max: {max_all}")
    print(f"min: {min_all}")
    '''

    x = np.arange(len(avg_intensity_profiles))
    spline = make_interp_spline(x, avg_intensity_profiles, k=3)  # Cubic spline
    x_smooth = np.linspace(x.min(), x.max(), 300)  # For smoother curve
    y_smooth = spline(x_smooth)

    y_smooth_lines.append(y_smooth)
    line_labels.append(label)
    x_values.append(x)
    original_profiles.append(avg_intensity_profiles)

img_show = Image.open(img_paths[0])
img_array_show = np.array(img_show)
plt.imshow(img_array_show, cmap='gray')
plt.axis('off')  # Hide axes
plt.title(f"Lines on measurement")
plt.show()  # Display the image with lines


# Plot all smoothed lines on the same chart
plt.figure(figsize=(11, 11))
for y_smooth, x, original, label in zip(y_smooth_lines, x_values, original_profiles, legend_labels):
    plt.plot(y_smooth, label=label, linewidth=3)  # Smoothed line
    plt.plot(x * 300 / (len(original) - 1), original, 'x', color='black', markersize=15, markeredgewidth=3)  # Original data points

    
plt.rcParams.update({'font.size': 12}) # Increase font size
# Adjust x-axis ticks to reflect the actual scale
current_ticks = plt.xticks()[0]  # Get current x-axis tick positions
new_tick_labels = [f"{tick / 11.54:.1f}" for tick in current_ticks]  # Divide each tick by 11.54 and format
plt.xticks(current_ticks, new_tick_labels, fontsize=30)  # Set new tick labels
plt.yticks(fontsize=30)  # Increase y-axis tick font size
plt.xlim(0, 300)
#plt.xticks(ticks=np.linspace(0, 300, 5), labels=[f"{x:.2f}" for x in np.linspace(0, len(avg_intensity_profiles)/11.54, 5)])
plt.xlabel('Distance along the line (μm)', fontsize=30)
plt.ylabel('Mean Pixel Intensity', fontsize=30)
#plt.legend(loc='upper right', fontsize=20)
#plt.title('(F) Intensity Profiles USAF G7E1 Vertical', fontsize=30)
plt.tight_layout()
plt.show()